class StreamHeader:
    def __init__(self, data: bytes):
        self.magic = data[0:4].decode("ascii")
        self.endian = data[4:].decode("ascii")

