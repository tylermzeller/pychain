from pychain.async_server import AsyncServer
from pychain.util import encodeMsg, decodeMsg, intToBytes

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
        'version':      nodeVersion,
        'bestHeight':   bestHeight
    }

# https://stackoverflow.com/questions/17667903/python-socket-receive-large-amount-of-data
def readMsg(sock):
    def recvall(sock, n):
        data = b''
        while len(data) < n:
            packetlen = n - len(data)
            if packetlen > 4096:
                packetlen = 4096
            packet = sock.recv(packetlen)
            if not packet: break
            data += packet
        return data

    # read the 4 byte msg length
    msglen = recvall(sock, 4)
    if not msglen: # invalid msg
        print("No msglen")
        sock.close()
        return None

    msglen = unpack('>I', msglen)[0]
    # print("Receiving a message of length %d" % msglen)
    return recvall(sock, msglen)

def formatCommand(command):
    if len(command) > commandLen:
        command = command[:commandLen]
    zlen = commandLen - len(command)
    return command + (zlen * b'\x00')

def getCommand(msg):
    command = b''
    for i, byte in enumerate(msg):
        c = intToBytes(byte)
        if c == b'\x00': break
        command += c
    return command

class SocketReader:
    def __init__(self, host='localhost', port=7667):
        self.server = AsyncServer(host, port)
        self.server.setReadHandler(self.handle_read)

    def setMsgHandlers(self, msgHandlers):
        if isinstance(msgHandlers, dict):
            self.msgHandlers = msgHandlers

    def start(self):
        print("Starting server")
        self.server.start()

    def stop(self):
        print("Stopping server")
        self.server.stop()

    def handle_read(self, sock):
        msg = readMsg(sock)
        if not msg:
            print("Found no data")
            sock.handle_close()
            return

        command = getCommand(msg[:commandLen])

        if command in self.msgHandlers:
            self.msgHandlers[command](msg[commandLen:])
        elif command == b'ping':
            pong = pack('>I', len(payload)) + b'pong'
            sock.send(pong)
        else:
            print('Msg contained unknown command')

        sock.handle_close()

class SocketWriter:
    def __init__(self, host='localhost', port=7667):
        try:
            self.sock = socket.create_connection((host, port), timeout=1)
        except socket.error as err:
            if isinstance(err, tuple):
                print("Error %d: %s" % err)
            else:
                print("Error: %s" % err)
            self.sock = None

    def isConnected(self):
        return self.sock is not None

    def send(self, data):
        error = False
        try:
            self.sock.sendall(data)
        except socket.timeout:
            print("Caught timeout")
            error = True
            self.sock.shutdown("SHUT_RDWR")
        except socket.error as err:
            print("Error %d: %s" % err)
            error = True
            self.sock.shutdown("SHUT_RDWR")
        self.sock.close()
        return error
