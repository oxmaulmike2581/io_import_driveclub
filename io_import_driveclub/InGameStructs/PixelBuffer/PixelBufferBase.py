class PixelBufferBase:
    def __init__(self):
        self.unk                    = None # only if m_VersionNumber == 0x20000
        self.m_WriteWidth           = None
        self.m_WriteHeight          = None
        self.m_Depth                = None
        self.m_PixelFormat          = None # 16 bits; -> PixelFormat if m_VersionNumber >= 0x20003 else PixelFormatOld
        self.m_MipLevels            = None
        self.m_Type                 = None # 8 bits
        self.m_serverUsage          = None # 8 bits
        
        # DriveClub (alpha or later)
        self.dcUnk                  = None # only if m_VersionNumber >= 0x20003
        self.m_StartMip             = None # only if m_VersionNumber >= 0x20003
        
        # DriveClub Retail
        self.dcUnk3                 = None # only if m_VersionNumber >= 0x20005
        
        self.TopMipsResrcIdentifier = None
        self.DataSize               = None
        self.ImageData              = None
