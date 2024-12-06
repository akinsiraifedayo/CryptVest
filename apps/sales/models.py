import decimal
import json
import os
import uuid
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.db.models import Max
from apps.website_settings.models import WebsiteSettings
from django.contrib.auth.models import User
import datetime
import string

class UserRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

class UserProfile(models.Model):
    ACCOUNT_TYPES = (
        ('retailer', 'Retailer'),
        ('vendor', 'Vendor'),
        ('custom', 'Custom'),
        ('merchant', 'Merchant')
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    investment_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True, null=True)
    referral_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True, null=True)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True, null=True)
    fees_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True, null=True)
    
    phone_number = models.CharField(max_length=15, null=True, blank=True, default="")
    account_type = models.CharField(max_length=8, choices=ACCOUNT_TYPES, default='retailer')
    expiry_date = models.DateTimeField(null=True, blank=True)
    referral_code = models.CharField(max_length=15, null=True, blank=True, default="")
    referred_by = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='referrals')
    bonus_given_to_referred_by = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True, null=True)
    bonus_gotten_from_referrals = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True, null=True)
    allowed_to_invest = models.BooleanField(default=True, blank=True, null=True)
    withdrawal_fees_percent = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    random_token = models.CharField(max_length=32, blank=True, default=True)



    transaction_in_progress = models.BooleanField(default=False)



    def __str__(self):
        return self.user.username
    
    def transfer_wallet_to_investment(self):
        self.investment_balance += self.wallet_balance
        self.wallet_balance = 0.00
        self.save()

    def transfer_wallet_to_fees(self):
        self.fees_balance += self.wallet_balance
        self.wallet_balance = 0.00
        self.save()

    def create_data_transaction(self, amount, transaction_type, sim, phone_number, data_package, tr_response):
        if transaction_type not in ['credit', 'debit']:
            raise ValueError('Invalid transaction type')

        if transaction_type == 'debit':
            sim.deduct_data(int(data_package.data_qty))
            self.give_referral_bonus(amount)
        else:  # credit
            self.balance += amount
        self.save()

        # Create a transaction record
        Transaction.objects.create(
            user_profile=self,
            amount=amount,
            transaction_type=transaction_type,
            timestamp=timezone.now(),
            sim=sim,
            phone_number=phone_number,
            package=data_package,
            tr_response=tr_response
        )

    def create_deposit_txn(self, amount):
        unique_id = str(uuid.uuid4().int)[:10]  # Unique 10-digit numeric ID
        transaction = OnlineTransaction.objects.create(
            user_profile=self,
            amount=amount,
            reference=f"TXN_{self.id}_{unique_id}",
            status="successful",
            is_processed=True
        )
        self.wallet_balance += decimal.Decimal(amount)
        self.save()

    def give_referral_bonus(self, amount):
        # referral aspect
        website_settings = WebsiteSettings.objects.first()
        if website_settings and self.referred_by:
            # Determine the referral bonus percentage
            if website_settings.merchant_referral_allowed and self.referred_by.account_type == 'merchant':
                referral_bonus_percentage = website_settings.merchant_referral_percentage
            elif website_settings.referral_allowed:
                referral_bonus_percentage = website_settings.referral_percentage
            else:
                referral_bonus_percentage = None

            # Apply the referral bonus if a valid percentage was found
            if referral_bonus_percentage:
                referral_bonus = amount * (referral_bonus_percentage / 100)
                self.bonus_given_to_referred_by += referral_bonus
                self.referred_by.referral_balance += referral_bonus
                self.referred_by.bonus_gotten_from_referrals += referral_bonus
                self.referred_by.save()

    def sufficent_balance(self, amount):
        if self.balance < amount:
            return False
        return True

    def sufficent_investment_balance(self, amount):
        if self.investment_balance < amount:
            return False
        return True

    
    
    def sufficent_withdrawal_balance(self, amount):
        if self.investment_balance < amount:
            return False
        return True

    def sufficent_referral_withdrawal_balance(self, amount):
        if self.referral_balance < amount:
            return False
        return True

    def add_balance_from_admin(self, amount, added_by):
        self.wallet_balance += amount
        self.save()
        AdminTransaction.objects.create(
            user_profile=self,
            amount=amount,
            added_by=added_by
        )

    def add_roi(self, roi):
        roi = int(roi)
        if self.investment_balance is None:
            self.investment_balance = 0.00
        self.investment_balance += roi
        self.save()

    def add_balance(self, amount):
        self.balance += amount
        self.save()

    def deduct_balance(self, amount):
        self.balance -= amount
        self.save()


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()



