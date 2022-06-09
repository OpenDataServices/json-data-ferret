import json
import os
import random
import tempfile
import urllib.parse

import pygments
import pygments.formatters
import pygments.lexers.data
import spreadsheetforms
from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

import jsondataferret.pythonapi.newevent

from .filters import EventFilter
from .forms import RecordImportForm
from .models import Edit, Event, Record, Type


############################ Index
@permission_required("jsondataferret.admin")
def index(request):
    return render(request, "jsondataferret/index.html")


############################ Types and Records


@permission_required("jsondataferret.admin")
def types_list(request):
    types = Type.objects.all()
    return render(request, "jsondataferret/types.html", {"types": types})


@permission_required("jsondataferret.admin")
def type_index(request, public_id):
    try:
        type = Type.objects.get(public_id=public_id)
    except Type.DoesNotExist:
        raise Http404("Type does not exist")

    type_data = settings.JSONDATAFERRET_TYPE_INFORMATION.get(type.public_id, {})

    return render(
        request,
        "jsondataferret/type/index.html",
        {
            "type": type,
            "download_form_available": bool(type_data.get("spreadsheet_form_guide")),
        },
    )


@permission_required("jsondataferret.admin")
def type_download_blank_form(request, type_id):
    try:
        type = Type.objects.get(public_id=type_id)
    except Type.DoesNotExist:
        raise Http404("Type does not exist")
    type_data = settings.JSONDATAFERRET_TYPE_INFORMATION.get(type.public_id, {})
    if not type_data.get("spreadsheet_form_guide"):
        raise Http404("Feature not available")

    out_file = os.path.join(
        tempfile.gettempdir(),
        "jsondataferret" + str(random.randrange(1, 100000000000)) + ".xlsx",
    )

    spreadsheetforms.api.make_empty_form(
        type_data.get("spreadsheet_form_guide"), out_file
    )

    with open(out_file, "rb") as fh:
        response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
        response["Content-Disposition"] = "inline; filename=record.xlsx"

    return response


@permission_required("jsondataferret.admin")
def type_record_list(request, type_id):
    try:
        type = Type.objects.get(public_id=type_id)
    except Type.DoesNotExist:
        raise Http404("Type does not exist")
    records = Record.objects.filter(type=type).order_by("public_id")
    paginator = Paginator(records, 100)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        "jsondataferret/type/records.html",
        {"type": type, "page_obj": page_obj},
    )


@permission_required("jsondataferret.admin")
def type_record_list_needs_moderation(request, type_id):
    try:
        type = Type.objects.get(public_id=type_id)
    except Type.DoesNotExist:
        raise Http404("Type does not exist")
    records = Record.objects.filter_needs_moderation_by_type(type)
    paginator = Paginator(records, 100)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        "jsondataferret/type/records_needing_moderation.html",
        {"type": type, "page_obj": page_obj},
    )


@permission_required("jsondataferret.admin")
def record_index(request, type_id, record_id):
    try:
        type = Type.objects.get(public_id=type_id)
        record = Record.objects.get(type=type, public_id=record_id)
    except Type.DoesNotExist:
        raise Http404("Type does not exist")
    except Record.DoesNotExist:
        raise Http404("Record does not exist")

    type_data = settings.JSONDATAFERRET_TYPE_INFORMATION.get(type.public_id, {})

    return render(
        request,
        "jsondataferret/type/record/index.html",
        {
            "type": type,
            "record": record,
            "download_form_available": bool(type_data.get("spreadsheet_form_guide")),
            "json_schema_available": bool(type_data.get("json_schema")),
        },
    )


@permission_required("jsondataferret.admin")
def record_moderate(request, type_id, record_id):
    try:
        type = Type.objects.get(public_id=type_id)
        record = Record.objects.get(type=type, public_id=record_id)
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
            jsondataferret.pythonapi.newevent.newEvent(
                actions, user=request.user, comment=request.POST.get("comment")
            )

            return HttpResponseRedirect(
                reverse(
                    "jsondataferret_record_index",
                    kwargs={"type_id": type_id, "record_id": record_id},
                )
            )

    return render(
        request,
        "jsondataferret/type/record/moderate.html",
        {"type": type, "record": record, "edits": edits},
    )


@permission_required("jsondataferret.admin")
def record_edit_json_schema(request, type_id, record_id):
    try:
        type = Type.objects.get(public_id=type_id)
        record = Record.objects.get(type=type, public_id=record_id)
    except Type.DoesNotExist:
        raise Http404("Type does not exist")
    except Record.DoesNotExist:
        raise Http404("Record does not exist")

    if request.method == "POST":

        # TODO check CSFR

        data = json.loads(request.POST.get("data"))

        new_event_data = jsondataferret.pythonapi.newevent.NewEventData(
            type,
            record,
            data,
            mode=jsondataferret.EVENT_MODE_REPLACE,
        )
        jsondataferret.pythonapi.newevent.newEvent(
            [new_event_data],
            user=request.user,
            comment=request.POST.get("comment"),
        )

        return HttpResponseRedirect(
            reverse(
                "jsondataferret_record_index",
                kwargs={"type_id": type_id, "record_id": record_id},
            )
        )

    type_data = settings.JSONDATAFERRET_TYPE_INFORMATION.get(type.public_id, {})

    return render(
        request,
        "jsondataferret/type/record/edit_json_schema.html",
        {
            "type": type,
            "record": record,
            "data_json_string": json.dumps(record.cached_data),
            "json_schema_string": json.dumps(type_data.get("json_schema")),
        },
    )


