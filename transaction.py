import base58
from wallet import hashPubKey
from wallet_manager import WalletManager
from transaction_input import TXInput
from transaction_output import TXOuput
from util import sha256

from pickle import dumps

subsidy = 50

class Transaction(object):
    def __init__(self, vin=[], vout=[], id=b''):
        self.vin = vin
        self.vout = vout
        if id:
            self.id = id
        else:
            self.setId()

    # TODO, match hash from github
    def setId(self):
        # We want an empty id when we hash this tx
        self.id = b''
        id = sha256(dumps(self))


    def isCoinbase(self):
        return len(self.vin) == 1 and len(self.vin[0].txId) == 0 and self.vin[0].vout == -1

    def trimmedCopy(self):
        # Don't populate signature or pubKey for inputs
        inputs =  [TXInput(txIn.txId, txIn.vout) for txIn in self.vin]
        outputs = [TXOutput(txOut.value, pubKeyHash=txOut.pubKeyHash) for txOut in self.vout]

        return Transaction(inputs, outputs, self.id)

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

def newTX(vin, vout):
    tx = Transaction(vin, vout)
    tx.setId()
    return tx

# Returns a Transaction instance
def newCoinbaseTX(to, data):
    if data == "":
        data = "Reward to %s" % to

    txin = TXInput(pubKey=data)
    txout = TXOutput(subsidy, address=to)

    return Transaction([txin], [txout])

def newUTXOTransaction(frum, to, amount, chain):
    wm = WalletManager()
    w = wm.getWallet(frum)
    pubKeyHash = hashPubKey(w.publicKey)
    # TODO: would it be better to return the actual output object as well?
    # This would negate the need to call getPrevTransactions() below.
    acc, validOutputs = chain.findSpendableOutputs(pubKeyHash, amount)

    if acc < amount:
        print('Not enough funds!')
        return None

    inputs = [TXInput(txId, outIdx, pubKey=w.publicKey) for txId in validOutputs for outIdx in validOutputs[txId]]
    outputs = [TXOutput(amount, address=to)]
    if acc > amount:
        outputs.append(TXOutput(acc - amount, address=frum))

    tx = Transaction(inputs, outputs)
    prevTXs = chain.getPrevTransactions(tx)
    tx.sign(w.privateKey, prevTXs)

    return tx
