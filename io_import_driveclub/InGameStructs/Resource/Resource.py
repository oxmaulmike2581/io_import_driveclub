from ...Utils.StreamReader import StreamReader
from .ResourceIdentifier import ResourceIdentifier

class Resource:
    def __init__(self):
        self.m_ResourceIdentifier = None
        self.m_VersionNumber = None
    
    def read(self, sr: StreamReader):
        self.m_ResourceIdentifier = ResourceIdentifier(sr.read_uint64())
        self.m_VersionNumber = sr.read_uint32()
        
        return self

