import os
import random
import tempfile
from abc import ABC

import spreadsheetforms.api
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View

import jsondataferret
from jsondataferret.models import Edit, Event, Record, Type
from jsondataferret.pythonapi.newevent import NewEventData, newEvent
from jsondataferretexampleapp import (  # noqa
    TYPE_ORGANISATION_FIELD_LIST,
    TYPE_ORGANISATION_PUBLIC_ID,
    TYPE_PROJECT_FIELD_LIST,
    TYPE_PROJECT_PUBLIC_ID,
)

from .forms import ModelImportForm, OrganisationNewForm, ProjectNewForm
from .models import Organisation, Project  # noqa

########################### Home Page


def index(request):
    return render(request, "jsondataferretexampleapp/index.html")


########################### Public


class ModelList(View, ABC):
    def get(self, request):
        datas = self.__class__._model.objects.filter(
            exists=True, status_public=True
        ).order_by("public_id")
        return render(
            request,
            "jsondataferretexampleapp/"
            + self.__class__._model.__name__.lower()
            + "s.html",
            {"datas": datas},
        )


class ProjectList(ModelList):
    _model = Project


class OrganisationList(ModelList):
    _model = Organisation


class ModelIndex(View, ABC):
    def get(self, request, public_id):
        try:
            data = self.__class__._model.objects.get(public_id=public_id)
        except self._model.DoesNotExist:
            raise Http404("Data does not exist")
        field_datas = jsondataferret.utils.get_field_list_from_json(
            self.__class__._model.type_id, data.data_public
        )
        return render(
            request,
            "jsondataferretexampleapp/"
            + self.__class__._model.__name__.lower()
            + "/index.html",
            {"data": data, "field_datas": field_datas},
        )


class ProjectIndex(ModelIndex):
    _model = Project
    _field_list = TYPE_PROJECT_FIELD_LIST


class OrganisationIndex(ModelIndex):
    _model = Organisation
    _field_list = TYPE_ORGANISATION_FIELD_LIST


########################### Admin


@login_required
def admin_index(request):
    return render(request, "jsondataferretexampleapp/admin/index.html")


class AdminModelList(LoginRequiredMixin, View, ABC):
    def get(self, request):
        try:
            type = Type.objects.get(public_id=self.__class__._type_public_id)
        except Type.DoesNotExist:
            raise Http404("Type does not exist")
        datas = Record.objects.filter(type=type).order_by("public_id")
        return render(
            request,
            "jsondataferretexampleapp/admin/"
            + self.__class__._model.__name__.lower()
            + "s.html",
            {"datas": datas},
        )


class AdminOrganisationList(AdminModelList):
    _model = Organisation
    _type_public_id = TYPE_ORGANISATION_PUBLIC_ID


class AdminProjectList(AdminModelList):
    _model = Project
    _type_public_id = TYPE_PROJECT_PUBLIC_ID


class AdminModelNew(LoginRequiredMixin, View, ABC):
    def get(self, request):
        form = self.__class__._form_class()
        return render(
            request,
            "jsondataferretexampleapp/admin/"
            + self.__class__._model.__name__.lower()
            + "/new.html",
            {
                "form": form,
            },
        )

    def post(self, request):
        try:
            type = Type.objects.get(public_id=self.__class__._type_public_id)
        except Type.DoesNotExist:
            raise Http404("Type does not exist")
        form = self.__class__._form_class(request.POST)
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
                    self.__class__._new_data_function(form.cleaned_data["title"]),
                    approved=True,
                )
                newEvent(
                    [data], user=request.user, comment=form.cleaned_data["comment"]
                )

                # redirect to a new URL:
                return HttpResponseRedirect(
                    reverse(
                        self.__class__._redirect_view,
                        kwargs={"public_id": id},
                    )
                )

        return render(
            request,
            "jsondataferretexampleapp/admin/"
            + self.__class__._model.__name__.lower()
            + "/new.html",
            {
                "form": form,
            },
        )


class AdminProjectNew(AdminModelNew):
    _model = Project
    _type_public_id = TYPE_PROJECT_PUBLIC_ID
    _form_class = ProjectNewForm
    _redirect_view = "jsondataferretexampleapp_admin_project_index"
    _new_data_function = lambda title: {"project_name": {"value": title}}


