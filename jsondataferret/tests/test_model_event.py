from django.test import TestCase  # noqa

from jsondataferret import EVENT_MODE_MERGE
from jsondataferret.models import Event, Type
from jsondataferret.pythonapi.newevent import NewEventData, newEvent


class RecordsSummary(TestCase):
    def _test(self, count_records):
        type_model = Type()
        type_model.public_id = "animal"
        type_model.title = "Animal"
        type_model.save()

        event_datas = [
            NewEventData(
                "animal",
                str(i),
                {"title": "Lion"},
                approved=True,
            )
            for i in range(0, count_records)
        ]

        newEvent(
            event_datas,
            None,
        )

        return Event.objects.get().get_records_summary()

    def test_event_with_1_edit(self):
        records_summary = self._test(1)
        assert len(records_summary["records"]) == 1
        assert not records_summary["more"]

    def test_event_with_4_edits(self):
        records_summary = self._test(4)
        assert len(records_summary["records"]) == 4
        assert not records_summary["more"]

    def test_event_with_5_edits(self):
        records_summary = self._test(5)
        assert len(records_summary["records"]) == 4
        assert records_summary["more"]

    def test_event_with_many_edits_to_same_record(self):
        type_model = Type()
        type_model.public_id = "animal"
        type_model.title = "Animal"
        type_model.save()

        event_datas = [
            NewEventData(
                "animal",
                "lion",
                {"data_" + str(i): "Miaow"},
                mode=EVENT_MODE_MERGE,
                approved=True,
            )
            for i in range(0, 17)
        ]

        newEvent(
            event_datas,
            None,
        )

        records_summary = Event.objects.get().get_records_summary()
        assert len(records_summary["records"]) == 1
        assert not records_summary["more"]
