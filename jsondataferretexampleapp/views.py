import os
import random
import tempfile
import uuid

import spreadsheetforms.api
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

import jsondataferret
from jsondataferret.models import Edit, Event, Record, Type
from jsondataferret.pythonapi.newevent import NewEventData, newEvent
from jsondataferretexampleapp import (  # noqa
    TYPE_ORGANISATION_FIELD_LIST,
    TYPE_ORGANISATION_PUBLIC_ID,
    TYPE_PROJECT_FIELD_LIST,
    TYPE_PROJECT_PUBLIC_ID,
)

from .forms import (
    OrganisationImportForm,
    OrganisationMakeDisputedForm,
    OrganisationMakePrivateForm,
    OrganisationNewForm,
    ProjectImportForm,
    ProjectMakeDisputedForm,
    ProjectMakePrivateForm,
    ProjectNewForm,
)
from .models import Organisation, Project  # noqa

########################### Home Page


def index(request):
    return render(request, "jsondataferretexampleapp/index.html")


########################### Public - Organisation


def organisations_list(request):
    organisations = Organisation.objects.filter(exists=True, status_public=True)
    return render(
        request,
        "jsondataferretexampleapp/organisations.html",
        {"organisations": organisations},
    )


def organisation_index(request, public_id):
    try:
        organisation = Organisation.objects.get(
            exists=True, status_public=True, public_id=public_id
        )
    except Organisation.DoesNotExist:
        raise Http404("Organisation does not exist")
    field_data = {}
    for field in TYPE_ORGANISATION_FIELD_LIST:
        if organisation.has_data_public_field(field["key"]):
            field_data[field["title"]] = organisation.get_data_public_field(
                field["key"]
            )
    return render(
        request,
        "jsondataferretexampleapp/organisation/index.html",
        {"organisation": organisation, "field_data": field_data},
    )


########################### Public - Project


def projects_list(request):
    projects = Project.objects.filter(exists=True, status_public=True)
    return render(
        request, "jsondataferretexampleapp/projects.html", {"projects": projects},
    )


def project_index(request, public_id):
    try:
        project = Project.objects.get(
            exists=True, status_public=True, public_id=public_id
        )
    except Project.DoesNotExist:
        raise Http404("Project does not exist")
    field_data = {}
    for field in TYPE_PROJECT_FIELD_LIST:
        if project.has_data_public_field(field["key"]):
            field_data[field["title"]] = project.get_data_public_field(field["key"])
    return render(
        request,
        "jsondataferretexampleapp/project/index.html",
        {"project": project, "field_data": field_data},
    )


########################### Admin


@login_required
def admin_index(request):
    return render(request, "jsondataferretexampleapp/admin/index.html")


########################### Admin - Organisation


@login_required
def admin_organisations_list(request):
    try:
        type = Type.objects.get(public_id=TYPE_ORGANISATION_PUBLIC_ID)
    except Type.DoesNotExist:
        raise Http404("Type does not exist")
    organisations = Record.objects.filter(type=type)
    return render(
        request,
        "jsondataferretexampleapp/admin/organisations.html",
        {"organisations": organisations},
    )


@login_required
def admin_organisation_index(request, public_id):
    try:
        organisation = Organisation.objects.get(public_id=public_id)
    except Organisation.DoesNotExist:
        raise Http404("Organisation does not exist")
    field_data = {}
    for field in TYPE_ORGANISATION_FIELD_LIST:
        if organisation.has_data_private_field(field["key"]):
            field_data[field["title"]] = organisation.get_data_private_field(
                field["key"]
            )
    return render(
        request,
        "jsondataferretexampleapp/admin/organisation/index.html",
        {"organisation": organisation, "field_data": field_data},
    )


@login_required
def admin_organisation_download_form(request, public_id):
    try:
        type = Type.objects.get(public_id=TYPE_ORGANISATION_PUBLIC_ID)
        record = Record.objects.get(type=type, public_id=public_id)
    except Type.DoesNotExist:
        raise Http404("Type does not exist")
    except Record.DoesNotExist:
        raise Http404("Record does not exist")

    guide_file = os.path.join(
        settings.BASE_DIR,
        "jsondataferretexampleapp",
        "spreadsheetform_guides",
        "organisation.xlsx",
    )

    out_file = os.path.join(
        tempfile.gettempdir(),
        "jsondataferretexampleapp" + str(random.randrange(1, 100000000000)) + ".xlsx",
    )

    spreadsheetforms.api.put_data_in_form(guide_file, record.cached_data, out_file)

    with open(out_file, "rb") as fh:
        response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
        response["Content-Disposition"] = "inline; filename=organisation.xlsx"

    return response


