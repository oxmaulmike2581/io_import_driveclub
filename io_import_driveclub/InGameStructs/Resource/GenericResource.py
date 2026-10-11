from ...Utils.StreamReader import StreamReader

# class for storing unknown resource data
class GenericResource:
    def __init__(self):
        self.m_VersionNumber = None
        self.m_rawData = None
    
    def read(self, sr: StreamReader, resSize: int):
        # read base data
        self.m_VersionNumber = sr.read_uint32()
        
        # read remain data as is
        # -20 because streamHeader is 8 bytes, resId is 8 bytes, versionNumber is 4 bytes. 8 + 8 + 4 = 20.
        self.m_rawData = sr.read_bytes(resSize - 20)
        
        return self

