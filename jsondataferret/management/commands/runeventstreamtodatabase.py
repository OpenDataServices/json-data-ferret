from django.core.management.base import BaseCommand

from jsondataferret.pythonapi.runevents import clear_data_and_run_all_events


class Command(BaseCommand):
    help = "Run Event Stream Into Database"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        clear_data_and_run_all_events()
