from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="jsondataferret_index"),
    path("pygments.css", views.pygments_css, name="jsondataferret_pygments_css"),
    path("type", views.types_list, name="jsondataferret_type_list"),
    path("type/<public_id>/", views.type_index, name="jsondataferret_type_index"),
    path(
        "type/<type_id>/download_blank_form",
        views.type_download_blank_form,
        name="jsondataferret_type_download_blank_form",
    ),
    path(
        "type/<type_id>/record",
        views.type_record_list,
        name="jsondataferret_type_record_list",
    ),
    path(
        "type/<type_id>/record_needs_moderation",
        views.type_record_list_needs_moderation,
        name="jsondataferret_type_record_list_needs_moderation",
    ),
    path(
        "type/<type_id>/record/<record_id>",
        views.record_index,
        name="jsondataferret_record_index",
    ),
    path(
        "type/<type_id>/record/<record_id>/edit_json_schema",
        views.record_edit_json_schema,
        name="jsondataferret_record_edit_json_schema",
    ),
    path(
        "type/<type_id>/record/<record_id>/download_form",
        views.record_download_form,
        name="jsondataferret_record_download_form",
    ),
    path(
        "type/<type_id>/record/<record_id>/import_form",
        views.record_import_form,
        name="jsondataferret_record_import_form",
    ),
    path(
        "type/<type_id>/record/<record_id>/moderate",
        views.record_moderate,
        name="jsondataferret_record_moderate",
    ),
    path(
        "type/<type_id>/record/<record_id>/event",
        views.record_event_list,
        name="jsondataferret_record_event_list",
    ),
    path("event", views.event_list, name="jsondataferret_event_list"),
    path("event/<event_id>/", views.event_index, name="jsondataferret_event_index"),
]
