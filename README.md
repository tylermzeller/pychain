# Blockchain in Python

Learning about blockchains from [Jeiwan](https://github.com/Jeiwan/blockchain_go) and porting to Python.

## DISCLAIMER
This repository is for personal experimentation and mainly for fun (you may even find a joke or two written throughout the code!). There is no set process for testing, so code in the master branch has no guarantees of running correctly.

## Current State

  * Persistence is accomplished using the [shelve](https://docs.python.org/3/library/shelve.html) library. With this library, there is no need to serialize/unserialize blocks or UTXOs!
  * Public/Private key cryptography (verifying/signing) is accomplished through the [ecdsa](https://github.com/warner/python-ecdsa) library. See their README for security considerations.
  * Blocks only support PTPKH transactions. No scripting. Just locking and unlocking outputs.

## Quick Start

## Single Node Using Docker
```bash
$ docker build -t pychain .
...
# -it lets you input characters (CTRL-C, and 'q' to quit)
# --rm deletes the container upon exit (i.e. deleting your databases)
$ docker run -it --rm pychain
```

## P2P Network Using Docker-Compose
```bash
$ docker build -t pychain .
# So far, the only tests have been with 2 nodes on the network.
$ docker-compose up --scale p2p=2
```

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

### Join Network
#### Command:
`up`
```bash
$ ./gucci_main.py up --address 13jXEksSr4khBY1bRg4pZtWod9Z3kud26S
This node is mining and will receive rewards to 13jXEksSr4khBY1bRg4pZtWod9Z3kud26S
My host: 172.17.0.2
My mining address 13jXEksSr4khBY1bRg4pZtWod9Z3kud26S

# this message will appear if your local
# blockchain hasn't been initialized yet
Empty blockchain. Creating genesis.
Created coinbase with reward going to 13jXEksSr4khBY1bRg4pZtWod9Z3kud26S
Merkle root e477945230fb23da77b2cfc7402494368cae487bbcbebe85f3ef1bb96819e075
Gensis block hash: 00007faa2e194e877c1caf6aa853e3054ef386ce12338d04e3415381de21e157

Starting server
Press 'q' or 'CTRL-C' to quit.
```
