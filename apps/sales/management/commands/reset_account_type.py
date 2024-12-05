from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.sales.models import UserProfile
from config.decorators import single_instance

class Command(BaseCommand):
    help = 'Reset account type to retailer if expiry date is reached'

    @single_instance()
    def handle(self, *args, **kwargs):
        now = timezone.now()
        expired_profiles = UserProfile.objects.filter(expiry_date__lte=now).exclude(account_type='retailer')
        for profile in expired_profiles:
            profile.account_type = 'retailer'
            profile.expiry_date = None
            profile.save()
            self.stdout.write(self.style.SUCCESS(f'Reset account type for {profile.user.username}'))
