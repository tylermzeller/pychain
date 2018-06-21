from iter_attr import IterAttr
from merkle_tree import MerkleTree
from pow import ProofOfWork
from transaction import encodeTX, decodeTX
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
    if isinstance(block, Block):
        encodedTXs = [encodeTX(tx) for tx in block.transactions]
        return {
                '__block__':    True,
                'transactions': encodedTXs,
                'timestamp':    block.timestamp,
                'prevHash':     block.prevHash,
                'hash':         block.hash,
                'nonce':        block.nonce,
                'height':       block.height,
                }

def decodeBlock(obj):
    if '__block__' in obj:
        block = Block(empty=True)
        block.timestamp = obj['timestamp']
        block.prevHash = obj['prevHash']
        block.height = obj['height']
        block.hash = obj['hash']
        block.nonce = obj['nonce']
        block.transactions = [decodeTX(txObj) for txObj in obj['transactions']]
    else: return None
