import hashlib
import json

class Block:
    def __init__(self, index, timestamp, data, previous_hash, hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.get_hash()
    # creates a sha256 hash, encodes it as utf-8
    def get_hash():
        # the "f{}" string method is a security flaw for consistency reasons.
        # json.dump(..., sort_keys=True) secures alphabetical ordering in keys.
        block_attrs = json.dump(self.__dict__, sort_keys=True) # __dict__ returns all writable attrs of the obj
        return hashlib.sha256(block_attrs.encode('utf-8').hexdigest())