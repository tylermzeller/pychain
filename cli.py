import pow
import argparse

class CLI(object):
    def __init__(self, chain):
        self.chain = chain

    def run(self):
        parser = argparse.ArgumentParser(description='Process blockchain commands')
        parser.add_argument('command', help='a command to perform on the blockchain')
        parser.add_argument('--data', dest='data')
        args = parser.parse_args()

        if args.command == 'addblock':
            self.addBlock(args.data)
        elif args.command == 'printchain':
            self.printChain()

    def addBlock(self, data):
        self.chain.addBlock(data.encode())
        print("Success!")

    def printChain(self):
        chainIterator = self.chain.iterator()

        while True:
            block = chainIterator.next()
            proof = pow.ProofOfWork(block)
            print('Prev. Hash: %s' % (block.prevHash.hex()))
            print('Data:       %s' % (block.data.decode()))
            print('Hash:       %s' % (block.hash.hex()))
            print('PoW:        %s\n'% (str(proof.validate())))

            if block.prevHash == b'\x00' * 32: break
