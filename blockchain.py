import block
import transaction
import util
from database_manager import DBManager


class BlockchainIterator:
    def __init__(self, currentHash=b''):
        self.blocks_db = DBManager().get('blocks')
        if not currentHash:
            currentHash = self.blocks_db.get(b'l')
        self.currentHash = currentHash

    def next(self):
        encodedBlock = self.blocks_db.get(self.currentHash)
        currentBlock = util.decodeBlock(encodedBlock, decoder=block.decodeBlock)
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
        return util.decodeMsg(self.blocks_db.get(hash), decoder=block.decodeBlock)

    def getTip(self):
        if not self.blocks_db.exists(b'l'):
            return None
        encodedBlock = self.blocks_db.get(self.blocks_db.get(b'l'))
        return util.decodeMsg(encodedBlock, decoder=block.decodeBlock)

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

        encoded_block = util.encodeMsg(blk, encoder=block.encodeBlock)
        self.blocks_db.put(blk.hash, encoded_block)
        self.setTip(blk)

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
                # for each output in the tx
                for outIdx, txOutput in tx.outDict.items():
                    # check if output was spent
                    if tx.id in spentTXOs and outIdx in spentTXOs[tx.id]:
                        continue

                    if not tx.id in UTXO:
                        UTXO[tx.id] = []
                    UTXO[tx.id].append(txOutput)

                if not tx.isCoinbase():
                    # for each input in the tx
                    for txInput in tx.vin:
                        inId = txInput.txId
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
