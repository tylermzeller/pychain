import util
import struct
from hashlib import sha256

targetBits = 24
maxInt64 = 2**63 - 1

class ProofOfWork(object):

    def __init__(self, block):
        self.block = block
        self.target = 1 << (256 - targetBits)

    def prepareData(self, nonce):
        b = self.block
        data = b''.join([
            b.prevHash,
            b.data,
            util.int64ToBytes(b.timestamp),
            util.int64ToBytes(targetBits),
            util.int64ToBytes(nonce)
        ])
        return data

    def run(self):
        nonce = 0
        print("Mining the block containing \"%s\"" % self.block.data.decode())
        powHash = b''
        while nonce < maxInt64:
            data = self.prepareData(nonce)
            hash = sha256()
            hash.update(data)
            # TODO: which is better? int(hash.hexdigest(), 16)
            hashInt = int.from_bytes(hash.digest(), 'big')
            if hashInt < self.target:
                powHash = hash.digest()
                print(powHash.hex())
                break
            else:
                nonce += 1

        print('\n')
        return nonce, powHash

    def validate(self):
        data = self.prepareData(self.block.nonce)
        hash = sha256()
        hash.update(data)
        hashInt = int.from_bytes(hash.digest(), 'big')

        return hashInt < self.target
