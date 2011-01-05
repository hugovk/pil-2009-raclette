# byte array wrapper

class ByteArray(object):
    def __init__(self, data):
        self.data = data
    def __getitem__(self, index):
        return ord(self.data[index])
