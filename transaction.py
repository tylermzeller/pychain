import base58
from wallet import hashPubKey

from pickle import dumps
from hashlib import sha256

subsidy = 50

class Transaction(object):
    def __init__(self, id, vin, vout):
        self.vin = vin
        self.vout = vout
        self.setId(id)

    # TODO, match hash from github
    def setId(self, id=None):
        if not id:
            hash = sha256()
            hash.update(dumps(self))
            id = hash.digest()

        self.id = id

    def isCoinbase(self):
        return len(self.vin) == 1 and len(self.vin[0].txId) == 0 and self.vin[0].vout == -1

    def trimmedCopy(self):
        # Don't populate signature or pubKey for inputs
        inputs =  [TXInput(txIn.txId, txIn.vout) for txIn in self.vin]
        outputs = [TXOutput(txOut.value, txOut.pubKeyHash) for txOut in self.vout]

        return Transaction(self.id, inputs, outputs)

    def sign(self, privKey, prevTxs):
        # Coinbase transactions have no inputs to sign
        if self.isCoinbase(): return

        # A trimmed copy is a copy of the TX, but the
        # inputs have no signatures or pubkeys
        trimCopy = self.trimmedCopy()

        for i, txInput in enumerate(self.vin):
            inCopy = trimCopy.vin[i]
            prevTx = prevTxs[txInput.txId.hex()]
            refTxOutput = prevTx.vout[txInput.vout]
            inCopy.signature = None
            inCopy.pubKey = refTxOutput.pubKeyHash
            trimCopy.setId()
            inCopy.pubKey = None
            txInput.signature = privKey.sign(trimCopy.id)

    def verify(self, prevTxs):
        # A trimmed copy is a copy of the TX, but the
        # inputs have no signatures or pubkeys
        trimCopy = self.trimmedCopy()

        # Loop through the true inputs of this transaction (not copies)
        for i, txInput in enumerate(self.vin):

            # grab a copy for signing
            inCopy = trimCopy.vin[i]

            # get the output this input references
            prevTx = prevTxs[txInput.txId.hex()]
            refTxOutput = prevTx.vout[txInput.vout]

            # Make sure the conditions of this input
            # (no signature, pubKey is out.pubKeyHash)
            # are same as when it was signed
            inCopy.signature = None
            inCopy.pubKey = refTxOutput.pubKeyHash

            # Hash the transaction with one input populated with a pubKeyHash
            trimCopy.setId()

            # Unset this input so we meet the conditions to verify
            # other inputs
            inCopy.pubKey = None

            # If we can't verify this input, the tx is invalid
            if not txInput.pubKey.verify(txInput.signature, trimCopy.id):
                return False

        # Didn't find any invalid txs
        return True

class TXOutput(object):
    def __init__(self, value, pubKeyHash=None):
        self.value = value
        self.pubKeyHash = pubKeyHash

    def Lock(self, address):
        self.pubKeyHash = base58.decode(address)[1:-4]

    def isLockedWithKey(self, pubKeyHash):
        return self.pubKeyHash == pubKeyHash

class TXInput(object):
    def __init__(self, txId, vout, signature=None, pubKey=None):
        self.txId = txId # ID of the transaction whose output is referenced by this input
        self.vout = vout # TODO: change this name. This is an int, not list of TXOutput objects
        self.signature = signature
        self.pubKey = pubKey

    def UsesKey(self, pubKeyHash):
        lockingHash = hashPubKey(self.pubKey)
        return lockingHash == pubKeyHash


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
