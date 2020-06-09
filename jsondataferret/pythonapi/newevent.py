import uuid

import json_merge_patch
from django.apps import apps
from django.db import transaction

from jsondataferret import EVENT_MODE_REPLACE
from jsondataferret.models import Edit, Event, Record, Type
from jsondataferret.pythonapi.runevents import apply_event
from jsondataferret.utils import apply_edit_get_new_cached_data


class NewEventData:
    def __init__(
        self, type, record, data, mode=EVENT_MODE_REPLACE, key="/", approved=False
    ):
        self.type = type
        self.record = record
        self.key = key
        self.data = data
        self.mode = mode
        self.approved = approved

    def _build_type_and_record(self, create_if_dont_exist=True):
        # self.type and  self.record can be passed as objects or strings
        # If strings, the objects should be loaded. If flag set, created and saved if they don't exist.
        if isinstance(self.type, str):
            types = Type.objects.filter(public_id=self.type)
            if types:
                self.type = types[0]
            elif create_if_dont_exist:
                type_model = Type()
                type_model.public_id = self.type
                type_model.title = self.type
                type_model.save()
                self.type = type_model

        if isinstance(self.type, Type) and isinstance(self.record, str):
            records = Record.objects.filter(type=self.type, public_id=self.record)
            if records:
                self.record = records[0]
            elif create_if_dont_exist:
                record_model = Record()
                record_model.type = self.type
                record_model.public_id = self.record
                record_model.save()
                self.record = record_model

    def does_this_create_or_change_record(self):
        self._build_type_and_record(create_if_dont_exist=False)
        # If record not currently exist, it's creating something
        if not isinstance(self.record, Record):
            return True
        # If does exist, need to check content for changes
        edit = Edit()
        edit.record = self.record
        edit.mode = self.mode
        edit.data_key = self.key
        edit.data = self.data
        new_cached_data = apply_edit_get_new_cached_data(edit)
        patch = json_merge_patch.create_patch(self.record.cached_data, new_cached_data)
        has_patch = bool(patch)
        return has_patch


class NewEventApproval:
    def __init__(self, edit):
        self.edit = edit


class NewEventRejection:
    def __init__(self, edit):
        self.edit = edit


def newEvent(datas, user=None, comment=None):
    record_ids = newEvent_apply(datas, user=user, comment=comment)

    for name, app in apps.app_configs.items():
        if hasattr(app.module, "JSONDATAFERRET_HOOKS"):
            callback_name = app.module.JSONDATAFERRET_HOOKS
            try:
                callback = __import__(
                    callback_name, globals(), locals(), ["on_update_callback"], 0
                )
                for record_id in record_ids:
                    callback.on_update_callback(Record.objects.get(id=record_id))
            except AttributeError:
                # on_update_callback prob doesn't exist. This is fine. Should maybe log err to check tho
                pass


@transaction.atomic
def newEvent_apply(datas, user=None, comment=None):
    record_ids = []

    event = Event()
    event.public_id = uuid.uuid4()
    event.user = user
    event.comment = comment or ""
    event.save()

    for data in datas:

        if isinstance(data, NewEventData):

            data._build_type_and_record(create_if_dont_exist=True)

            edit = Edit()
            edit.public_id = uuid.uuid4()
            edit.record = data.record
            edit.creation_event = event
            if data.approved:
                edit.approval_event = event
            edit.mode = data.mode
            edit.data_key = data.key
            edit.data = data.data
            edit.save()

            if data.record.id not in record_ids:
                record_ids.append(data.record.id)

        elif isinstance(data, NewEventApproval):
            data.edit.approval_event = event
            data.edit.save()

            if data.edit.record.id not in record_ids:
                record_ids.append(data.edit.record.id)

        elif isinstance(data, NewEventRejection):
            data.edit.refusal_event = event
            data.edit.save()

            if data.edit.record.id not in record_ids:
                record_ids.append(data.edit.record.id)

    apply_event(event)

    return record_ids
