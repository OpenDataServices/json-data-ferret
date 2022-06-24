import json

import json_merge_patch
import jsonmerge
import jsonpointer
import jsonschema
import pygments
import pygments.formatters
import pygments.lexers.data
from django.conf import settings
from django.db import models

from jsondataferret import EVENT_MODE_MERGE, EVENT_MODE_REPLACE

from .utils import get_field_list_from_json, get_field_list_from_json_with_differences


class JSONDataFerret(models.Model):
    class Meta:
        managed = False
        permissions = (("admin", "Can Admin All Data Managed by JSON Data Ferret"),)


class Type(models.Model):
    public_id = models.CharField(max_length=200, unique=True)
    title = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.public_id}: {self.title}"


class RecordManager(models.Manager):
    def filter_needs_moderation_by_type(self, type_model):
        return Record.objects.raw(
            "SELECT jsondataferret_record.* "
            + "FROM jsondataferret_record "
            + "JOIN jsondataferret_edit ON "
            + "jsondataferret_edit.record_id = jsondataferret_record.id AND "
            + "jsondataferret_edit.refusal_event_id IS NULL AND "
            + "jsondataferret_edit.approval_event_id IS NULL "
            + "WHERE jsondataferret_record.type_id = %s "
            + "GROUP BY jsondataferret_record.id "
            + "ORDER BY jsondataferret_record.id ASC",
            [type_model.id],
        )


class Record(models.Model):
    type = models.ForeignKey(Type, on_delete=models.PROTECT)
    public_id = models.CharField(max_length=200)
    cached_exists = models.BooleanField(default=False)
    cached_data = models.JSONField(default=dict)
    cached_jsonschema_validation_errors = models.JSONField(null=True, blank=True)
    objects = RecordManager()

    class Meta:
        unique_together = (
            "type",
            "public_id",
        )

    def get_cached_data_html(self):
        return pygments.highlight(
            json.dumps(self.cached_data, indent=4),
            pygments.lexers.data.JsonLexer(),
            pygments.formatters.HtmlFormatter(),
        )

    def get_cached_data_fields(self):
        return get_field_list_from_json(
            self.type.public_id,
            self.cached_data,
        )

    def validate_with_json_schema(self, json_schema):
        # TODO use correct version of Draft Validator
        schema_validator = jsonschema.Draft7Validator(json_schema)
        errors = sorted(schema_validator.iter_errors(self.cached_data), key=str)
        if errors:
            self.cached_jsonschema_validation_errors = [
                {
                    "message": err.message,
                    "path": list(err.path),
                    "path_str": "/".join([str(element) for element in list(err.path)]),
                    "schema_path": list(err.schema_path),
                    "schema_path_str": "/".join(
                        [str(element) for element in list(err.schema_path)]
                    ),
                }
                for err in errors
            ]
        else:
            self.cached_jsonschema_validation_errors = None


class EventManager(models.Manager):
    def filter_by_record(self, record):
        return Event.objects.raw(
            "SELECT jsondataferret_event.* "
            + "FROM jsondataferret_event "
            + "JOIN jsondataferret_edit ON "
            + "jsondataferret_edit.creation_event_id = jsondataferret_event.id OR "
            + "jsondataferret_edit.refusal_event_id = jsondataferret_event.id OR "
            + "jsondataferret_edit.approval_event_id = jsondataferret_event.id "
            + "WHERE jsondataferret_edit.record_id = %s "
            + "GROUP BY jsondataferret_event.id "
            + "ORDER bY jsondataferret_event.created ASC",
            [record.id],
        )


class Event(models.Model):
    public_id = models.CharField(max_length=200, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True
    )
    comment = models.TextField(default="")
    objects = EventManager()

    def get_records(self, limit=-1, approved_edits_only=False):
        sql = (
            "SELECT jsondataferret_record.id, jsondataferret_record.public_id, "
            + "max(jsondataferret_type.public_id) AS type_public_id, max(jsondataferret_type.title) AS type_title  FROM jsondataferret_record "
            + "JOIN jsondataferret_edit ON jsondataferret_edit.record_id = jsondataferret_record.id "
            + "JOIN jsondataferret_type ON jsondataferret_record.type_id = jsondataferret_type.id "
            + (
                "WHERE jsondataferret_edit.approval_event_id = %(event_id)s "
                if approved_edits_only
                else "WHERE jsondataferret_edit.creation_event_id = %(event_id)s OR jsondataferret_edit.refusal_event_id = %(event_id)s OR jsondataferret_edit.approval_event_id = %(event_id)s"
            )
            + "GROUP BY jsondataferret_record.id "
            + "ORDER BY max(jsondataferret_type.title) ASC,  jsondataferret_record.public_id ASC"
        )
        params = {"event_id": self.id}
        if int(limit) > 0:
            sql += " LIMIT %(limit)s"
            params["limit"] = int(limit)
        records = Record.objects.raw(sql, params)
        return records

    def get_records_summary(self):
        records = self.get_records(limit=5, approved_edits_only=False)
        return {"records": records[:4], "more": len(records) == 5}


