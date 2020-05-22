from django.test import TestCase  # noqa

from .models import Edit, Type
from .pythonapi.newevent import NewEventData, newEvent


class NewEditCase(TestCase):
    def setUp(self):
        Type.objects.create(public_id="animal", title="Animal")

    def test_basic(self):
        """hello world"""
        data = NewEventData("animal", "lion", {"title": "Lion", "sound": "Roar!"})
        newEvent([data], None)

        edits = Edit.objects.all()
        assert 1 == len(edits)
        assert edits[0].data["sound"] == "Roar!"