@login_required
def admin_organisation_import_form(request, public_id):
    try:
        type = Type.objects.get(public_id=TYPE_ORGANISATION_PUBLIC_ID)
        data = Record.objects.get(type=type, public_id=public_id)
    except Type.DoesNotExist:
        raise Http404("Type does not exist")
    except Record.DoesNotExist:
        raise Http404("Record does not exist")

    if request.method == "POST":

        # Create a form instance and populate it with data from the request (binding):
        form = OrganisationImportForm(request.POST, request.FILES)

        # Check if the form is valid:
        if form.is_valid():

            # get data
            guide_file = os.path.join(
                settings.BASE_DIR,
                "jsondataferretexampleapp",
                "spreadsheetform_guides",
                "organisation.xlsx",
            )
            json_data = spreadsheetforms.api.get_data_from_form(
                guide_file,
                request.FILES["file"].temporary_file_path(),
                date_format=getattr(
                    settings, "JSONDATAFERRET_SPREADSHEET_FORM_DATE_FORMAT", None
                ),
            )

            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            # Save the event
            new_event_data = NewEventData(
                TYPE_ORGANISATION_PUBLIC_ID,
                data.public_id,
                json_data,
                mode=jsondataferret.EVENT_MODE_MERGE,
            )
            newEvent([new_event_data], user=request.user)

            # redirect to a new URL:
            return HttpResponseRedirect(
                reverse(
                    "jsondataferretexampleapp_admin_organisation_index",
                    kwargs={"public_id": data.public_id},
                )
            )

        # If this is a GET (or any other method) create the default form.
    else:
        form = OrganisationImportForm()

    context = {
        "data": data,
        "form": form,
    }

    return render(
        request, "jsondataferretexampleapp/admin/organisation/import_form.html", context
    )


@login_required
def admin_organisation_make_private(request, public_id):
    try:
        type = Type.objects.get(public_id=TYPE_ORGANISATION_PUBLIC_ID)
        record = Record.objects.get(type=type, public_id=public_id)
    except Type.DoesNotExist:
        raise Http404("Type does not exist")
    except Record.DoesNotExist:
        raise Http404("Record does not exist")

    if request.method == "POST":

        # Create a form instance and populate it with data from the request (binding):
        form = OrganisationMakePrivateForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():

            # Save the event
            new_event_data = NewEventData(
                type,
                record,
                {"status": "PRIVATE"},
                mode=jsondataferret.EVENT_MODE_MERGE,
            )
            newEvent([new_event_data], user=request.user)

            # redirect to a new URL:
            return HttpResponseRedirect(
                reverse(
                    "jsondataferretexampleapp_admin_organisation_index",
                    kwargs={"public_id": record.public_id},
                )
            )

    else:

        form = OrganisationMakePrivateForm()

    context = {
        "record": record,
        "form": form,
    }

    return render(
        request,
        "jsondataferretexampleapp/admin/organisation/make_private.html",
        context,
    )


@login_required
def admin_organisation_make_disputed(request, public_id):
    try:
        type = Type.objects.get(public_id=TYPE_ORGANISATION_PUBLIC_ID)
        record = Record.objects.get(type=type, public_id=public_id)
    except Type.DoesNotExist:
        raise Http404("Type does not exist")
    except Record.DoesNotExist:
        raise Http404("Record does not exist")

    if request.method == "POST":

        # Create a form instance and populate it with data from the request (binding):
        form = OrganisationMakeDisputedForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():

            # Save the event
            new_event_data = NewEventData(
                type,
                record,
                {"status": "DISPUTED"},
                mode=jsondataferret.EVENT_MODE_MERGE,
            )
            newEvent([new_event_data], user=request.user)

            # redirect to a new URL:
            return HttpResponseRedirect(
                reverse(
                    "jsondataferretexampleapp_admin_organisation_index",
                    kwargs={"public_id": record.public_id},
                )
            )

    else:

        form = OrganisationMakeDisputedForm()

    context = {
        "record": record,
        "form": form,
    }

    return render(
        request,
        "jsondataferretexampleapp/admin/organisation/make_disputed.html",
        context,
    )


