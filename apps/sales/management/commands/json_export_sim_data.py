import json
from django.core.management.base import BaseCommand
from apps.sales.models import Sim

class Command(BaseCommand):
    help = 'Export Sim data to JSON'

    def handle(self, *args, **kwargs):
        # Fetch all Sim instances
        sims = Sim.objects.all()

        # Prepare the data in the specified format
        data = {"numbers": {}}
        for sim in sims:
            sim_phone_num = str(sim.phone_number)
            data["numbers"][sim.phone_number] = {
                "access_token": sim.access_token,
                "Auth0-Client": sim.auth0_client,
                "client_id": sim.client_id,
                "Cookie": sim.cookie,
                "otp": sim.otp,
                "phone_number": f'+234{sim_phone_num[1:]}',
                "refresh_token": sim.refresh_token,
                "data_left": sim.data_left,
                "data_sent": sim.data_sent,
                "is_exhausted": sim.is_exhausted,
                "prev_day_data_sent": sim.prev_day_data_sent,
                "number": sim.sim_number,
                "current_balance": sim.current_balance,
                "logged_in": "true" if sim.logged_in else "false",
                "data_left_before_logout": sim.data_left_before_logout
            }
        print(data)

        # Convert the data to JSON
        json_data = json.dumps(data, indent=4)

        # Write JSON data to a file
        with open('./sim_data.json', 'w') as json_file:
            print('opened')
            json_file.write(json_data)

        self.stdout.write(self.style.SUCCESS('Successfully exported Sim data to sim_data.json'))
