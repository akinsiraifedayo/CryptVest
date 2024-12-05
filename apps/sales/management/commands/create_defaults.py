# myapp/management/commands/populate_default_data.py

from django.core.management.base import BaseCommand
from apps.website_settings.models import WebsiteSettings, InvestmentSetting
from apps.sales.models import DataPackage

class Command(BaseCommand):
    help = 'Populate the database with default data'

    def handle(self, *args, **kwargs):
        # Create default data
        if not WebsiteSettings.objects.exists():
            WebsiteSettings.objects.create()
            self.stdout.write(self.style.SUCCESS('WebsiteSettings created successfully.'))
        else:
            self.stdout.write(self.style.NOTICE('WebsiteSettings already exists.'))

        if not DataPackage.objects.exists():
            DataPackage.objects.create(name="500 MB", description="ME2U_NG_Data2Share_857", vendor_price=125, data_qty=500)
            self.stdout.write(self.style.SUCCESS('DataPackage created successfully.'))
        else:
            self.stdout.write(self.style.NOTICE('DataPackage already exists.'))

        if not InvestmentSetting.objects.exists():
            InvestmentSetting.objects.create()
            self.stdout.write(self.style.SUCCESS('InvestmentSetting created successfully.'))
        else:
            self.stdout.write(self.style.NOTICE('InvestmentSetting already exists.'))
