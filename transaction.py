import base58
from wallet import hashPubKey
from wallet_manager import WalletManager
from transaction_input import TXInput
from transaction_output import TXOutput, OutputDict
from util import sha256

from pickle import dumps
from random import randint

subsidy = 50

class Transaction(object):
    def __init__(self, vin=[], outDict=None, id=b''):
        self.vin = vin
        if not outDict or not isinstance(outDict, OutputDict):
            outDict = OutputDict()

        self.outDict = outDict
        if id:
            self.id = id
        else:
            self.setId()

    def __str__(self):
        lines = ['<tx id=%s>' % self.id.hex()]

        for i, txInput in enumerate(self.vin):
            lines.append("  <input i=%d>" % i)
            lines.append("    <outputID>%s</outputID>" % txInput.txId.hex())
            lines.append("    <outIdx>%d</outIdx>" % txInput.outIdx)
            lines.append("    <signature>%s</signature>" % txInput.signature.hex())
            if isinstance(txInput.pubKey, str):
                lines.append("    <pubKey>%s</pubkey>" % txInput.pubKey)
            else:
                lines.append("    <pubKey>%s</pubkey>" % txInput.pubKey.to_string().hex())
            lines.append("  </input>")

        for i, txOutput in self.outDict.items():
            lines.append("  <output i=%d>" % i)
            lines.append("    <value>%d</value>" % txOutput.value)
            lines.append("    <pubKeyHash>%s</pubKeyHash>" % txOutput.pubKeyHash.hex())
            lines.append("  </output>")

        lines.append("</tx>")
        return '\n'.join(lines)

    def setId(self):
        # We want an empty id when we hash this tx
        self.id = b''
        self.id = sha256(dumps(self))

    def isCoinbase(self):
        return len(self.vin) == 1 and len(self.vin[0].txId) == 0 and self.vin[0].outIdx == -1

    def trimmedCopy(self):
        # Don't populate signature or pubKey for inputs
        inputs =  [TXInput(txIn.txId, txIn.outIdx) for txIn in self.vin]
        # Readability may be shitty, but this copies the output dictionary
        # outputs = {idx: TXOutput(self.outDict[idx].value, idx=self.outDict[idx].idx, pubKeyHash=self.outDict[idx].pubKeyHash) for idx in self.outDict}
        outputs = OutputDict(d=self.outDict)

        return Transaction(inputs, outputs, self.id)

    def sign(self, privKey, prevTxs):
        # Coinbase transactions have no inputs to sign
        if self.isCoinbase(): return

        # A trimmed copy is a copy of the TX, but the
        # inputs have no signatures or pubkeys
        trimCopy = self.trimmedCopy()

        for i, txInput in enumerate(self.vin):
            inCopy = trimCopy.vin[i]
            prevTx = prevTxs[txInput.txId]
            refTxOutput = prevTx.outDict[txInput.outIdx]
            inCopy.signature = None
            inCopy.pubKey = refTxOutput.pubKeyHash
            trimCopy.setId()
            inCopy.pubKey = None
            txInput.signature = privKey.sign(trimCopy.id)

    def verify(self, prevTxs):
        if self.isCoinbase(): return True

        for txInput in self.vin:
            if txInput.txId not in prevTxs:
                raise Exception("Prev TX for TXInput %s not found" % txInput.txId.hex())
            if not prevTxs[txInput.txId].id:
                print(prevTxs[txInput.txId])
                raise Exception("Invalid previous tx.")
        # A trimmed copy is a copy of the TX, but the
        # inputs have no signatures or pubkeys
        trimCopy = self.trimmedCopy()

        # Loop through the true inputs of this transaction (not copies)
        for i, txInput in enumerate(self.vin):

            # grab a copy for signing
            inCopy = trimCopy.vin[i]

            # get the output this input references
            prevTx = prevTxs[txInput.txId]
            refTxOutput = prevTx.outDict[txInput.outIdx]

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

def newTX(vin, outDict):
    tx = Transaction(vin, outDict)
    tx.setId()
    return tx

# Returns a Transaction instance
def newCoinbaseTX(to):
    randbytes = b''
    for i in range(40):
        randbytes += bytes([randint(0, 255)])

    txin = TXInput(pubKey=randbytes.hex())
    outDict = OutputDict()
    outDict.append(TXOutput(subsidy, address=to))

    return Transaction([txin], outDict)

def newUTXOTransaction(frum, to, amount, utxoSet):
    wm = WalletManager()
    w = wm.getWallet(frum)
    pubKeyHash = hashPubKey(w.publicKey)
    # TODO: would it be better to return the actual output object as well?
    # This would negate the need to call getPrevTransactions() below.
    acc, validOutputs = utxoSet.findSpendableOutputs(pubKeyHash, amount)

    if acc < amount:
        print('Not enough funds!')
        return None

    inputs = [TXInput(txId, outIdx, pubKey=w.publicKey) for txId in validOutputs for outIdx in validOutputs[txId]]
    # outputs = [TXOutput(amount, idx=0, address=to)]
    outDict = OutputDict()
    outDict.append(TXOutput(amount, address=to))
    if acc > amount:
        outDict.append(TXOutput(acc - amount, address=frum))

    tx = Transaction(inputs, outDict)
    prevTXs = utxoSet.bc.getPrevTransactions(tx)
    tx.sign(w.privateKey, prevTXs)

    return tx
