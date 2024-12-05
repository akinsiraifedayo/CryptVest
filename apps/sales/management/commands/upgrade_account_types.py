from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.sales.models import UserProfile

class Command(BaseCommand):
    help = 'Update account types and expiry dates'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        one_year_from_now = now + timedelta(days=365)  # 1 year from now

        # Filter and update expiry dates for all profiles
        UserProfile.objects.update(expiry_date=one_year_from_now)
        UserProfile.objects.update(account_type='vendor')
        
        self.stdout.write(self.style.SUCCESS('Updated expiry dates and account type for all profiles'))
