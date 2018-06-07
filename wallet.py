from ecdsa import SigningKey, SECP256k1
import hashlib

addressChecksumLength = 4
VERSION = b'\x00'

def newKeyPair():
    priv = SigningKey.generate(curve=SECP256k1)
    pub = priv.get_verifying_key()
    return priv, pub

def hashPubKey(publickey):
    sha = hashlib.sha256()
    sha.update(publickey.to_string())
    ripemd = hashlib.new('ripemd160')
    ripemd.update(sha.digest())
    return ripemd.digest()

def checksum(payload):
    hash1 = hashlib.sha256()
    hash1.update(payload)
    hash2 = hashlib.sha256()
    hash2.update(hash1.digest())
    return hash2.digest()[:addressChecksumLength]

class Wallet(object):
    def __init__(self, privKey, pubKey):
        self.privateKey = privKey
        self.publicKey  = pubKey

    def getAddress(self):
        pubKeyHash = hashPubKey(self.publickey)
        versionedPayload = VERSION + pubKeyHash
        fullPayload = versionedPayload + checksum(versionedPayload)
        return base58Encode(fullPayload)


def newWallet():
    return Wallet(*newKeyPair())
