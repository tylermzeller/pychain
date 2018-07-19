import pychain.base58 as base58
import pychain.miner as miner
import pychain.p2p_interface as p2p
import pychain.transaction as transaction

from pychain.async_server import AsyncServer
from pychain.block import encodeBlock, decodeBlock
from pychain.blockchain import Blockchain
from pychain.block_explorer import BlockExplorer
from pychain.miner import Miner
from pychain.node_discovery import discoverNodes
from pychain.util import encodeMsg, decodeMsg, waitKey, canWaitKey, toStr
from pychain.utxo_set import UTXOSet
from pychain.wallet_manager import WalletManager

import random
import time
from socket import gethostname, gethostbyname
from struct import pack

nodeVersion = 1
nodeAddress = gethostbyname(gethostname())
miner = None
knownNodes = []
blocksInTransit = {}

def sendPayload(address, command, payload):
    command = p2p.formatCommand(command)
    payload = command + encodeMsg(payload)
    payload = pack('>I', len(payload)) + payload
    port = 7667
    if ':' in address:
        [address, port] = address.split(':')
        port = int(port)
    sock = p2p.SocketWriter(address, port)
    if sock.isConnected():
        sock.send(payload)


def sendAddr(address):
    # print("Sending addr to %s" % address)
    command = b'addr'
    addresses = p2p.addr([*knownNodes, nodeAddress])
    sendPayload(address, command, addresses)

def sendBlock(address, block):
    print("Sending block %s to %s" % (block.hash.hex(), address))
    command = b'block'
    blck = p2p.block(nodeAddress, encodeBlock(block))
    sendPayload(address, command, blck)

def sendInv(address, typ, items):
    # print("Sending inv to %s" % address)
    command = b'inv'
    inv = p2p.inv(nodeAddress, typ, items)
    sendPayload(address, command, inv)

def sendGetBlocks(address):
    # print("Sending getblocks to %s" % address)
    command = b'getblocks'
    getblocks = p2p.getblocks(nodeAddress)
    sendPayload(address, command, getblocks)

def sendGetData(address, typ, id):
    # print("Sending getdata of type %s to %s" % (toStr(typ), address))
    command = b'getdata'
    getdata = p2p.getdata(nodeAddress, typ, id)
    sendPayload(address, command, getdata)

def sendTX(address, tx):
    print("Sending tx %s to %s" % (tx.id.hex(), address))
    command = b'tx'
    x = p2p.tx(nodeAddress, transaction.encodeTX(tx))
    sendPayload(address, command, x)

def sendVersion(address):
    # print("Sending version")
    command = b'version'
    version = p2p.version(nodeAddress, nodeVersion, Blockchain().getBestHeight())
    sendPayload(address, command, version)

def requestBlocks():
    # print("Broadcasting a request for blocks")
    for address in knownNodes:
        print(address)
        sendGetBlocks(address)

def handleAddr(msg):
    # print("Handling addr")
    addresses = decodeMsg(msg)
    knownNodes.extend(addresses['addrList'])
    print("There are now %d peers" % len(knownNodes))
    requestBlocks()

def handleBlock(msg):
    blc = decodeMsg(msg)
    # print("Handling block from %s" % blc['addrFrom'])
    block = decodeBlock(blc['block'])
    addrFrom = blc['addrFrom']

    if addrFrom in blocksInTransit:
        try:
            blocksInTransit[addrFrom].remove(block.hash)
        except ValueError:
            print("Got block that wasn't requested.")
            return
    else:
        print("Got block that wasn't requested")
        return

    Blockchain().addBlock(block)
    print("Added block %s" % block.hash.hex())

    if len(blocksInTransit[addrFrom]) > 0:
        sendGetData(addrFrom, b'block', blocksInTransit[addrFrom][0])
    else:
        del blocksInTransit[addrFrom]
        UTXOSet().reindex()


def handleInv(msg):
    inv = decodeMsg(msg)
    # print("Handling inv with %d %ss from %s" % (len(inv['items']), toStr(inv['type']), inv['addrFrom']))

    if len(inv['items']) == 0: return

    if inv['type'] == b'block':
        addrFrom = inv['addrFrom']
        if addrFrom not in blocksInTransit:
            blocksInTransit[addrFrom] = []
        blocksInTransit[addrFrom].extend(inv['items'])
        hash = inv['items'][0]
        sendGetData(addrFrom, b'block', hash)
    elif inv['type'] == b'tx':
        txID = inv['items'][0]
        if txID not in miner.mempool:
            sendGetData(inv['addrFrom'], b'tx', txID)


def handleGetBlocks(msg):
    getblocks = decodeMsg(msg)
    # print("Handling getblocks from %s" % getblocks['addrFrom'])
    sendInv(getblocks['addrFrom'], b'block', Blockchain().getBlockHashes())

def handleGetData(msg):
    getdata = decodeMsg(msg)
    # print("Handling getdata from %s" % getdata['addrFrom'])

    if getdata['type'] == b'block':
        block = Blockchain().getBlock(getdata['id'])
        if not block: return

        sendBlock(getdata['addrFrom'], block)

    elif getdata['type'] == b'tx':
        txID = getdata['id']
        if txID not in miner.mempool: return

        sendTX(getdata['addrFrom'], miner.mempool[txID])

