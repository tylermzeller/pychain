import pychain.base58 as base58
import pychain.pow as pow
import pychain.transaction as transaction
import pychain.wallet as wallet
import pychain.network as network
import pychain.util as util

from pychain.blockchain import Blockchain
from pychain.block_explorer import BlockExplorer
from pychain.miner import Miner
from pychain.utxo_set import UTXOSet
from pychain.wallet_manager import WalletManager

import argparse
import json
import random

def createWallet():
    wm = WalletManager()
    w = wm.create_wallet()
    newAddress = util.toStr(w.get_address())
    print("New address: %s" % newAddress)
    return newAddress

def listAddresses():
    wm = WalletManager()
    addresses = wm.get_addresses()
    if not addresses:
        print("Error: Could not get wallets")
        return

    for address in addresses:
        print(util.toStr(address))

def printChain(full=False):
    for i, block in enumerate(BlockExplorer().iter_blocks()):
        proof = pow.ProofOfWork(block)
        if not proof.validate():
            print("Error! This block could not be validated")
        if full:
            print(json.dumps(block.toDict(), indent=2))
        else:
            print(block.hash.hex())

def newBlockchain(address):
    if Blockchain().getBestHeight >= 0:
        print("Error: Blockchain already exists")
        return

    if not wallet.validateAddress(address.encode()):
        print("Error: Address is not valid")
        return

    miner = Miner(address.encode())
    miner.mine_block()
    print("New blockchain created")

def getBalance(address):
    if not wallet.validateAddress(address.encode()):
        print("Error: Can't get balance of invalid address.")
        return None

    us = UTXOSet()
    return us.get_balance(address=address.encode())

def printBalance(address):
    balance = getBalance(address)
    if balance:
        print("Balance of '%s': %d" % (address, balance))

def send(frum, to, amount):
    if not wallet.validateAddress(frum.encode()):
        print("Error: Sender address is not valid")
        return

    if not wallet.validateAddress(to.encode()):
        print("Error: Recipient address is not valid")
        return

    w = WalletManager().get_wallet(frum.encode())
    tx = w.create_tx(to.encode(), amount, UTXOSet())
    if tx:
        miner = Miner(frum.encode())
        coinbase = miner.new_coinbase_tx()
        miner.mine_block([coinbase, tx])
        print("Send success!")

def startServer(minerAddress):
    if minerAddress is None:
        minerAddress = createWallet()
    if len(minerAddress) > 0 and wallet.validateAddress(minerAddress.encode()):
        #print("This node is mining and will receive rewards to %s" % minerAddress)
        pass
    else:
        print("No or incorrect mining address. This node is not mining and will not receive rewards.")

    network.startServer(minerAddress.encode())

def run():
    parser = argparse.ArgumentParser(description='Process blockchain commands')
    parser.add_argument('command', help='a command to perform on the blockchain')
    parser.add_argument('--address', dest='address')
    parser.add_argument('--from', dest='frum')
    parser.add_argument('--to', dest='to')
    parser.add_argument('--amount', dest='amount', type=int)
    parser.add_argument('--full', dest='full')
    args = parser.parse_args()

    command = args.command.lower()

    if util.isSubstringOf(command, 'print-blockchain'):
        full = False
        if not args.getattr('full'):
            args.setattr('full', 'false')
        full = args.full.lower() in ['y', 'true', 't', '1']
        printChain(full)
    elif util.isSubstringOf(command, 'init-blockchain'):
        newBlockchain(args.address)
    elif util.isSubstringOf(command, 'get-balance'):
        printBalance(args.address)
    elif util.isSubstringOf(command, 'send'):
        send(args.frum, args.to, args.amount)
    elif util.isSubstringOf(command, 'create-wallet'):
        createWallet()
    elif util.isSubstringOf(command, 'list-addresses'):
        listAddresses()
    elif util.isSubstringOf(command, 'up'):
        startServer(args.address)
    else:
        print("No such command.")
