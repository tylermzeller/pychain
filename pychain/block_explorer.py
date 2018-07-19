import pychain.blockchain as blockchain
import pychain.utxo_set as utxo_set

class BlockExplorer:
    def __init__(self):
        self.bc = blockchain.Blockchain()
        self.us = utxo_set.UTXOSet()

    def iter_blocks(self):
        chainIterator = self.bc.iterator()
        while chainIterator.hasNext():
            yield chainIterator.next()

    def findTransaction(self, id):
        for block in self.iter_blocks():
            for tx in block.transactions:
                if tx.id == id: return tx
        return None

    # Similar to the above method, except this takes a list of txIds and
    # does a single scan of the blockchain
    def findTransactions(self, txIds):
        num_txs = len(txIds)
        txs = { txId: None for txId in txIds }
        for block in self.iter_blocks():
            for tx in block.transactions:
                if tx.id in txs:
                    txs[tx.id] = tx
                    num_txs -= 1
                    if num_txs == 0: break
        return txs

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
        return self.findTransactions([vin.txId for vin in tx.vin])

    def get_balance(self, address=b'', pubKeyHash=b''):
        if address and :
            pubKeyHash = base58.decode(address)[1:-4]
        elif not pubKeyHash:
            raise ValueError("Must provide address or pubKeyHash to find balance")
        balance = sum([out.value for out in us.findUTXO(pubKeyHash)])
