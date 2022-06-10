import datetime
from unittest import mock

from django.test import TestCase, override_settings  # noqa

from jsondataferret import EVENT_MODE_MERGE, EVENT_MODE_REPLACE
from jsondataferret.models import CachedRecordHistory, Edit, Type
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
class Test1(TestCase):
    def _test_current_data_to_new_data(self, current_data, new_data, new_mode):
        # Create type
        type_model = Type()
        type_model.public_id = "animal"
        type_model.title = "Animal"
        type_model.save()

        # Create a record, approve straight away
        mocked = datetime.datetime(2022, 1, 1, 11, 0, 0)
        with mock.patch("django.utils.timezone.now", mock.Mock(return_value=mocked)):
            newEvent(
                [
                    NewEventData(
                        "animal",
                        "lion",
                        current_data,
                        approved=True,
                        mode=EVENT_MODE_REPLACE,
                    )
                ],
                None,
            )

        # Create an edit that is approved straight away
        mocked = datetime.datetime(2022, 1, 1, 15, 0, 0)
        with mock.patch("django.utils.timezone.now", mock.Mock(return_value=mocked)):
            newEvent(
                [
                    NewEventData(
                        "animal", "lion", new_data, approved=True, mode=new_mode
                    )
                ],
                None,
            )

        # Get cached record histories for testing
        return (
            CachedRecordHistory.objects.filter().order_by("event__created"),
            Edit.objects.filter().order_by("creation_event__created"),
        )

    def test_simple_change_replace(self):
        current_data = {"title": "Lion", "sound": "Roar!"}
        new_data = {"title": "Lion", "sound": "Roar! Rrrrrrrrrr!"}
        cached_record_histories, edits = self._test_current_data_to_new_data(
            current_data, new_data, EVENT_MODE_REPLACE
        )
        assert 2 == len(cached_record_histories)
        assert 2 == len(edits)
        # test cached_record_histories has expected data
        assert current_data == cached_record_histories[0].data
        assert new_data == cached_record_histories[1].data
        # test edits.get_data_diff_previous_cached_record_history
        assert None == edits[0].get_previous_cached_record_history()
        assert {"sound": "Roar! Rrrrrrrrrr!"} == edits[
            1
        ].get_data_diff_previous_cached_record_history()
        # test cached_record_histories.get_data_diff_previous_cached_record_history
        assert {"sound": "Roar!", "title": "Lion"} == cached_record_histories[
            0
        ].get_data_diff_previous_cached_record_history()
        assert {"sound": "Roar! Rrrrrrrrrr!"} == cached_record_histories[
            1
        ].get_data_diff_previous_cached_record_history()
        # test edits.get_data_fields_include_differences_from_previous_data
        assert [
            {
                "key": "/title",
                "title": "Title",
                "value": "Lion",
                "different_from_previous_value": False,
            },
            {
                "key": "/sound",
                "title": "Sound",
                "value": "Roar! Rrrrrrrrrr!",
                "different_from_previous_value": True,
            },
        ] == edits[1].get_data_fields_include_differences_from_previous_data()
        # test cached_record_histories.get_data_fields_include_differences_from_previous_data
        assert [
            {
                "key": "/title",
                "title": "Title",
                "value": "Lion",
                "different_from_previous_value": True,
            },
            {
                "key": "/sound",
                "title": "Sound",
                "value": "Roar!",
                "different_from_previous_value": True,
            },
        ] == cached_record_histories[
            0
        ].get_data_fields_include_differences_from_previous_data()
        assert [
            {
                "key": "/title",
                "title": "Title",
                "value": "Lion",
                "different_from_previous_value": False,
            },
            {
                "key": "/sound",
                "title": "Sound",
                "value": "Roar! Rrrrrrrrrr!",
                "different_from_previous_value": True,
            },
        ] == cached_record_histories[
            1
        ].get_data_fields_include_differences_from_previous_data()

    def test_simple_change_merge(self):
        current_data = {"title": "Lion", "sound": "Roar!"}
        new_data = {"sound": "Roar! Rrrrrrrrrr!"}
        cached_record_histories, edits = self._test_current_data_to_new_data(
            current_data, new_data, EVENT_MODE_MERGE
        )
        assert 2 == len(cached_record_histories)
        assert 2 == len(edits)
        # test cached_record_histories has expected data
        assert current_data == cached_record_histories[0].data
        assert {
            "sound": "Roar! Rrrrrrrrrr!",
            "title": "Lion",
        } == cached_record_histories[1].data
        # test edits.get_data_diff_previous_cached_record_history
        assert None == edits[0].get_previous_cached_record_history()
        assert {"sound": "Roar! Rrrrrrrrrr!"} == edits[
            1
        ].get_data_diff_previous_cached_record_history()
        # test cached_record_histories.get_data_diff_previous_cached_record_history
        assert {"sound": "Roar!", "title": "Lion"} == cached_record_histories[
            0
        ].get_data_diff_previous_cached_record_history()
        assert {"sound": "Roar! Rrrrrrrrrr!"} == cached_record_histories[
            1
        ].get_data_diff_previous_cached_record_history()
        # test edits.get_data_fields_include_differences_from_previous_data
        assert [
            {
                "key": "/title",
                "title": "Title",
                "value": "Lion",
                "different_from_previous_value": False,
            },
            {
                "key": "/sound",
                "title": "Sound",
                "value": "Roar! Rrrrrrrrrr!",
                "different_from_previous_value": True,
            },
        ] == edits[1].get_data_fields_include_differences_from_previous_data()
        # test cached_record_histories.get_data_fields_include_differences_from_previous_data
        assert [
            {
                "key": "/title",
                "title": "Title",
                "value": "Lion",
                "different_from_previous_value": True,
            },
            {
                "key": "/sound",
                "title": "Sound",
                "value": "Roar!",
                "different_from_previous_value": True,
            },
        ] == cached_record_histories[
            0
        ].get_data_fields_include_differences_from_previous_data()
        assert [
            {
                "key": "/title",
                "title": "Title",
                "value": "Lion",
                "different_from_previous_value": False,
            },
            {
                "key": "/sound",
                "title": "Sound",
                "value": "Roar! Rrrrrrrrrr!",
                "different_from_previous_value": True,
            },
        ] == cached_record_histories[
            1
        ].get_data_fields_include_differences_from_previous_data()
