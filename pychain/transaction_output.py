import base58

class TXOutput:
    def __init__(self, value=0, idx=-1, address=None, pubKeyHash=None, empty=False):
        if empty: return
        self.value = value
        self.idx = idx
        if pubKeyHash:
            self.pubKeyHash = pubKeyHash
        elif address:
            self.lock(address)

    def toDict(self):
        return {
            'idx': self.idx,
            'value': self.value,
            'pubKeyHash': self.pubKeyHash.hex(),
        }

    def lock(self, address):
        # the first byte is the verion # and the last 4 bytes
        # are the version + pubkey checksum
        self.pubKeyHash = base58.decode(address)[1:-4]

    def isLockedWithKey(self, pubKeyHash):
        return self.pubKeyHash == pubKeyHash

def encodeTXOutput(txOutput):
    if isinstance(txOutput, TXOutput):
        return {
            b'__txoutput__': True,
            b'value': txOutput.value,
            b'idx': txOutput.idx,
            b'pubKeyHash': txOutput.pubKeyHash,
        }

def decodeTXOutput(obj):
    if b'__txoutput__' in obj:
        txOutput = TXOutput(empty=True)
        txOutput.value      = obj[b'value']
        txOutput.idx        = obj[b'idx']
        txOutput.pubKeyHash = obj[b'pubKeyHash']
        return txOutput


class OutputDict(dict):
    # constructor is a copy constructor
    def __init__(self, d={}):
        self.latestIdx = -1
        for idx, txOutput in d.items():
            if self.mustRejectDict(idx, txOutput):
                self.cleanUp()
                return

            self.latestIdx = max(self.latestIdx, idx)
            self[idx] = TXOutput(txOutput.value, idx=txOutput.idx, pubKeyHash=txOutput.pubKeyHash)

    def appendList(self, l=[]):
        for txOutput in l:
            if checkTXOutput(txOutput):
                if txOutput.idx != -1:
                    print("Error: TXOutput already has a valid idx. Cannot reindex.")
                    continue
                self.latestIdx += 1
                txOutput.idx = self.latestIdx
                self[self.latestIdx] = txOutput

    def append(self, txOutput):
        if checkTXOutput(txOutput):
            if txOutput.idx != -1:
                print("Error: TXOutput already has a valid idx. Cannot reindex.")
                return
            self.latestIdx += 1
            txOutput.idx = self.latestIdx
            self[self.latestIdx] = txOutput


    def mustRejectDict(self, key, value):
        return (
            not checkInt(key) or
            not checkTXOutput(value) or
            self.checkDuplicateKey(key) or
            not checkKeyIndexMatch(key, value.idx)
        )

    def checkDuplicateKey(self, key):
        if key in self:
            print("Error: Attempted to enter duplicate key (%d) into OutputDict" % key)
            return True
        return False

    def cleanUp(self):
        self.clear()
        self.latestIdx = 0


def checkInt(value):
    if not isinstance(value, int):
        print("Error: " + str(value) + " must be an instance of int.")
        print("Instead found " + str(type(value)))
        return False
    return True

def checkTXOutput(value):
    if not isinstance(value, TXOutput):
        print("Error: " + str(value) + " must be an instance of TXOutput.")
        print("Instead found " + str(type(value)))
        return False
    return True

def checkKeyIndexMatch(key, idx):
    if not key == idx:
        print("Error: key for OutputDict (%d) and TXOutput.idx (%d) do not match." % (key, idx))
        return False
    return True
