from ...Utils.StreamReader import StreamReader

class ResourceInfoBlockHeader:
    def __init__(self):
        self.marker_start              = None
        self.count                     = None
        self.aliasCount                = None
        self.dependancyCount           = None
        self.nameStringPoolSize        = None
        self.sourceAssetStringPoolSize = None
        self.Unk3Count                 = None
        self.Unk4Count                 = None
    
    def read(self, sr: StreamReader, ver: int):
        self.marker_start              = sr.read_uint32()
        self.count                     = sr.read_uint32()
        self.aliasCount                = sr.read_uint32()
        self.dependancyCount           = sr.read_uint32()
        self.nameStringPoolSize        = sr.read_uint32()
        self.sourceAssetStringPoolSize = sr.read_uint32()
        
        if ver >= 0x40002:
            self.Unk3Count             = sr.read_uint32()
            self.Unk4Count             = sr.read_uint32()
        
        return self

