import pychain.block as block
import pychain.util as util
from pychain.database_manager import DBManager

class BlockchainIterator:
    def __init__(self, currentHash=b''):
        self.blocks_db = db_manager.DBManager().get('blocks')
        if not currentHash:
            currentHash = self.blocks_db.get(b'l')
        self.currentHash = currentHash

    def next(self):
        encodedBlock = self.blocks_db.get(self.currentHash)
        currentBlock = block.decodeBlock(util.decodeMsg(encodedBlock))
        self.currentHash = currentBlock.prevHash
        return currentBlock

    def hasNext(self):
        return self.blocks_db.exists(self.currentHash)

class Blockchain:
    def __init__(self):
        self.blocks_db = DBManager().get('blocks')

    def getBlock(self, hash):
        if not self.blocks_db.exists(hash):
            return None
        return block.decodeBlock(util.decodeMsg(self.blocks_db.get(hash)))

    def getTip(self):
        if not self.blocks_db.exists(b'l'):
            return None
        encodedBlock = self.blocks_db.get(self.blocks_db.get(b'l'))
        return block.decodeBlock(util.decodeMsg(encodedBlock))

    def setTip(self, blk):
        lastBlock = self.getTip()
        if lastBlock:
            if blk.height > lastBlock.height:
                self.blocks_db.put(b'l', blk.hash)
        else:
            self.blocks_db.put(b'l', blk.hash)

    def getBestHeight(self):
        lastBlock = self.getTip()
        if not lastBlock:
            return -1
        return lastBlock.height

    def getBlockHashes(self):
        return [block.hash for block in self.iter_blocks()]

    def addBlock(self, blk):
        if self.blocks_db.exists(blk.hash):
            return

        encoded_block = util.encodeMsg(block.encodeBlock(blk))
        self.blocks_db.put(blk.hash, encoded_block)
        self.setTip(blk)

    def iterator(self):
        return BlockchainIterator()
