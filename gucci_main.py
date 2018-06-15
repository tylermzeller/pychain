import cli
from blockchain import BlockchainManager
from utxo_set import UTXOSet
from wallet_manager import WalletManager

def main():
    try:
        cli.run()
    finally:
        print("Cleaning up...")
        # ecksdee U+1F602
        for bad_python_code in [UTXOSet, WalletManager, BlockchainManager]:
            bad_python_code().closeDB()
        print("Cleanup done.")
if __name__=='__main__':
    main()
