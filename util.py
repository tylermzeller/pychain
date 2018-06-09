import hashlib
from struct import pack

def int64ToBinary(i):
    # TODO: error handling
    # >q means big endian, long long (int64)
    return pack(">q", i)

def intToBytes(i):
    return bytes([i])

def sha256(data):
    return hashData(hashlib.sha256(), data)

def ripemd160(data):
    return hashData(hashlib.new('ripemd160'), data)

def hashData(hashObj, data):
    hashObj.update(data)
    return hashObj.digest()
