import block
from blockchain_iterator import BlockchainIterator
import shelve

dbFile = 'blockchain'

class Blockchain(object):

    def __init__(self, tip, db):
        self.tip = tip
        self.db = db

    def addBlock(self, data):
        lastHash = self.db['l']
        newBlock = block.Block(data, lastHash)
        self.db[newBlock.hash.hex()] = newBlock
        self.db['l'] = newBlock.hash
        self.tip = newBlock.hash

    def iterator(self):
        return BlockchainIterator(self.tip, self.db)

def newBlockchain():
    tip = None
    db = shelve.open(dbFile)
    if not 'l' in db:
        genesis = block.newGenesisBlock()
        db[genesis.hash.hex()] = genesis
        db['l'] = genesis.hash
        tip = genesis.hash
    else:
        tip = db['l']

    chain = Blockchain(tip, db)
    return chain
