from django.apps import apps
from django.conf import settings
from django.db import connection

from jsondataferret.models import Edit, Event, Record, Type
from jsondataferret.utils import apply_edit_get_new_cached_data


def clear_data_and_run_all_events():
    # Clear the cached values
    with connection.cursor() as cursor:
        cursor.execute(
            "update jsondataferret_record set cached_exists='f', cached_data='{}'"
        )

    # Run all events
    for event in Event.objects.filter().order_by("created"):
        apply_event(event)

    # Call any callbacks
    for type in Type.objects.filter():
        for name, app in apps.app_configs.items():
            if hasattr(app.module, "JSONDATAFERRET_HOOKS"):
                callback_name = app.module.JSONDATAFERRET_HOOKS
                try:
                    callback = __import__(
                        callback_name, globals(), locals(), ["on_update_callback"], 0
                    )
                    for record in Record.objects.filter(type=type):
                        callback.on_update_callback(record)
                except AttributeError:
                    # on_update_callback prob doesn't exist. This is fine.
                    pass


def apply_event(event):
    for edit in Edit.objects.filter(approval_event=event):

        # --------------------------------- Make new data
        edit.record.cached_data = apply_edit_get_new_cached_data(edit)

        # --------------------------------- Validate Result
        type_data = settings.JSONDATAFERRET_TYPE_INFORMATION.get(
            edit.record.type.public_id, {}
        )
        if type_data.get("json_schema"):
            edit.record.validate_with_json_schema(type_data.get("json_schema"))
        else:
            edit.record.cached_jsonschema_validation_errors = None

        # --------------------------------- Mark record existing (any data does that) and save!
        edit.record.cached_exists = True
        edit.record.save()
