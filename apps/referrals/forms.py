from django import forms

class ReferralWithdrawalForm(forms.Form):
    PAYMENT_OPTION_CHOICES = [
        ('databalance', 'Add to Investment Balance'),
        # ('banktransfer', 'Bank Transfer'),
        # ('card', 'Card'),
        # ('paypal', 'PayPal'),
        # ('crypto', 'Cryptocurrency'),
    ]

    CRYPTO_CHOICES = [
        ('bitcoin', 'Bitcoin'),
        ('usdt', 'USDT (BEP 20)'),
        ('bnb', 'BNB Smart Chain'),
    ]

    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0.00,
        max_value=500000.00,
        label='Withdrawal Amount',
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
            'onchange': 'showPaymentDetails(this.value);'
        })
    )

    bank_account_details = forms.CharField(
        label='Bank Account Details (Name, Bank and Account Number)',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter bank account details (name, bank and account number)',
            'rows': 4
        })
    )

    card_details = forms.CharField(
        label='Card Details',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter card details',
            'rows': 4
        })
    )

    paypal_email = forms.EmailField(
        label='PayPal Email',
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter PayPal email'
        })
    )

    crypto_option = forms.ChoiceField(
        label='Cryptocurrency',
        choices=CRYPTO_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    crypto_address = forms.CharField(
        label='Cryptocurrency Wallet Address',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter crypto wallet address'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        payment_option = cleaned_data.get('payment_option')

        if payment_option == 'banktransfer' and not cleaned_data.get('bank_account_details'):
            self.add_error('bank_account_details', 'Bank account details are required for bank transfer.')

        if payment_option == 'card' and not cleaned_data.get('card_details'):
            self.add_error('card_details', 'Card details are required for card payment.')

        if payment_option == 'paypal' and not cleaned_data.get('paypal_email'):
            self.add_error('paypal_email', 'PayPal email is required for PayPal payment.')

        if payment_option == 'crypto':
            if not cleaned_data.get('crypto_option'):
                self.add_error('crypto_option', 'Cryptocurrency type is required for crypto payment.')
            if not cleaned_data.get('crypto_address'):
                self.add_error('crypto_address', 'Cryptocurrency wallet address is required for crypto payment.')

        return cleaned_data
