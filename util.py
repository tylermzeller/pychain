import hashlib
from msgpack import packb, unpackb
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

# prefer to_s(bytes) than bytes.decode() for readability
def to_str(bytesString):
    return bytesString.decode()

def isSubstringOf(a, b):
    return b.find(a) == 0

def encodeMsg(d, encoder=None):
    return packb(d, default=encoder, use_bin_type=True)

def decodeMsg(msg, decoder=None):
    return unpackb(msg, object_hook=decoder, raw=False)

# https://stackoverflow.com/a/34956791
# Cross platform, blocking function to get a pressed key
def waitKey():
    ''' Wait for a key press on the console and return it. '''
    import os, sys
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
