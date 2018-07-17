import pychain.util as util
import pychain.wallet as wallet

from pychain.database_manager import DBManager

class WalletManager:
    def __init__(self):
        self.wallets_db = DBManager().get('wallets')

    # creates a new wallet and saves it to the database
    def create_wallet(self):
        w = wallet.Wallet()
        address = w.getAddress()
        encoded_wallet = util.encodeMsg(wallet.encodeWallet(w))
        self.wallets_db.put(address, encoded_wallet)
        return w

    def get_addresses(self):
        with self.wallets_db.snapshot() as s, s.iterator(include_value=False) as it:
            return [address for address in it]

    def get_wallet(self, address):
        if isinstance(address, str):
            address = address.encode()
        if self.wallets_db.exists(address):
            return util.decodeMsg(self.wallets_db.get(address), decoder=wallet.decodeWallet)
        return None
