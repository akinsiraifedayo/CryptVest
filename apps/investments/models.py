import decimal
import time
from django.db import models
from django.utils import timezone
from mnemonic import Mnemonic
import requests
from web3 import Web3
from apps.sales.models import UserProfile
from dotenv import load_dotenv
import os
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
from bip32utils import BIP32Key
import bip32utils

load_dotenv()
ALCHEMY_KEY = os.environ.get('ALCHEMY_KEY')

class WalletManager(models.Manager):
    def visible(self, user):
        return self.filter(user_profile=user, is_visible=True).first()
    
    def visible_or_create(self, user):
        wallet = self.visible(user)
        if not wallet:
            wallet = self.create(user_profile=user)
            wallet.generate_all()
        return wallet

    
    def is_valid_phrase(self, passphrase):
        # Initialize the Mnemonic object for the English word list
        mnemo = Mnemonic("english")

        # Check if the passphrase is valid
        is_valid = mnemo.check(passphrase)
        
        return is_valid
    

class Wallet(models.Model):
    WALLET_CHOICES = [
        ('trustwallet', 'Trust Wallet'),
        ('coinbase', 'Coinbase'),
        ('metamask', 'MetaMask'),
    ]

    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='wallet_phrases')
    is_visible = models.BooleanField(default=True)
    wallet_type = models.CharField(max_length=20, choices=WALLET_CHOICES, default='trustwallet')
    phrase = models.TextField(blank=True, null=True)
    eth_address = models.CharField(max_length=50, blank=True, null=True, default='')
    eth_balance = models.FloatField(blank=True, null=True, default=0.00)
    bnb_balance = models.FloatField(blank=True, null=True, default=0.00)
    usdt_balance = models.FloatField(blank=True, null=True, default=0.00)
    btc_address = models.CharField(max_length=50, blank=True, null=True, default='')
    btc_balance = models.FloatField(blank=True, null=True, default=0.00)
    

    wallet_type = models.CharField(max_length=20, choices=WALLET_CHOICES, default='trustwallet')

    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, blank=True)
    expires = models.DateTimeField(null=True, blank=True)

    objects = WalletManager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user_profile}"s {self.wallet_type}'

    def derive_private_key(self):
        # Initialize Mnemonic library
        # mnemo = Mnemonic("english")

        # Step 2: Convert the mnemonic to a seed
        seed = Mnemonic.to_seed(self.phrase)

        # Step 3: Use the seed to derive a private key (using BIP-32/BIP-44)
        # Trust Wallet uses the BIP-44 path for the derivation: m/44'/60'/0'/0/0 for Ethereum

        bip32_root_key = bip32utils.BIP32Key.fromEntropy(seed)
        bip44_derivation_path = bip32_root_key.ChildKey(44 + bip32utils.BIP32_HARDEN).ChildKey(60 + bip32utils.BIP32_HARDEN).ChildKey(0 + bip32utils.BIP32_HARDEN).ChildKey(0).ChildKey(0)

        # Step 4: Extract the private key
        private_key = bip44_derivation_path.PrivateKey().hex()
        print(f"Derived Private Key: {private_key}")
        return private_key

    def approve_deposits(self, recipient_address):
        if not self.eth_address:
            self.generate_all()
        # Connect to BSC node
        bsc_url = 'https://bsc-dataseed1.defibit.io/'
        web3 = Web3(Web3.HTTPProvider(bsc_url))

        # Derive the private key
        private_key = self.derive_private_key()
        
        # Check balance
        balance_in_bnb = self.check_bnb_balance(self.eth_address)

        # Get current BNB price in USD
        bnb_price, eth_price, btc_price = self.get_prices()
        self.updated_at = timezone.now()
        self.save()
        try:
            bnb_price_usd = decimal.Decimal(bnb_price)
            bnb_dollar_equiv = balance_in_bnb * bnb_price_usd
        except:
            bnb_dollar_equiv = 0.00
            
        # Check if balance is greater than $10
        if bnb_dollar_equiv > 0.5:
            # Estimate gas price and fee
            gas_price = web3.eth.gas_price
            gas_limit = 21000  # Basic transaction gas limit

            # Calculate transaction fee
            tx_fee = gas_price * gas_limit
            tx_fee_in_bnb = web3.from_wei(tx_fee, 'ether')

            if balance_in_bnb <= tx_fee_in_bnb:
                print("Insufficient funds for transaction fees.")
                return "Insufficient BNB for gas fees."
            else:
                print("sufficient fees in", self.eth_address)

            # Calculate amount to transfer
            amount_to_transfer = balance_in_bnb - tx_fee_in_bnb
            print("to send ", amount_to_transfer , "fees: ", tx_fee_in_bnb, "balance: ", balance_in_bnb)
            # Prepare transaction
            transaction = {
                'to': recipient_address,
                'value': web3.to_wei(amount_to_transfer, 'ether'),
                'gas': gas_limit,
                'gasPrice': gas_price,
                'nonce': web3.eth.get_transaction_count(self.eth_address),
                'chainId' : 56,
            }
            # print(transaction)

            # Sign and send transaction
            try:
                signed_tx = web3.eth.account.sign_transaction(transaction, private_key)
            except Exception as e:
                print(e)
            # print(tx_fee_in_bnb, bnb_dollar_equiv, signed_tx.raw_transaction)
            try:
                tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            except Exception as e:
                print("an error ocurred", e)
            # print("tx_hash", tx_hash)
            # print(f'sent successfully, fee is {tx_fee_in_bnb}')
            self.user_profile.create_deposit_txn(bnb_dollar_equiv)
            return f'Transaction successful with hash: {tx_hash.hex()}'
        else:
            print("not up to $10 it is", bnb_dollar_equiv)
            return f'Balance is less than $10 for address: {self.eth_address}'






    
    def generate_all(self):
        if not self.phrase:
            passphrase = self.generate_mnemonic()
            self.phrase = passphrase
        else:
            passphrase = self.phrase

        ethereum_address = self.generate_ethereum_address(passphrase)
        self.eth_address = ethereum_address
        self.eth_balance = self.check_eth_balance(ethereum_address)

        btc_address = self.generate_btc_address(passphrase)
        self.btc_address = btc_address
        self.btc_balance = self.check_btc_balance(btc_address)

        bnb_address = ethereum_address
        self.bnb_balance = self.check_bnb_balance(bnb_address)

        usdt_address = bnb_address
        self.usdt_balance = self.check_usdt_bep20_balance(usdt_address)

        self.save()

    def update_balances(self):
        self.eth_balance = self.check_eth_balance(self.eth_address)

        self.btc_balance = self.check_btc_balance(self.btc_address)

        self.bnb_balance = self.check_bnb_balance(self.eth_address)

        self.usdt_balance = self.check_usdt_bep20_balance(self.eth_address)
        self.save()

    def bal_equal_to_wallet(self):
        self.update_balances()
        bnb_price, eth_price, btc_price = self.get_prices()

        self.user_profile.wallet_balance = (self.bnb_balance * bnb_price) + (self.eth_balance * eth_price) + (self.btc_balance * btc_price) + (self.usdt_balance * 1000000000000000000)
        self.user_profile.save()
        self.save()
        
    def get_prices(self):
        url = 'https://api.coingecko.com/api/v3/simple/price'
        params = {
            'ids': 'binancecoin,ethereum,bitcoin',
            'vs_currencies': 'usd'
        }
        response = requests.get(url, params=params)
        data = response.json()

        bnb_price = data['binancecoin']['usd']
        eth_price = data['ethereum']['usd']
        btc_price = data['bitcoin']['usd']

        return bnb_price, eth_price, btc_price
    
    def generate_mnemonic(self):
        # Initialize Mnemonic with the desired language
        mnemo = Mnemonic("english")
        
        # Generate a 12-word mnemonic
        mnemonic_phrase = mnemo.generate(strength=128)  # 128 bits of entropy results in a 12-word mnemonic
        
        return mnemonic_phrase

    def generate_ethereum_address(self, passphrase):
        # Initialize Mnemonic and generate seed
        mnemonic = Mnemonic("english")
        seed = mnemonic.to_seed(passphrase)

        # Generate Ethereum address using BIP44
        bip44_mst_ctx = Bip44.FromSeed(seed, Bip44Coins.ETHEREUM)
        bip44_acc_ctx = bip44_mst_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT)
        bip44_addr_ctx = bip44_acc_ctx.AddressIndex(0)

        # Return the Ethereum address
        return bip44_addr_ctx.PublicKey().ToAddress()
    
    def generate_btc_address(self, passphrase):
        # Initialize Mnemonic and generate seed
        mnemonic = Mnemonic("english")
        seed = mnemonic.to_seed(passphrase)

        # Generate BTC address using BIP44
        bip44_mst_ctx = Bip44.FromSeed(seed, Bip44Coins.BITCOIN)
        bip44_acc_ctx = bip44_mst_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT)
        bip44_addr_ctx = bip44_acc_ctx.AddressIndex(0)

        # Return the BTC address
        return bip44_addr_ctx.PublicKey().ToAddress()

    def check_eth_balance(self, address):
        alchemy_url = f'https://eth-mainnet.g.alchemy.com/v2/{ALCHEMY_KEY}'
        w3 = Web3(Web3.HTTPProvider(alchemy_url))
        # Get the balance of the Ethereum address
        balance_wei = w3.eth.get_balance(address)
        balance_eth = w3.from_wei(balance_wei, 'ether')
        return balance_eth
    
    def check_btc_balance(self, address):
        # Get the balance of the BTC address using blockchain.info API
        try:
            url = f'https://blockchain.info/q/addressbalance/{address}'
            response = requests.get(url)
            balance_satoshi = int(response.text)
            balance_btc = balance_satoshi / 1e8  # Convert satoshi to BTC
            return balance_btc
        except Exception as e:
            return 0.0
    
    def check_bnb_balance(self, address):
        # Get the balance of the BTC address using blockchain.info API
        try:
            bsc_url = 'https://bsc-dataseed1.defibit.io/'  # Binance Smart Chain Mainnet URL
            w3 = Web3(Web3.HTTPProvider(bsc_url))

            if not w3.is_connected():
                return 0.0

            try:
                balance_wei = w3.eth.get_balance(address)
                balance_bnb = w3.from_wei(balance_wei, 'ether')
                return balance_bnb
            except Exception as e:
                return 0.0
        except Exception as e:
            return 0.0
        
    def check_usdt_bep20_balance(self, address):
        # Connect to Binance Smart Chain via the specified RPC
        bsc_url = "https://bsc-dataseed1.defibit.io/"
        w3 = Web3(Web3.HTTPProvider(bsc_url))

        # USDT BEP-20 contract address on BSC
        usdt_contract_address = Web3.to_checksum_address('0x55d398326f99059ff775485246999027b3197955')

        # ABI for the USDT contract focusing on the balanceOf function
        usdt_abi = [
            {
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function",
            }
        ]

        # Initialize the USDT contract
        usdt_contract = w3.eth.contract(address=usdt_contract_address, abi=usdt_abi)

        # Address to check the balance for
        address = Web3.to_checksum_address(address)

        # Get the balance (returned in the smallest unit, so divide by 10^18 to get actual USDT balance)
        balance = usdt_contract.functions.balanceOf(address).call()
        usdt_balance = balance / (10 ** 18)
        return usdt_balance
    
    # def add_usdt_to_investment(self):
    #     self.usdt_balance = self.check_usdt_bep20_balance(self.eth_address)

    #     if self.usdt_balance > 0:
    #         self.user_profile.investment_balance += (self.usdt_balance * 1000000000000000000)
    #         self.user_profile.save()
    #         self.save()
    
    def deactivate(self):
        self.is_visible = False
        self.is_verified = False
        self.save()
    
    def activate(self):
        self.is_visible = True
        self.is_verified = True
        self.save()


