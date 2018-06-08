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
