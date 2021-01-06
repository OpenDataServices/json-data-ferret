from django.test import TestCase  # noqa

from jsondataferret.models import Edit, Event, Record, Type
from jsondataferret.pythonapi.newevent import NewEventData, newEvent
from jsondataferret.pythonapi.purge import purge_record


class FilterCase(TestCase):
    def test_filter_needs_moderation_by_type(self):
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

        records = Record.objects.all()
        assert 1 == len(records)

        # Purge record
        purge_record(records[0])

        # Test
        assert 0 == len(Record.objects.all())
        assert 0 == len(Event.objects.all())
        assert 0 == len(Edit.objects.all())
