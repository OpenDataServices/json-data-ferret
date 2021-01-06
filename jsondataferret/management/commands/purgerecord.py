from django.core.management.base import BaseCommand

from jsondataferret.models import Record, Type
from jsondataferret.pythonapi.purge import purge_record


class Command(BaseCommand):
    help = "Purge a record from the database"

    def add_arguments(self, parser):
        parser.add_argument("type_id")
        parser.add_argument("record_id")

    def handle(self, *args, **options):
        type = Type.objects.get(public_id=options["type_id"])
        if type:
            record = Record.objects.get(public_id=options["record_id"])
            if record:
                purge_record(record)
                print("Done")