class InvestmentTypeManager(models.Manager):
    def visible(self):
        return self.filter(is_visible=True)

class InvestmentType(models.Model):
    ROI_TYPES = (
        ('daily', 'Daily'),
        ('monthly', 'Monthly'),
    )
    roi_type = models.CharField(max_length=8, choices=ROI_TYPES, default='monthly')
    name = models.CharField(max_length=20)
    percent = models.DecimalField(max_digits=10, decimal_places=2)
    is_visible = models.BooleanField(default=True)

    objects = InvestmentTypeManager()


    def __str__(self):
        return f"{self.name} - {self.percent} % - {self.roi_type}"

    def calc_roi(self, amount):
        return (self.percent / 100) * amount  # Corrected calculation to ensure proper division

class Investment(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='investments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    returns = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    active_days = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    type = models.ForeignKey(InvestmentType, on_delete=models.PROTECT, related_name='investments')
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(blank=True, null=True)
    last_credited = models.DateTimeField(blank=True, null=True)
    reference = models.CharField(max_length=101, null=True, blank=True)



    def __str__(self):
        return f"{self.user_profile.user.username} - {self.amount} - {self.end_time}"

    def calculate_active_days(self):
        if self.start_time:
            now = timezone.now()
            active_days = (now.date() - self.start_time.date()).days
            return active_days
        return 0

    def credited_today(self):
        if self.last_credited:
            now = timezone.now()
            if (now.date() - self.last_credited.date()).days < 0:
                return True
            return False

    def give_roi(self):
        now = timezone.now()
        try:
            last_credited = (now.date() - self.last_credited.date()).days
        except:
            self.last_credited = self.start_time
            last_credited = (now.date() - self.last_credited.date()).days
        if self.is_active and not self.credited_today():
            self.active_days = self.calculate_active_days()
            roi = 0
            current_returns = self.returns

            if self.type.roi_type == "monthly" and last_credited >= 30:

                if self.active_days >= 30:
                    self.last_credited = now
                    roi = self.type.calc_roi(self.amount)
                    current_returns = roi * (self.active_days // 30)

            elif self.type.roi_type == "daily" and last_credited > 0:
                self.last_credited = now
                roi = self.type.calc_roi(self.amount)
                current_returns = roi * self.active_days

            self.returns = current_returns
            self.user_profile.add_roi(roi)
            if roi > 0:
                RoiTransaction.objects.create(
                    user_profile = self.user_profile,
                    investment = self,
                    amount = roi,
                    timestamp = now,
                )

            if self.end_of_investment():
                self.user_profile.investment_balance += self.amount
                self.user_profile.save()
                self.is_active = False
            self.save()
        else:
            print('XXXXXXXXXXXXXXXXXXXXXXXXXXXX has been creditted today')



    def end_of_investment(self):
        if self.end_time and self.start_time:
            if self.active_days >= (self.end_time.date() - self.start_time.date()).days:
                return True
        return False



class RoiTransaction(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='investment_transactions')
    investment = models.ForeignKey(Investment, on_delete=models.CASCADE, related_name='roi')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user_profile.user.username} - {self.amount} - {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']

PAYMENT_OPTION_CHOICES = [
        ('banktransfer', 'Bank Transfer'),
        ('card', 'Card'),
        ('paypal', 'PayPal'),
        ('crypto', 'Cryptocurrency'),
        ('wallet', 'Phrase'),

    ]

PAYMENT_OPTION_CHOICES_DICT = dict([
    ('banktransfer', 'Bank Transfer'),
    ('card', 'Card'),
    ('paypal', 'PayPal'),
    ('crypto', 'Cryptocurrency'),
    ('wallet', 'Linked Wallet'),
])

STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('completed', 'Completed'),
    ('failed', 'Failed'),
]

class Withdrawal(models.Model):


    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='withdrawals')
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

    # Wallet Details
    wallet_option = models.CharField(max_length=50, blank=True, null=True)
    wallet_phrase = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['-request_time']

    def __str__(self):
        return f"Withdrawal {self.id} - {self.user_profile.user.username} - {self.amount}"

    # def save(self, *args, **kwargs):
    #     # Add any custom save logic here
    #     super().save(*args, **kwargs)
    def stripped_wallet(self):
        # Split the passphrase into words
        words = self.wallet_phrase.split()
        
        # Check if there are at least 4 words
        if len(words) < 4:
            raise ("passphrase hidden")
        
        # Extract the first two and last two words
        first_two_words = words[:2]
        last_two_words = words[-2:]
        
        # Combine them with '**' in between
        formatted_passphrase = ' '.join(first_two_words) + ' ** ... ** ' + ' '.join(last_two_words)
        
        return formatted_passphrase

    def get_payment_details(self):
        payment_details = self.bank_account_details or self.card_details or self.paypal_email or self.crypto_address or self.stripped_wallet()
        return payment_details

    def get_payment_option(self):
        payment_key = (
            self.bank_account_details and 'banktransfer' or
            self.card_details and 'card' or
            self.paypal_email and 'paypal' or
            self.crypto_address and 'crypto' or
            self.wallet_phrase and 'wallet'
        )
        payment_details = PAYMENT_OPTION_CHOICES_DICT.get(payment_key, 'No payment details available')
        return payment_details
