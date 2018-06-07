from struct import pack

# TODO: rename int64ToBinary
def int64ToBytes(i):
    # TODO: error handling
    # >q means big endian, long long (int64)
    return pack(">q", i)

def intToBytes(i):
    return bytes([i])