class AdminOrganisationNew(AdminModelNew):
    _model = Organisation
    _type_public_id = TYPE_ORGANISATION_PUBLIC_ID
    _form_class = OrganisationNewForm
    _redirect_view = "jsondataferretexampleapp_admin_organisation_index"
    _new_data_function = lambda title: {"title": title}


class AdminModelIndex(LoginRequiredMixin, View, ABC):
    def get(self, request, public_id):
        try:
            data = self.__class__._model.objects.get(public_id=public_id)
        except self._model.DoesNotExist:
            raise Http404("Data does not exist")
        field_datas = jsondataferret.utils.get_field_list_from_json(
            self.__class__._model.type_id, data.data_private
        )
        return render(
            request,
            "jsondataferretexampleapp/admin/"
            + self.__class__._model.__name__.lower()
            + "/index.html",
            {"data": data, "field_datas": field_datas},
        )


class AdminProjectIndex(AdminModelIndex):
    _model = Project


class AdminOrganisationIndex(AdminModelIndex):
    _model = Organisation


class AdminModelDownloadForm(LoginRequiredMixin, View, ABC):
    def get(self, request, public_id):
        try:
            type = Type.objects.get(public_id=self.__class__._model.type_id)
            record = Record.objects.get(type=type, public_id=public_id)
        except Type.DoesNotExist:
            raise Http404("Type does not exist")
        except Record.DoesNotExist:
            raise Http404("Record does not exist")

        out_file = os.path.join(
            tempfile.gettempdir(),
            "jsondataferretexampleapp"
            + str(random.randrange(1, 100000000000))
            + ".xlsx",
        )

        spreadsheetforms.api.put_data_in_form(
            self.__class__._guide_file, record.cached_data, out_file
        )

        with open(out_file, "rb") as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response["Content-Disposition"] = (
                "inline; filename=" + self.__class__._model.__name__.lower() + ".xlsx"
            )

        return response


class AdminProjectDownloadForm(AdminModelDownloadForm):
    _model = Project
    _guide_file = os.path.join(
        settings.BASE_DIR,
        "jsondataferretexampleapp",
        "spreadsheetform_guides",
        "project.xlsx",
    )


class AdminOrganisationDownloadForm(AdminModelDownloadForm):
    _model = Organisation
    _guide_file = os.path.join(
        settings.BASE_DIR,
        "jsondataferretexampleapp",
        "spreadsheetform_guides",
        "organisation.xlsx",
    )


class AdminModelImportForm(LoginRequiredMixin, View, ABC):
    def get(self, request, public_id):
        try:
            type = Type.objects.get(public_id=self.__class__._model.type_id)
            data = Record.objects.get(type=type, public_id=public_id)
        except Type.DoesNotExist:
            raise Http404("Type does not exist")
        except Record.DoesNotExist:
            raise Http404("Record does not exist")

        form = ModelImportForm()

        context = {
            "data": data,
            "form": form,
        }

        return render(
            request,
            "jsondataferretexampleapp/admin/"
            + self.__class__._model.__name__.lower()
            + "/import_form.html",
            context,
        )

    def post(self, request, public_id):
        try:
            type = Type.objects.get(public_id=self.__class__._model.type_id)
            data = Record.objects.get(type=type, public_id=public_id)
        except Type.DoesNotExist:
            raise Http404("Type does not exist")
        except Record.DoesNotExist:
            raise Http404("Record does not exist")

        # Create a form instance and populate it with data from the request (binding):
        form = ModelImportForm(request.POST, request.FILES)

        # Check if the form is valid:
        if form.is_valid():
            # get data
            json_data = spreadsheetforms.api.get_data_from_form(
                self.__class__._guide_file,
                request.FILES["file"].temporary_file_path(),
                date_format=getattr(
                    settings, "JSONDATAFERRET_SPREADSHEET_FORM_DATE_FORMAT", None
                ),
            )

            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            # Save the event
            new_event_data = NewEventData(
                self.__class__._model.type_id,
                data.public_id,
                json_data,
                mode=jsondataferret.EVENT_MODE_MERGE,
            )
            newEvent(
                [new_event_data],
                user=request.user,
                comment=form.cleaned_data["comment"],
            )

            # redirect to a new URL:
            return HttpResponseRedirect(
                reverse(
                    self.__class__._redirect_view,
                    kwargs={"public_id": data.public_id},
                )
            )

        context = {
            "data": data,
            "form": form,
        }

        return render(
            request,
            "jsondataferretexampleapp/admin/"
            + self.__class__._model.__name__.lower()
            + "/import_form.html",
            context,
        )