def handleTX(msg):
    # print("Handling tx")
    txMsg = decodeMsg(msg)
    tx = transaction.decodeTX(txMsg['tx'])
    miner.add_txs([tx])

    # broadcast the new TX to all nodes.
    # NOTE: This will not cause an infinite broadcast loop,
    # because only txs nodes haven't seen get broadcast
    broadcast_tx(tx, exclude=[txMsg['addrFrom']])

    # NOTE: We DON'T want to mine blocks in the server's thread
    # [Keep for reference]
    # if len(mempool) >= 2 and len(miningAddress) > 0:
    #     mine_transactions()

def handleVersion(msg):
    # print("Handling version")
    version = decodeMsg(msg)
    print(version)
    localBestHeight = Blockchain().getBestHeight()
    remoteBestHeight = version['bestHeight']
    if localBestHeight < remoteBestHeight:
        sendGetBlocks(version['addrFrom'])
    elif localBestHeight > remoteBestHeight:
        sendVersion(version['addrFrom'])

    if version['addrFrom'] not in knownNodes:
        knownNodes.append(version['addrFrom'])
        sendAddr(version['addrFrom'])

msgHandlers = {
    b'addr':         handleAddr,
    b'block':        handleBlock,
    b'inv':          handleInv,
    b'getblocks':    handleGetBlocks,
    b'getdata':      handleGetData,
    b'tx':           handleTX,
    b'version':      handleVersion
}

def broadcast_block(new_block, exclude=[]):
    global nodeAddress
    for node in knownNodes:
        if node != nodeAddress and not node in exclude:
            sendInv(node, b'block', [new_block.hash])

def broadcast_tx(new_tx, exclude=[]):
    global nodeAddress
    for node in knownNodes:
        if node != nodeAddress and not node in exclude:
            sendInv(node, b'tx', [new_tx.id])

def create_random_tx():
    wm = WalletManager()
    addresses = wm.get_addresses()
    while len(addresses) < 10:
        w = wm.create_wallet()
        addresses.append(w.get_address())
        print("Creating a new wallet %s" % toStr(w.get_address()))

    random.shuffle(addresses)
    frum = b''
    us = UTXOSet()
    for address in addresses:
        balance = us.get_balance(address=address)
        if balance > 0:
            frum = address
            break

    if not frum:
        print("Found no wallets with a balance > 0")
        return None

    random.shuffle(addresses)
    to = addresses[0]
    if to == frum: to = addresses[1]

    print("Making a random tx of %2.3f from %s to %s" % (balance / 2, toStr(frum), toStr(to)))
    sender_wallet = wm.get_wallet(frum)
    tx = sender_wallet.create_tx(to, balance / 2, us)
    return tx

def startServer(mineAddr):
    global knownNodes, miner
    print("My host: %s" % nodeAddress)
    miner = Miner(mineAddr)

    print("My mining address %s" % toStr(miner.address))

    nodes = discoverNodes()
    for name in nodes:
        address = gethostbyname(name)
        if address != nodeAddress:
            knownNodes.append(address)

    print("Known nodes: %s" % str(knownNodes))

    sr = p2p.SocketReader(nodeAddress)
    sr.setMsgHandlers(msgHandlers)
    sr.start()
    bc = Blockchain()

    #done = False
    #while not done:
    while 1:
        start = time.time()
        bestHeight = bc.getBestHeight()
        # generate empty blocks to seed the miners' wallets
        if bestHeight < 5:
            new_block = miner.mine_block()
            broadcast_block(new_block)
        # for blocks 5-10, generate random txs. These will get broadcast
        # across the network (randomly) and eventually fill the mempool.
        # A full mempool will trigger the mining of a new block.
        elif bestHeight < 10:
            if bestHeight == 5:
                print("My balance after 5 blocks: %3.3f" % UTXOSet().get_balance(address=miner.address))
            # Produce a tx every ~2-3 seconds
            time.sleep(random.random() + 2)
            rand_tx = create_random_tx()
            if rand_tx:
                miner.add_txs([rand_tx])
                broadcast_tx(rand_tx)

            # NOTE: We DO want to mine blocks in the miner's thread
            if len(miner.mempool) >= 2:
                time.sleep(0.5)
                print("mempool full, mining txs")
                new_block = miner.mine_transactions()
                broadcast_block(new_block)
        else:
            balance = UTXOSet().get_balance(address=miner.address)
            print("My balance: %3.3f" % balance)
            # pubKeyHash = base58.decode(miner.address)[1:-4]
            # print("My unspent outputs from UTXOSet:")
            # for txOutput in UTXOSet().findUTXO(pubKeyHash):
            #     print(txOutput.toDict())
            #
            # print("My unspent outputs from BlockExplorer:")
            # for txId, txOutputs in BlockExplorer().findUTXO().items():
            #     for txOutput in txOutputs:
            #         if txOutput.isLockedWithKey(pubKeyHash):
            #             print("TXID: %s" % txId.hex())
            #             print(txOutput.toDict())
            sr.stop()
            break

        # writing the loop this way supports
        # attaching/detaching tty terminals (e.g. via Docker)
        # if canWaitKey():
        #     print("Press 'q' or 'CTRL-C' to quit.")
        #     done = waitKey() in ['q', 'SIGINT']
