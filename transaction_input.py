from wallet import hashPubKey

class TXInput(object):
    def __init__(self, txId=b'', vout=-1, pubKey=None):
        self.txId = txId # ID of the transaction whose output is referenced by this input
        self.vout = vout # TODO: change this name. This is an int, not list of TXOutput objects
        self.pubKey = pubKey
        self.signature = b'\x00' * 64

    def usesKey(self, pubKeyHash):
        lockingHash = hashPubKey(self.pubKey)
        return lockingHash == pubKeyHash
