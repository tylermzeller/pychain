# Blockchain in Python

Learning about blockchains from [Jeiwan](https://github.com/Jeiwan/blockchain_go) and porting to Python.

## Current State

  * Persistence is accomplished using the [shelve](https://docs.python.org/3/library/shelve.html) library.
  * Public/Private key cryptography (verifying/signing) is accomplished through the [ecdsa](https://github.com/warner/python-ecdsa) library. See their README for security considerations.
  * Blocks only support PTPKH transactions. No scripting. Just locking and unlocking outputs.


## TODO
  * Transaction Mempool
  * Networking

## Quick Start

### Creating Wallets
Command: `create-wallet`
```bash
$ ./gucci_main.py c
New address: 1BRRYXYbCMxZ3sJAZjKYkFiTkLjRus51wY
$ ./gucci_main.py c
New address: 12JShnTCMeqib8ezHcdPotTSxaSwJqauMn
```

### Creating a Blockchain
#### Command:
`init-blockchain`
```bash
$ ./gucci_main.py i --address 1BRRYXYbCMxZ3sJAZjKYkFiTkLjRus51wY

Done
```

### Printing the Blockchain
#### Command:
`print-blockchain`
```bash
$ ./gucci_main.py p
******* Block 000000f9acec4af7e34e14450f3077c2491bab5a2c4c674341a939e29f350f76 *******
Prev. Hash:   0000000000000000000000000000000000000000000000000000000000000000
PoW:          True
```

### Get Wallet balance
### Command:
`get-balance`
```bash
$ ./gucci_main.py g --address 1BRRYXYbCMxZ3sJAZjKYkFiTkLjRus51wY
```
