import pychain.base58 as base58
import pychain.pow as pow
import pychain.transaction as transaction
import pychain.wallet as wallet
import pychain.network as network
import pychain.util as util

from pychain.blockchain import Blockchain
from pychain.utxo_set import UTXOSet
from pychain.wallet_manager import WalletManager

import argparse
import json
import random

def createWallet():
    wm = WalletManager()
    w = wm.create_wallet()
    newAddress = util.toStr(w.getAddress())
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

def printChain():
    for i, block in enumerate(Blockchain().iter_blocks()):
        proof = pow.ProofOfWork(block)
        if not proof.validate():
            print("Error! This block could not be validated")
        #print(json.dumps(block.toDict(), indent=2))
        print(block.hash.hex())
        for tx in block.transactions:
            print(json.dumps(tx.toDict(), indent=2))

def newBlockchain(address):
    if not wallet.validateAddress(address.encode()):
        print("Error: Address is not valid")
        return

    Blockchain().mineBlock([transaction.newCoinbaseTX(address)])
    UTXOSet().reindex()
    print("New blockchain created")

def getBalance(address):
    if not wallet.validateAddress(address.encode()):
        print("Error: Can't get balance of invalid address.")
        return None

    us = UTXOSet()
    pubKeyHash = base58.decode(address.encode())[1:-4]
    return sum([out.value for out in us.findUTXO(pubKeyHash)])

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

    UTXOSet().reindex()
    tx = transaction.newUTXOTransaction(frum.encode(), to.encode(), amount)
    if tx:
        coinbase = transaction.newCoinbaseTX(frum.encode())
        newBlock = Blockchain().mineBlock([coinbase, tx])
        UTXOSet().update(newBlock)
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
    printChain()

def run():
    parser = argparse.ArgumentParser(description='Process blockchain commands')
    parser.add_argument('command', help='a command to perform on the blockchain')
    parser.add_argument('--address', dest='address')
    parser.add_argument('--from', dest='frum')
    parser.add_argument('--to', dest='to')
    parser.add_argument('--amount', dest='amount', type=int)
    args = parser.parse_args()

    command = args.command.lower()

    if util.isSubstringOf(command, 'print-blockchain'):
        printChain()
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
