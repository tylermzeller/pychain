import block
import transaction
import shelve

blockchainFile = 'blockchain'

class BlockchainManager:
    class __BlockchainManager:
        def __init__(self):
            self.db = shelve.open(blockchainFile)

        def exists(self, key):
            return key in self.db

        def put(self, key, value):
            self.db[key] = value

        def get(self, key):
            return self.db[key]

        def closeDB(self):
            self.db.close()

    instance = None
    def __init__(self):
        if not BlockchainManager.instance:
            BlockchainManager.instance = BlockchainManager.__BlockchainManager()

    def __getattr__(self, name):
        return getattr(self.instance, name)

class BlockchainIterator:
    def __init__(self, currentHash=b''):
        if not currentHash:
            currentHash = BlockchainManager().get('l')
        self.currentHash = currentHash

    def next(self):
        bm = BlockchainManager()
        currentBlock = bm.get(self.currentHash.hex())
        self.currentHash = currentBlock.prevHash
        return currentBlock

    def hasNext(self):
        return not (self.currentHash == (b'\x00' * 32))

class Blockchain:
    def __init__(self, address=None):
        bm = BlockchainManager()
        if not bm.exists('l'):
            if not address:
                print("Error: Address is required.")
                raise Exception("Blockchain not initialized")
            coinbase = transaction.newCoinbaseTX(address)
            genesis = block.newGenesisBlock(coinbase)
            bm.put(genesis.hash.hex(), genesis)
            bm.put('l', genesis.hash)

    def mineBlock(self, transactions):
        for tx in transactions:
            prevTXs = self.getPrevTransactions(tx)
            if not tx.verify(prevTXs):
                print("Error verifying transactions")
                print(tx)
                return

        bm = BlockchainManager()
        lastHash = bm.get('l')
        newBlock = block.Block(transactions, lastHash)
        bm.put(newBlock.hash.hex(), newBlock)
        bm.put('l', newBlock.hash)
        return newBlock

    def iterator(self):
        bm = BlockchainManager()
        return BlockchainIterator(bm.get('l'))

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
        print(tx)

        for vin in tx.vin:
            print('ID ' + vin.txId.hex())
            prevTX = self.findTransaction(vin.txId)
            if prevTX:
                prevTXs[prevTX.id] = prevTX
            else:
                print('Could not find!')

        return prevTXs
