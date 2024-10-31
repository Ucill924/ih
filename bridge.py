import json
import random
import time
from web3 import Web3
from eth_account.signers.local import LocalAccount
from colorama import init, Fore

init(autoreset=True)

with open('config_rpc.json') as config_file:
    config = json.load(config_file)
    rpc_url = config["rpc_url"]
    max_fee_per_gas = config["maxFeePerGas"]
    max_priority_fee_per_gas = config["maxPriorityFeePerGas"]
    chain_id = config["chainId"]
    gas_limit = config["gasLimit"]

w3 = Web3(Web3.HTTPProvider(rpc_url))
a = '0x35A54c8C757806eB6820629bc82d90E056394C92'

with open('pk.txt') as pk_file:
    private_keys = [line.strip() for line in pk_file if line.strip()]

num_transactions = int(input(Fore.GREEN + "Masukkan jumlah transaksi: "))
eth_input = float(input(Fore.GREEN + "Masukkan jumlah ETH yang akan di-bridge (misal: 0.001): "))
mint_value = int(eth_input * 10**18)

for tx_number in range(1, num_transactions + 1):
    for private_key in private_keys:
        account: LocalAccount = w3.eth.account.from_key(private_key)
        print(Fore.BLUE + f'Derived account address: {account.address}')

        with open('contract_abi.json') as abi_file:
            abi = json.load(abi_file)

        contract = w3.eth.contract(address=a, abi=abi)
        nonce = w3.eth.get_transaction_count(account.address)
        print(Fore.YELLOW + f'Nonce for {account.address}: {nonce}')

        transaction_data = contract.functions.requestL2TransactionDirect({
            'chainId': 11124,
            'mintValue': mint_value,
            'l2Contract': Web3.to_checksum_address(account.address),
            'l2Value': 100000000000000,
            'l2Calldata': b'',
            'l2GasLimit': 384513,
            'l2GasPerPubdataByteLimit': 800,
            'factoryDeps': [],
            'refundRecipient': Web3.to_checksum_address(account.address)
        }).build_transaction({
            'from': account.address,
            'gas': gas_limit,
            'nonce': nonce,
        })

        expected_value_in_wei = mint_value
        transaction = {
            'from': account.address,
            'to': a,
            'gas': gas_limit,
            'value': expected_value_in_wei,
            'nonce': nonce,
            'data': transaction_data['data'],
            'maxFeePerGas': w3.to_wei(max_fee_per_gas, 'gwei'),
            'maxPriorityFeePerGas': w3.to_wei(max_priority_fee_per_gas, 'gwei'),
            'chainId': chain_id
        }

        signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
        try:
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            print(Fore.CYAN + f'Transaction {tx_number}: Hash: {tx_hash.hex()}')
        except Exception as e:
            print(Fore.RED + f'Error sending transaction {tx_number}: {e}')

        delay = random.randint(50, 100)
        print(Fore.YELLOW + f'Waiting for {delay} seconds before the next transaction...')
        time.sleep(delay)