@permission_required("jsondataferret.admin")
def record_download_form(request, type_id, record_id):
    try:
        type = Type.objects.get(public_id=type_id)
        record = Record.objects.get(type=type, public_id=record_id)
    except Type.DoesNotExist:
        raise Http404("Type does not exist")
    except Record.DoesNotExist:
        raise Http404("Record does not exist")

    type_data = settings.JSONDATAFERRET_TYPE_INFORMATION.get(type.public_id, {})

    if not type_data.get("spreadsheet_form_guide"):
        raise Http404("Feature not available")

    out_file = os.path.join(
        tempfile.gettempdir(),
        "jsondataferret" + str(random.randrange(1, 100000000000)) + ".xlsx",
    )

    spreadsheetforms.api.put_data_in_form(
        type_data.get("spreadsheet_form_guide"), record.cached_data, out_file
    )

    with open(out_file, "rb") as fh:
        response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
        response["Content-Disposition"] = "inline; filename=record.xlsx"

    return response


@permission_required("jsondataferret.admin")
def record_import_form(request, type_id, record_id):
    try:
        type = Type.objects.get(public_id=type_id)
        record = Record.objects.get(type=type, public_id=record_id)
    except Type.DoesNotExist:
        raise Http404("Type does not exist")
    except Record.DoesNotExist:
        raise Http404("Record does not exist")

    type_data = settings.JSONDATAFERRET_TYPE_INFORMATION.get(type.public_id, {})

    if not type_data.get("spreadsheet_form_guide"):
        raise Http404("Feature not available")

    if request.method == "POST":

        # Create a form instance and populate it with data from the request (binding):
        form = RecordImportForm(request.POST, request.FILES)

        # Check if the form is valid:
        if form.is_valid():

            # get data
            json_data = spreadsheetforms.api.get_data_from_form(
                type_data.get("spreadsheet_form_guide"),
                request.FILES["file"].temporary_file_path(),
                date_format=getattr(
                    settings, "JSONDATAFERRET_SPREADSHEET_FORM_DATE_FORMAT", None
                ),
            )

            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            # Save the event
            new_event_data = jsondataferret.pythonapi.newevent.NewEventData(
                type,
                record,
                json_data,
                mode=jsondataferret.EVENT_MODE_MERGE,
            )
            jsondataferret.pythonapi.newevent.newEvent(
                [new_event_data],
                user=request.user,
                comment=form.cleaned_data["comment"],
            )

            # redirect to a new URL:
            return HttpResponseRedirect(
                reverse(
                    "jsondataferret_record_index",
                    kwargs={"type_id": type.public_id, "record_id": record.public_id},
                )
            )

        # If this is a GET (or any other method) create the default form.
    else:
        form = RecordImportForm()

    context = {
        "type": type,
        "record": record,
        "form": form,
    }

    return render(request, "jsondataferret/type/record/import_form.html", context)


@permission_required("jsondataferret.admin")
def record_event_list(request, type_id, record_id):
    try:
        type = Type.objects.get(public_id=type_id)
        record = Record.objects.get(type=type, public_id=record_id)
    except Type.DoesNotExist:
        raise Http404("Type does not exist")
    except Record.DoesNotExist:
        raise Http404("Record does not exist")

    events = Event.objects.filter_by_record(record)

    return render(
        request,
        "jsondataferret/type/record/events.html",
        {"type": type, "record": record, "events": events},
    )


############################ Events


@permission_required("jsondataferret.admin")
def event_list(request):
    filter = EventFilter(request.GET, queryset=Event.objects.all().order_by("created"))
    paginator = Paginator(filter.qs, 100)
    page_number = request.GET.get("page")
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    pagination_get_params = urllib.parse.urlencode(filter.get_get_params_for_paging())
    return render(
        request,
        "jsondataferret/events.html",
        {
            "page_obj": page_obj,
            "filter": filter,
            "pagination_get_params": pagination_get_params,
        },
    )


@permission_required("jsondataferret.admin")
def event_index(request, event_id):
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
        "jsondataferret/event/index.html",
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


############################ Misc


@permission_required("jsondataferret.admin")
def pygments_css(request):
    response = HttpResponse(
        content=pygments.formatters.HtmlFormatter().get_style_defs(".highlight")
    )
    response["Content-Type"] = "text/css"
    return response
