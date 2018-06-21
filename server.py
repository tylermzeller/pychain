protocol = 'tcp'
nodeVersion = 1
commandLength = 12

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
