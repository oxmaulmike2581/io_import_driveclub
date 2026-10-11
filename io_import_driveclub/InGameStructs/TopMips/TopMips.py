from ...Utils.StreamReader import StreamReader
from ..Resource.ResourceIdentifier import ResourceIdentifier

class TopMips:
    def __init__(self):
        self.m_VersionNumber       = None
        self.PixelBufferIdentifier = None
        self.TopMipsSize           = None
        self.Data                  = None
    
    def read(self, sr: StreamReader):
        self.m_VersionNumber       = sr.read_uint32()
        self.PixelBufferIdentifier = ResourceIdentifier(sr.read_uint64())
        self.TopMipsSize           = sr.read_uint32()
        self.Data                  = sr.read_bytes(self.TopMipsSize)
        
        return self

