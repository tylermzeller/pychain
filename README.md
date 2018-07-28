# Blockchain in Python

Learning about blockchains from [Jeiwan](https://github.com/Jeiwan/blockchain_go) and porting to Python.

## DISCLAIMER
This repository is for personal experimentation and mainly for fun (you may even find a joke or two written throughout the code!). There is no set process for testing, so code in the master branch has no guarantees of running correctly.

## Current State

  * Persistence is accomplished using the [Plyvel](https://plyvel.readthedocs.io/en/latest/index.html) library. Previously this was done using [shelve](https://docs.python.org/3/library/shelve.html). Moving from Shelve to Plyvel, we lost the convenience of letting the database handle serialization of blocks, UTXOs, and wallets. However, Plyvel should be a more robust and efficient database, giving us snapshots, sorted iterators, write batches, and more!
  * Public/Private key cryptography (verifying/signing) is accomplished through the [ecdsa](https://github.com/warner/python-ecdsa) library. See their README for security considerations.
  * Blocks only support PTPKH transactions. No scripting. Just locking and unlocking outputs.
  * P2P testing so far has been limited (only 4 peers, no bad actors).
  * Since block times are so low, the blockchain will often fork. The network handles this gracefully and always reaches consensus.
# Tests
See the [README](./pychain/tests/README.md) in the tests directory

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
It's recommended you use the provided deployment scripts
```bash
$ cd scripts
$ ./deploy_network --num-nodes=3
```

Alternatively, you can roll your own docker-compose setup.
```bash
$ docker build -t pychain .

# you will need a valid docker-compose.yml file for this to work. You can use the template in this repo as a reference.
$ docker-compose up --scale p2p=3
```


## Node CLI
The following commands can be ran on a single Pychain node.

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
{
  "hash": "000006a4c3c01d76ac261a2cd5c6ac6297b2bd4dc4984bbef91d5d9d624e6e78",
  "prevHash": "0000000000000000000000000000000000000000000000000000000000000000",
  "timestamp": 1530423399,
  "height": 0,
  "nonce": 370089,
  "merkleRoot": "af24b2c82707d87a608fe21c830a11a63960fc585816d972cc7d42725a7799ac",
  "txs": [
    {
      "id": "5fbac38f51bc0daa4b2d261a8d49a15cd8a68e4c10ab3e0c9d33093a756561b5",
      "inputs": [
        {
          "refTxId": "",
          "refOutIdx": -1,
          "signature": "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
          "pubKey": "1995389d31069c544da983a95027e9319d93cbf81fd38c3786f115f9a9938547d2df7272d1258bb3"
      }
      ],
      "outputs": [
        {
          "idx": 0,
          "value": 50,
          "pubKeyHash": "9f9a193d56e9599090417053ed6450ff93fed822"
        }
      ]
    }
  ]
}
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
