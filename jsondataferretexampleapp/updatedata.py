import copy

import jsonpointer

from jsondataferret.models import Record, Type
from jsondataferretexampleapp import (
    TYPE_ORGANISATION_FILTER_KEYS_LIST,
    TYPE_ORGANISATION_PUBLIC_ID,
    TYPE_PROJECT_FILTER_KEYS_LIST,
    TYPE_PROJECT_PUBLIC_ID,
)
from jsondataferretexampleapp.models import Organisation, Project


def update_all_data():

    try:
        type_organisation = Type.objects.get(public_id=TYPE_ORGANISATION_PUBLIC_ID)
        for organisation in Record.objects.filter(type=type_organisation):
            update_organisation(organisation)
    except Type.DoesNotExist:
        pass

    try:
        type_project = Type.objects.get(public_id=TYPE_PROJECT_PUBLIC_ID)
        for project in Record.objects.filter(type=type_project):
            update_project(project)
    except Type.DoesNotExist:
        pass


def update_organisation(record):

    try:
        organisation = Organisation.objects.get(public_id=record.public_id)
    except Organisation.DoesNotExist:
        organisation = Organisation()
        organisation.public_id = record.public_id

    # Exists
    organisation.exists = record.cached_exists
    # Status
    record_status = (
        record.cached_data.get("status", "").strip().lower()
        if isinstance(record.cached_data.get("status", ""), str)
        else ""
    )
    organisation.status_public = record.cached_exists and record_status == "public"
    # Public data
    organisation.data_public = (
        filter_values(record.cached_data, TYPE_ORGANISATION_FILTER_KEYS_LIST)
        if organisation.status_public
        else {}
    )
    # Private Data
    organisation.data_private = record.cached_data if record.cached_exists else {}
    # Finally, Save
    organisation.save()


def update_project(record):

    try:
        project = Project.objects.get(public_id=record.public_id)
    except Project.DoesNotExist:
        project = Project()
        project.public_id = record.public_id

    # Exists
    project.exists = record.cached_exists
    # Status
    record_status = (
        record.cached_data.get("status", "").strip().lower()
        if isinstance(record.cached_data.get("status", ""), str)
        else ""
    )
    project.status_public = record.cached_exists and record_status == "public"
    # Public data
    project.data_public = (
        filter_values(record.cached_data, TYPE_PROJECT_FILTER_KEYS_LIST)
        if project.status_public
        else {}
    )
    # Private Data
    project.data_private = record.cached_data if record.cached_exists else {}
    # Finally, Save
    project.save()


def filter_values(data, keys):
    data = copy.deepcopy(data)

    for key in keys:
        try:
            key_data = jsonpointer.resolve_pointer(data, key)
        except jsonpointer.JsonPointerException:
            # Data does not exist anyway, nothing to do!
            continue
        key_status = key_data.get("status", "") if isinstance(key_data, dict) else ""
        if isinstance(key_status, str) and key_status.strip().lower() == "public":
            pass
        else:
            jsonpointer.set_pointer(data, key, None)

    return data
