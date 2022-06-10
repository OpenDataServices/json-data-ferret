import jsonpointer
from django.conf import settings


def get_field_list_from_json_with_differences(
    type_public_id, old_data, current_data, diff_key
):
    old_fields = get_field_list_from_json(type_public_id, old_data)
    old_fields_by_key = {f["key"]: f for f in old_fields}

    current_fields = get_field_list_from_json(
        type_public_id,
        current_data,
    )
    current_fields_by_key = {f["key"]: f for f in current_fields}

    # This will collect changes where the field is in both old and new, and changes where a field exists in new only
    for field in current_fields:
        old_value = None
        if field["key"] in old_fields_by_key:
            old_value = old_fields_by_key[field["key"]]["value"]
        field[diff_key] = old_value != field["value"]

    # So now we have to add any changes where the field exists in old only
    for key, field_data in old_fields_by_key.items():
        if key not in current_fields_by_key:
            field_data[diff_key] = True
            field_data["value"] = None
            current_fields.append(field_data)

    return current_fields


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
            return [
                {
                    "key": field_config["key"],
                    "title": field_config["title"],
                    "value": value,
                }
            ]
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
                            "key": field_config["key"]
                            + "["
                            + str(idx - 1)
                            + "]"
                            + item_field_config["key"],
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


def apply_edit_get_new_cached_data(edit):
    """Only left for backwards compatibility"""
    return edit.get_new_data_when_edit_applied_to_latest_record_cached_data()
