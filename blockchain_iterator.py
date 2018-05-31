class BlockchainIterator(object):
    def __init__(self, currentHash, db):
        self.currentHash = currentHash
        self.db = db

    def next(self):
        currentBlock = self.db[self.currentHash.hex()]
        self.currentHash = currentBlock.prevHash
        return currentBlock
