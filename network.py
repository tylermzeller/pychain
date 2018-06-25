import p2p_interface as p2p
from async_server import AsyncServer
from block import encodeBlock, decodeBlock
from blockchain import Blockchain
from transaction import encodeTX, decodeTX, newCoinbaseTX
from util import encodeMsg, decodeMsg, waitKey
from utxo_set import UTXOSet

from socket import gethostname, gethostbyname
from struct import pack

nodeVersion = 1
nodeAddress = ''
miningAddress = ''
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
    command = b'addr'
    addresses = p2p.addr([*knownNodes, nodeAddress])
    sendPayload(address, command, addresses)

def sendBlock(address, block):
    command = b'block'
    blck = p2p.block(nodeAddress, encodeBlock(block))
    sendPayload(address, command, blck)

def sendInv(address, typ, items):
    command = b'inv'
    inv = p2p.inv(nodeAddress, typ, items)
    sendPayload(address, command, inv)

def sendGetBlocks(address):
    command = b'getblocks'
    getblocks = p2p.getblocks(nodeAddress)
    sendPayload(address, command, getblocks)

def sendGetData(address, typ, id):
    command = b'getdata'
    getdata = p2p.getdata(nodeAddress, typ, id)
    sendPayload(address, command, getdata)

def sendTX(address, tx):
    command = b'tx'
    x = p2p.tx(nodeAddress, encodeTX(tx))
    sendPayload(address, command, x)

def sendVersion(address):
    command = b'version'
    version = p2p.version(nodeAddress, nodeVersion, Blockchain().getBestHeight())
    sendPayload(address, command, version)

def requestBlocks():
    pass

def mineTransactions():
    print("Attempting to mine new block")
    bc = Blockchain()
    txs = [tx for tx in mempool.values() if tx.verify()]

    if len(txs) == 0:
        print("All transactions were invalid! Waiting for more...")
        return

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
    addresses = decodeMsg(msg)
    knownNodes.extend(addresses['addrList'])
    print("There are now %d peers" % len(knownNodes))
    requestBlocks()

def handleBlock(msg):
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
    inv = decodeMsg(msg)
    print("Received inventory with %d %ss" % (len(inv['items']), inv['type']))

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
    sendInv(getblocks['addrFrom'], b'block', Blockchain().getBlockHashes())

def handleGetData(msg):
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

    if len(mempool) >= 2 && len(miningAddress) > 0:
        mineTransactions()

def handleVersion(msg):
    version = decodeMsg(msg)
    localBestHeight = Blockchain().getBestHeight()
    remoteBestHeight = version['bestHeight']
    if myBestHeight < remoteBestHeight:
        sendGetBlocks(version['addrFrom'])
    elif myBestHeight > remoteBestHeight:
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
    nodeAddress = gethostbyname(gethostname())
    miningAddress = mineAddr

    # create blockchain if not already created
    Blockchain(mineAddr)

    sr = p2p.SocketReader(nodeAddress)
    sr.setMsgHandlers(msgHandlers)
    sr.start()

    print("Press 'q' or 'CTRL-C' to quit.")
    while waitKey() not in ['q', 'SIGINT']:
        print("Press 'q' or 'CTRL-C' to quit.")
