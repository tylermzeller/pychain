from pow import ProofOfWork
from util import sha256

from time import time


class Block(object):
    def __init__(self, transactions, prevHash):
        self.transactions = transactions
        self.prevHash = prevHash
        self.timestamp = int(time())
        self.nonce, self.hash = ProofOfWork(self).run()

    def hashTransactions(self):
        txHashes = [tx.id for tx in self.transactions]
        return sha256(b''.join(txHashes))

def newGenesisBlock(coinbase):
    return Block([coinbase], b'\x00' * 32)
