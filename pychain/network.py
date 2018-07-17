import pychain.base58 as base58
import pychain.p2p_interface as p2p
import pychain.transaction as transaction

from pychain.async_server import AsyncServer
from pychain.block import encodeBlock, decodeBlock
from pychain.blockchain import Blockchain
from pychain.node_discovery import discoverNodes
from pychain.util import encodeMsg, decodeMsg, waitKey, canWaitKey, toStr
from pychain.utxo_set import UTXOSet
from pychain.wallet_manager import WalletManager

import random
from socket import gethostname, gethostbyname
from struct import pack

nodeVersion = 1
nodeAddress = gethostbyname(gethostname())
miningAddress = b''
knownNodes = []
blocksInTransit = {}
mempool = {}

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
        if txID not in mempool:
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
        if txID not in mempool: return

        sendTX(getdata['addrFrom'], mempool[txID])

def handleTX(msg):
    # print("Handling tx")
    txMsg = decodeMsg(msg)
    tx = transaction.decodeTX(txMsg['tx'])

    # old news
    if tx.id in mempool: return
    mempool[tx.id] = tx
    print("Added tx %s" % tx.id.hex())

    # broadcast the new TX to all nodes.
    # This will not cause an infinite broadcast loop,
    # because only txs nodes haven't seen get broadcast
    broadcast_tx(tx, exclude=[txMsg['addrFrom']])

    # NOTE: We DON'T want to mine blocks in the server's thread!
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

def mine_transactions():
    global miningAddress
    print("Attempting to mine new block")
    txs = [tx for tx in mempool.values() if tx.verify()]

    if len(txs) == 0:
        print("All transactions were invalid! Waiting for more...")
        return

    fees = transaction.calcFees(txs)
    print("fees = %2.3f" % fees)
    cb = transaction.newCoinbaseTX(miningAddress, fees=fees)
    txs.append(cb)
    new_block = Blockchain().mineBlock(txs)
    UTXOSet().reindex()

    for tx in txs:
        if tx.id in mempool:
            print("deleting tx %s from mempool" % tx.id.hex())
            del mempool[tx.id]

    broadcast_block(new_block)

    # if len(mempool) > 0:
    #     mine_transactions()

def broadcast_block(new_block, exclude=[]):
    global nodeAddress
    #print("Broadcasting block %s" % new_block.hash.hex())
    for node in knownNodes:
        if node != nodeAddress and not node in exclude:
            sendInv(node, b'block', [new_block.hash])

def broadcast_tx(new_tx, exclude=[]):
    global nodeAddress
    #print("Broadcasting tx %s" % new_tx.id.hex())
    for node in knownNodes:
        if node != nodeAddress and not node in exclude:
            sendInv(node, b'tx', [new_tx.id])

def create_random_tx():
    print("creating random tx")
    wm = WalletManager()
    addresses = wm.get_addresses()
    while len(addresses) < 10:
        w = wm.create_wallet()
        addresses.append(w.getAddress())
        print("Creating a new wallet %s" % toStr(w.getAddress()))

    random.shuffle(addresses)
    frum = b''
    us = UTXOSet()
    for address in addresses:
        pubKeyHash = base58.decode(address)[1:-4]
        balance = sum([out.value for out in us.findUTXO(pubKeyHash)])
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
    tx = transaction.newUTXOTransaction(frum, to, balance / 2)
    return tx

def startServer(mineAddr):
    import time
    global miningAddress
    global knownNodes
    print("My host: %s" % nodeAddress)
    miningAddress = mineAddr
    print("My mining address %s" % toStr(miningAddress))

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
        print("Height time = %f" % (time.time() - start))
        # generate empty blocks to seed the miner's wallets
        if bestHeight < 5:
            new_block = bc.mineBlock([transaction.newCoinbaseTX(miningAddress)])
            UTXOSet().reindex()
            broadcast_block(new_block)
        # for blocks 5-10, generate random txs. These will get broadcast
        # across the network (randomly) and eventually fill the mempoolself.
        # A full mempool will trigger the mining of a new block.
        elif bestHeight < 10:
            # Unpredictably produce transactions
            x = random.randint(0, 5e6)
            if x < 1000:
                rand_tx = create_random_tx()
                if rand_tx:
                    mempool[rand_tx.id] = rand_tx
                    broadcast_tx(rand_tx)

            # NOTE: We DO want to mine blocks in the miner's thread
            if len(mempool) >= 2 and len(miningAddress) > 0:
                print("mempool full, mining txs")
                mine_transactions()
        else:
            sr.stop()
            break

        # writing the loop this way supports
        # attaching/detaching tty terminals (e.g. via Docker)
        # if canWaitKey():
        #     print("Press 'q' or 'CTRL-C' to quit.")
        #     done = waitKey() in ['q', 'SIGINT']
