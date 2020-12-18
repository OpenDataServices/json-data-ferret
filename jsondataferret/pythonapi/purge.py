from jsondataferret.models import Edit, Event


def purge_record(record):
    # Remove all Edits linked
    for edit in Edit.objects.filter(record=record):
        edit.delete()

    # Remove the Record
    record.delete()

    # Remove any Events than now have no Edits
    sql = (
        "SELECT jsondataferret_event.* FROM jsondataferret_event "
        + "LEFT JOIN jsondataferret_edit ON "
        + "jsondataferret_edit.creation_event_id = jsondataferret_event.id OR "
        + "jsondataferret_edit.approval_event_id = jsondataferret_event.id OR "
        + "jsondataferret_edit.refusal_event_id = jsondataferret_event.id "
        + "WHERE jsondataferret_edit.id IS NULL"
    )
    for event in Event.objects.raw(sql):
        event.delete()
