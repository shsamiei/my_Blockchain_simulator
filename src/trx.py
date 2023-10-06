import time

class Trx():
    def __init__(self, gas, size, id):
        self.gas = gas
        self.size = size
        self.id = id
        self.type = type
        self.gen_time = time.ctime()
        self.appended_time = None
        self.blocked_time = None

    def __repr__(self):
        return str(self.id)