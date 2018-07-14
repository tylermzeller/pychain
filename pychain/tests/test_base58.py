import pychain.base58 as base58
from binascii import unhexlify

encoded_samples = [
    b'',
    b'2g',
    b'a3gV',
    b'aPEr',
    b'2cFupjhnEsSn59qHXstmK2ffpLv2',
    b'1NS17iag9jJgTHD1VXjvLCEnZuQ3rJDE9L',
    b'ABnLTmg',
    b'3SEo3LWLoPntC',
    b'3EFU7m',
    b'EJDM8drfXA6uyA',
    b'Rt5zm',
    b'1111111111',
    b'123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz',
    b'1cWB5HCBdLjAuqGGReWE3R3CguuwSjw6RHn39s2yuDRTS5NsBgNiFpWgAnEx6VQi8csexkgYw3mdYrMHr8x9i7aEwP8kZ7vccXWqKDvGv3u1GxFKPuAkn8JCPPGDMf3vMMnbzm6Nh9zh1gcNsMvH3ZNLmP5fSG6DGbbi2tuwMWPthr4boWwCxf7ewSgNQeacyozhKDDQQ1qL5fQFUW52QKUZDZ5fw3KXNQJMcNTcaB723LchjeKun7MuGW5qyCBZYzA1KjofN1gYBV3NqyhQJ3Ns746GNuf9N2pQPmHz4xpnSrrfCvy6TVVz5d4PdrjeshsWQwpZsZGzvbdAdN8MKV5QsBDY'
]
# All of the decoded samples are hexadecimal strings
decoded_samples = [
    '',
    '61',
    '626262',
    '636363',
    '73696d706c792061206c6f6e6720737472696e67',
    '00eb15231dfceb60925886b67d065299925915aeb172c06647',
    '516b6fcd0f',
    'bf4f89001e670274dd',
    '572e4794',
    'ecac89cad93923c02321',
    '10c8511e',
    '00000000000000000000',
    '000111d38e5fc9071ffcd20b4a763cc9ae4f252bb4e48fd66a835e252ada93ff480d6dd43dc62a641155a5',
    '000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f202122232425262728292a2b2c2d2e2f303132333435363738393a3b3c3d3e3f404142434445464748494a4b4c4d4e4f505152535455565758595a5b5c5d5e5f606162636465666768696a6b6c6d6e6f707172737475767778797a7b7c7d7e7f808182838485868788898a8b8c8d8e8f909192939495969798999a9b9c9d9e9fa0a1a2a3a4a5a6a7a8a9aaabacadaeafb0b1b2b3b4b5b6b7b8b9babbbcbdbebfc0c1c2c3c4c5c6c7c8c9cacbcccdcecfd0d1d2d3d4d5d6d7d8d9dadbdcdddedfe0e1e2e3e4e5e6e7e8e9eaebecedeeeff0f1f2f3f4f5f6f7f8f9fafbfcfdfeff',
    # The samples above this comment are all taken from the official bitcoin repository
]

def test_encode():
    global encoded_samples, decoded_samples
    for es, ds in zip(encoded_samples[:], decoded_samples[:]):
        ds = unhexlify(ds)
        assert base58.encode(ds) == es

def test_decode():
    global encoded_samples, decoded_samples
    for es, ds in zip(encoded_samples[:], decoded_samples[:]):
        assert base58.decode(es).hex() == ds

def test_encode_inverse_decode():
    global encoded_samples, decoded_samples
    for es in encoded_samples[:]:
        assert base58.encode(base58.decode(es)) == es

    for ds in decoded_samples[:]:
        ds = unhexlify(ds)
        assert base58.decode(base58.encode(ds)) == ds