class Edit(models.Model):
    public_id = models.CharField(max_length=200, unique=True)
    # link to record
    record = models.ForeignKey(Record, on_delete=models.PROTECT)
    # the events that changed this
    creation_event = models.ForeignKey(
        Event, on_delete=models.PROTECT, related_name="edits_created"
    )
    approval_event = models.ForeignKey(
        Event,
        on_delete=models.PROTECT,
        related_name="edits_approved",
        null=True,
        blank=True,
    )
    refusal_event = models.ForeignKey(
        Event,
        on_delete=models.PROTECT,
        related_name="edits_refused",
        null=True,
        blank=True,
    )
    # the changes in the edit
    mode = models.CharField(max_length=200, default=EVENT_MODE_REPLACE)
    data_key = models.TextField(default="/")
    data = models.JSONField(default=dict)

    # Use get_previous_cached_record_history() to access information.
    # _previous_cached_record_history variable caches result to avoid repeated DB lookups.
    # -1 means it hasn't been looked for yet, None means nothing exists or it could be a CachedRecordHistory instance.
    _previous_cached_record_history = -1

    def get_data_html(self):
        return pygments.highlight(
            json.dumps(self.data, indent=4),
            pygments.lexers.data.JsonLexer(),
            pygments.formatters.HtmlFormatter(),
        )

    def has_data_field(self, field):
        # TODO work with data_key field.
        try:
            return bool(
                jsonpointer.resolve_pointer(
                    self.data,
                    field,
                )
            )
        except jsonpointer.JsonPointerException:
            return False

    def get_data_field(self, field):
        # TODO work with data_key field.
        try:
            return jsonpointer.resolve_pointer(
                self.data,
                field,
            )
        except jsonpointer.JsonPointerException:
            return False

    def get_data_fields(self):
        # TODO work with data_key field.
        return get_field_list_from_json(
            self.record.type.public_id,
            self.data,
        )

    def get_previous_cached_record_history(self):
        """For the record of this edit, returns the previous CachedRecordHistory before this event was applied.
        If this is the first event to change a record, this method could return None."""
        if self._previous_cached_record_history == -1:
            self._previous_cached_record_history = (
                CachedRecordHistory.objects.filter(
                    record=self.record, event__created__lt=self.creation_event.created
                )
                .order_by("-event__created")
                .first()
            )
        return self._previous_cached_record_history

    def get_new_data_when_edit_applied_to_data(self, current_data):
        if self.mode == EVENT_MODE_REPLACE:
            if self.data_key == "/":
                return self.data
            else:
                raise Exception("TODO Not Implemented Yet")
        elif self.mode == EVENT_MODE_MERGE:
            if self.data_key == "/":
                return jsonmerge.merge(current_data, self.data)
            else:
                raise Exception("TODO Not Implemented Yet")

    def get_new_data_when_edit_applied_to_latest_record_cached_data(self):
        """Applies this edit to the latest version of a record as the edit is being approved.
        Returns the new latest version of a record."""
        return self.get_new_data_when_edit_applied_to_data(self.record.cached_data)

    def get_new_data_when_edit_applied_to_previous_cached_record_history(self):
        pcrh = self.get_previous_cached_record_history()
        if pcrh:
            return self.get_new_data_when_edit_applied_to_data(pcrh.data)
        else:
            return self.get_new_data_when_edit_applied_to_data({})

    def get_new_data_when_edit_applied_to_previous_cached_record_history_html(self):
        return pygments.highlight(
            json.dumps(
                self.get_new_data_when_edit_applied_to_previous_cached_record_history(),
                indent=4,
            ),
            pygments.lexers.data.JsonLexer(),
            pygments.formatters.HtmlFormatter(),
        )

    def get_data_diff_previous_cached_record_history(self):
        """Returns dict of differences between this version of the record and the previous one"""
        pcrh = self.get_previous_cached_record_history()
        if pcrh:
            return json_merge_patch.create_patch(
                pcrh.data,
                self.get_new_data_when_edit_applied_to_previous_cached_record_history(),
            )
        else:
            return (
                self.get_new_data_when_edit_applied_to_previous_cached_record_history()
            )

    def get_data_diff_previous_cached_record_history_html(self):
        """HTML version of get_data_diff_previous_cached_record_history, for use in templates"""
        return pygments.highlight(
            json.dumps(self.get_data_diff_previous_cached_record_history(), indent=4),
            pygments.lexers.data.JsonLexer(),
            pygments.formatters.HtmlFormatter(),
        )

    def get_data_fields_include_differences_from_latest_data(self):
        """Returns list of fields with boolean key different_from_latest_value to indicate if they have changed from the current latest data.
        This is intended to be used on edits not moderated yet, to show what the affect of approving them would be."""
        if self.approval_event or self.refusal_event:
            raise Exception(
                "get_data_fields_include_differences_from_latest_data should only be used on edits not moderated yet"
            )
        # TODO work with data_key field.
        return get_field_list_from_json_with_differences(
            self.record.type.public_id,
            self.record.cached_data if self.record.cached_exists else {},
            self.get_new_data_when_edit_applied_to_latest_record_cached_data(),
            "different_from_latest_value",
        )

    def get_data_fields_include_differences_from_previous_data(self):
        """Returns list of fields with boolean key different_from_previous_value to indicate if they have changed since this edit was created."""
        # TODO work with data_key field.
        previous_cached_record_history = self.get_previous_cached_record_history()
        return get_field_list_from_json_with_differences(
            self.record.type.public_id,
            previous_cached_record_history.data
            if previous_cached_record_history
            else {},
            self.get_new_data_when_edit_applied_to_previous_cached_record_history(),
            "different_from_previous_value",
        )


