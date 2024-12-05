from django.core.management.base import BaseCommand
from apps.sales.models import Sim, Transaction, OnlineTransaction, WebhookLog, UserRequest
from apps.investments.models import Investment
import os
from datetime import datetime, timedelta
from django.db import transaction
from django.utils import timezone
from config.decorators import single_instance




class Command(BaseCommand):
    ENVIRONMENT = os.getenv('DJANGO_ENVIRONMENT', 'development')

    if ENVIRONMENT == 'production':
        JSON_FILE_PATH = os.getenv('JSON_FILE_PATH', './data.json')
    else:
        JSON_FILE_PATH = './data.json'

    help = 'Restocks Data of Numbers from a JSON file'

    # Hardcoded path to the JSON file
    @single_instance()
    def handle(self, *args, **kwargs,):
        # with open(self.JSON_FILE_PATH, 'r') as file:
        #     data = json.load(file)

        # numbers = data.get('numbers', {})
        # count = 0
        # for phone_number, info in numbers.items():
        #     try:
        #         sim = Sim.objects.get(phone_number=phone_number)
        #         sim.data_left = 5000

        #         if phone_number == '07061755693':
        #             sim.data_left = 0
        #         sim.is_exhausted = False
        #         sim.prev_day_data_sent = sim.data_sent
        #         sim.data_sent = 0
        #         sim.data_left_before_logout = 0
        #         sim.restock_time = timezone.now()
        #         count += 1
        #         sim.save()
        #     except Exception as e:
        #         self.stdout.write(self.style.ERROR(f'Error restocking {phone_number}: {e}'))
        sims = Sim.objects.all()
        count = 0
        dont_restock = set(['09030796423', '07077539772', '07075621971', '07077079152'])

        for sim in sims:
            try:
                sim.data_left = 5000
                if sim.phone_number in dont_restock:
                    sim.data_left = 0
                sim.is_exhausted = False
                sim.prev_day_data_sent = sim.data_sent
                sim.data_sent = 0
                sim.data_left_before_logout = 0
                sim.restock_time = timezone.now()
                count += 1
                sim.save()
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error restocking {sim.phone_number}: {e}'))
        print(f'restocked {count} sims')




        one_month_ago = datetime.now() - timedelta(days=30)
        try:
            # Delete transactions older than one month
            with transaction.atomic():
                deleted_count, _ = Transaction.objects.filter(timestamp__lt=one_month_ago).delete()

            print(f"Deleted {deleted_count} transactions older than one month.")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error Deleting Transaction: {e}'))

        # delete online transactions older than one month
        try:
            with transaction.atomic():
                deleted_count, _ = OnlineTransaction.objects.filter(created_at__lt=one_month_ago).delete()

            print(f"Deleted {deleted_count} online transactions older than one month.")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error Deleting Transaction: {e}'))

        # delete pending online transactions older than one month
        try:
            with transaction.atomic():
                deleted_count, _ = WebhookLog.objects.filter(timestamp__lt=one_month_ago).delete()

            print(f"Deleted {deleted_count} WebHook logs older than one month.")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error Deleting Transaction: {e}'))



        # give all investments
        investments = Investment.objects.filter(is_active=True)
        for investment in investments:
            investment.give_roi()


        day_before_yesterday = datetime.now() - timedelta(days=2)
        try:
            # Delete transactions older than one month
            with transaction.atomic():
                deleted_count, _ = UserRequest.objects.filter(timestamp__lt=day_before_yesterday).delete()

            print(f"Deleted {deleted_count} user requests older than day_before_yesterday.")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error Deleting UserRequest: {e}'))
