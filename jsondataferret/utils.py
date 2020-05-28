import jsonpointer
from django.conf import settings


def get_field_list_from_json(type_public_id, data):
    fields = settings.JSONDATAFERRET_TYPE_INFORMATION.get(type_public_id, {}).get(
        "fields", []
    )
    out = []
    for field_config in fields:
        out.extend(get_field_list_from_json_and_field_config(data, field_config))
    return out


def get_field_list_from_json_and_field_config(data, field_config):
    if field_config.get("type") == "list":
        return get_field_list_from_json_and_field_config_type_list(data, field_config)
    else:
        return get_field_list_from_json_and_field_config_type_value(data, field_config)


def get_field_list_from_json_and_field_config_type_value(data, field_config):
    try:
        value = jsonpointer.resolve_pointer(data, field_config["key"])
        if value:
            return [{"title": field_config["title"], "value": value,}]
    except jsonpointer.JsonPointerException:
        pass

    return []


def get_field_list_from_json_and_field_config_type_list(data, field_config):
    try:
        list_values = jsonpointer.resolve_pointer(data, field_config["key"])
    except jsonpointer.JsonPointerException:
        return []

    if not isinstance(list_values, list):
        return []

    out = []
    idx = 0
    for list_value in list_values:
        idx += 1
        for item_field_config in field_config["fields"]:
            try:
                value = jsonpointer.resolve_pointer(
                    list_value, item_field_config["key"]
                )
                if value:
                    out.append(
                        {
                            "title": field_config["title"]
                            + " "
                            + str(idx)
                            + ": "
                            + item_field_config["title"],
                            "value": value,
                        }
                    )
            except jsonpointer.JsonPointerException:
                pass
    return out
