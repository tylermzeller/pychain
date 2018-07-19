import pychain.block as block
import pychain.blockchain as blockchain
import pychain.block_explorer as block_explorer
import pychain.transaction as transaction
import pychain.transaction_input as transaction_input
import pychain.transaction_output as transaction_output

class Miner:
    def __init__(self, address):
        self.address = address
        self.mempool = {}
        self.bx = block_explorer.BlockExplorer()
        self.bc = blockchain.Blockchain()

    # Returns a Transaction instance
    def newCoinbaseTX(self, fees=0):
        if len(self.address) = 0:
            raise RuntimeError("Error: Miners without addresses cannot create coinbases.")

        randbytes = b''
        for i in range(40):
            randbytes += bytes([randint(0, 255)])

        # as the miner, I can include anything I want in this pubKey arg,
        # be it a poem or any arbitrary string. I just need to prepend
        # some random bytes to it, or else the tx hash won't be unique
        txin = transaction_input.TXInput(pubKey=randbytes.hex())
        outDict = OutputDict()
        outDict.append(transaction_output.TXOutput(subsidy + fees, address=self.address))

        return transaction.Transaction([txin], outDict)

    def verify(self, tx):
        if tx.isCoinbase(): return True

        prevTxs = self.bx.getPrevTransactions(tx)

        for txInput in tx.vin:
            if txInput.txId not in prevTxs:
                raise Exception("Prev TX for TXInput %s not found" % txInput.txId.hex())
            if not prevTxs[txInput.txId].id:
                print(prevTxs[txInput.txId])
                raise Exception("Invalid previous tx.")
        # A trimmed copy is a copy of the TX, but the
        # inputs have no signatures or pubkeys
        trimCopy = tx.trimmedCopy()

        # Loop through the true inputs of this transaction (not copies)
        for i, txInput in enumerate(tx.vin):

            # grab a copy for signing
            inCopy = trimCopy.vin[i]

            # get the output this input references
            prevTx = prevTxs[txInput.txId]
            refTxOutput = prevTx.outDict[txInput.outIdx]

            # Make sure the conditions of this input
            # (no signature, pubKey is out.pubKeyHash)
            # are same as when it was signed
            inCopy.signature = None
            inCopy.pubKey = refTxOutput.pubKeyHash

            # Hash the transaction with one input populated with a pubKeyHash
            trimCopy.setId()

            # Unset this input so we meet the conditions to verify
            # other inputs
            inCopy.pubKey = None

            # If we can't verify this input, the tx is invalid
            if not txInput.pubKey.verify(txInput.signature, trimCopy.id):
                return False

        # Didn't find any invalid txs
        return True

    def calcFees(txs):
        s = 0
        for tx in txs:
          prevTxs = self.bx.getPrevTransactions(tx)
          s += sum([prevTxs[vin.txId].outDict[vin.outIdx].value for vin in tx.vin])
        return s - sum([vout.value for tx in txs for vout in tx.outDict.values()])

    def mine_block(self, transactions=[]):
        if len(self.address) = 0:
            raise RuntimeError("Error: Miners without addresses cannot mine blocks.")

        if len(transactions) == 0:
            transactions.append(self.newCoinbaseTX())

        found_coinbase = False
        for tx in transactions:
            if not self.verify(tx):
                print("Error verifying transactions")
                print(tx)
                return
            if tx.isCoinbase():
                found_coinbase = True

        if not found_coinbase:
            raise ValueError("Error: Coinbase must be included in list of txs to mine block.")

        last_block = self.bc.getTip()

        if not last_block:
            print("\nEmpty blockchain. Creating genesis.")
            if len(transactions) != 1:
                raise ValueError("Error: should be a single tx in the genesis block. Instead found %d" % len(transactions))
            new_block = block.newGenesisBlock(transactions[0])
        else:
            new_block = block.Block(transactions, last_block.hash, last_block.height + 1)

        print("Mined block %s" % new_block.hash.hex())

        # NOTE: We don't reindex UTXO after every added block...
        # We reindex after every successful mined block.
        # When receiving another node's inventory, we may add many blocks and
        # then perform a batch reindex
        self.bc.addBlock(new_block)
        utxo_set.UTXOSet().reindex()
        return new_block

    def mine_transactions(self):
        if len(self.address) = 0:
            raise RuntimeError("Error: Miners without addresses cannot mine blocks.")

        print("Attempting to mine new block")
        txs = [tx for tx in self.mempool.values() if self.verify(tx)]

        if len(txs) == 0:
            print("All transactions were invalid! Waiting for more...")
            return

        fees = self.calcFees(txs)
        print("fees = %2.3f" % fees)
        cb = self.newCoinbaseTX(fees=fees)
        txs.append(cb)
        new_block = self.mine_block(txs)

        for tx in txs:
            if tx.id in self.mempool:
                print("deleting tx %s from mempool" % tx.id.hex())
                del self.mempool[tx.id]

        # if len(mempool) > 0:
        #     mine_transactions()

        return block