class CachedRecordHistory(models.Model):
    """Stores the historical state of data on a record AFTER a particular event has been applied to it.
    These are generated only after events with approved edits (created or refused edits do not change a record)
    """

    id = models.BigAutoField(primary_key=True)
    record = models.ForeignKey(Record, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    data = models.JSONField(default=dict)

    # Use get_previous_cached_record_history() to access information.
    # _previous_cached_record_history variable caches result to avoid repeated DB lookups.
    # -1 means it hasn't been looked for yet, None means nothing exists or it could be a CachedRecordHistory instance.
    _previous_cached_record_history = -1

    def get_data_html(self):
        return pygments.highlight(
            json.dumps(self.data, indent=4),
            pygments.lexers.data.JsonLexer(),
            pygments.formatters.HtmlFormatter(),
        )

    def get_previous_cached_record_history(self):
        """For any record, returns the previous CachedRecordHistory before this event was applied.
        If this is the first event to change a record, this method could return None."""
        if self._previous_cached_record_history == -1:
            self._previous_cached_record_history = (
                CachedRecordHistory.objects.filter(
                    record=self.record, event__created__lt=self.event.created
                )
                .order_by("-event__created")
                .first()
            )
        return self._previous_cached_record_history

    def get_data_diff_previous_cached_record_history(self):
        """Returns dict of differences between this version of the record and the previous one"""
        pcrh = self.get_previous_cached_record_history()
        if pcrh:
            return json_merge_patch.create_patch(pcrh.data, self.data)
        else:
            return self.data

    def get_data_diff_previous_cached_record_history_html(self):
        """HTML version of get_data_diff_previous_cached_record_history, for use in templates"""
        return pygments.highlight(
            json.dumps(self.get_data_diff_previous_cached_record_history(), indent=4),
            pygments.lexers.data.JsonLexer(),
            pygments.formatters.HtmlFormatter(),
        )

    def get_data_fields_include_differences_from_previous_data(self):
        """Returns list of fields with boolean key different_from_previous_value to indicate if they have changed"""
        pcrh = self.get_previous_cached_record_history()
        return get_field_list_from_json_with_differences(
            self.record.type.public_id,
            pcrh.data if pcrh else {},
            self.data,
            "different_from_previous_value",
        )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["record", "event"],
                name="cachedrecordhistory_unique_record_event",
            )
        ]
