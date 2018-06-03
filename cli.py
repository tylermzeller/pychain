import argparse

import blockchain
import pow
import transaction

class CLI(object):
    def run(self):
        parser = argparse.ArgumentParser(description='Process blockchain commands')
        parser.add_argument('command', help='a command to perform on the blockchain')
        parser.add_argument('--address', dest='address')
        parser.add_argument('--from', dest='frum')
        parser.add_argument('--to', dest='to')
        parser.add_argument('--amount', dest='amount', type=int)
        args = parser.parse_args()

        if args.command.lower() in ['p', 'print', 'log', 'show', 'display']:
            self.printChain()
        elif args.command.lower() in ['nbc', 'newblockchain', 'newchain']:
            self.newBlockchain(args.address)
        elif args.command.lower() in ['gb', 'getbalance', 'b', 'balance']:
            self.getBalance(args.address)
        elif args.command.lower() in ['s', 'send', 'pay']:
            self.send(args.frum, args.to, args.amount)
        else:
            print("No such command.")

    def printChain(self):
        bc = blockchain.newBlockchain("Tyler")
        chainIterator = bc.iterator()

        while chainIterator.hasNext():
            block = chainIterator.next()
            proof = pow.ProofOfWork(block)
            print('Prev. Hash: %s' % (block.prevHash.hex()))
            print('Hash:       %s' % (block.hash.hex()))
            print('PoW:        %s\n'% (str(proof.validate())))
        bc.db.close()

    def newBlockchain(self, address):
        bc = blockchain.newBlockchain(address)
        bc.db.close()
        print("Done")

    def getBalance(self, address):
        bc = blockchain.newBlockchain(address)
        balance = sum([out.value for out in bc.findUTXO(address)])
        bc.db.close()
        print("Balance of '%s': %d" % (address, balance))

    def send(self, frum, to, amount):
        bc = blockchain.newBlockchain(frum)
        tx = transaction.newUTXOTransaction(frum, to, amount, bc)
        if tx:
            bc.mineBlock([tx])
            print("Success!")
        bc.db.close()
