from django.core.management.base import BaseCommand
from django.core.serializers import deserialize
from apps.sales.models import Sim

class Command(BaseCommand):
    help = 'Import Sim model data from JSON'

    def handle(self, *args, **kwargs):
        with open('sim_data.json', 'r') as f:
            for obj in deserialize('json', f.read()):
                obj.save()
        self.stdout.write(self.style.SUCCESS('Successfully imported data from sim_data.json'))
