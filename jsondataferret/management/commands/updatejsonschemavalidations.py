from django.conf import settings
from django.core.management.base import BaseCommand

from jsondataferret.models import Record, Type


class Command(BaseCommand):
    help = "When JSON Schema changed, update all cached validations"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        for type in Type.objects.all():
            type_data = settings.JSONDATAFERRET_TYPE_INFORMATION.get(type.public_id, {})
            if type_data.get("json_schema"):
                for record in Record.objects.filter(type=type, cached_exists=True):
                    record.validate_with_json_schema(type_data.get("json_schema"))
                    record.save()
