import block
import transaction
from util import toStr

import shelve

blockchainFile = 'blockchain'

class BlockchainManager:
    class __BlockchainManager:
        def __init__(self):
            self.db = shelve.open(blockchainFile)

        def exists(self, key):
            return key in self.db

        def put(self, key, value):
            # explicily reject falsey inputs
            if not key:
                return
            self.db[key] = value

        def get(self, key):
            return self.db[key]

        def closeDB(self):
            if self.db:
                self.db.close()

    instance = None
    def __init__(self):
        if not BlockchainManager.instance:
            BlockchainManager.instance = BlockchainManager.__BlockchainManager()

    def __getattr__(self, name):
        return getattr(self.instance, name)

class BlockchainIterator:
    def __init__(self, currentHash=b''):
        bm = BlockchainManager()
        if not currentHash:
            if bm.exists('l'):
                currentHash = BlockchainManager().get('l')
            else:
                currentHash = b''
        self.currentHash = currentHash

    def next(self):
        bm = BlockchainManager()
        currentBlock = bm.get(self.currentHash.hex())
        self.currentHash = currentBlock.prevHash
        return currentBlock

    def hasNext(self):
        return BlockchainManager().exists(self.currentHash.hex())

class Blockchain:

    def getBlock(self, hash):
        bm = BlockchainManager()
        if not bm.exists(hash.hex()):
            return None
        return bm.get(hash.hex())

    def getTip(self):
        bm = BlockchainManager()
        if not bm.exists('l'):
            return None
        return bm.get(bm.get('l').hex())

    def setTip(self, block):
        bm = BlockchainManager()
        lastBlock = self.getTip()
        if lastBlock:
            if block.height > lastBlock.height:
                bm.put('l', block.hash)
            else:
                bm.put('l', block.hash)

    def getBestHeight(self):
        lastBlock = self.getTip()
        if not lastBlock:
            return -1
            return lastBlock.height

    def getBlockHashes(self):
        return [block.hash for block in self.iter_blocks()]


    def addBlock(self, block):
        bm = BlockchainManager()
        if bm.exists(block.hash.hex()):
            return

        bm.put(block.hash.hex(), block)
        self.setTip(block)

    def mineBlock(self, transactions):
        foundCoinbase = False
        for tx in transactions:
            prevTXs = self.getPrevTransactions(tx)
            if not tx.verify(prevTXs):
                print("Error verifying transactions")
                print(tx)
                return
            if tx.isCoinbase():
                foundCoinbase = True

        if not foundCoinbase:
            raise ValueError("Error: Coinbase must be included in list of txs to mine block.")

        bm = BlockchainManager()
        lastBlock = self.getTip()

        if not lastBlock:
            print("\nEmpty blockchain. Creating genesis.")
            if len(transactions) > 1:
                raise ValueError("Error: should only be a single tx in the genesis block.")
            elif len(transactions) == 0:
                coinbase = transaction.newCoinbaseTX(address)
            elif len(transactions) == 1:
                coinbase = transactions[0]
            newBlock = block.newGenesisBlock(coinbase)
        else:
            newBlock = block.Block(transactions, lastBlock.hash, lastBlock.height + 1)
            
        print("Mined a new block %s" % newBlock.hash.hex())
        self.addBlock(newBlock)
        return newBlock

    def iterator(self):
        return BlockchainIterator()

    def iter_blocks(self):
        chainIterator = self.iterator()
        while chainIterator.hasNext():
            yield chainIterator.next()

    def findTransaction(self, id):
        for block in self.iter_blocks():
            for tx in block.transactions:
                if tx.id == id: return tx
        return None

    def findUTXO(self):
        UTXO = {}
        spentTXOs = {}

        # for each block in the chain
        for block in self.iter_blocks():
            # for each tx in the block
            for tx in block.transactions:
                txId = tx.id.hex()
                # for each output in the tx
                for outIdx, txOutput in tx.outDict.items():
                    # check if output was spent
                    if txId in spentTXOs and outIdx in spentTXOs[txId]:
                        continue

                    if not txId in UTXO:
                        UTXO[txId] = []
                    UTXO[txId].append(txOutput)

                if not tx.isCoinbase():
                    # for each input in the tx
                    for txInput in tx.vin:
                        inId = txInput.txId.hex()
                        if not inId in spentTXOs:
                            spentTXOs[inId] = set()
                        spentTXOs[inId].add(txInput.outIdx)
        return UTXO

    # Get's a hash table of transactions referenced by the inputs
    # hashed by the previous transactions' IDs
    def getPrevTransactions(self, tx):
        prevTXs = {}

        for vin in tx.vin:
            prevTX = self.findTransaction(vin.txId)
            if prevTX:
                prevTXs[prevTX.id] = prevTX

        return prevTXs
