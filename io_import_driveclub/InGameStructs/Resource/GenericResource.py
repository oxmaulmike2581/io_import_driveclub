from ...Utils.StreamReader import StreamReader

# class for storing unknown resource data
class GenericResource:
    def __init__(self, versionNumber=None, raw_data=None):
        self.m_VersionNumber = versionNumber
        self.m_rawData = raw_data
    
    def read(self, sr: StreamReader, resSize: int):
        # read base data
        self.m_VersionNumber = sr.read_uint32()
        
        # read remain data as is
        # -20 because streamHeader is 8 bytes, resId is 8 bytes, versionNumber is 4 bytes. 8 + 8 + 4 = 20.
        self.m_rawData = sr.read_bytes(resSize - 20)
        
        return self

