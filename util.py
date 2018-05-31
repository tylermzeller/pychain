import struct

def int64ToBytes(i):
    # TODO: error handling
    # >q means big endian, long long (int64)
    return struct.pack(">q", i)
