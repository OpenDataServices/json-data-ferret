import json

import jsonpointer
import pygments
import pygments.formatters
import pygments.lexers.data
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models

from jsondataferret import EVENT_MODE_REPLACE


class Type(models.Model):
    public_id = models.CharField(max_length=200, unique=True)
    title = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)


class Record(models.Model):
    type = models.ForeignKey(Type, on_delete=models.PROTECT)
    public_id = models.CharField(max_length=200)
    cached_exists = models.BooleanField(default=False)
    cached_data = JSONField(default=dict)
    cached_jsonschema_validation_errors = JSONField(null=True, blank=True)

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
