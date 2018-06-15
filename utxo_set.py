import shelve
from binascii import unhexlify

utxoFile = 'utxoset'

class UTXOSet:
    class __UTXOSet:
        def __init__(self, blockchain):
            self.bc = blockchain
            self.db = shelve.open(utxoFile)

        def reindex(self):
            # empty the current indexed UTXOs
            self.db.clear()
            # get the new UTXOs
            UTXO = self.bc.findUTXO()
            for txId, txOutputs in UTXO.items():
                # add them to the cache
                self.db[txId] = txOutputs

        def update(self, block):
            for tx in block.transactions:
                # coinbase txs don't have inputs, duh
                if not tx.isCoinbase():
                    # for each input, remove the output that it spends from the UTXO set
                    for txInput in tx.vin:
                        txOutputs = self.db[txInput.txId.hex()]
                        updatedOutputs = [txOutput for txOutput in txOutputs if txOutput.idx != txInput.outIdx]

                        if len(updatedOutputs) == 0:
                            del self.db[txInput.txId.hex()]
                        else:
                            self.db[txInput.txId.hex()] = updatedOutputs

                # add new outputs to the UTXO set
                self.db[tx.id.hex()] = tx.outDict.values()

        def findSpendableOutputs(self, pubKeyHash, amount):
            unspentOutIndices = {}
            accumulated = 0

            for txId in self.db:
                for txOutput in self.db[txId]:
                    if txOutput.isLockedWithKey(pubKeyHash) && accumulated < amount:
                        accumulated += txOutput.value
                        if txId not in unspentOutIndices:
                            unspentOutIndices[txId] = []
                        unspentOutIndices[txId].append(txOutput.idx)

            return accumulated, unspentOutIndices

        def findUTXO(self, pubKeyHash):
            return [txOutput for txId in self.db for txOutput in self.db[txId] if txOutput.isLockedWithKey(pubKeyHash)]

        def closeDB(self):
            self.db.close()

    instance = None
    def __init__(self, blockchain):
        if not UTXOSet.instance:
            UTXOSet.instance = UTXOSet.__UTXOSet(blockchain)

    def __getattr__(self, name):
        return getattr(self.instance, name)
