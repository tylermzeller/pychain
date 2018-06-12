class TXOutput(object):
    def __init__(self, value, address=None, pubKeyHash=None):
        self.value = value
        if pubKeyHash:
            self.pubKeyHash = pubKeyHash
        elif address:
            self.lock(address)

    def lock(self, address):
        # the first byte is the verion # and the last 4 bytes
        # are the version + pubkey checksum
        self.pubKeyHash = base58.decode(address)[1:-4]

    def isLockedWithKey(self, pubKeyHash):
        return self.pubKeyHash == pubKeyHash