@login_required
def admin_organisations_new(request):

    # If this is a POST request then process the Form data
    if request.method == "POST":

        # Create a form instance and populate it with data from the request (binding):
        form = OrganisationNewForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            # Save the event
            id = str(uuid.uuid4())
            data = NewEventData(
                TYPE_ORGANISATION_PUBLIC_ID,
                id,
                {"title": form.cleaned_data["title"],},
                approved=True,
            )
            newEvent([data], user=request.user)

            # redirect to a new URL:
            return HttpResponseRedirect(
                reverse(
                    "jsondataferretexampleapp_admin_organisation_index",
                    kwargs={"public_id": id},
                )
            )

    # If this is a GET (or any other method) create the default form.
    else:
        form = OrganisationNewForm()

    context = {
        "form": form,
    }

    return render(
        request, "jsondataferretexampleapp/admin/organisation/new.html", context
    )


@login_required
def admin_organisation_moderate(request, public_id):
    try:
        type = Type.objects.get(public_id=TYPE_ORGANISATION_PUBLIC_ID)
        record = Record.objects.get(type=type, public_id=public_id)
    except Type.DoesNotExist:
        raise Http404("Type does not exist")
    except Record.DoesNotExist:
        raise Http404("Record does not exist")

    edits = Edit.objects.filter(record=record, approval_event=None, refusal_event=None)

    if request.method == "POST":

        # TODO check CSFR

        actions = []
        for edit in edits:
            action = request.POST.get("action_" + str(edit.id))
            if action == "approve":
                actions.append(jsondataferret.pythonapi.newevent.NewEventApproval(edit))
            elif action == "reject":
                actions.append(
                    jsondataferret.pythonapi.newevent.NewEventRejection(edit)
                )

        if actions:
            jsondataferret.pythonapi.newevent.newEvent(actions, user=request.user)

        return HttpResponseRedirect(
            reverse(
                "jsondataferretexampleapp_admin_organisation_index",
                kwargs={"public_id": public_id},
            )
        )

    return render(
        request,
        "jsondataferretexampleapp/admin/organisation/moderate.html",
        {"type": type, "record": record, "edits": edits},
    )


@login_required
def admin_project_download_blank_form(request):
    type_data = settings.JSONDATAFERRET_TYPE_INFORMATION.get(TYPE_PROJECT_PUBLIC_ID, {})
    if not type_data.get("spreadsheet_form_guide"):
        raise Http404("Feature not available")

    out_file = os.path.join(
        tempfile.gettempdir(),
        "jsondataferretexampleapp" + str(random.randrange(1, 100000000000)) + ".xlsx",
    )

    spreadsheetforms.api.make_empty_form(
        type_data.get("spreadsheet_form_guide"), out_file
    )

    with open(out_file, "rb") as fh:
        response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
        response["Content-Disposition"] = "inline; filename=project.xlsx"

    return response


@login_required
def admin_projects_list(request):
    try:
        type = Type.objects.get(public_id=TYPE_PROJECT_PUBLIC_ID)
    except Type.DoesNotExist:
        raise Http404("Type does not exist")
    projects = Record.objects.filter(type=type)
    return render(
        request, "jsondataferretexampleapp/admin/projects.html", {"projects": projects},
    )


@login_required
def admin_project_index(request, public_id):
    try:
        project = Project.objects.get(public_id=public_id)
    except Project.DoesNotExist:
        raise Http404("Project does not exist")
    field_data = {}
    for field in TYPE_PROJECT_FIELD_LIST:
        if project.has_data_private_field(field["key"]):
            field_data[field["title"]] = project.get_data_private_field(field["key"])
    return render(
        request,
        "jsondataferretexampleapp/admin/project/index.html",
        {"project": project, "field_data": field_data},
    )


@login_required
def admin_project_download_form(request, public_id):
    try:
        type = Type.objects.get(public_id=TYPE_PROJECT_PUBLIC_ID)
        record = Record.objects.get(type=type, public_id=public_id)
    except Type.DoesNotExist:
        raise Http404("Type does not exist")
    except Record.DoesNotExist:
        raise Http404("Record does not exist")

    guide_file = os.path.join(
        settings.BASE_DIR,
        "jsondataferretexampleapp",
        "spreadsheetform_guides",
        "project.xlsx",
    )

    out_file = os.path.join(
        tempfile.gettempdir(),
        "jsondataferretexampleapp" + str(random.randrange(1, 100000000000)) + ".xlsx",
    )

    spreadsheetforms.api.put_data_in_form(guide_file, record.cached_data, out_file)

    with open(out_file, "rb") as fh:
        response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
        response["Content-Disposition"] = "inline; filename=project.xlsx"

    return response


