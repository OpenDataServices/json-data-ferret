import json

import jsonpointer
import jsonschema
import pygments
import pygments.formatters
import pygments.lexers.data
from django.conf import settings
from django.contrib.postgres.fields import JSONField
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
    cached_data = JSONField(default=dict)
    cached_jsonschema_validation_errors = JSONField(null=True, blank=True)
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
        return get_field_list_from_json(self.type.public_id, self.cached_data,)

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
    data = JSONField(default=dict)

    def get_data_html(self):
        return pygments.highlight(
            json.dumps(self.data, indent=4),
            pygments.lexers.data.JsonLexer(),
            pygments.formatters.HtmlFormatter(),
        )

    def has_data_field(self, field):
        # TODO work with data_key field.
        try:
            return bool(jsonpointer.resolve_pointer(self.data, field,))
        except jsonpointer.JsonPointerException:
            return False

    def get_data_field(self, field):
        # TODO work with data_key field.
        try:
            return jsonpointer.resolve_pointer(self.data, field,)
        except jsonpointer.JsonPointerException:
            return False

    def get_data_fields(self):
        return get_field_list_from_json(self.record.type.public_id, self.data,)
