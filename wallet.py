import base58
from util import sha256, ripemd160

from ecdsa import SigningKey, SECP256k1

addressChecksumLength = 4
VERSION = b'\x00'

def newKeyPair():
    priv = SigningKey.generate(curve=SECP256k1)
    pub = priv.get_verifying_key()
    return priv, pub

def hashPubKey(publicKey):
    return ripemd160(sha256(publicKey.to_string))

def checksum(payload):
    return sha256(sha256(payload))[:addressChecksumLength]

class Wallet(object):
    def __init__(self, privKey, pubKey):
        self.privateKey = privKey
        self.publicKey  = pubKey

    def getAddress(self):
        pubKeyHash = hashPubKey(self.publicKey)
        versionedPayload = VERSION + pubKeyHash
        fullPayload = versionedPayload + checksum(versionedPayload)
        return base58.encode(fullPayload)

def newWallet():
    return Wallet(*newKeyPair())
