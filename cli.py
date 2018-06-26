import base58
import pow
import transaction
import wallet
import network

from blockchain import Blockchain
from util import to_str, isSubstringOf
from utxo_set import UTXOSet
from wallet_manager import WalletManager

import argparse

def createWallet():
    wm = WalletManager()
    w = wm.createWallet()
    print("New address: %s" % to_str(w.getAddress()))

def listAddresses():
    wm = WalletManager()
    addresses = wm.getAddresses()
    if not addresses:
        print("Error: Could not get wallets")
        return

    for address in addresses:
        print(address)

# TODO: use actual XML (or JSON or whatever) serialization
def printChain():
    bc = Blockchain(b'')
    for block in bc.iter_blocks():
        proof = pow.ProofOfWork(block)

        print('\n<block hash=%s>' % block.hash.hex())
        print('  <prevHash>%s</prevHash>' % (block.prevHash.hex()))
        print('  <proof>%s</proof>' % (str(proof.validate())))
        for tx in block.transactions:
            print(tx)
        print('</block>\n')

def newBlockchain(address):
    if not wallet.validateAddress(address.encode()):
        print("Error: Address is not valid")
        return

    bc = Blockchain(address.encode())

    us = UTXOSet(bc)
    us.reindex()
    print("Done")

def getBalance(address):
    if not wallet.validateAddress(address.encode()):
        print("Error: Address is not valid")
        return

    bc = Blockchain()
    us = UTXOSet(bc)
    pubKeyHash = base58.decode(address.encode())[1:-4]
    balance = sum([out.value for out in us.findUTXO(pubKeyHash)])
    print("Balance of '%s': %d" % (address, balance))

def send(frum, to, amount):
    if not wallet.validateAddress(frum.encode()):
        print("Error: Sender address is not valid")
        return

    if not wallet.validateAddress(to.encode()):
        print("Error: Recipient address is not valid")
        return

    bc = Blockchain()
    us = UTXOSet(bc)
    us.reindex()
    tx = transaction.newUTXOTransaction(frum.encode(), to.encode(), amount, us)
    if tx:
        coinbase = transaction.newCoinbaseTX(frum.encode())
        newBlock = bc.mineBlock([coinbase, tx])
        us.update(newBlock)
        print("Success!")

def startServer(minerAddress):
    if len(minerAddress) > 0 and wallet.validateAddress(minerAddress.encode()):
        print("This node is mining and will receive rewards to %s" % minerAddress)
    else:
        print("No or incorrect mining address. This node is not mining and will not receive rewards.")

    network.startServer(minerAddress)

def run():
    parser = argparse.ArgumentParser(description='Process blockchain commands')
    parser.add_argument('command', help='a command to perform on the blockchain')
    parser.add_argument('--address', dest='address')
    parser.add_argument('--from', dest='frum')
    parser.add_argument('--to', dest='to')
    parser.add_argument('--amount', dest='amount', type=int)
    args = parser.parse_args()

    command = args.command.lower()

    if isSubstringOf(command, 'print-blockchain'):
        printChain()
    elif isSubstringOf(command, 'init-blockchain'):
        newBlockchain(args.address)
    elif isSubstringOf(command, 'get-balance'):
        getBalance(args.address)
    elif isSubstringOf(command, 'send'):
        send(args.frum, args.to, args.amount)
    elif isSubstringOf(command, 'create-wallet'):
        createWallet()
    elif isSubstringOf(command, 'list-addresses'):
        listAddresses()
    elif isSubstringOf(command, 'up'):
        startServer(args.address)
    else:
        print("No such command.")
