from django.core.management.base import BaseCommand
from django.core.serializers import serialize
from apps.sales.models import Sim

class Command(BaseCommand):
    help = 'Export Sim model data to JSON'

    def handle(self, *args, **kwargs):
        data = serialize('json', Sim.objects.all())
        with open('sim_data.json', 'w') as f:
            f.write(data)
        self.stdout.write(self.style.SUCCESS('Successfully exported data to sim_data.json'))
