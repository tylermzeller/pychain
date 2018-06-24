import p2p_interface as p2p
from async_server import AsyncServer
from block import encodeBlock
from blockchain import Blockchain
from transaction import encodeTX
from util import encodeMsg

from struct import pack

nodeVersion = 1
nodeAddress = ''
knownNodes = []
blocksInTransit = []
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

def sendTX(address, tx):
    command = b'tx'
    x = p2p.tx(nodeAddress, encodeTX(tx))
    sendPayload(address, command, x)

def sendVersion(address):
    command = b'version'
    version = p2p.version(nodeAddress, nodeVersion, Blockchain().getBestHeight())
    sendPayload(address, command, version)

def handleAddr(msg):
    pass

def handleBlock(msg):
    pass

def handleInv(msg):
    pass

def handleGetBlocks(msg):
    pass

def handleGetData(msg):
    pass

def handleTX(msg):
    pass

def handleVersion(msg):
    pass

msgHandlers = {
    b'addr':         handleAddr,
    b'block':        handleBlock,
    b'inv':          handleInv,
    b'getblocks':    handleGetBlocks,
    b'getdata':      handleGetData,
    b'tx':           handleTX,
    b'version':      handleVersion
}