@login_required
def admin_project_import_form(request, public_id):
    try:
        type = Type.objects.get(public_id=TYPE_PROJECT_PUBLIC_ID)
        data = Record.objects.get(type=type, public_id=public_id)
    except Type.DoesNotExist:
        raise Http404("Type does not exist")
    except Record.DoesNotExist:
        raise Http404("Record does not exist")

    if request.method == "POST":

        # Create a form instance and populate it with data from the request (binding):
        form = ProjectImportForm(request.POST, request.FILES)

        # Check if the form is valid:
        if form.is_valid():

            # get data
            guide_file = os.path.join(
                settings.BASE_DIR,
                "jsondataferretexampleapp",
                "spreadsheetform_guides",
                "project.xlsx",
            )
            json_data = spreadsheetforms.api.get_data_from_form(
                guide_file,
                request.FILES["file"].temporary_file_path(),
                date_format=getattr(
                    settings, "JSONDATAFERRET_SPREADSHEET_FORM_DATE_FORMAT", None
                ),
            )

            # process the data in form.cleaned_data as required
            # Save the event
            new_event_data = NewEventData(
                TYPE_PROJECT_PUBLIC_ID,
                data.public_id,
                json_data,
                mode=jsondataferret.EVENT_MODE_MERGE,
            )
            newEvent([new_event_data], user=request.user)

            # redirect to a new URL:
            return HttpResponseRedirect(
                reverse(
                    "jsondataferretexampleapp_admin_project_index",
                    kwargs={"public_id": data.public_id},
                )
            )

        # If this is a GET (or any other method) create the default form.
    else:
        form = ProjectImportForm()

    context = {
        "data": data,
        "form": form,
    }

    return render(
        request, "jsondataferretexampleapp/admin/project/import_form.html", context
    )


@login_required
def admin_project_make_private(request, public_id):
    try:
        type = Type.objects.get(public_id=TYPE_PROJECT_PUBLIC_ID)
        record = Record.objects.get(type=type, public_id=public_id)
    except Type.DoesNotExist:
        raise Http404("Type does not exist")
    except Record.DoesNotExist:
        raise Http404("Record does not exist")

    if request.method == "POST":

        # Create a form instance and populate it with data from the request (binding):
        form = ProjectMakePrivateForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():

            # Save the event
            new_event_data = NewEventData(
                type,
                record,
                {"status": "PRIVATE"},
                mode=jsondataferret.EVENT_MODE_MERGE,
            )
            newEvent([new_event_data], user=request.user)

            # redirect to a new URL:
            return HttpResponseRedirect(
                reverse(
                    "jsondataferretexampleapp_admin_project_index",
                    kwargs={"public_id": record.public_id},
                )
            )

    else:

        form = ProjectMakePrivateForm()

    context = {
        "record": record,
        "form": form,
    }

    return render(
        request, "jsondataferretexampleapp/admin/project/make_private.html", context,
    )


@login_required
def admin_project_make_disputed(request, public_id):
    try:
        type = Type.objects.get(public_id=TYPE_PROJECT_PUBLIC_ID)
        record = Record.objects.get(type=type, public_id=public_id)
    except Type.DoesNotExist:
        raise Http404("Type does not exist")
    except Record.DoesNotExist:
        raise Http404("Record does not exist")

    if request.method == "POST":

        # Create a form instance and populate it with data from the request (binding):
        form = ProjectMakeDisputedForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():

            # Save the event
            new_event_data = NewEventData(
                type,
                record,
                {"status": "DISPUTED"},
                mode=jsondataferret.EVENT_MODE_MERGE,
            )
            newEvent([new_event_data], user=request.user)

            # redirect to a new URL:
            return HttpResponseRedirect(
                reverse(
                    "jsondataferretexampleapp_admin_project_index",
                    kwargs={"public_id": record.public_id},
                )
            )

    else:

        form = ProjectMakeDisputedForm()

    context = {
        "record": record,
        "form": form,
    }

    return render(
        request, "jsondataferretexampleapp/admin/project/make_disputed.html", context,
    )


