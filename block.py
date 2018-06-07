import pow

from time import time
from hashlib import sha256

class Block(object):
    def __init__(self, transactions, prevHash):
        self.transactions = transactions
        self.prevHash = prevHash
        self.timestamp = int(time())

        proof = pow.ProofOfWork(self)
        self.nonce, self.hash = proof.run()

    def hashTransactions(self):
        txHashes = [tx.id for tx in self.transactions]
        hash = sha256()
        hash.update(b''.join(txHashes))
        return hash.digest()

def newGenesisBlock(coinbase):
    return Block([coinbase], b'\x00' * 32)
