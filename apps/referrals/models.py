from django.utils import timezone
from django.db import models
from apps.sales.models import UserProfile
# Create your models here.

PAYMENT_OPTION_CHOICES = [
        ('databalance', 'Add to Investment Balance'),
        ('banktransfer', 'Bank Transfer'),
        ('card', 'Card'),
        ('paypal', 'PayPal'),
        ('crypto', 'Cryptocurrency'),
    ]

PAYMENT_OPTION_CHOICES_DICT = dict([
    ('databalance', 'Added to Investment Balance'),
    ('banktransfer', 'Bank Transfer'),
    ('card', 'Card'),
    ('paypal', 'PayPal'),
    ('crypto', 'Cryptocurrency'),
])

STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('completed', 'Completed'),
    ('failed', 'Failed'),
]

class ReferralWithdrawal(models.Model):

    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='referral_withdrawals')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_option = models.CharField(max_length=20, choices=PAYMENT_OPTION_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    request_time = models.DateTimeField(default=timezone.now)
    processed_time = models.DateTimeField(null=True, blank=True)

    # Bank Transfer Details
    bank_account_details = models.TextField(max_length=255, blank=True, null=True)

    # Card Details
    card_details = models.TextField(max_length=255, blank=True, null=True)

    # PayPal Details
    paypal_email = models.EmailField(blank=True, null=True)

    # Cryptocurrency Details
    crypto_option = models.CharField(max_length=50, blank=True, null=True)
    crypto_address = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['-request_time']

    def __str__(self):
        return f"Withdrawal {self.id} - {self.user_profile.user.username} - {self.amount}"

    # def save(self, *args, **kwargs):
    #     # Add any custom save logic here
    #     super().save(*args, **kwargs)

    def get_payment_details(self):
        payment_details = self.bank_account_details or self.card_details or self.paypal_email or self.crypto_address
        return payment_details

    def get_payment_option(self):
        payment_key = (
            self.bank_account_details and 'banktransfer' or
            self.card_details and 'card' or
            self.paypal_email and 'paypal' or
            self.crypto_address and 'crypto' or
            'Added to Data Balance' and 'databalance'
        )
        payment_details = PAYMENT_OPTION_CHOICES_DICT.get(payment_key, 'No payment details available')
        return payment_details
