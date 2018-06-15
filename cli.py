import base58
import blockchain
import pow
import transaction
import wallet

from util import to_str
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
    bc = blockchain.newBlockchain(b'')
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

    bc = blockchain.Blockchain(address.encode())

    utxoSet = UTXOSet(bc)
    utxoSet.reindex()
    print("Done")

def getBalance(address):
    if not wallet.validateAddress(address.encode()):
        print("Error: Address is not valid")
        return

    bc = blockchain.Blockchain(address.encode())
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

    bc = blockchain.Blockchain(frum.encode())
    utxoSet = UTXOSeT(bc)
    utxoSet.reindex()
    tx = transaction.newUTXOTransaction(frum.encode(), to.encode(), amount, bc)
    if tx:
        newBlock = bc.mineBlock([tx])
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

    if args.command.lower() in ['p', 'print', 'log', 'show', 'display']:
        printChain()
    elif args.command.lower() in ['nbc', 'newblockchain', 'newchain']:
        newBlockchain(args.address)
    elif args.command.lower() in ['gb', 'getbalance', 'b', 'balance']:
        getBalance(args.address)
    elif args.command.lower() in ['s', 'send', 'pay']:
        send(args.frum, args.to, args.amount)
    elif args.command.lower() in ['cw', 'createwallet']:
        createWallet()
    elif args.command.lower() in ['l', 'la', 'list', 'listaddresses']:
        listAddresses()
    else:
        print("No such command.")
