class TXInput(object):
    def __init__(self, txId, vout, signature=None, pubKey=None):
        self.txId = txId # ID of the transaction whose output is referenced by this input
        self.vout = vout # TODO: change this name. This is an int, not list of TXOutput objects
        self.signature = signature
        self.pubKey = pubKey

    def UsesKey(self, pubKeyHash):
        lockingHash = hashPubKey(self.pubKey)
        return lockingHash == pubKeyHash
