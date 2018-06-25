from iter_attr import IterAttr
from merkle_tree import MerkleTree
from pow import ProofOfWork
from util import sha256

from pickle import dumps
from time import time


class Block:
    def __init__(self, transactions, prevHash, height, empty=False):
        if empty:
            return
        self.transactions = transactions
        self.prevHash = prevHash
        self.height = height
        self.timestamp = int(time())
        self.nonce, self.hash = ProofOfWork(self).run()

    def hashTransactions(self):
        txs = [dumps(tx) for tx in self.transactions]
        tree = MerkleTree(txs)
        return tree.data

def newGenesisBlock(coinbase):
    return Block([coinbase], b'\x00' * 32, 0)

def encodeBlock(block):
    from transaction import encodeTX
    if isinstance(block, Block):
        encodedTXs = [encodeTX(tx) for tx in block.transactions]
        return {
                b'__block__':    True,
                b'transactions': encodedTXs,
                b'timestamp':    block.timestamp,
                b'prevHash':     block.prevHash,
                b'hash':         block.hash,
                b'nonce':        block.nonce,
                b'height':       block.height,
        }

def decodeBlock(obj):
    from transaction import decodeTX
    if b'__block__' in obj:
        block = Block(empty=True)
        block.timestamp =   obj[b'timestamp']
        block.prevHash =    obj[b'prevHash']
        block.height =      obj[b'height']
        block.hash =        obj[b'hash']
        block.nonce =       obj[b'nonce']
        block.transactions = [decodeTX(txObj) for txObj in obj[b'transactions']]
        return block
