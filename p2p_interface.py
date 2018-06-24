from async_server import AsyncServer
from util import decodeMsg

from struct import pack, unpack

nodeVersion = 1
commandLen = 12

class addr:
    def __init__(self, addrList):
        self.addrList = addrList

class block:
    def __init__(self, addrFrom, block):
        self.addrFrom = addrFrom
        self.block = block

class getblocks:
    def __init__(self, addrFrom):
        self.addrFrom = addrFrom

class getdata:
    def __init__(self, typ, id):
        self.addrFrom = addrFrom
        self.type = typ
        self.id = id

class inv:
    def __init__(self, addrFrom, typ, items):
        self.addrFrom = addrFrom
        self.type = typ
        self.items = items

class tx:
    def __init__(self, addrFrom, transaction):
        self.addrFrom = addrFrom
        self.transaction = transaction

class version:
    def __init__(self, addrFrom, version, bestHeight):
        self.addrFrom = addrFrom
        self.version = version
        self.bestHeight = bestHeight

def readMsg(sock):
    def recvall(sock, n):
        data = b''
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet: return None
            data += packet
        return data

    # read the 4 byte msg length
    msglen = recvall(sock, 4)
    if not msglen: # invalid msg
        sock.close()
        return None

    msglen = unpack('>I', msglen)[0]
    print("Receiving a message of length %d" % msglen)
    return recvall(sock, msglen)

def getCommand(msg):
    command = b''
    for i, c in enumerate(msg):
        if c == b'\x00': break
        command += c
    return command

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
    'addr':         handleAddr,
    'block':        handleBlock,
    'inv':          handleInv,
    'getblocks':    handleGetBlocks,
    'getdata':      handleGetData,
    'tx':           handleTX,
    'version':      handleVersion
}

class SocketReader:
    def __init__(self, host='localhost', port=7667):
        self.server = AsyncServer(host, port)
        self.server.set_read_handler(self.handleRead)

    def handleRead(self, sock):
        msg = readMsg(sock)
        if not msg:
            sock.close()
            return

        command = getCommand(msg[:commandLen])

        if command in msgHandlers:
            msgHandlers[command](msg[commandLen:])
        else:
            print('Unknown command!')

        sock.close()
