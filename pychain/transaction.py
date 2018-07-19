import pychain.base58 as base58

from pychain.transaction_input import TXInput, encodeTXInput, encodeTXInput
from pychain.transaction_output import TXOutput, OutputDict, encodeTXOutput, decodeTXOutput
from pychain.util import sha256

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

def encodeTX(tx):
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
    if b'__tx__' in obj:
        tx = Transaction(empty=True)
        tx.vin = [decodeTXInput(v) for v in obj[b'vin']]
        outDict = { k: decodeTXOutput(v) for k, v in obj[b'outDict'].items() }
        tx.outDict = OutputDict(d=outDict)
        tx.id = obj[b'id']
        return tx
