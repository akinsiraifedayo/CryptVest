import json
from django.core.management.base import BaseCommand
from apps.sales.models import Sim
import os




class Command(BaseCommand):
    ENVIRONMENT = os.getenv('DJANGO_ENVIRONMENT', 'development')

    if ENVIRONMENT == 'production':
        JSON_FILE_PATH = os.getenv('JSON_FILE_PATH', './data.json')
    else:
        JSON_FILE_PATH = './data.json'
        
    help = 'Empties Data'

    # Hardcoded path to the JSON file

    def handle(self, *args, **kwargs):
        with open(self.JSON_FILE_PATH, 'r') as file:
            data = json.load(file)

        numbers = data.get('numbers', {})

        for phone_number, info in numbers.items():
            try:
                sim = Sim.objects.get(phone_number=phone_number)
                if sim.data_left > 0:
                    sim.data_left_before_logout = sim.data_left
                    sim.data_left = 0
                    sim.save()
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error emptying data of {phone_number}: {e}'))
