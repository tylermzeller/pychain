import node_discovery
import p2p_interface as p2p
from async_server import AsyncServer
from block import encodeBlock, decodeBlock
from blockchain import Blockchain, BlockchainManager
from node_discovery import discoverNodes
from transaction import encodeTX, decodeTX, newCoinbaseTX
from util import encodeMsg, decodeMsg, waitKey, canWaitKey, toStr
from utxo_set import UTXOSet

from socket import gethostname, gethostbyname
from struct import pack

nodeVersion = 1
nodeAddress = nodeAddress = gethostbyname(gethostname())
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
    sock = p2p.SocketWriter(address, port)
    if sock.isConnected():
        sock.send(payload)

def sendAddr(address):
    print("Sending addr to %s" % address)
    command = b'addr'
    addresses = p2p.addr([*knownNodes, nodeAddress])
    sendPayload(address, command, addresses)

def broadcastBlock(block):
    print("Broadcasting block")
    for address in knownNodes:
        sendBlock(address, block)

def sendBlock(address, block):
    print("Sending block to %s" % address)
    command = b'block'
    blck = p2p.block(nodeAddress, encodeBlock(block))
    sendPayload(address, command, blck)

def sendInv(address, typ, items):
    print("Sending inv to %s" % address)
    command = b'inv'
    inv = p2p.inv(nodeAddress, typ, items)
    sendPayload(address, command, inv)

def sendGetBlocks(address):
    print("Sending getblocks to %s" % address)
    command = b'getblocks'
    getblocks = p2p.getblocks(nodeAddress)
    sendPayload(address, command, getblocks)

def sendGetData(address, typ, id):
    print("Sending getdata to %s" % address)
    command = b'getdata'
    getdata = p2p.getdata(nodeAddress, typ, id)
    sendPayload(address, command, getdata)

def sendTX(address, tx):
    print("Sending tx to %s" % address)
    command = b'tx'
    x = p2p.tx(nodeAddress, encodeTX(tx))
    sendPayload(address, command, x)

def sendVersion(address):
    print("Sending version")
    command = b'version'
    version = p2p.version(nodeAddress, nodeVersion, Blockchain().getBestHeight())
    sendPayload(address, command, version)

def requestBlocks():
    print("Broadcasting a request for blocks")
    for address in knownNodes:
        print(address)
        sendGetBlocks(address)

def mineTransactions():
    print("Attempting to mine new block")
    txs = [tx for tx in mempool.values() if tx.verify()]

    # NOTE: for testing, I'm letting the miners simply mine empty blocks
    #if len(txs) == 0:
        #print("All transactions were invalid! Waiting for more...")
        #return

    cb = newCoinbaseTX(miningAddress)
    txs.append(cb)
    newBlock = Blockchain().mineBlock(txs)
    UTXOSet().reindex()

    print("Mined a new block %s" % newBlock.hash.hex())

    for tx in txs:
        if tx.id in mempool:
            del mempool[tx.id]

    for node in knownNodes:
        if node != nodeAddress:
            sendInv(node, b'block', [newBlock.hash])

    if len(mempool) > 0:
        mineTransactions()

def handleAddr(msg):
    print("Handling addr")
    addresses = decodeMsg(msg)
    knownNodes.extend(addresses['addrList'])
    print("There are now %d peers" % len(knownNodes))
    requestBlocks()

def handleBlock(msg):
    print("Handling block")
    blc = decodeMsg(msg)
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
    print("Handling inv")
    inv = decodeMsg(msg)
    print("Received inv with %d %ss" % (len(inv['items']), toStr(inv['type'])))

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
    print("Handling getblocks")
    getblocks = decodeMsg(msg)
    sendInv(getblocks['addrFrom'], b'block', Blockchain().getBlockHashes())

def handleGetData(msg):
    print("Handling getdata")
    getdata = decodeMsg(msg)

    if getdata['type'] == b'block':
        block = Blockchain().getBlock(getdata['id'])
        if not block: return

        sendBlock(getdata['addrFrom'], block)

    elif getdata['type'] == b'tx':
        txID = getdata['id']
        if txID not in mempool: return

        sendTX(getdata['addrFrom'], mempool[txID])

def handleTX(msg):
    print("Handling tx")
    txMsg = decodeMsg(msg)
    tx = decodeTX(tx['tx'])

    # old news
    if tx.id in mempool: return
    mempool[tx.id] = tx

    # broadcast the new TX to all nodes.
    # This will not cause an infinite broadcast loop,
    # because only new transactions get broadcast
    for node in knownNodes:
        if node != nodeAddress and node != txMsg['addrFrom']:
            sendInv(node, b'tx', [tx.id])

    if len(mempool) >= 2 and len(miningAddress) > 0:
        mineTransactions()

def handleVersion(msg):
    print("Handling version")
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

def startServer(mineAddr):
    global miningAddress
    print("My host: %s" % nodeAddress)
    miningAddress = mineAddr
    print("My mining address %s" % toStr(miningAddress))

    nodes = discoverNodes()
    for name in nodes:
        address = gethostbyname(name)
        if address != nodeAddress:
            knownNodes.append(address)

    print("Known nodes: %s" % str(knownNodes))

    # We want blocks to be mined before starting the server
    Blockchain(miningAddress)

    sr = p2p.SocketReader(nodeAddress)
    sr.setMsgHandlers(msgHandlers)
    sr.start()

    requestBlocks()

    done = False
    while not done:
        mineTransactions()
        # writing the loop this way supports
        # attaching/detaching tty terminals (e.g. via Docker)
        # if canWaitKey():
        #     print("Press 'q' or 'CTRL-C' to quit.")
        #     done = waitKey() in ['q', 'SIGINT']
