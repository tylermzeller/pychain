import pickle
from hashlib import sha256
subsidy = 50

class Transaction(object):
    def __init__(self, vin, vout):
        self.vin = vin
        self.vout = vout
        self.setId()

    def setId(self):
        hash = sha256()
        hash.update(pickle.dumps(self))
        self.id = hash.digest()

    def isCoinbase(self):
        return len(self.vin) == 1 and len(self.vin[0].txId) == 0 and self.vin[0].vout == -1

class TXOutput(object):
    def __init__(self, value, scriptPubKey):
        self.value = value
        self.scriptPubKey = scriptPubKey

    def canBeUnlockedWith(self, unlockingData):
        return self.scriptPubKey == unlockingData

class TXInput(object):
    def __init__(self, txId, vout, scriptSig):
        self.txId = txId # ID of the transaction whose output is referenced by this input
        self.vout = vout # TODO: change this name. This is an int, not list of TXOutput objects
        self.scriptSig = scriptSig

    def canUnlockOutputWith(self, unlockingData):
        return self.scriptSig == unlockingData


# Returns a Transaction instance
def newCoinbaseTX(to, data):
    if data == "":
        data = "Reward to %s" % to

    txin = TXInput(b'', -1, data)
    txout = TXOutput(subsidy, to)

    return Transaction([txin], [txout])

def newUTXOTransaction(frum, to, amount, chain):
    inputs = []
    outputs = []

    acc, validOutputs = chain.findSpendableOutputs(frum, amount)

    if acc < amount:
        print('Not enough funds!')
        return None

    inputs = [TXInput(txId, outIdx, frum) for txId in validOutputs for outIdx in validOutputs[txId]]
    outputs = [TXOutput(amount, to)]
    if acc > amount:
        outputs.append(TXOutput(acc - amount, frum))

    return Transaction(inputs, outputs)
