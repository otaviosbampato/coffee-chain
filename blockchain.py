import hashlib
import json

# block class (kind of generic). more params can be added, such as specifics for our own solution
class Block:
    def __init__(self, index, timestamp, data, previous_hash, nonce):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.get_hash()
    # creates a sha256 hash, encodes it as utf-8
    def get_hash():
        # the "f{}" string method is a flaw for consistency reasons in ordering of key pairing and key ordering.
        # json.dump(..., sort_keys=True) secures consistent alphabetical ordering in keys, and is preferred.
        block_attrs = json.dump(self.__dict__, sort_keys=True) # __dict__ returns all writable attrs of the obj
        return hashlib.sha256(block_attrs.encode('utf-8').hexdigest())

class Blockchain:
    def __init__(self):
        self