import base58
import utxo_set
from blockchain import Blockchain
from wallet import hashPubKey
from wallet_manager import WalletManager
from transaction_input import TXInput
from transaction_output import TXOutput, OutputDict
from util import sha256

from pickle import dumps
from random import randint

subsidy = 50
default_fee = 0.1

class Transaction:
    def __init__(self, vin=[], outDict=None, id=b'', empty=False):
        if empty:
            return
        self.vin = vin
        if not outDict or not isinstance(outDict, OutputDict):
            outDict = OutputDict()

        self.outDict = outDict
        if id:
            self.id = id
        else:
            self.setId()

    def toDict(self):
        return {
            'id': self.id.hex(),
            'inputs': [txInput.toDict() for txInput in self.vin],
            'outputs': [txOutput.toDict() for txOutput in self.outDict.values()]
        }

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

    def sign(self, privKey, prevTxs=None):
        # Coinbase transactions have no inputs to sign
        if self.isCoinbase(): return

        if prevTxs is None:
            prevTxs = Blockchain().getPrevTransactions(self)

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

    def verify(self, prevTxs=None):
        if self.isCoinbase(): return True

        if prevTxs is None:
            prevTxs = Blockchain().getPrevTransactions(self)

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
def newCoinbaseTX(to, fees=0):
    randbytes = b''
    for i in range(40):
        randbytes += bytes([randint(0, 255)])

    txin = TXInput(pubKey=randbytes.hex())
    outDict = OutputDict()
    outDict.append(TXOutput(subsidy + fees, address=to))

    return Transaction([txin], outDict)

def newUTXOTransaction(frum, to, amount, utxoSet=None, fee=default_fee):
    if utxoSet is None:
        utxoSet = utxo_set.UTXOSet()
    wm = WalletManager()
    w = wm.getWallet(frum)
    pubKeyHash = hashPubKey(w.publicKey)
    amountWithFee = amount + fee
    acc, validOutputs = utxoSet.findSpendableOutputs(pubKeyHash, amountWithFee)

    if acc < amountWithFee:
        print('Not enough funds!')
        return None

    inputs = [TXInput(txId, outIdx, pubKey=w.publicKey) for txId in validOutputs for outIdx in validOutputs[txId]]
    outDict = OutputDict()
    outDict.append(TXOutput(amount, address=to))
    if acc > amountWithFee:
        outDict.append(TXOutput(acc - amountWithFee, address=frum))

    tx = Transaction(inputs, outDict)
    tx.sign(w.privateKey)

    return tx

def calcFees(txs):
    s = 0
    for tx in txs:
      prevTxs = Blockchain().getPrevTransactions(tx)
      s += sum([prevTxs[vin.txId].outDict[vin.outIdx].value for vin in tx.vin])
    return s - sum([vout.value for tx in txs for vout in tx.outDict.values()])

def encodeTX(tx):
    from transaction_input import encodeTXInput
    from transaction_output import encodeTXOutput
    if isinstance(tx, Transaction):
        inputs = [encodeTXInput(v) for v in tx.vin]
        outputs = { k: encodeTXOutput(v) for k, v in tx.outDict.items() }
        return {
            b'__tx__': True,
            b'id': tx.id,
            b'vin': inputs,
            b'outDict': outputs
        }

def decodeTX(obj):
    from transaction_input import decodeTXInput
    from transaction_output import decodeTXOutput
    if b'__tx__' in obj:
        tx = Transaction(empty=True)
        tx.vin = [decodeTXInput(v) for v in obj[b'vin']]
        outDict = { k: decodeTXOutput(v) for k, v in obj[b'outDict'].items() }
        tx.outDict = OutputDict(d=outDict)
        tx.id = obj[b'id']
        return tx
