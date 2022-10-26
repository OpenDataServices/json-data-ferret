from django.test import TestCase  # noqa

from jsondataferret import EVENT_MODE_MERGE, EVENT_MODE_REPLACE
from jsondataferret.models import Edit, Type
from jsondataferret.pythonapi.newevent import NewEventData, newEvent


class NewEditCase(TestCase):
    type = None

    def setUp(self):
        self.type = Type()
        self.type.public_id = "animal"
        self.type.title = "Animal"
        self.type.save()

    def test_basic(self):
        """hello world"""
        data = NewEventData("animal", "lion", {"title": "Lion", "sound": "Roar!"})
        assert {
            "title": "Lion",
            "sound": "Roar!",
        } == data.get_new_data_when_event_applied_to_latest_record_cached_data()
        newEvent([data], None)

        edits = Edit.objects.all()
        assert 1 == len(edits)
        assert edits[0].data["sound"] == "Roar!"

    def test_replace_mode_with_no_change(self):
        # Apply inital data
        data_initial = NewEventData(
            "animal",
            "lion",
            {"title": "Lion", "sound": "Roar!"},
            approved=True,
        )
        assert data_initial.does_this_create_or_change_record()
        assert (
            {"title": "Lion", "sound": "Roar!"}
            == data_initial.get_new_data_when_event_applied_to_latest_record_cached_data()
        )
        # Save it so we have record to compare more edits to
        newEvent([data_initial], None)
        # Data with Mode Replace
        data_replace = NewEventData(
            "animal",
            "lion",
            {"title": "Lion", "sound": "Roar!"},
            mode=EVENT_MODE_REPLACE,
        )
        assert not data_replace.does_this_create_or_change_record()
        assert (
            {"title": "Lion", "sound": "Roar!"}
            == data_replace.get_new_data_when_event_applied_to_latest_record_cached_data()
        )

    def test_merge_mode_with_no_change(self):
        # Apply inital data
        data_initial = NewEventData(
            "animal",
            "lion",
            {"title": "Lion", "sound": "Roar!"},
            approved=True,
        )
        assert data_initial.does_this_create_or_change_record()
        assert (
            {"title": "Lion", "sound": "Roar!"}
            == data_initial.get_new_data_when_event_applied_to_latest_record_cached_data()
        )
        # Save it so we have record to compare more edits to
        newEvent([data_initial], None)
        # Data with Mode Merge
        data_merge = NewEventData(
            "animal", "lion", {"title": "Lion"}, mode=EVENT_MODE_MERGE
        )
        assert not data_merge.does_this_create_or_change_record()
        assert (
            {"title": "Lion", "sound": "Roar!"}
            == data_merge.get_new_data_when_event_applied_to_latest_record_cached_data()
        )

    def test_replace_mode_with_change(self):
        # Apply inital data
        data_initial = NewEventData(
            "animal",
            "lion",
            {"title": "Lion", "sound": "Roar!"},
            approved=True,
        )
        assert data_initial.does_this_create_or_change_record()
        assert (
            {"title": "Lion", "sound": "Roar!"}
            == data_initial.get_new_data_when_event_applied_to_latest_record_cached_data()
        )
        # Save it so we have record to compare more edits to
        newEvent([data_initial], None)
        # Data with Mode Replace
        data_replace = NewEventData(
            "animal",
            "lion",
            {"title": "Big Cat", "sound": "Roar!"},
            mode=EVENT_MODE_REPLACE,
        )
        assert data_replace.does_this_create_or_change_record()
        assert (
            {"title": "Big Cat", "sound": "Roar!"}
            == data_replace.get_new_data_when_event_applied_to_latest_record_cached_data()
        )

    def test_merge_mode_with_change(self):
        # Apply inital data
        data_initial = NewEventData(
            "animal",
            "lion",
            {"title": "Lion", "sound": "Roar!"},
            approved=True,
        )
        assert data_initial.does_this_create_or_change_record()
        assert (
            {"title": "Lion", "sound": "Roar!"}
            == data_initial.get_new_data_when_event_applied_to_latest_record_cached_data()
        )
        # Save it so we have record to compare more edits to
        newEvent([data_initial], None)
        # Data with Mode Merge
        data_merge = NewEventData(
            "animal", "lion", {"title": "Pretty Cat"}, mode=EVENT_MODE_MERGE
        )
        assert data_merge.does_this_create_or_change_record()
        assert (
            {"title": "Pretty Cat", "sound": "Roar!"}
            == data_merge.get_new_data_when_event_applied_to_latest_record_cached_data()
        )
