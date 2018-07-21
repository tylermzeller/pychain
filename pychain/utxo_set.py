import pychain.base58 as base58
import pychain.transaction_output as txout
import pychain.util as util

import pychain.block_explorer as bx
from pychain.database_manager import DBManager

from binascii import unhexlify

class UTXOSet:
    def __init__(self):
        self.utxos_db = DBManager().get('utxos')

    def reindex(self):
        # empty the current indexed UTXOs
        self.utxos_db.clear()
        # get the new UTXOs
        UTXO = bx.BlockExplorer().findUTXO()
        with self.utxos_db.write_batch() as wb:
            for txId, txOutputs in UTXO.items():
                # add them to the cache
                txOutputs = list(txOutputs)
                encodedTXOutputs = util.encodeMsg(txOutputs, encoder=txout.encodeTXOutput)
                wb.put(txId, encodedTXOutputs)

    def update(self, block):
        with self.utxos_db.snapshot() as s, self.utxo_db.write_batch() as wb:
            for tx in block.transactions:
                # coinbase txs don't have inputs, duh
                if not tx.isCoinbase():
                    # for each input, remove the output that it spends from the UTXO set
                    for txInput in tx.vin:
                        txOutputs = util.decodeMsg(s.get(txInput.txId))
                        updatedOutputs = [txOutput for txOutput in txOutputs if txOutput[b'idx'] != txInput.outIdx]

                        if len(updatedOutputs) == 0:
                            wb.delete(txInput.txId)
                        else:
                            encodedOutputs = util.encodeMsg(updatedOutputs)
                            wb.put(txInput.txId, encodedOutputs)

                # add new outputs to the UTXO set
                encodedNewOutputs = util.encodeMsg(list(tx.outDict.values()), encoder=txout.encodeTXOutput)
                wb.put(tx.id, encodedNewOutputs)

    def findSpendableOutputs(self, pubKeyHash, amount):
        outputDict = {}
        accumulated = 0

        for txId, encodedOutputs in self.utxos_db.iter_items():
            unspentOutputs = util.decodeMsg(encodedOutputs, decoder=txout.decodeTXOutput)
            for txOutput in unspentOutputs:
                if txOutput.isLockedWithKey(pubKeyHash) and accumulated < amount:
                    if txId not in outputDict:
                        outputDict[txId] = {}
                    if txOutput.idx in outputDict[txId]:
                        print("Collision! TXOutput already accounted for.")
                    else:
                        outputDict[txId][txOutput.idx] = txOutput
                        accumulated += txOutput.value
        return accumulated, outputDict

    def find_utxo(self, pub_key_hash):
        utxo = []
        for encoded_outs in self.utxos_db.iter_values():
            unspent_outs = util.decodeMsg(encoded_outs, decoder=txout.decodeTXOutput)
            utxo.extend([tx_out for tx_out in unspent_outs if tx_out.isLockedWithKey(pub_key_hash)])
        return utxo

    def get_unspent_outputs(self, tx_id):
        encoded_outs = self.utxos_db.get(tx_id)
        if encoded_outs == b'':
            return []
        return util.decodeMsg(encoded_outs, decoder=txout.decodeTXOutput)

    def get_balance(self, address=b'', pub_key_hash=b''):
        if address and isinstance(address, bytes):
            pub_key_hash = base58.decode(address)[1:-4]
        elif not pubKeyHash:
            raise ValueError("Must provide address or pubKeyHash to find balance")
        return sum([out.value for out in self.find_utxo(pub_key_hash)])
