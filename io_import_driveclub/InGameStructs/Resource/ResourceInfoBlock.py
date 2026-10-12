from ...Utils.StreamReader import StreamReader
from .Resource import Resource
from .ResourceInfoBlockHeader import ResourceInfoBlockHeader
from .ResourceIdentifier import ResourceIdentifier
from .ResourceInfo import ResourceInfo
from .Unk3_Stru import Unk3_Stru

class ResourceInfoBlock:
    def __init__(self):
        self.m_Resource            = None
        self.m_Header              = None
        self.MainIdentifier        = None
        self.nameStringPool        = []
        self.sourceAssetStringPool = []
        self.ResourceInfos         = []
        self.Unk3                  = []
        self.Unk4                  = []
        self.MarkerMagicEnd        = None
    
    def read(self, sr: StreamReader):
        self.m_Resource            = Resource().read(sr)
        self.m_Header              = ResourceInfoBlockHeader().read(sr, self.m_Resource.m_VersionNumber)
        self.MainIdentifier        = ResourceIdentifier(sr.read_uint64())
        
        # read raw bytes of strings (we'll parse them later)
        self.nameStringPool        = StreamReader(sr.read_bytes(self.m_Header.nameStringPoolSize))
        self.sourceAssetStringPool = StreamReader(sr.read_bytes(self.m_Header.sourceAssetStringPoolSize))
        
        # read resource meta table
        for i in range(self.m_Header.count):
            self.ResourceInfos.append(ResourceInfo().read(sr, self.nameStringPool, self.sourceAssetStringPool))
        
        # read unknown structs if needed
        if self.m_Header.Unk3Count is not None and self.m_Header.Unk3Count > 0:
            for i in range(self.m_Header.Unk3Count):
                self.Unk3.append(Unk3_Stru().read(sr))
        
        # read unknown offsets if needed
        if self.m_Header.Unk4Count is not None and self.m_Header.Unk4Count > 0:
            self.Unk4 = sr.read_uint32_array(self.m_Header.Unk4Count)
        
        # read end marker
        self.MarkerMagicEnd        = sr.read_uint32()
        
        if self.MarkerMagicEnd != 0x99999999:
            print("Warning: Resource Info Block end magic marker did not match 0x99999999")
        
        return self

