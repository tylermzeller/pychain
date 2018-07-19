import hashlib
import os
import sys
import msgpack
from struct import pack

addressChecksumLength = 4

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

def hashPubKey(publicKey):
    return ripemd160(sha256(publicKey.to_string()))

def checksum(payload):
    return sha256(sha256(payload))[:addressChecksumLength]

def hashData(hashObj, data):
    hashObj.update(data)
    return hashObj.digest()

# prefer toStr(bytes) than bytes.decode() for readability
def toStr(obj):
    if isinstance(obj, str):
        return obj
    if isinstance(obj, bytes):
        return obj.decode()
    return str(obj)

def isSubstringOf(a, b):
    return b.find(a) == 0

# msgpack serialize
def encodeMsg(d, encoder=None):
    return msgpack.packb(d, default=encoder, use_bin_type=True)

# msgpack deserialize
def decodeMsg(msg, decoder=None):
    return msgpack.unpackb(msg, object_hook=decoder, raw=False)

def decodeList(msg, decoder):
    encodedObjs = decodeMsg(msg)
    return [decoder(obj) for obj in encodedObjs]

def canWaitKey():
    return sys.stdin.isatty()
# https://stackoverflow.com/a/34956791
# Cross platform, blocking function to get a pressed key
def waitKey():
    ''' Wait for a key press on the console and return it. '''
    result = None
    if os.name == 'nt':
        import msvcrt
        result = msvcrt.getch()
    else:
        import termios
        fd = sys.stdin.fileno()
        oldterm = termios.tcgetattr(fd)
        newattr = termios.tcgetattr(fd)
        newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSANOW, newattr)

        try:
            result = sys.stdin.read(1)
        except IOError:
            pass
        except KeyboardInterrupt:
            result = 'SIGINT'
        finally:
            termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)

    return result
