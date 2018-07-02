import os
import plyvel

# WARNING: you should NEVER use the /tmp directory for persistence
# in a production environment. You should except the contents of
# that dir to be erased by the OS periodically.
base_db_path = os.getenv('DBDBPATH', default='/tmp/')

db_paths = {
    'blocks':   base_db_path + 'blocks/',
    'wallets':  base_db_path + 'wallets/',
    'utxos':    base_db_path + 'utxos/',
}

class DBInterface:
    def __init__(self, db_name):
        global db_paths
        self.db = plyvel.DB(db_paths[db_name], create_if_missing=True)

    def _check_values(self, *values):
        for value in values:
            if not isinstance(value, bytes):
                raise ValueError("Database keys/values must be of type bytes")

    def _check_open(self):
        if self.db.closed:
            raise RuntimeError("Cannot perform operations on a closed DB.")

    def exists(self, key):
        self._check_open()
        self._check_values(key)
        return self.db.get(key, b'') != b''

    def put(self, key, value):
        self._check_open()
        self._check_values(key, value)
        # explicitly reject empty keys
        if not key:
            return

        self.db.put(key, value)

    def get(self, key):
        self._check_open()
        self._check_values(key)

        return self.db.get(key, b'')

    def iter_keys(self):
        with self.db.snapshot() as s, s.iterator(include_values=False) as it:
            for key in it:
                yield key

    def iter_values(self):
        with self.db.snapshot() as s, s.iterator(include_keys=False) as it:
            for value in it:
                yield value

    def clear(self):
        self._check_open()
        with self.db.snapshot() as s, self.db.write_batch() as wb, s.iterator(include_values=False) as it:
            for key in it:
                wb.delete(key)

    def close(self):
        if not self.db.closed:
            self.db.close()

class DBManager:
    class __DBManager:
        def __init__(self):
            self.db_refs = {
                'blocks':   None,
                'wallets':  None,
                'utxos':    None,
            }

        def get(self, db):
            if not db in self.db_refs:
                raise ValueError("%s is not a valid db name" % str(db))

            if self.db_refs[db] is None:
                self.db_refs = DBInterface(db)

            return self.db_refs[db]

        def close(self):
            for db_ref in self.db_refs.values():
                if db_ref != None:
                    db_ref.close()

    instance = None

    def __init__(self):
        if not DBManager.instance:
            DBManager.instance = DBManager.__DBManager()

    def __getattr__(self, name):
        return getattr(self.instance, name)
