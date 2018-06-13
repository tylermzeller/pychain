# Blockchain in Python

Learning about blockchains from [Jeiwan](https://github.com/Jeiwan/blockchain_go) and porting to Python.

## Current State

  * Persistence is accomplished using the [shelve](https://docs.python.org/3/library/shelve.html) library.
  * Public/Private key cryptography (verifying/signing) is accomplished through the [ecdsa](https://github.com/warner/python-ecdsa) library. See their README for security considerations.
  * Blocks only support PTPKH transactions. No scripting. Just locking and unlocking outputs.


## TODO
  * Block mining
    - Mining Rewards
    - Transaction Mempool
  * Networking

## Quick Start

### Creating wallets
Command: `cw` or `createwallet`
```bash
$ python gucci_main.py cw
New address: 1BRRYXYbCMxZ3sJAZjKYkFiTkLjRus51wY
$ python gucci_main.py cw
New address: 12JShnTCMeqib8ezHcdPotTSxaSwJqauMn
```

### Creating a Blockchain
#### Command:
`nbc`, `newchain`, or `newblockchain`
```bash
$ python gucci_main.py nbc --address 1BRRYXYbCMxZ3sJAZjKYkFiTkLjRus51wY

Done
```

### Printing the Blockchain
#### Command:
`print`, `newchain`, or `newblockchain`
```bash
$ python gucci_main.py print
******* Block 000000f9acec4af7e34e14450f3077c2491bab5a2c4c674341a939e29f350f76 *******
Prev. Hash:   0000000000000000000000000000000000000000000000000000000000000000
PoW:          True
```
