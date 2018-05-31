import time
import struct
import pow
from hashlib import sha256

class Block(object):
    def __init__(self, data, prevHash):
        if isinstance(data, str):
            data = data.encode()
        self.data = data
        self.prevHash = prevHash
        self.timestamp = int(time.time())

        proof = pow.ProofOfWork(self)
        self.nonce, self.hash = proof.run()

def newGenesisBlock():
    return Block('Genesis Block', b'\x00' * 32)
