#!/usr/bin/env python

import cli
from database_manager import DBManager

def main():
    try:
        cli.run()
    finally:
        print("\n\nCleaning up...")
        DBManager().close()
        print("Cleanup done.")
if __name__=='__main__':
    main()
