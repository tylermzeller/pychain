from pychain.util import sha256

class MerkleNode:
    def __init__(self, left=None, right=None, data=None):
        if left is not None and right is not None:
            data = left.data + right.data
        self.data = sha256(data)
        self.left = left
        self.right = right

class MerkleTree:
    def __init__(self, data):
        nodes = [MerkleNode(data=datum) for datum in data]

        if len(nodes) == 0:
            raise ValueError("No data given to create a Merkle Tree!")

        while len(nodes) > 1:
            if len(nodes) % 2 != 0:
                nodes.append(nodes[-1])
            level = []
            for i in range(0, len(nodes), 2):
                level.append(MerkleNode(nodes[i], nodes[i+1]))

            nodes = level

        self.root = nodes[0]
