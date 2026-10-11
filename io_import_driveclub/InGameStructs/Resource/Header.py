from ...Utils.StreamReader import StreamReader
from .StreamHeader import StreamHeader

class Header:
    def __init__(self):
        self.m_StreamHeader = None
        self.Name           = None
        self.SizeOfToC      = None
        self.OffsetToToC    = None
    
    def read(self, sr: StreamReader):
        self.m_StreamHeader = StreamHeader(sr.read_bytes(8))
        self.Name           = sr.read_string(sr.read_uint32())
        self.SizeOfToC      = sr.read_uint32()
        self.OffsetToToC    = sr.read_uint32()
        
        return self

