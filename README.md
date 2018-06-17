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
#### Command:
`create-wallet`
```bash
$ ./gucci_main.py c
New address: 17vsuqM11VJ7RYy6m6y5dZ2yk9LDMF91Wh
$ ./gucci_main.py c
New address: 1Fmjs3MCtDswPeLry1BBabFk5A1SEURc4r
```

### List Addresses
#### Command:
`list-addresses`
```bash
$ ./gucci_main.py l
1Fmjs3MCtDswPeLry1BBabFk5A1SEURc4r
17vsuqM11VJ7RYy6m6y5dZ2yk9LDMF91Wh
```

### Creating a Blockchain
#### Command:
`init-blockchain`
```bash
$ ./gucci_main.py i --address 1Fmjs3MCtDswPeLry1BBabFk5A1SEURc4r

Done
```

### Printing the Blockchain
#### Command:
`print-blockchain`
```bash
$ ./gucci_main.py p
<block hash=00004a43389100408a3a3566c4d15ae57874e2986a84d46902a43fb4b52212d5>
  <prevHash>0000000000000000000000000000000000000000000000000000000000000000</prevHash>
  <proof>True</proof>
  <tx id=e2b37d8533f7ef6b4d4690055c8e558373c9a261629bff9c6591c7a1e52e5ab9>
    <input i=0>
      <outputID></outputID>
      <outIdx>-1</outIdx>
      <signature>00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000</signature>
      <pubKey>5050ca76ff36437d2c163d0654f9293cffd3533ce2bff115cfaae3895cf102095827b24c7cc55652</pubkey>
    </input>
    <output i=0>
      <value>50</value>
      <pubKeyHash>a207d7e452a061b175a908de217b58e35230d92d</pubKeyHash>
    </output>
  </tx>
</block>
```

### Get Wallet balance
#### Command:
`get-balance`
```bash
$ ./gucci_main.py g --address 1Fmjs3MCtDswPeLry1BBabFk5A1SEURc4r
Balance of '1Fmjs3MCtDswPeLry1BBabFk5A1SEURc4r': 50
```

### Send Coins
#### Command:
`send`
```bash
# cannot send more than you have
$ ./gucci_main.py s --from 1Fmjs3MCtDswPeLry1BBabFk5A1SEURc4r --to 17vsuqM11VJ7RYy6m6y5dZ2yk9LDMF91Wh --amount 51
Not enough funds!

# for now, the sender mines the coinbase reward
$ ./gucci_main.py s --from 1Fmjs3MCtDswPeLry1BBabFk5A1SEURc4r --to 17vsuqM11VJ7RYy6m6y5dZ2yk9LDMF91Wh --amount 50

Success!

# sender sent all 50 of his coins, then received the 50 miner reward
$ ./gucci_main.py g --address 1Fmjs3MCtDswPeLry1BBabFk5A1SEURc4r
Balance of '1Fmjs3MCtDswPeLry1BBabFk5A1SEURc4r': 50

# sendee has all 50 of the sender's coins
$ ./gucci_main.py g --address 17vsuqM11VJ7RYy6m6y5dZ2yk9LDMF91Wh
Balance of '17vsuqM11VJ7RYy6m6y5dZ2yk9LDMF91Wh': 50
```
