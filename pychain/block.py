import pychain.transaction as transaction

from pychain.merkle_tree import MerkleTree
from pychain.pow import ProofOfWork

from pickle import dumps
from time import time

class Block:
    def __init__(self, transactions=[], prevHash=b'', height=-1, empty=False):
        if empty:
            return
        self.transactions = transactions
        self.prevHash = prevHash
        self.height = height
        self.timestamp = int(time())
        self.merkleRoot = self.hashTransactions()
        self.nonce, self.hash = ProofOfWork(self).run()

    def toDict(self):
        return {
            'hash': self.hash.hex(),
            'prevHash': self.prevHash.hex(),
            'timestamp': self.timestamp,
            'height': self.height,
            'nonce': self.nonce,
            'merkleRoot': self.merkleRoot.hex(),
            'txs': [tx.toDict() for tx in self.transactions],
        }

    def hashTransactions(self):
        txs = [dumps(tx) for tx in self.transactions]
        tree = MerkleTree(txs)
        return tree.root.data

def newGenesisBlock(coinbase):
    # WARNING: a zero address (32 zero bytes) as the genesis prevHash
    # is wrong in principle. A block *could* hash to this value,
    # creating a cycle in the chain.
    return Block([coinbase], b'\x00' * 32, 0)

def encodeBlock(block):
    if isinstance(block, Block):
        encodedTXs = [transaction.encodeTX(tx) for tx in block.transactions]
        return {
                b'__block__':    True,
                b'transactions': encodedTXs,
                b'timestamp':    block.timestamp,
                b'prevHash':     block.prevHash,
                b'hash':         block.hash,
                b'merkleRoot':   block.merkleRoot,
                b'nonce':        block.nonce,
                b'height':       block.height,
        }

def decodeBlock(obj):
    if b'__block__' in obj:
        block = Block(empty=True)
        block.timestamp =   obj[b'timestamp']
        block.prevHash =    obj[b'prevHash']
        block.height =      obj[b'height']
        block.hash =        obj[b'hash']
        block.merkleRoot =  obj[b'merkleRoot']
        block.nonce =       obj[b'nonce']
        block.transactions = [transaction.decodeTX(txObj) for txObj in obj[b'transactions']]
        return block
