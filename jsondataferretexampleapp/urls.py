from django.urls import path

from . import views

urlpatterns = [
    ########################### Home Page
    path("", views.index, name="jsondataferretexampleapp_index"),
    ########################### Public - Organisation
    path(
        "organisation",
        views.OrganisationList.as_view(),
        name="jsondataferretexampleapp_organisation_list",
    ),
    path(
        "organisation/<public_id>",
        views.OrganisationIndex.as_view(),
        name="jsondataferretexampleapp_organisation_index",
    ),
    ########################### Public - Project
    path(
        "project",
        views.ProjectList.as_view(),
        name="jsondataferretexampleapp_project_list",
    ),
    path(
        "project/<public_id>",
        views.ProjectIndex.as_view(),
        name="jsondataferretexampleapp_project_index",
    ),
    ########################### Admin
    path("admin/", views.admin_index, name="jsondataferretexampleapp_admin_index"),
    ########################### Admin - Organisation
    path(
        "admin/organisation",
        views.AdminOrganisationList.as_view(),
        name="jsondataferretexampleapp_admin_organisation_list",
    ),
    path(
        "admin/organisation/<public_id>",
        views.AdminOrganisationIndex.as_view(),
        name="jsondataferretexampleapp_admin_organisation_index",
    ),
    path(
        "admin/organisation/<public_id>/download_form",
        views.AdminOrganisationDownloadForm.as_view(),
        name="jsondataferretexampleapp_admin_organisation_download_form",
    ),
    path(
        "admin/organisation/<public_id>/import_form",
        views.AdminOrganisationImportForm.as_view(),
        name="jsondataferretexampleapp_admin_organisation_import_form",
    ),
    path(
        "admin/organisation/<public_id>/moderate",
        views.AdminOrganisationModerate.as_view(),
        name="jsondataferretexampleapp_admin_organisation_moderate",
    ),
    path(
        "admin/organisation/<public_id>/history",
        views.AdminOrganisationHistory.as_view(),
        name="jsondataferretexampleapp_admin_organisation_history",
    ),
    path(
        "admin/new_organisation",
        views.AdminOrganisationNew.as_view(),
        name="jsondataferretexampleapp_admin_organisation_new",
    ),
    ########################### Admin - Project
    path(
        "admin/project",
        views.AdminProjectList.as_view(),
        name="jsondataferretexampleapp_admin_project_list",
    ),
    path(
        "admin/project/<public_id>",
        views.AdminProjectIndex.as_view(),
        name="jsondataferretexampleapp_admin_project_index",
    ),
    path(
        "admin/project/<public_id>/download_form",
        views.AdminProjectDownloadForm.as_view(),
        name="jsondataferretexampleapp_admin_project_download_form",
    ),
    path(
        "admin/project/<public_id>/import_form",
        views.AdminProjectImportForm.as_view(),
        name="jsondataferretexampleapp_admin_project_import_form",
    ),
    path(
        "admin/project/<public_id>/moderate",
        views.AdminProjectModerate.as_view(),
        name="jsondataferretexampleapp_admin_project_moderate",
    ),
    path(
        "admin/project/<public_id>/history",
        views.AdminProjectHistory.as_view(),
        name="jsondataferretexampleapp_admin_project_history",
    ),
    path(
        "admin/new_project",
        views.AdminProjectNew.as_view(),
        name="jsondataferretexampleapp_admin_project_new",
    ),
    ########################### Admin - Event
    path(
        "admin/event/<event_id>",
        views.admin_event_index,
        name="jsondataferretexampleapp_admin_event_index",
    ),
]
