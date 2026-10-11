from ...Utils.StreamReader import StreamReader
from .ResourceIdentifier import ResourceIdentifier

class Unk3_Stru:
    def __init__(self):
        self.Unk3_Ident = None
        self.Unk3Offset = None
    
    def read(self, sr: StreamReader):
        self.Unk3_Ident = ResourceIdentifier(sr.read_uint64())
        self.Unk3Offset = sr.read_uint32()
        
        return self

