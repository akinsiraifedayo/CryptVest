import json
from django.core.management.base import BaseCommand
from apps.sales.models import Sim
import os
from config.decorators import single_instance




class Command(BaseCommand):
    ENVIRONMENT = os.getenv('DJANGO_ENVIRONMENT', 'development')

    if ENVIRONMENT == 'production':
        JSON_FILE_PATH = os.getenv('JSON_FILE_PATH', './data.json')
    else:
        JSON_FILE_PATH = './data.json'

    help = 'Restocks Data of Logged Out Sims or JWT Token Expired Ones'

    # Hardcoded path to the JSON file
    @single_instance()
    def handle(self, *args, **kwargs):
        with open(self.JSON_FILE_PATH, 'r') as file:
            data = json.load(file)

        numbers = data.get('numbers', {})

        for phone_number, info in numbers.items():
            try:
                sim = Sim.objects.get(phone_number=phone_number)
                if sim.logged_in and (sim.data_left == 10 or sim.data_left == 5005 or sim.data_left == 1):
                    if sim.data_left == 10:
                        # SIM HAS INSUFFICIENT BALANCE REDUCE AND TRY AGAIN
                        sim.data_left = sim.data_left_before_logout - 500
                        sim.data_left_before_logout = 0
                        sim.save()
                    elif (sim.data_left == 5005) or (sim.data_left == 1):
                        # JWT TOKEN NO NEED TO REDUCE BALANCE
                        sim.data_left = sim.data_left_before_logout
                        sim.data_left_before_logout = 0
                        sim.save()
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error restocking {phone_number}: {e}'))
