import time
import hashlib

class Block():

    def __init__(self, size, id, trxs, node, prev_hash):
        self.size = size
        self.hash = self.hash_gen(trxs)
        self.prev_hash = prev_hash
        self.type = 2
        self.generated_by = node
        self.id = id
        self.trxs = trxs
        self.timestamp = time.ctime()

    def __repr__(self):
        return str(self.id)


    def hash_gen(self, tasks):
        re = [(task.id) for task in tasks]
        re.sort()
        appended_hash_ids = ','.join(map(str, re)).encode('utf-8')
        return hashlib.sha256(appended_hash_ids).hexdigest()

    def validator(self, tasks):
        pass

    def view_blocks(self):
        pass