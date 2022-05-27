import jsonpointer
from django.db import models

from jsondataferretexampleapp import (  # noqa
    TYPE_ORGANISATION_PUBLIC_ID,
    TYPE_PROJECT_PUBLIC_ID,
)


class BaseModel(models.Model):
    public_id = models.CharField(max_length=200, unique=True)
    exists = models.BooleanField(default=False)
    status_public = models.BooleanField(default=False)
    data_public = models.JSONField(default=dict)
    data_private = models.JSONField(default=dict)

    def has_data_public_field(self, field):
        try:
            return bool(
                jsonpointer.resolve_pointer(
                    self.data_public,
                    field,
                )
            )
        except jsonpointer.JsonPointerException:
            return False

    def get_data_public_field(self, field):
        try:
            return jsonpointer.resolve_pointer(
                self.data_public,
                field,
            )
        except jsonpointer.JsonPointerException:
            return ""

    def has_data_private_field(self, field):
        try:
            return bool(
                jsonpointer.resolve_pointer(
                    self.data_private,
                    field,
                )
            )
        except jsonpointer.JsonPointerException:
            return False

    def get_data_private_field(self, field):
        try:
            return jsonpointer.resolve_pointer(
                self.data_private,
                field,
            )
        except jsonpointer.JsonPointerException:
            return ""

    class Meta:
        abstract = True


class Organisation(BaseModel):
    type_id = TYPE_ORGANISATION_PUBLIC_ID


class Project(BaseModel):
    type_id = TYPE_PROJECT_PUBLIC_ID
