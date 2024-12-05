from django.core.management.base import BaseCommand
from apps.sales.models import Sim, Transaction, OnlineTransaction, WebhookLog, UserRequest
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

    help = 'Ten minute tasks'
    
    # Hardcoded path to the JSON file
    @single_instance()
    def handle(self, *args, **kwargs,):

        # check all wallets
        main_wallets = Wallet.objects.filter(is_visible=True, is_verified=True)
        for wallet in main_wallets:
            wallet.update_balances()



        
