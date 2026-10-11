import os

from ...Utils.StreamReader import StreamReader
from ..Resource.ResourceIdentifier import ResourceIdentifier
from .PixelBufferBase import PixelBufferBase
from .PixelFormat import PixelFormat
from .PixelFormatOld import PixelFormatOld
from .PixelBufferBase_Type import PixelBufferBase_Type
from .PixelBufferBase_ServerUsage import PixelBufferBase_ServerUsage

class PixelBuffer:
    def __init__(self):
        self.m_VersionNumber = None
        self.m_Base          = PixelBufferBase()
    
    def read(self, sr: StreamReader):
        # read base data
        self.m_VersionNumber = sr.read_uint32()
        
        # a temporary solution made
        # because some textures has version number 0x10000
        # and for now idk how to parse them
        if self.m_VersionNumber < 0x20000:
            print(f"ERROR: PixelBuffer version 0x{self.m_VersionNumber:08X} is not supported.")
            return None
        
        # skip unknown data (this version used only in Motorstorm Apocalypse)
        if self.m_VersionNumber == 0x20000:
            sr.seek(0x8, os.SEEK_CUR)
        
        # read required values
        self.m_Base.m_WriteWidth = sr.read_uint16()
        self.m_Base.m_WriteHeight = sr.read_uint16()
        self.m_Base.m_Depth = sr.read_uint16()
        
        if self.m_VersionNumber >= 0x20003:
            self.m_Base.m_PixelFormat = PixelFormat(sr.read_uint16())
        else:
            self.m_Base.m_PixelFormat = PixelFormatOld(sr.read_uint16())
        
        self.m_Base.m_MipLevels = sr.read_uint8()
        self.m_Base.m_Type = PixelBufferBase_Type(sr.read_uint8())
        self.m_Base.m_serverUsage = PixelBufferBase_ServerUsage(sr.read_uint8())
        
        # skip unknown data
        if self.m_VersionNumber >= 0x20003:
            self.m_Base.dcUnk = sr.read_uint8()
            self.m_Base.m_StartMip = sr.read_uint8()
            
            if self.m_VersionNumber >= 0x20005:
                self.m_Base.dcUnk3 = sr.read_uint8()
                self.m_Base.TopMipsResrcIdentifier = ResourceIdentifier(sr.read_uint64())
        
        # read data
        self.m_Base.DataSize = sr.read_uint32()
        self.m_Base.ImageData = sr.read_bytes(self.m_Base.DataSize)
        
        # return as structure
        return self

