import pychain.base58 as base58

from pychain.util import sha256, ripemd160, intToBytes

import shelve
from ecdsa import SigningKey, VerifyingKey, SECP256k1

addressChecksumLength = 4
default_fee = 0.1
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

    def create_tx(self, to, amount, utxoSet, fee=default_fee):
        pubKeyHash = hashPubKey(self.publicKey)
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
        # NOTE: for testing only
        for tx_in in tx.vin:
            if not tx_in.txId in validOutputs:
                print(tx.toDict())
                raise ValueError("Transaction has inputs whose previous outputs could not be found.")

        self.sign(tx, validOutputs)

        return tx

    def sign(self, tx, prevTxs):
        # Coinbase transactions have no inputs to sign
        if tx.isCoinbase(): return

        # A trimmed copy is a copy of the TX, but the
        # inputs have no signatures or pubkeys
        trimCopy = tx.trimmedCopy()

        for i, txInput in enumerate(self.vin):
            inCopy = trimCopy.vin[i]
            refTxOutput = prevTxs[txInput.txId][txInput.outIdx]
            inCopy.signature = None
            inCopy.pubKey = refTxOutput.pubKeyHash
            trimCopy.setId()
            inCopy.pubKey = None
            txInput.signature = self.privKey.sign(trimCopy.id)

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
