import pychain.util

targetBits = 20
maxInt64 = 2**63 - 1

class ProofOfWork:

    def __init__(self, block):
        self.block = block
        self.target = 1 << (256 - targetBits)

    def prepareData(self, nonce):
        b = self.block
        data = b''.join([
            b.prevHash,
            b.merkleRoot,
            util.int64ToBinary(b.timestamp),
            util.int64ToBinary(targetBits),
            util.int64ToBinary(nonce)
        ])
        return data

    def run(self):
        nonce = 0
        powHash = b''
        while nonce < maxInt64:
            data = self.prepareData(nonce)
            hash = util.sha256(data)
            hashInt = int.from_bytes(hash, 'big')
            if hashInt < self.target:
                powHash = hash
                break
            else:
                nonce += 1

        return nonce, powHash

    def validate(self):
        # TODO: can calc merkle root here to verify there was
        # no bamboozle in transit
        data = self.prepareData(self.block.nonce)
        hash = util.sha256(data)
        hashInt = int.from_bytes(hash, 'big')

        return hashInt < self.target
