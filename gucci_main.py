#!/usr/bin/env python

import cli
from blockchain import BlockchainManager
from utxo_set import UTXOSet
from wallet_manager import WalletManager

def main():
    try:
        cli.run()
    finally:
        print("\n\nCleaning up...")
        # ecksdee U+1F602
        for bad_python_code in [UTXOSet, WalletManager, BlockchainManager]:
            try:
                bad_python_code().closeDB()
            except Exception as e:
                # Some dbs require parameters to initialize, and if the db was
                # never opened (due to an earlier exception) then
                # closing will throw an exception
                pass
        print("Cleanup done.")
if __name__=='__main__':
    main()
