from django.test import TestCase, override_settings  # noqa

from jsondataferret.utils import get_field_list_from_json

NEW_JSONDATAFERRET_TYPE_INFORMATION_SETTINGS = {
    "test": {
        "fields": [
            {"key": "/name", "title": "Name"},
            {
                "type": "list",
                "key": "/alternative_names",
                "title": "Alternative Names",
                "fields": [
                    {"key": "/name", "title": "Name"},
                ],
            },
        ]
    }
}


@override_settings(
    JSONDATAFERRET_TYPE_INFORMATION=NEW_JSONDATAFERRET_TYPE_INFORMATION_SETTINGS
)
class TestGetFieldListFromJSON(TestCase):
    def test1(self):
        data = {
            "name": "Roberta",
            "alternative_names": [{"name": "Bobby"}, {"name": "Bob"}],
        }
        out = get_field_list_from_json("test", data)
        assert len(out) == 3
        assert out[0]["key"] == "/name"
        assert out[0]["title"] == "Name"
        assert out[0]["value"] == "Roberta"
        assert out[1]["key"] == "/alternative_names[0]/name"
        assert out[1]["title"] == "Alternative Names 1: Name"
        assert out[1]["value"] == "Bobby"
        assert out[2]["key"] == "/alternative_names[1]/name"
        assert out[2]["title"] == "Alternative Names 2: Name"
        assert out[2]["value"] == "Bob"
