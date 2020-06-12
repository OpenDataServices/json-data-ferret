from django.test import TestCase  # noqa

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