class AccountType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    exact_name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=50, unique=True, default=None)
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    yearly_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)


    def __str__(self):
        return self.name

    def get_functions(self):
        return [function.description for function in self.functions.all()]

class AccountFunction(models.Model):
    account_type = models.ForeignKey(AccountType, related_name='functions', on_delete=models.CASCADE)
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.description


class AdminTransaction(models.Model):
    user_profile = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='admin_transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(default=timezone.now)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user_profile.user.username} - {self.amount} - {self.timestamp}"

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    )

    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=6, choices=TRANSACTION_TYPES)
    timestamp = models.DateTimeField()
    sim = models.ForeignKey('Sim', on_delete=models.CASCADE, related_name='transactions', null=True, blank=True)
    package = models.ForeignKey('DataPackage', on_delete=models.CASCADE, related_name='transactions', null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    tr_response = models.TextField(blank=True, null=True, default='tr_response')




    def __str__(self):
        return f"{self.user_profile.user.username} - {self.transaction_type} - {self.amount}"

    def save(self, *args, **kwargs):
        if not self.id:
            last_transaction = Transaction.objects.order_by('-id').first()
            if last_transaction:
                last_id = int(last_transaction.id)
                if last_id < 9000000:
                    last_id = 9000000
            else:
                last_id = 9000000  # Start from 9 million if no transactions exist yet
            new_id = last_id + 1
            self.id = str(new_id)
        super().save(*args, **kwargs)

    def sim_number(self):
        return self.sim.sim_number



class DataPackageManager(models.Manager):
    def select_package(self, description):
        return self.filter(description=description).first()


class DataPackage(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    vendor_price = models.DecimalField(max_digits=10, decimal_places=2)
    retailer_price = models.DecimalField(max_digits=10, decimal_places=2, default=99999)
    custom_price = models.DecimalField(max_digits=10, decimal_places=2, default=99999)
    data_qty = models.IntegerField()  # e.g., '1GB', '5GB'
    display_order = models.IntegerField(default=100, null=True, blank=True)

    objects = DataPackageManager()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.vendor_price:
            # Calculate vendor price as 1.25 times the retailer price
            self.vendor_price = self.retailer_price * 1.25
        super().save(*args, **kwargs)

    def get_price(self, account_type):
        if account_type in ['vendor', 'merchant']:
            return self.vendor_price
        elif account_type == 'retailer':
            return self.retailer_price
        elif account_type == 'custom':
            return self.custom_price
        else:
            return self.retailer_price



class SimManager(models.Manager):
    def with_data_left(self):
        return self.filter(data_left__gt=0)

    def with_enough_data(self, data_requested):
        data_requested = int(data_requested) - 1
        eligible_sims = self.filter(data_left__gt=data_requested, logged_in=True, just_refreshed=True)
        # if data_requested < 50:
        #     return eligible_sims.order_by('-expiry_date', 'priority').first()

        # if data_requested < 500:
        #     return self.filter(is_exhausted=False, logged_in=True).order_by('-expiry_date', '-priority').last()

        if data_requested > 4000:
            return eligible_sims.order_by('-expiry_date').first()

        # General case
        return eligible_sims.order_by('expiry_date', 'priority').first()


    def max_data_left(self):
        max_data_value = self.aggregate(Max('data_left'))['data_left__max']
        if max_data_value is not None:
            return self.filter(data_left=max_data_value).first()
        return None

    def all_sims_balance(self):
        sims = self.all()
        total = 0
        total_num_of_sims = sims.count()
        for sim in sims:
            total += sim.data_left
        try:
            total_percent = total / (total_num_of_sims * 5000) * 100
        except:
            total_percent = 0
        return f'{format(total_percent, ".2f")} %'

    def needs_fresh_token(self):
        first_five = list(self.filter(data_left__gt=4999, logged_in=True)
                                    .order_by('-expiry_date')
                                    .values_list('phone_number', flat=True)[:5])

        # Fetch phone numbers for the last five SIMs based on expiry_date and -priority
        last_five = list(self.filter(data_left__gt=499, logged_in=True)
                                    .order_by('expiry_date', 'priority')
                                    .values_list('phone_number', flat=True)[:5])

        needs_refresh = set(first_five + last_five)


        return needs_refresh

    def refresh_all_sims_from_json(self):
        ENVIRONMENT = os.getenv('DJANGO_ENVIRONMENT', 'development')

        if ENVIRONMENT == 'production':
            JSON_FILE_PATH = os.getenv('JSON_FILE_PATH', './data.json')
        else:
            JSON_FILE_PATH = './data.json'

        # Hardcoded path to the JSON file
        with open(JSON_FILE_PATH, 'r') as file:
            data = json.load(file)

        numbers = data.get('numbers', {})

        for phone_number, info in numbers.items():
            try:
                sim, created = Sim.objects.get_or_create(phone_number=phone_number)
                sim.access_token = info.get('access_token', '')
                sim.refresh_token = info.get('refresh_token', '')
                sim.refresh_time = timezone.now()

                # unneeded stuff starts here
                sim.client_id = info.get('client_id', '')
                sim.cookie = info.get('Cookie', '')
                sim.otp = info.get('otp', '')
                sim.phone_number = phone_number
                sim.auth0_client = info.get('Auth0-Client', '')
                # sim.data_left = 5000
                sim.sim_number = int(info.get('number', ''))
                logged_in = info.get('logged_in', '')
                if logged_in == "false" and not sim.logged_in:
                    sim.confirmed_logged_in = False
                else:
                    sim.confirmed_logged_in = True

                sim.logged_in = False if logged_in == "false" else True

                if created:
                    sim.expiry_date = timezone.now() + datetime.timedelta(days=80)
                sim.just_refreshed = True if info.get('just_refreshed') == 'true' else False
                sim.save()
            except:
                print('error')



class Sim(models.Model):
    data_left = models.IntegerField(default=5000, blank=True, null=True)
    data_sent = models.IntegerField(default=0, blank=True, null=True)
    is_exhausted = models.BooleanField(default=False, blank=True, null=True)
    prev_day_data_sent = models.IntegerField(default=0, blank=True, null=True)
    registered_by = models.TextField(blank=True, null=True)

    sim_number = models.IntegerField(blank=True, null=True)
    current_balance = models.IntegerField(default=400000)
    logged_in = models.BooleanField(default=True, blank=True, null=True)
    just_refreshed = models.BooleanField(default=False, blank=True, null=True)

    confirmed_logged_in = models.BooleanField(default=True, blank=True, null=True)
    data_left_before_logout = models.IntegerField(default=0, blank=True, null=True)
    restock_time = models.DateTimeField(null=True, blank=True)
    refresh_time = models.DateTimeField(null=True, blank=True)
    priority = models.IntegerField(default=100)

    access_token = models.TextField(blank=True, null=True)
    auth0_client = models.TextField(blank=True, null=True)
    client_id = models.CharField(max_length=255, blank=True, null=True)
    cookie = models.TextField(blank=True, null=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    refresh_token = models.TextField(blank=True, null=True)
    expiry_date = models.DateTimeField(default=datetime.datetime(2023, 12, 31, 23, 59, 59), null=True, blank=True)


    objects = SimManager()
    class Meta:
        ordering = ['-expiry_date']
        indexes = [
            models.Index(fields=['data_left']),
            models.Index(fields=['sim_number']),
            models.Index(fields=['logged_in']),
            models.Index(fields=['priority']),
            models.Index(fields=['expiry_date']),
        ]


    def __str__(self):
        return self.phone_number or "Unknown Sim"

    def restock_empty_sim(self):
        self.data_left = 5000
        self.current_balance = 400000
        self.priority = 100
        self.is_exhausted = False
        self.expiry_date = timezone.now() + datetime.timedelta(days=80)
        self.save()

    def deduct_data(self, data):
        data_left = self.int_data_left()
        data_left -= data
        self.data_left = data_left

        data_sent = self.int_data_sent()
        data_sent += data
        self.data_sent = data_sent

        current_balance = self.int_curent_balance()
        current_balance -= data
        self.current_balance = current_balance
        self.save()

    def restore_balance(self):
        self.data_left = 5000
        self.save()

    def empty_data(self):
        self.data_left = 0
        self.save()

    def int_data_left(self):
        return int(self.data_left)

    def int_data_sent(self):
        return int(self.data_sent)

    def int_curent_balance(self):
        return int(self.current_balance)


# FLUTTERWAVE
class OnlineTransaction(models.Model):
    user_profile = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='online_transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=101)
    status = models.CharField(max_length=10, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user_profile.user.username} - {self.amount} - {self.status}"

    def process(self):
        self.status = 'successful'
        self.save()
        self.user_profile.balance += self.amount
        self.user_profile.save()

class WebhookLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    event_type = models.CharField(max_length=255, blank=True, null=True)
    transaction_reference = models.CharField(max_length=255, blank=True, null=True)
    payload = models.JSONField()
    header = models.TextField(default='header')
    status = models.CharField(max_length=50, default='received')

    def __str__(self):
        return f"Webhook Event {self.event_type} at {self.timestamp}"
