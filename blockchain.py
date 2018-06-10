import block
import transaction
import shelve

genesisCoinbaseData = 'ravioli ravioli give me the formuoli'
dbFile = 'blockchain'

class BlockchainIterator(object):
    def __init__(self, currentHash, db):
        self.currentHash = currentHash
        self.db = db

    def next(self):
        currentBlock = self.db[self.currentHash.hex()]
        self.currentHash = currentBlock.prevHash
        return currentBlock

    def hasNext(self):
        return not (self.currentHash == (b'\x00' * 32))

class Blockchain(object):
    def __init__(self, tip, db):
        self.tip = tip
        self.db = db

    def mineBlock(self, transactions):
        for tx in transactions:
            if not self.verifyTransaction(tx):
                print("Error verifying transactions")
                print(tx)
                return
                
        lastHash = self.db['l']
        newBlock = block.Block(transactions, lastHash)
        self.db[newBlock.hash.hex()] = newBlock
        self.db['l'] = newBlock.hash
        self.tip = newBlock.hash

    def iterator(self):
        return BlockchainIterator(self.tip, self.db)

    def iter_blocks(self):
        chainIterator = self.iterator()
        while chainIterator.hasNext():
            yield chainIterator.next()

    def findTransaction(self, id):
        for block in self.iter_blocks():
            for tx in block.transactions:
                if tx.id == id: return tx
        return None

    def findUnspentTransactions(self, pubKeyHash):
        unspentTXs = []
        spentTXOs = {}

        # for each block in the chain
        for block in self.iter_blocks():
            # for each tx in the block
            for tx in block.transactions:
                # for each output in the tx
                for outIdx, txOutput in enumerate(tx.vout):
                    # check if output was spent
                    # TODO: this can probably happen in one set lookup
                    # Set of txID + outIdx hashes?
                    if tx.id in spentTXOs and outIdx in spentTXOs[tx.id]:
                        continue

                    # the output was not spent
                    if txOutput.isLockedWithKey(pubKeyHash):
                        unspentTXs.append(tx)

                if not tx.isCoinbase():
                    # for each input in the tx
                    for txInput in tx.vin:
                        # check if input references outputs with this address
                        if txInput.usesKey(pubKeyHash):
                            if not txInput.txId in spentTXOs:
                                spentTXOs[txInput.txId] = []
                            spentTXOs[txInput.txId].append(txInput.vout)
        return unspentTXs

    def findUTXO(self, pubKeyHash):
        UTXs = self.findUnspentTransactions(pubKeyHash)
        return [out for tx in UTXs for out in tx.vout if out.isLockedWithKey(pubKeyHash)]

    def findSpendableOutputs(self, address, amount):
        UTXOs = {}
        UTXs = self.findUnspentTransactions(address)
        accumulated = 0

        for tx in UTXs:
            for outIdx, txOutput in enumerate(tx.vout):
                if txOutput.canBeUnlockedWith(address) and accumulated < amount:
                    accumulated += txOutput.value
                    if not tx.id in UTXOs:
                        UTXOs[tx.id] = []
                    UTXOs[tx.id].append(outIdx)

                    if accumulated >= amount:
                        break

            if accumulated >= amount:
                break
        return accumulated, UTXOs

    def signTransaction(self, tx, privKey):
        prevTXs = {}

        for vin in tx.vin:
            prevTX = self.findTransaction(vin.txId)
            prevTXs[prevTX.hex()] = prevTX

        tx.sign(privKey, prevTXs)

    def verifyTransaction(tx):
        prevTXs = {}

        for vin in tx.vin:
            prevTX = self.findTransaction(vin.txId)
            prevTXs[prevTX.hex()] = prevTX

        return tx.verify(prevTXs)

def newBlockchain(address):
    tip = None
    db = shelve.open(dbFile)
    if not 'l' in db:
        coinbase = transaction.newCoinbaseTX(address, genesisCoinbaseData)
        genesis = block.newGenesisBlock(coinbase)
        db[genesis.hash.hex()] = genesis
        db['l'] = genesis.hash
        tip = genesis.hash
    else:
        tip = db['l']

    chain = Blockchain(tip, db)
    return chain
