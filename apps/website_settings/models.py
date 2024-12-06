from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.
class WebsiteSettings(models.Model):
    ACCOUNT_TYPES = (
        ('retailer', 'Retailer'),
        ('vendor', 'Vendor'),
        ('custom', 'Custom'),
    )

    referral_allowed = models.BooleanField(default=False)
    referral_percentage = models.DecimalField(max_digits=10, decimal_places=2, default=5)
    merchant_referral_allowed = models.BooleanField(default=False)
    merchant_referral_percentage = models.DecimalField(max_digits=10, decimal_places=2, default=10)
    max_num_of_data_retries = models.IntegerField(default=5)
    support_email = models.EmailField(null=True, blank=True)
    support_phone = models.CharField(null=True, blank=True, max_length=15)
    investment_allowed = models.BooleanField(default=False)
    investment_withdrawal_allowed = models.BooleanField(default=False)
    deposit_address = models.CharField(null=True, blank=True, max_length=50, default="0x4e5acf9684652BEa56F2f01b7101a225Ee33d23f")

    referral_withdrawal_allowed = models.BooleanField(default=True)

    maintenance_mode = models.BooleanField(default=False)
    maintenance_end = models.DateTimeField(null=True, blank=True)
    


    def save(self, *args, **kwargs):
        if not self.pk and WebsiteSettings.objects.exists():
            raise ValidationError('There can be only one WebsiteSettings instance')
        return super(WebsiteSettings, self).save(*args, **kwargs)

    def end_maintenance(self):
        self.maintenance_mode = False
        self.maintenance_end = ""
        self.save()

    def __str__(self):
        return "Website Settings"

class InvestmentSetting(models.Model):
    min_investment = models.DecimalField(max_digits=10, decimal_places=2, default=1000)
    max_investment = models.DecimalField(max_digits=10, decimal_places=2, default=500000)
    min_withdrawal = models.DecimalField(max_digits=10, decimal_places=2, default=1000)
    max_withdrawal = models.DecimalField(max_digits=10, decimal_places=2, default=500000)
    withdrawal_fees_percent = models.DecimalField(max_digits=10, decimal_places=2, default=10)
    
    def save(self, *args, **kwargs):
        if not self.pk and InvestmentSetting.objects.exists():
            raise ValidationError('There can be only one InvestmentSetting instance')
        return super(InvestmentSetting, self).save(*args, **kwargs)

    def end_maintenance(self):
        self.maintenance_mode = False
        self.maintenance_end = ""
        self.save()

    def __str__(self):
        return "Investment Settings"
    
