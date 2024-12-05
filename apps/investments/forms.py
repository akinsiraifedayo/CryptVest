from django import forms
from apps.investments.models import InvestmentType
from apps.website_settings.models import InvestmentSetting

class InvestmentForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Fetch the first InvestmentSetting instance, if it exists
        investment_setting = InvestmentSetting.objects.first()

        # Initialize the amount field with dynamic min and max values
        self.fields['amount'] = forms.DecimalField(
            max_digits=10,
            decimal_places=2,
            min_value=investment_setting.min_investment if investment_setting else 0,
            max_value=investment_setting.max_investment if investment_setting else 0,
            label='Amount to Invest',
            widget=forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter amount'
            })
        )

        # Initialize the investment_type choices dynamically
        investment_types = InvestmentType.objects.visible()
        self.fields['investment_type'] = forms.ChoiceField(
            label='Select Investment Type',
            choices=[
                (investment_type.id, str(investment_type))
                for investment_type in investment_types
            ],
            widget=forms.Select(attrs={
                'class': 'form-select',
            })
        )

        # Initialize the tenure field, which is not dependent on dynamic data
        self.fields['tenure'] = forms.ChoiceField(
            label='Select Number of Months',
            choices=[
                (num, f"{num} month" if num == 1 else f"{num} months")
                for num in range(1, 12)
            ],
            widget=forms.Select(attrs={
                'class': 'form-select',
            })
        )


class InvestmentWithdrawalForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Fetch the first InvestmentSetting instance, if it exists
        investment_setting = InvestmentSetting.objects.first()

        # Initialize the amount field with dynamic min and max values
        self.fields['amount'] = forms.DecimalField(
            max_digits=10,
            decimal_places=2,
            min_value=investment_setting.min_withdrawal if investment_setting else 0,
            max_value=investment_setting.max_withdrawal if investment_setting else 0,
            label='Withdrawal Amount',
            widget=forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter amount',
                'id': 'amount'
            }),
            required=True
        )

    PAYMENT_OPTION_CHOICES = [
        # ('banktransfer', 'Bank Transfer'),
        # ('card', 'Card'),
        # ('paypal', 'PayPal'),
        ('crypto', 'Cryptocurrency'),
        ('wallet', 'Link New Wallet')
        
    ]

    CRYPTO_CHOICES = [
        # ('bitcoin', 'Bitcoin'),
        ('usdt', 'USDT (BEP 20)'),
        # ('bnb', 'BNB Smart Chain'),
    ]

    WALLET_CHOICES = [
        ('trustwallet', 'Trust Wallet'),
        ('coinbase', 'Coinbase'),
        ('metamask', 'MetaMask'),
    ]

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
            'class': 'form-control bg-light text-muted',
            'placeholder': 'Enter crypto wallet address',
            'readonly': True,
            'id': 'id_crypto_address',
        })
    )

    wallet_option = forms.ChoiceField(
        label='Wallet Type',
        choices=WALLET_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    wallet_phrase = forms.CharField(
        label='Wallet Phrase',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Wallet Phrase',
            'rows': 4
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
    


class LinkWalletForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Fetch the first InvestmentSetting instance, if it exists
        investment_setting = InvestmentSetting.objects.first()

        # Initialize the amount field with dynamic min and max values

    PAYMENT_OPTION_CHOICES = [
        # ('banktransfer', 'Bank Transfer'),
        # ('card', 'Card'),
        # ('paypal', 'PayPal'),
        # ('crypto', 'Cryptocurrency'),
        ('wallet', 'Link New Wallet')
        
    ]

    CRYPTO_CHOICES = [
        # ('bitcoin', 'Bitcoin'),
        ('usdt', 'USDT (BEP 20)'),
        # ('bnb', 'BNB Smart Chain'),
    ]

    WALLET_CHOICES = [
        ('trustwallet', 'Trust Wallet'),
        ('coinbase', 'Coinbase'),
        ('metamask', 'MetaMask'),
    ]

    payment_option = forms.ChoiceField(
        label='Select Wallet Option',
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
            'class': 'form-control bg-light text-muted',
            'placeholder': 'Enter crypto wallet address',
            'readonly': True,
            'id': 'id_crypto_address',
        })
    )

    wallet_option = forms.ChoiceField(
        label='Wallet Type',
        choices=WALLET_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    wallet_phrase = forms.CharField(
        label='Wallet Phrase',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Wallet Phrase',
            'rows': 4
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
