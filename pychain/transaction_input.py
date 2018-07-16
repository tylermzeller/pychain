from pychain.wallet import hashPubKey

from ecdsa import VerifyingKey, SECP256k1

class TXInput:
    def __init__(self, txId=b'', outIdx=-1, pubKey=None, empty=False):
        if empty: return
        self.txId = txId # ID of the transaction whose output is referenced by this input
        self.outIdx = outIdx
        # pubKey is an object. Use .to_string() for bytes rep
        self.pubKey = pubKey
        self.signature = b'\x00' * 64

    def toDict(self):
        obj = {
            'refTxId': self.txId.hex(),
            'refOutIdx': self.outIdx,
            'signature': self.signature.hex(),
        }
        if isinstance(self.pubKey, VerifyingKey):
            obj['pubKey'] = self.pubKey.to_string()
        elif isinstance(self.pubKey, bytes):
            obj['pubKey'] = self.pubKey.hex()
        elif isinstance(self.pubKey, str):
            obj['pubKey'] = self.pubKey

        return obj

    def usesKey(self, pubKeyHash):
        lockingHash = hashPubKey(self.pubKey)
        return lockingHash == pubKeyHash

def encodePubKey(pubKey):
    if isinstance(pubKey, VerifyingKey):
        return {
            b'__pubKeyObj__': True,
            b'pubKeyData': pubKey.to_string(),
        }
    elif isinstance(pubKey, str):
        return {
            b'__pubKeyStr__': True,
            b'pubKeyData': pubKey.encode(),
        }
    elif isinstance(pubKey, bytes):
        return {
            b'__pubKeyBytes__': True,
            b'pubKeyData': pubKey,
        }

def decodePubKey(obj):
    if b'__pubKeyObj__' in obj:
        return VerifyingKey.from_string(obj[b'pubKeyData'], curve=SECP256k1)
    elif b'__pubKeyStr__' in obj:
        return obj[b'pubKeyData'].decode()
    elif b'__pubKeyBytes__' in obj:
        return obj[b'pubKeyData']

def encodeTXInput(txInput):
    if isinstance(txInput, TXInput):
        return {
            b'__txinput__': True,
            b'txId':        txInput.txId,
            b'outIdx':      txInput.outIdx,
            b'pubKey':      encodePubKey(txInput.pubKey),
            b'signature':   txInput.signature,
        }

def decodeTXInput(obj):
    if b'__txinput__' in obj:
        txInput = TXInput(empty=True)
        txInput.txId      = obj[b'txId']
        txInput.outIdx    = obj[b'outIdx']
        txInput.signature = obj[b'signature']
        txInput.pubKey    = decodePubKey(obj[b'pubKey'])
        return txInput
