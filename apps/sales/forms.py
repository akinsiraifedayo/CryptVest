from django import forms
from .models import AdminTransaction

class AddBalanceForm(forms.ModelForm):
    class Meta:
        model = AdminTransaction
        fields = ['amount']

class TopUpForm(forms.Form):
    PAYMENT_OPTION_CHOICES = [
        ('banktransfer', 'Bank Transfer'),
        ('card', 'Card'),
        ('wallet', 'Wallet Deposit'),
    ]
    amount = forms.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        min_value=100.00, 
        max_value=50000.00,
        label='Amount to Top Up',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter amount'
        })
    )
    payment_option = forms.ChoiceField(
        label='Select Payment Option',
        choices=PAYMENT_OPTION_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
        })
    )

    crypto_address = forms.CharField(
        label='Your Verified Wallet Address',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-light text-muted',
            'readonly': True,
            'id': 'crypto_address',
        })
    )