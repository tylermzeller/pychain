import pychain.merkle_tree as merkle
from pychain.util import sha256

from pickle import dumps
data = [
    [b''],
    ]
data.append(data[0] + [b'pychain'])
data.append(data[1] + [(42).to_bytes(4, byteorder='big')])
data.append(data[2] + [dumps({'foo': 'bar', 'pychain': 4})])

def hash_samples(samples):
    if len(samples) % 2 == 1:
        assert False

    hashes = []
    for i in range(0, len(samples), 2):
        hashes.append(sha256(samples[i] + samples[i + 1]))
    return hashes

def test_root():
    for sample in data:
        sample_list = sample[:]
        if len(sample_list) % 2 == 1:
            sample_list.append(sample[-1])

        hashes = [sha256(s) for s in sample_list]
        while 1:
            hashes = hash_samples(hashes)
            if len(hashes) == 1: break
            if len(hashes) % 2 == 1:
                hashes.append(hashes[-1])

        assert len(hashes) == 1
        assert hashes[0] == merkle.MerkleTree(sample_list).root.data
