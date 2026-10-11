from ...Utils.StreamReader import StreamReader
from .IndexBufferBase import IndexBufferBase

class IndexBuffer:
    def __init__(self):
        self.m_VersionNumber = None
        self.m_Base          = IndexBufferBase()
    
    def read(self, sr: StreamReader):
        # read base data
        self.m_VersionNumber           = sr.read_uint32()
        
        # read unknown value (maybe padding)
        self.m_Base.Unk                = sr.read_uint16()
        
        # read stride
        self.m_Base.ElementSizeInBytes = sr.read_uint16()
        
        # read indices count
        self.m_Base.NumElements        = sr.read_uint32()
        
        # read index data
        self.m_Base.Data               = sr.read_bytes(self.m_Base.ElementSizeInBytes * self.m_Base.NumElements)
        
        return self

