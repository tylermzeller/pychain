from binascii import unhexlify
import pychain.util as util

alphabet = b'123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def encode(payload):
    if not isinstance(payload, bytes):
        raise ValueError('Payload must be of type bytes.')

    if len(payload) == 0:
        return b''

    n = int(payload.hex(), 16)

    res = b'' # bytes object result
    while n > 0:
        n, r = divmod(n, len(alphabet))
        # indexing a bytes object returns ints in python3
        # so we must convert it back into a bytes object
        res += util.intToBytes(alphabet[r])
    res = res[::-1]

    pad = 0
    # NOTE, WARNING: this only works for python3!
    # in python3, integers are returned from a byte array
    # in python2, the zero byte is b'\x00'
    for b in payload:
        if b == 0: pad += 1
        else: break

    res = util.intToBytes(alphabet[0]) * pad + res
    return res

def decode(payload):
    if not payload:
        return b''

    n = 0
    for b in payload:
        n *= len(alphabet)
        if b not in alphabet:
            print('Error decoding %s: %s not in base58 alphabet' % (payload.decode(), chr(b)))
            return b''
        d = alphabet.index(b)
        n += d

    h = '%x' % n
    if len(h) % 2:
        h = '0' + h
    res = unhexlify(h.encode('utf8'))

    pad = 0
    for b in payload[:-1]:
        if b == alphabet[0]: pad += 1
        else: break
    return b'\x00' * pad + res
