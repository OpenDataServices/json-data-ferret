from django.urls import path

from . import views

urlpatterns = [
    ########################### Home Page
    path("", views.index, name="jsondataferretexampleapp_index"),
    ########################### Public - Organisation
    path(
        "organisation",
        views.organisations_list,
        name="jsondataferretexampleapp_organisation_list",
    ),
    path(
        "organisation/<public_id>",
        views.organisation_index,
        name="jsondataferretexampleapp_organisation_index",
    ),
    ########################### Public - Project
    path("project", views.projects_list, name="jsondataferretexampleapp_project_list",),
    path(
        "project/<public_id>",
        views.project_index,
        name="jsondataferretexampleapp_project_index",
    ),
    ########################### Admin
    path("admin/", views.admin_index, name="jsondataferretexampleapp_admin_index"),
    ########################### Admin - Organisation
    path(
        "admin/organisation",
        views.admin_organisations_list,
        name="jsondataferretexampleapp_admin_organisation_list",
    ),
    path(
        "admin/organisation/<public_id>",
        views.admin_organisation_index,
        name="jsondataferretexampleapp_admin_organisation_index",
    ),
    path(
        "admin/organisation/<public_id>/make_private",
        views.admin_organisation_make_private,
        name="jsondataferretexampleapp_admin_organisation_make_private",
    ),
    path(
        "admin/organisation/<public_id>/make_disputed",
        views.admin_organisation_make_disputed,
        name="jsondataferretexampleapp_admin_organisation_make_disputed",
    ),
    path(
        "admin/organisation/<public_id>/download_form",
        views.admin_organisation_download_form,
        name="jsondataferretexampleapp_admin_organisation_download_form",
    ),
    path(
        "admin/organisation/<public_id>/import_form",
        views.admin_organisation_import_form,
        name="jsondataferretexampleapp_admin_organisation_import_form",
    ),
    path(
        "admin/organisation/<public_id>/moderate",
        views.admin_organisation_moderate,
        name="jsondataferretexampleapp_admin_organisation_moderate",
    ),
    path(
        "admin/new_organisation",
        views.admin_organisations_new,
        name="jsondataferretexampleapp_admin_organisation_new",
    ),
    ########################### Admin - Project
    path(
        "admin/project_download_blank_form",
        views.admin_project_download_blank_form,
        name="jsondataferretexampleapp_admin_project_download_blank_form",
    ),
    path(
        "admin/project",
        views.admin_projects_list,
        name="jsondataferretexampleapp_admin_project_list",
    ),
    path(
        "admin/project/<public_id>",
        views.admin_project_index,
        name="jsondataferretexampleapp_admin_project_index",
    ),
    path(
        "admin/project/<public_id>/make_private",
        views.admin_project_make_private,
        name="jsondataferretexampleapp_admin_project_make_private",
    ),
    path(
        "admin/project/<public_id>/make_disputed",
        views.admin_project_make_disputed,
        name="jsondataferretexampleapp_admin_project_make_disputed",
    ),
    path(
        "admin/project/<public_id>/download_form",
        views.admin_project_download_form,
        name="jsondataferretexampleapp_admin_project_download_form",
    ),
    path(
        "admin/project/<public_id>/import_form",
        views.admin_project_import_form,
        name="jsondataferretexampleapp_admin_project_import_form",
    ),
    path(
        "admin/project/<public_id>/moderate",
        views.admin_project_moderate,
        name="jsondataferretexampleapp_admin_project_moderate",
    ),
    path(
        "admin/project/<public_id>/history",
        views.admin_project_history,
        name="jsondataferretexampleapp_admin_project_history",
    ),
    path(
        "admin/new_project",
        views.admin_projects_new,
        name="jsondataferretexampleapp_admin_project_new",
    ),
    ########################### Admin - Event
    path(
        "admin/event/<event_id>",
        views.admin_event_index,
        name="jsondataferretexampleapp_admin_event_index",
    ),
]
