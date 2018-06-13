from util import to_str

import wallet
import time
import shelve

walletFile = 'wallets'

class WalletManager:
    class __WalletManager:
        def __init__(self):
            self.db = shelve.open(walletFile)

        def createWallet(self):
            w = wallet.newWallet()
            address = to_str(w.getAddress())
            self.db[address] = w
            return w

        def getAddresses(self):
            return [address for address in self.db]

        def getWallet(self, address):
            return self.db[to_str(address)]

    instance = None
    def __init__(self):
        if not WalletManager.instance:
            WalletManager.instance = WalletManager.__WalletManager()

    def __getattr__(self, name):
        return getattr(self.instance, name)
