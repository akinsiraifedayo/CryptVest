
from django.core.management.base import BaseCommand
from apps.investments.models import Investment
import os
from datetime import datetime, timedelta
from django.db import transaction
from django.utils import timezone
from config.decorators import single_instance
from apps.investments.models import Wallet
from apps.website_settings.models import WebsiteSettings




class Command(BaseCommand):
    ENVIRONMENT = os.getenv('DJANGO_ENVIRONMENT', 'development')

    help = 'Daily Tasks'

    # Hardcoded path to the JSON file
    @single_instance()
    def handle(self, *args, **kwargs,):    
        investments = Investment.objects.filter(is_active=True)
        for investment in investments:
            investment.give_roi()

        for wallet in Wallet.objects.all():
            wallet.update_balances()