@login_required
def admin_projects_new(request):
    try:
        type = Type.objects.get(public_id=TYPE_PROJECT_PUBLIC_ID)
    except Type.DoesNotExist:
        raise Http404("Type does not exist")

    # If this is a POST request then process the Form data
    if request.method == "POST":

        # Create a form instance and populate it with data from the request (binding):
        form = ProjectNewForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # Save the event
            id = form.cleaned_data["id"]
            existing_record = Record.objects.filter(type=type, public_id=id)
            if existing_record:
                form.add_error("id", "This ID already exists")
            else:
                data = NewEventData(
                    type,
                    id,
                    {"project_name": {"value": form.cleaned_data["title"]}},
                    approved=True,
                )
                newEvent([data], user=request.user)

                # redirect to a new URL:
                return HttpResponseRedirect(
                    reverse(
                        "jsondataferretexampleapp_admin_project_index",
                        kwargs={"public_id": id},
                    )
                )

    # If this is a GET (or any other method) create the default form.
    else:
        form = ProjectNewForm()

    context = {
        "form": form,
    }

    return render(request, "jsondataferretexampleapp/admin/project/new.html", context)


@login_required
def admin_project_moderate(request, public_id):
    try:
        type = Type.objects.get(public_id=TYPE_PROJECT_PUBLIC_ID)
        record = Record.objects.get(type=type, public_id=public_id)
    except Type.DoesNotExist:
        raise Http404("Type does not exist")
    except Record.DoesNotExist:
        raise Http404("Record does not exist")

    edits = Edit.objects.filter(record=record, approval_event=None, refusal_event=None)

    if request.method == "POST":

        # TODO check CSFR

        actions = []
        for edit in edits:
            action = request.POST.get("action_" + str(edit.id))
            if action == "approve":
                actions.append(jsondataferret.pythonapi.newevent.NewEventApproval(edit))
            elif action == "reject":
                actions.append(
                    jsondataferret.pythonapi.newevent.NewEventRejection(edit)
                )

        if actions:
            jsondataferret.pythonapi.newevent.newEvent(actions, user=request.user)

        return HttpResponseRedirect(
            reverse(
                "jsondataferretexampleapp_admin_project_index",
                kwargs={"public_id": public_id},
            )
        )

    for edit in edits:
        edit.field_datas = []
        for field in TYPE_PROJECT_FIELD_LIST:
            if edit.has_data_field(field["key"]):
                edit.field_datas.append(
                    {
                        "title": field["title"],
                        "value": edit.get_data_field(field["key"]),
                    }
                )

    return render(
        request,
        "jsondataferretexampleapp/admin/project/moderate.html",
        {"type": type, "record": record, "edits": edits},
    )


@login_required
def admin_project_history(request, public_id):
    try:
        type = Type.objects.get(public_id=TYPE_PROJECT_PUBLIC_ID)
        record = Record.objects.get(type=type, public_id=public_id)
    except Type.DoesNotExist:
        raise Http404("Type does not exist")
    except Record.DoesNotExist:
        raise Http404("Record does not exist")

    events = Event.objects.filter_by_record(record)

    return render(
        request,
        "jsondataferretexampleapp/admin/project/history.html",
        {"type": type, "record": record, "events": events},
    )


########################### Admin - Event


@login_required
def admin_event_index(request, event_id):
    try:
        event = Event.objects.get(public_id=event_id)
    except Event.DoesNotExist:
        raise Http404("Event does not exist")
    edits_created = event.edits_created.all()
    edits_approved = event.edits_approved.all()
    edits_refused = event.edits_refused.all()
    edits_created_and_approved = list(set(edits_created).intersection(edits_approved))
    edits_only_created = [
        edit for edit in edits_created if edit not in edits_created_and_approved
    ]
    edits_only_approved = [
        edit for edit in edits_approved if edit not in edits_created_and_approved
    ]
    return render(
        request,
        "jsondataferretexampleapp/admin/event/index.html",
        {
            "event": event,
            "edits_created": edits_created,
            "edits_approved": edits_approved,
            "edits_refused": edits_refused,
            "edits_only_created": edits_only_created,
            "edits_only_approved": edits_only_approved,
            "edits_created_and_approved": edits_created_and_approved,
        },
    )
