from ...Utils.StreamReader import StreamReader
from .StreamFormatBase import StreamFormatBase
from .StreamFormatEntry import StreamFormatEntry
from .FieldSemantic import FieldSemantic
from .FieldType import FieldType
from .FieldFrequencyMode import FieldFrequencyMode

class StreamFormat:
    def __init__(self):
        self.m_VersionNumber = None
        self.m_Base = StreamFormatBase()
    
    def read(self, sr: StreamReader):
        # read base data
        self.m_VersionNumber = sr.read_uint32()
        
        # read StreamFormatBase
        self.m_Base.EntryCount = sr.read_uint8()
        
        # read each entry
        for i in range(self.m_Base.EntryCount):
            entry = StreamFormatEntry()
            entry.Semantic = FieldSemantic(sr.read_uint8())
            entry.Type = FieldType(sr.read_uint8())
            entry.UsageOrdinal = sr.read_uint8()
            
            if (self.m_VersionNumber >= 0x20000):
                entry.FrequencyMode = FieldFrequencyMode(sr.read_uint8())
                entry.Divider = sr.read_uint8()
            
            self.m_Base.Entries.append(entry)
        
        return self

