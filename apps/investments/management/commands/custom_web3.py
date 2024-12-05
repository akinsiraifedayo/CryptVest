from web3 import Web3

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
address = Web3.to_checksum_address('0x91622Dbf9488b68D70e5dE6E6e0aA2A16fBddD4B')

# Get the balance (returned in the smallest unit, so divide by 10^18 to get actual USDT balance)
balance = usdt_contract.functions.balanceOf(address).call()
usdt_balance = balance / (10 ** 18)

print(f"USDT Balance: {usdt_balance}")
