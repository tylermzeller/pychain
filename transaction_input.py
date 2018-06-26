from wallet import hashPubKey

from ecdsa import VerifyingKey, SECP256k1

class TXInput(object):
    def __init__(self, txId=b'', outIdx=-1, pubKey=None, empty=False):
        if empty: return
        self.txId = txId # ID of the transaction whose output is referenced by this input
        self.outIdx = outIdx
        # pubKey is an object. Use .to_string() for str rep
        self.pubKey = pubKey
        self.signature = b'\x00' * 64

    def usesKey(self, pubKeyHash):
        lockingHash = hashPubKey(self.pubKey)
        return lockingHash == pubKeyHash

def encodeTXInput(txInput):
    if isinstance(txInput, TXInput):
        return {
            b'__txinput__': True,
            b'txId':        txInput.txId,
            b'outIdx':      txInput.outIdx,
            b'pubKey':      txInput.pubKey.to_string(),
            b'signature':   txInput.signature,
        }

def decodeTXInput(obj):
    if b'__txinput__' in obj:
        txInput = TXInput(empty=True)
        txInput.txId      = obj[b'txId']
        txInput.outIdx    = obj[b'outIdx']
        txInput.signature = obj[b'signature']
        txInput.pubKey    = VerifyingKey.from_string(obj[b'pubKey'], curve=SECP256k1)
        return txInput
