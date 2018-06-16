import base58
import pow
import transaction
import wallet

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

def printChain():
    bc = Blockchain(b'')
    for block in bc.iter_blocks():
        proof = pow.ProofOfWork(block)

        print('******* Block %s *******' % block.hash.hex())
        print('Prev. Hash:   %s' % (block.prevHash.hex()))
        print('PoW:          %s'% (str(proof.validate())))
        for tx in block.transactions:
            print(tx)
        print('\n')

def newBlockchain(address):
    if not wallet.validateAddress(address.encode()):
        print("Error: Address is not valid")
        return

    bc = Blockchain(address.encode())

    utxoSet = UTXOSet(bc)
    utxoSet.reindex()
    print("Done")

def getBalance(address):
    if not wallet.validateAddress(address.encode()):
        print("Error: Address is not valid")
        return

    bc = Blockchain()
    pubKeyHash = base58.decode(address.encode())[1:-4]
    balance = sum([out.value for out in bc.findUTXO(pubKeyHash)])
    print("Balance of '%s': %d" % (address, balance))

def send(frum, to, amount):
    if not wallet.validateAddress(frum.encode()):
        print("Error: Sender address is not valid")
        return

    if not wallet.validateAddress(to.encode()):
        print("Error: Recipient address is not valid")
        return

    bc = Blockchain()
    utxoSet = UTXOSeT(bc)
    utxoSet.reindex()
    tx = transaction.newUTXOTransaction(frum.encode(), to.encode(), amount, utxoSet)
    if tx:
        coinbase = transaction.newCoinbaseTX(frum.encode())
        newBlock = bc.mineBlock([coinbase, tx])
        utxoSet.update(newBlock)
        print("Success!")

def run():
    parser = argparse.ArgumentParser(description='Process blockchain commands')
    parser.add_argument('command', help='a command to perform on the blockchain')
    parser.add_argument('--address', dest='address')
    parser.add_argument('--from', dest='frum')
    parser.add_argument('--to', dest='to')
    parser.add_argument('--amount', dest='amount', type=int)
    args = parser.parse_args()

    command = args.command.lower()

    if isSubstringOf('print-blockchain', command):
        printChain()
    elif isSubstringOf('init-blockchain', command):
        newBlockchain(args.address)
    elif isSubstringOf('get-balance', command):
        getBalance(args.address)
    elif isSubstringOf('send', command):
        send(args.frum, args.to, args.amount)
    elif isSubstringOf('create-wallet', command):
        createWallet()
    elif isSubstringOf('list-addresses', command):
        listAddresses()
    else:
        print("No such command.")
