import json

import jsonpointer
import jsonschema
import pygments
import pygments.formatters
import pygments.lexers.data
from django.conf import settings
from django.db import models

from jsondataferret import EVENT_MODE_REPLACE

from .utils import get_field_list_from_json


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

    def get_records(self, limit=-1):
        sql = (
            "SELECT jsondataferret_record.id, jsondataferret_record.public_id, "
            + "max(jsondataferret_type.public_id) AS type_public_id, max(jsondataferret_type.title) AS type_title  FROM jsondataferret_record "
            + "JOIN jsondataferret_edit ON jsondataferret_edit.record_id = jsondataferret_record.id "
            + "JOIN jsondataferret_type ON jsondataferret_record.type_id = jsondataferret_type.id "
            + "WHERE jsondataferret_edit.creation_event_id = %s OR jsondataferret_edit.refusal_event_id = %s OR jsondataferret_edit.approval_event_id = %s "
            + "GROUP BY jsondataferret_record.id "
            + "ORDER BY max(jsondataferret_type.title) ASC,  jsondataferret_record.public_id ASC"
        )
        params = [self.id, self.id, self.id]
        if int(limit) > 0:
            sql += " LIMIT %s"
            params.append(int(limit))
        records = Record.objects.raw(sql, params)
        return records

    def get_records_summary(self):
        records = self.get_records(limit=5)
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

    def get_data_fields_include_differences_from_latest_data(self):
        if self.approval_event or self.refusal_event:
            raise Exception(
                "get_data_fields_include_differences_from_latest_data should only be used on edits not moderated yet"
            )
        # TODO work with data_key field.
        if not self.record.cached_exists:
            # No existing data, so nothing special we can do here
            edit_fields = get_field_list_from_json(
                self.record.type.public_id,
                self.data,
            )
            for e in edit_fields:
                e["different_from_latest_value"] = True
            return edit_fields
        else:

            latest_fields = get_field_list_from_json(
                self.record.type.public_id, self.record.cached_data
            )
            latest_fields_by_key = {f["key"]: f for f in latest_fields}

            edit_fields = get_field_list_from_json(
                self.record.type.public_id,
                self.data,
            )
            edit_fields_by_key = {f["key"]: f for f in edit_fields}

            # This will collect changes where the field is in both old and new, and changes where a field exists in new only
            for field in edit_fields:
                latest_value = None
                if field["key"] in latest_fields_by_key:
                    latest_value = latest_fields_by_key[field["key"]]["value"]
                field["different_from_latest_value"] = latest_value != field["value"]

            # So new we have to add any changes where the field exists in old only
            for key, field_data in latest_fields_by_key.items():
                if key not in edit_fields_by_key:
                    field_data["different_from_latest_value"] = True
                    field_data["value"] = None
                    edit_fields.append(field_data)

            return edit_fields
