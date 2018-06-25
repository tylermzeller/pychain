from async_server import AsyncServer
from util import decodeMsg

import socket
from struct import pack, unpack

nodeVersion = 1
commandLen = 12

def addr(addrList):
    return {
        'addrList': addrList
    }

def block(addrFrom, block):
    return {
        'addrFrom': addrFrom,
        'block': block
    }

def getblocks(addrFrom):
    return {
        'addrFrom': addrFrom
    }

def getdata(addrFrom, typ, id):
    return {
        'addrFrom': addrFrom,
        'type':     typ,
        'id':       id,
    }

def inv(addrFrom, typ, items):
    return {
        'addrFrom': addrFrom,
        'type':     typ,
        'items':    items,
    }

def tx(addrFrom, transaction):
    return {
        'addrFrom': addrFrom,
        'tx':       transaction,
    }

def version(addrFrom, version, bestHeight):
    return {
        'addrFrom':     addrFrom,
        'version':      versioned,
        'bestHeight':   bestHeight
    }

# https://stackoverflow.com/questions/17667903/python-socket-receive-large-amount-of-data
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

def formatCommand(command):
    if len(command) > commandLen:
        command = command[:commandLen]
    zlen = commandLen - len(command)
    return command + (zlen * b'\x00')

def getCommand(msg):
    command = b''
    for i, c in enumerate(msg):
        if c == b'\x00': break
        command += c
    return command

class SocketReader:
    def __init__(self, host='localhost', port=7667):
        self.server = AsyncServer(host, port)
        self.server.set_read_handler(self.handleRead)

    def setMsgHandlers(self, msgHandlers):
        if isinstance(msgHandlers, dict):
            self.msgHandlers = msgHandlers

    def start(self):
        self.server.start()

    # If you want to close a connection, use sock.close()
    def stop(self):
        self.server.stop()

    def handleRead(self, sock):
        msg = readMsg(sock)
        if not msg:
            sock.close()
            return

        command = getCommand(msg[:commandLen])

        if command in msgHandlers:
            self.msgHandlers[command](msg[commandLen:])
        else:
            print('Unknown command!')

        sock.close()

class SocketWriter:
    def __init__(self, host='localhost', port=7667):
        try:
            self.sock = socket.create_connection((host, port), timeout=1)
        except socket.error as err:
            if isinstance(err, tuple):
                print("Error %d: %s", % err)
            else:
                print("Error: %s", % err)
            self.sock = None

    def isConnected(self):
        return self.sock is not None

    def send(self, data):
        self.sock.sendall(data)
        self.sock.close()
