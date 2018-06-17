from pow import ProofOfWork
from util import sha256
from merkle_tree import MerkleTree

from pickle import dumps
from time import time


class Block(object):
    def __init__(self, transactions, prevHash):
        self.transactions = transactions
        self.prevHash = prevHash
        self.timestamp = int(time())
        self.nonce, self.hash = ProofOfWork(self).run()

    def hashTransactions(self):
        txs = [dumps(tx) for tx in self.transactions]
        tree = MerkleTree(txs)
        return tree.data

def newGenesisBlock(coinbase):
    return Block([coinbase], b'\x00' * 32)
