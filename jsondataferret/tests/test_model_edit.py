from django.test import TestCase, override_settings  # noqa

from jsondataferret import EVENT_MODE_MERGE, EVENT_MODE_REPLACE
from jsondataferret.models import Edit, Type
from jsondataferret.pythonapi.newevent import NewEventData, newEvent

NEW_JSONDATAFERRET_TYPE_INFORMATION_SETTINGS = {
    "animal": {
        "fields": [
            {"key": "/title", "title": "Title"},
            {"key": "/sound", "title": "Sound"},
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
class TestGetDataFieldsIncludeDifferencesFromLatestData(TestCase):
    def _test_current_data_to_new_data(self, current_data, new_data, new_mode):
        # Create type
        type_model = Type()
        type_model.public_id = "animal"
        type_model.title = "Animal"
        type_model.save()

        # Create a record, approve straight away
        newEvent(
            [
                NewEventData(
                    "animal",
                    "lion",
                    current_data,
                    approved=True,
                )
            ],
            None,
        )

        # Create an edit that needs approval
        newEvent(
            [NewEventData("animal", "lion", new_data, approved=False, mode=new_mode)],
            None,
        )

        # Get unapproved edit & return fields for testing
        edit = Edit.objects.get(approval_event=None)
        return edit.get_data_fields_include_differences_from_latest_data()

    def test_no_change(self):
        fields = self._test_current_data_to_new_data(
            {"title": "Lion", "sound": "Roar!"},
            {"title": "Lion", "sound": "Roar!"},
            EVENT_MODE_REPLACE,
        )
        assert 2 == len(fields)
        assert fields[0]["key"] == "/title"
        assert not fields[0]["different_from_latest_value"]
        assert fields[1]["key"] == "/sound"
        assert not fields[1]["different_from_latest_value"]

    def test_simple_change(self):
        fields = self._test_current_data_to_new_data(
            {"title": "Lion", "sound": "Roar!"},
            {"title": "Lion", "sound": "Roar! Rrrrrrrrrr!"},
            EVENT_MODE_REPLACE,
        )
        assert 2 == len(fields)
        assert fields[0]["key"] == "/title"
        assert not fields[0]["different_from_latest_value"]
        assert fields[1]["key"] == "/sound"
        assert fields[1]["different_from_latest_value"]

    def test_field_removed(self):
        fields = self._test_current_data_to_new_data(
            {"title": "Lion", "sound": "Roar!"}, {"title": "Lion"}, EVENT_MODE_REPLACE
        )
        assert 2 == len(fields)
        assert fields[0]["key"] == "/title"
        assert not fields[0]["different_from_latest_value"]
        assert fields[1]["key"] == "/sound"
        assert fields[1]["different_from_latest_value"]

    def test_field_added(self):
        fields = self._test_current_data_to_new_data(
            {"title": "Lion"}, {"title": "Lion", "sound": "Roar!"}, EVENT_MODE_REPLACE
        )
        assert 2 == len(fields)
        assert fields[0]["key"] == "/title"
        assert not fields[0]["different_from_latest_value"]
        assert fields[1]["key"] == "/sound"
        assert fields[1]["different_from_latest_value"]

    def test_no_change_with_list(self):
        fields = self._test_current_data_to_new_data(
            {"title": "Lion", "alternative_names": [{"name": "Big kitty"}]},
            {"title": "Lion", "alternative_names": [{"name": "Big kitty"}]},
            EVENT_MODE_REPLACE,
        )
        assert 2 == len(fields)
        assert fields[0]["key"] == "/title"
        assert not fields[0]["different_from_latest_value"]
        assert fields[1]["key"] == "/alternative_names[0]/name"
        assert not fields[1]["different_from_latest_value"]

    def test_simple_change_with_list(self):
        fields = self._test_current_data_to_new_data(
            {"title": "Lion", "alternative_names": [{"name": "Big kitty"}]},
            {"title": "Lion", "alternative_names": [{"name": "Massive cutie pie"}]},
            EVENT_MODE_REPLACE,
        )
        assert 2 == len(fields)
        assert fields[0]["key"] == "/title"
        assert not fields[0]["different_from_latest_value"]
        assert fields[1]["key"] == "/alternative_names[0]/name"
        assert fields[1]["different_from_latest_value"]

    def test_list_item_removed(self):
        fields = self._test_current_data_to_new_data(
            {"title": "Lion", "alternative_names": [{"name": "Big kitty"}]},
            {"title": "Lion", "alternative_names": []},
            EVENT_MODE_REPLACE,
        )
        assert 2 == len(fields)
        assert fields[0]["key"] == "/title"
        assert not fields[0]["different_from_latest_value"]
        assert fields[1]["key"] == "/alternative_names[0]/name"
        assert fields[1]["different_from_latest_value"]

    def test_list_item_added(self):
        fields = self._test_current_data_to_new_data(
            {"title": "Lion", "alternative_names": []},
            {"title": "Lion", "alternative_names": [{"name": "Big kitty"}]},
            EVENT_MODE_REPLACE,
        )
        assert 2 == len(fields)
        assert fields[0]["key"] == "/title"
        assert not fields[0]["different_from_latest_value"]
        assert fields[1]["key"] == "/alternative_names[0]/name"
        assert fields[1]["different_from_latest_value"]

    def test_simple_change_merge(self):
        fields = self._test_current_data_to_new_data(
            {"title": "Lion", "sound": "Roar!"},
            {"sound": "Roar! Rrrrrrrrrr!"},
            EVENT_MODE_MERGE,
        )
        assert 2 == len(fields)
        assert fields[0]["key"] == "/title"
        assert not fields[0]["different_from_latest_value"]
        assert fields[1]["key"] == "/sound"
        assert fields[1]["different_from_latest_value"]
