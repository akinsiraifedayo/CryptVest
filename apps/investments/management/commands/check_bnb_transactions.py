import requests
from django.core.management.base import BaseCommand
from apps.sales.models import UserProfile, OnlineTransaction
from apps.investments.models import Wallet

class Command(BaseCommand):
    help = 'Check BNB transactions for wallet addresses and create transactions'

    BLOCK_STEP = 10  # Number of blocks to query per request
    RPC_URL = 'https://rpc.ankr.com/bsc'

    def handle(self, *args, **kwargs):
        wallet_addresses = ['0x4e5acf9684652BEa56F2f01b7101a225Ee33d23f', '0x1120a5fbF507D77448568c5077Bd7668993cF672', '0x506cBEAC1068Fa4E1D502459E40817b99762304e']
        for wallet_address in wallet_addresses:
            self.check_wallet(wallet_address)

    def check_wallet(self, wallet_address):
        latest_block = self.get_latest_block()
        print(latest_block)
        start_block = 42003100
        
        while start_block <= latest_block:
            end_block = min(start_block + self.BLOCK_STEP - 1, latest_block)
            self.fetch_and_process_transactions(wallet_address, start_block, end_block)
            start_block += self.BLOCK_STEP

    def get_latest_block(self):
        try:
            response = requests.post(self.RPC_URL, json={"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1})
            data = response.json()
            print(data)
            if 'result' in data:
                return int(data['result'], 16)  # Convert hex to int
            else:
                self.stdout.write(self.style.ERROR(f"Error fetching latest block number: {data.get('error')}"))
                return 0
        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f"An error occurred while fetching the latest block: {e}"))
            return 0

    def fetch_and_process_transactions(self, wallet_address, start_block, end_block):
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_getLogs",
            "params": [{
                "fromBlock": hex(start_block),
                "toBlock": hex(end_block),
                "address": wallet_address
            }],
            "id": 1
        }

        try:
            response = requests.post(self.RPC_URL, json=payload)
            data = response.json()

            if 'result' in data:
                transactions = data['result']
                for transaction in transactions:
                    self.process_transaction(transaction, wallet_address)
            else:
                self.stdout.write(self.style.ERROR(f"Error fetching logs: {data.get('error')}"))

        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f"An error occurred while fetching transactions: {e}"))

    def process_transaction(self, transaction, wallet_address):
        tx_hash = transaction['transactionHash']
        value = int(transaction['value'], 16) / (10**18)  # Convert Wei to BNB
        to_address = transaction['to']
        from_address = transaction['from']
        
        wallet = Wallet.objects.filter(eth_address=wallet_address).first()
        if wallet:
            user_profile = wallet.user_profile
            # Check if this transaction is already recorded
            if not OnlineTransaction.objects.filter(reference=tx_hash).exists():
                OnlineTransaction.objects.create(
                    user_profile=user_profile,
                    amount=value,
                    reference=tx_hash,
                    status='pending'
                )
                self.stdout.write(self.style.SUCCESS(f"Created transaction record for {wallet_address}: {tx_hash}"))
            else:
                self.stdout.write(self.style.INFO(f"Transaction {tx_hash} already exists."))
        else:
            self.stdout.write(self.style.ERROR(f"Wallet {wallet_address} not found."))
