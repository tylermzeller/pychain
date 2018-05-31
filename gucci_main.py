import blockchain
import cli

def main():
    bc = blockchain.newBlockchain()
    cl = cli.CLI(bc)
    cl.run()
    bc.db.close()

if __name__=='__main__':
    main()
