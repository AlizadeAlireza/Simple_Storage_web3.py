from solcx import compile_standard, install_solc
import json
from web3 import Web3, HTTPProvider
import os
from dotenv import load_dotenv

load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()
    # print(simple_storage_file)

# compile our solidity

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.6.0",
)

with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)


# get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]


# get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# for connecting to Kovan

w3 = Web3(
    Web3.HTTPProvider("https://kovan.infura.io/v3/cddf1174c93747a79f6b0979bd20eea6")
)
chain_id = 42
my_address = "0x82ffc7cF103cccF50571bD671C7D1EA73EC388D5"
# private keys MUST start with 0x
private_key = os.getenv("PRIVATE_KEY")


# Create the contract in python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
# Get the latests transaction
nonce = w3.eth.getTransactionCount(my_address)
# print(nonce)

# 1. Build a transaction
# 2. Sign a transaction
# 3. Send a transaction
# 4. We waited for the transaction to finish
transaction = SimpleStorage.constructor().buildTransaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce,
    }
)
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
# send this signed transaction
print("Deploying Contract...")
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Deployed!")
# working with the contract
# Contract Address
# Contract ABI
# update with address feature instead tx_receipt.contractAddress
simple_storage = w3.eth.contract(address="address", abi=abi)
# Call -> Simulate making the call and getting a return value
# Call -> don't make a state change to the blockchian
# Call -> like in remix we call blue buttons and nothing on blockchain actually change
# transact -> orange button in remix
# transact -> Actually make a state change and build a transaction
# transact -> and send a transaction

# Initial value of favorite number
print(simple_storage.functions.retrieve().call())
print("Updating Contract...")
# print(simple_storage.functions.store(15).call())

# 1.
store_transaction = simple_storage.functions.store(15).buildTransaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce + 1,
        # we're going to need to do nonce + 1 because
        # we actually use nonce already
        # a nonce can be use in one transaction
        # must have a different nonce than the nonce we use to deploy contract
    }
)
# 2.
# sign the Transaction
signed_store_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)
# 3.
# now we need to send it
send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
# 4.
# let's grab the transaction receipt and wait to transaction
# to finish
tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)
print("Updated!")

print(simple_storage.functions.retrieve().call())
