import base58
from util import sha256, ripemd160, intToBytes

import shelve
from ecdsa import SigningKey, VerifyingKey, SECP256k1

addressChecksumLength = 4
VERSION = b'\x00'

def newKeyPair():
    priv = SigningKey.generate(curve=SECP256k1)
    pub = priv.get_verifying_key()
    return priv, pub

def hashPubKey(publicKey):
    return ripemd160(sha256(publicKey.to_string()))

def checksum(payload):
    return sha256(sha256(payload))[:addressChecksumLength]

def validateAddress(address):
    pubKeyHash = base58.decode(address)
    chksum = pubKeyHash[-4:]
    version = intToBytes(pubKeyHash[0])
    pubKeyHash = pubKeyHash[1:-4]
    return checksum(version + pubKeyHash) == chksum

class Wallet:
    def __init__(self, privKey=None, pubKey=None):
        if privKey is None:
            self.privateKey, self.publicKey = newKeyPair()
        elif pubKey is None:
            self.privateKey, self.publiKey = privKey, privKey.get_verifying_key()
        else:
            self.privateKey, self.publicKey = privKey, pubKey

    def getAddress(self):
        pubKeyHash = hashPubKey(self.publicKey)
        versionedPayload = VERSION + pubKeyHash
        fullPayload = versionedPayload + checksum(versionedPayload)
        return base58.encode(fullPayload)

def encodeWallet(w):
    if isinstance(w, Wallet):
        return {
            b'__wallet__': True,
            b'privateKey': w.privateKey.to_string(),
            b'publicKey':  w.publicKey.to_string(),
        }

def decodeWallet(w):
    if b'__wallet__' in w:
        sk = SigningKey.from_string(w[b'privateKey'], curve=SECP256k1)
        vk = VerifyingKey.from_string(w[b'publicKey'], curve=SECP256k1)
        return Wallet(sk, vk)
