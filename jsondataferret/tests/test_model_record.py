from django.test import TestCase  # noqa

from jsondataferret import EVENT_MODE_MERGE
from jsondataferret.models import Record, Type
from jsondataferret.pythonapi.newevent import NewEventData, newEvent


class FilterCase(TestCase):
    def test_filter_needs_moderation_by_type(self):
        type_model = Type()
        type_model.public_id = "animal"
        type_model.title = "Animal"
        type_model.save()

        # no records, so no results
        assert 0 == len(Record.objects.filter_needs_moderation_by_type(type_model))

        # Create a record, approve straight away
        newEvent(
            [
                NewEventData(
                    "animal",
                    "lion",
                    {"title": "Lion", "sound": "Roar!"},
                    approved=True,
                )
            ],
            None,
        )

        # already approved so no results
        assert 0 == len(Record.objects.filter_needs_moderation_by_type(type_model))

        # Create a edit to that record that is not approved
        newEvent(
            [
                NewEventData(
                    "animal",
                    "lion",
                    {"title": "Lion", "sound": "Roar ROAR!"},
                    approved=False,
                )
            ],
            None,
        )

        # now there is a record
        assert 1 == len(Record.objects.filter_needs_moderation_by_type(type_model))

        # Create a second edit to that record that is not approved
        newEvent(
            [
                NewEventData(
                    "animal",
                    "lion",
                    {"title": "Lion", "sound": "Purr"},
                    approved=False,
                )
            ],
            None,
        )

        # Several edits, but only one record
        assert 1 == len(Record.objects.filter_needs_moderation_by_type(type_model))


class TestCachedData(TestCase):
    def _setup_basic_record(self):
        # Not using setUp - if we do, any problems count as a error not failure.

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
                    {"title": "Lion", "sound": "Roar!"},
                    approved=True,
                )
            ],
            None,
        )

        # Test record cached data
        record = Record.objects.get()
        assert {"title": "Lion", "sound": "Roar!"} == record.cached_data

    def test_replace_edit(self):
        self._setup_basic_record()

        # Replace whole record
        newEvent(
            [
                NewEventData(
                    "animal",
                    "lion",
                    {"title": "Lion", "sound": "Roar! Rrrrrrrrrrrrr!"},
                    approved=True,
                )
            ],
            None,
        )

        # Test record cached data
        record = Record.objects.get()
        assert {"title": "Lion", "sound": "Roar! Rrrrrrrrrrrrr!"} == record.cached_data

    def test_merge_edit(self):
        self._setup_basic_record()

        # Replace whole record
        newEvent(
            [
                NewEventData(
                    "animal",
                    "lion",
                    {"sound": "Roar! Rrrrrrrrrrrrr!"},
                    approved=True,
                    mode=EVENT_MODE_MERGE,
                )
            ],
            None,
        )

        # Test record cached data
        record = Record.objects.get()
        assert {"title": "Lion", "sound": "Roar! Rrrrrrrrrrrrr!"} == record.cached_data