class AdminProjectImportForm(AdminModelImportForm):
    _model = Project
    _guide_file = os.path.join(
        settings.BASE_DIR,
        "jsondataferretexampleapp",
        "spreadsheetform_guides",
        "project.xlsx",
    )
    _redirect_view = "jsondataferretexampleapp_admin_project_index"


class AdminOrganisationImportForm(AdminModelImportForm):
    _model = Organisation
    _guide_file = os.path.join(
        settings.BASE_DIR,
        "jsondataferretexampleapp",
        "spreadsheetform_guides",
        "organisation.xlsx",
    )
    _redirect_view = "jsondataferretexampleapp_admin_organisation_index"


class AdminModelModerate(LoginRequiredMixin, View, ABC):
    def get(self, request, public_id):
        try:
            type = Type.objects.get(public_id=self.__class__._model.type_id)
            record = Record.objects.get(type=type, public_id=public_id)
        except Type.DoesNotExist:
            raise Http404("Type does not exist")
        except Record.DoesNotExist:
            raise Http404("Record does not exist")

        edits = Edit.objects.filter(
            record=record, approval_event=None, refusal_event=None
        )

        for edit in edits:
            edit.field_datas = []
            for field in self.__class__._field_list:
                if edit.has_data_field(field["key"]):
                    edit.field_datas.append(
                        {
                            "title": field["title"],
                            "value": edit.get_data_field(field["key"]),
                        }
                    )

        context = {"type": type, "record": record, "edits": edits}

        return render(
            request,
            "jsondataferretexampleapp/admin/"
            + self.__class__._model.__name__.lower()
            + "/moderate.html",
            context,
        )

    def post(self, request, public_id):
        try:
            type = Type.objects.get(public_id=self.__class__._model.type_id)
            record = Record.objects.get(type=type, public_id=public_id)
        except Type.DoesNotExist:
            raise Http404("Type does not exist")
        except Record.DoesNotExist:
            raise Http404("Record does not exist")

        edits = Edit.objects.filter(
            record=record, approval_event=None, refusal_event=None
        )

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
                    self.__class__._redirect_view,
                    kwargs={"public_id": public_id},
                )
            )

        return self.get(request, public_id)


class AdminProjectModerate(AdminModelModerate):
    _model = Project
    _guide_file = os.path.join(
        settings.BASE_DIR,
        "jsondataferretexampleapp",
        "spreadsheetform_guides",
        "project.xlsx",
    )
    _redirect_view = "jsondataferretexampleapp_admin_project_index"
    _field_list = TYPE_PROJECT_FIELD_LIST


class AdminOrganisationModerate(AdminModelModerate):
    _model = Organisation
    _guide_file = os.path.join(
        settings.BASE_DIR,
        "jsondataferretexampleapp",
        "spreadsheetform_guides",
        "organisation.xlsx",
    )
    _redirect_view = "jsondataferretexampleapp_admin_organisation_index"
    _field_list = TYPE_ORGANISATION_FIELD_LIST


class AdminModelHistory(LoginRequiredMixin, View, ABC):
    def get(self, request, public_id):
        try:
            type = Type.objects.get(public_id=self.__class__._model.type_id)
            record = Record.objects.get(type=type, public_id=public_id)
        except Type.DoesNotExist:
            raise Http404("Type does not exist")
        except Record.DoesNotExist:
            raise Http404("Record does not exist")

        events = Event.objects.filter_by_record(record)

        return render(
            request,
            "jsondataferretexampleapp/admin/"
            + self.__class__._model.__name__.lower()
            + "/history.html",
            {"record": record, "events": events},
        )


class AdminProjectHistory(AdminModelHistory):
    _model = Project


class AdminOrganisationHistory(AdminModelHistory):
    _model = Organisation


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
