TYPE_ORGANISATION_PUBLIC_ID = "org"
TYPE_PROJECT_PUBLIC_ID = "project"

JSONDATAFERRET_HOOKS = "jsondataferretexampleapp.jsondataferret"

_extra_value_components = ["value", "source", "status"]

TYPE_ORGANISATION_FIELD_LIST = [
    {"key": "/status", "title": "Status"},
    {"key": "/title", "title": "Title"},
    {"key": "/contact/email", "title": "Email"},
    {"key": "/contact/telephone", "title": "Phone"},
    {"key": "/contact/name/value", "title": "Contact Name (Value)"},
    {"key": "/contact/name/source", "title": "Contact Name (Source)"},
    {"key": "/contact/name/status", "title": "Contact Name (Status)"},
    {"key": "/contact/position/value", "title": "Contact Position (Value)"},
    {"key": "/contact/position/source", "title": "Contact Position (Source)"},
    {"key": "/contact/position/status", "title": "Contact Position (Status)"},
]

TYPE_ORGANISATION_FILTER_KEYS_LIST = ["/contact/name", "/contact/position"]

TYPE_PROJECT_FIELD_LIST = [
    {"key": "/status", "title": "Status"},
]

for path, label in {
    "/project_name": "Project Name",
    "/fund_name": "Fund Name",
    "/launch_date": "Launch Date",
}.items():
    TYPE_PROJECT_FIELD_LIST.extend(
        [
            {"key": path + "/" + extra, "title": label + " (" + extra + ")"}
            for extra in _extra_value_components
        ]
    )

TYPE_PROJECT_FILTER_KEYS_LIST = ["/project_name", "/fund_name", "/launch_date"]
