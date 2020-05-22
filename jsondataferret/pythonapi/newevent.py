import uuid

from django.apps import apps
from django.db import transaction

from jsondataferret import EVENT_MODE_REPLACE
from jsondataferret.models import Edit, Event, Record, Type
from jsondataferret.pythonapi.runevents import apply_event


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


class NewEventApproval:
    def __init__(self, edit):
        self.edit = edit


class NewEventRejection:
    def __init__(self, edit):
        self.edit = edit


def newEvent(datas, user=None):
    record_ids = newEvent_apply(datas, user=user)

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
def newEvent_apply(datas, user=None):
    record_ids = []

    event = Event()
    event.public_id = uuid.uuid4()
    event.user = user
    event.save()

    for data in datas:

        if isinstance(data, NewEventData):

            if isinstance(data.type, str):
                types = Type.objects.filter(public_id=data.type)
                if len(types) == 0:
                    type = Type()
                    type.public_id = data.type
                    type.title = data.type
                    type.save()
                else:
                    type = types[0]
            else:
                type = data.type

            if isinstance(data.record, str):
                records = Record.objects.filter(type=type, public_id=data.record)
                if len(records) == 0:
                    record = Record()
                    record.type = type
                    record.public_id = data.record
                    record.save()
                else:
                    record = records[0]
            else:
                record = data.record

            edit = Edit()
            edit.public_id = uuid.uuid4()
            edit.record = record
            edit.creation_event = event
            if data.approved:
                edit.approval_event = event
            edit.mode = data.mode
            edit.data_key = data.key
            edit.data = data.data
            edit.save()

            if record.id not in record_ids:
                record_ids.append(record.id)

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
