import json
from django.core.management.base import BaseCommand
from apps.sales.models import Sim
import os
from django.utils import timezone
from datetime import timedelta
from config.decorators import single_instance
import time


class Command(BaseCommand):
    ENVIRONMENT = os.getenv('DJANGO_ENVIRONMENT', 'development')

    if ENVIRONMENT == 'production':
        JSON_FILE_PATH = os.getenv('JSON_FILE_PATH', './data.json')
    else:
        JSON_FILE_PATH = './data.json'

    help = 'Update access tokens from a JSON file'

    # Hardcoded path to the JSON file
    @single_instance()
    def handle(self, *args, **kwargs):
        with open(self.JSON_FILE_PATH, 'r') as file:
            data = json.load(file)

        numbers = data.get('numbers', {})

        for phone_number, info in numbers.items():
            try:
                sim, created = Sim.objects.get_or_create(phone_number=phone_number)
                sim.access_token = info.get('access_token', '')
                sim.refresh_token = info.get('refresh_token', '')
                sim.refresh_time = timezone.now()

                # unneeded stuff starts here
                sim.client_id = info.get('client_id', '')
                sim.cookie = info.get('Cookie', '')
                sim.otp = info.get('otp', '')
                sim.phone_number = phone_number
                sim.auth0_client = info.get('Auth0-Client', '')
                # sim.data_left = 5000
                sim.sim_number = int(info.get('number', ''))
                logged_in = info.get('logged_in', '')
                if logged_in == "false" and not sim.logged_in:
                    sim.confirmed_logged_in = False
                else:
                    sim.confirmed_logged_in = True
                if logged_in == "false":
                    sim.logged_in = False
                else:
                    sim.logged_in = True
                if not sim.expiry_date:
                    sim.expiry_date = timezone.now() + timedelta(days=80)


                # sim.current_balance = int(info.get('current_balance', ''))

                # unneeded stuff ends here
                sim.save()
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Successfully created new SIM for {phone_number}'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Successfully updated SIM for {phone_number}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error updating {phone_number}: {e}'))
