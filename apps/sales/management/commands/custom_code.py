import json
from django.core.management.base import BaseCommand
from apps.sales.models import Sim
import os
from apps.sales.models import Sim, UserProfile
from django.utils import timezone
from datetime import timedelta, datetime




class Command(BaseCommand):

    JSON_FILE_PATH = './sim_data.json'
    help = 'Restocks Data of some sims'

    # Hardcoded path to the JSON file

    def handle(self, *args, **kwargs):
        # with open(self.JSON_FILE_PATH, 'r') as file:
        #     data = json.load(file)

        # numbers = data.get('numbers', {})

        # for phone_number, info in numbers.items():
        #     try:
        #         sim = Sim.objects.get(phone_number=phone_number)
        #         # sim.sim_number = info['number']
        #         if sim.sim_number > 75 and sim.sim_number < 91:
        #             # sim.data_left = 5000
        #             # sim.data_sent = 0
        #             sim.priority = 999
        #         else:
        #             sim.priority = 100
        #         sim.save()

        #     except Exception as e:
        #         self.stdout.write(self.style.ERROR(f'Error editing {phone_number}: {e}'))
        # now = timezone.now()
        # today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        # today = today - timedelta(hours=1)

        # Retrieve SIMs with no transactions yesterday
        # UserProfile.objects.all().update(transaction_in_progress=False)

        # Sim.objects.filter(data_left=5).update(data_left=5005)


        # today = timezone.now().date()
        # print(today)

        # # Filter sims whose restock_date is not today
        # sims_not_restocked_today = Sim.objects.exclude(restock_time__date=today)

        # for sim in Sim.objects.all():
        #     print(f"Sim ID: {sim.sim_number}, Phone Number: {sim.phone_number}, Restock Date: {sim.restock_time}")
        # print('nooooooooooooooooooooooooooooooooooooooo')
        # # Print the results
        # for sim in sims_not_restocked_today:
        #     print(f"Sim ID: {sim.sim_number}, Phone Number: {sim.phone_number}, Restock Date: {sim.restock_time}")

        # # START 
        # # verify a specidic transaction with flutterwve ID
        # from apps.sales.views import verify_transaction
        # print(verify_transaction(1509973466))
        # # END
        
        # self.stdout.write(self.style.SUCCESS(f'Successfully updated expiry_date for {updated_count} records.'))
        
        # start restock -2 sims
        exhausted_sims = Sim.objects.filter(current_balance=-2)
        for sim in exhausted_sims:
            sim.data_left = 5000
            sim.current_balance = (sim.expiry_date - timezone.now()).days * 5000
            sim.save()
        print("done")
