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
            for txId in UTXO:
                # add them to the cache
                self.db[txId.hex()] = UTXO[txId]

        def findSpendableOutputs(self, pubKeyHash, amount):
            unspentOutIndices = {}
            accumulated = 0

            for txId in self.db:
                rawId = unhexlify(txId)
                for outIdx, out in enumerate(self.db[txId]):
                    if out.isLockedWithKey(pubKeyHash) && accumulated < amount:
                        accumulated += out.value
                        if rawId not in unspentOutIndices:
                            unspentOutIndices[rawId] = []
                        unspentOutIndices[rawId].append(outIdx)

            return accumulated, unspentOutIndices

        def findUTXO(pubKeyHash):
            return [out for txId in self.db for out in self.db[txId] if out.isLockedWithKey(pubKeyHash)]

    instance = None
    def __init__(self, blockchain):
        if not UTXOSet.instance:
            UTXOSet.instance = UTXOSet.__UTXOSet(blockchain)

    def __getattr__(self, name):
        return getattr(self.instance, name)
