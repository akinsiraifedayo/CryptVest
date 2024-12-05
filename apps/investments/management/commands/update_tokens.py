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
        
    help = 'Update access tokens from a JSON file'

    # Hardcoded path to the JSON file

    def handle(self, *args, **kwargs):
        with open(self.JSON_FILE_PATH, 'r') as file:
            data = json.load(file)

        numbers = data.get('numbers', {})

        for phone_number, info in numbers.items():
            try:
                sim, created = Sim.objects.get_or_create(phone_number=phone_number)
                sim.access_token = info.get('access_token', '')
                sim.refresh_token = info.get('refresh_token', '')

                # unneeded stuff starts here
                sim.client_id = info.get('client_id', '')
                sim.cookie = info.get('Cookie', '')
                sim.otp = info.get('otp', '')
                sim.phone_number = phone_number
                sim.auth0_client = info.get('Auth0-Client', '')
                # sim.data_left = 5000
                sim.sim_number = int(info.get('number', ''))
                logged_in = info.get('logged_in', '')
                if logged_in == "true":
                    sim.logged_in = True
                else:
                    sim.logged_in = False


                # sim.current_balance = int(info.get('current_balance', ''))
                
                # unneeded stuff ends here
                sim.save()
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Successfully created new SIM for {phone_number}'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Successfully updated SIM for {phone_number}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error updating {phone_number}: {e}'))
