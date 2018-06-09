class TXOutput(object):
    def __init__(self, value, pubKeyHash=None):
        self.value = value
        self.pubKeyHash = pubKeyHash

    def Lock(self, address):
        # the first byte is the verion # and the last 4 bytes
        # are the version + pubkey checksum
        self.pubKeyHash = base58.decode(address)[1:-4]

    def isLockedWithKey(self, pubKeyHash):
        return self.pubKeyHash == pubKeyHash
