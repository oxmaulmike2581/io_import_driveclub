import os

from ...Utils.StreamReader import StreamReader
from ..StreamFormat.StreamFormat import StreamFormat
from ..VertexBuffer.VertexBuffer import VertexBuffer
from ..IndexBuffer.IndexBuffer import IndexBuffer
from ..PixelBuffer.PixelBuffer import PixelBuffer
from ..Mesh.Mesh import Mesh
from ..Hierarchy.Hierarchy import Hierarchy
from ..TopMips.TopMips import TopMips
from .ResourceIdentifier import ResourceIdentifier
from .ResourceData import ResourceData
from .StreamHeader import StreamHeader
from .GenericResource import GenericResource

class ResourceInfo:
    def __init__(self):
        self.m_ResourceId           = None
        self.m_Size                 = None
        self.m_Offset               = None
        self.m_NumDependancies      = None
        self.m_pDependancies        = []
        self.m_NumNames             = None
        self.m_pNames               = []
        self.SourceAssetPathCount   = None
        self.SourceAssetPathOffsets = []
        self.ResourceNames          = []
        self.SourceAssets           = []
        self.ResourceData           = None
    
    def read(self, sr: StreamReader, nsr: StreamReader, sar: StreamReader):
        self.m_ResourceId      = ResourceIdentifier(sr.read_uint64())
        self.m_Size            = sr.read_uint32()
        self.m_Offset          = sr.read_uint32()
        self.m_NumDependancies = sr.read_uint16()
        
        if self.m_NumDependancies != 0:
            for i in range(self.m_NumDependancies):
                self.m_pDependancies.append(ResourceIdentifier(sr.read_uint64()))
        
        self.m_NumNames             = sr.read_uint16()
        self.m_pNames               = sr.read_uint32_array(self.m_NumNames)
        self.SourceAssetPathCount   = sr.read_uint16()
        self.SourceAssetPathOffsets = sr.read_uint32_array(self.SourceAssetPathCount)
        
        # save the current offset
        cPos = sr.position
        
        # read names
        if self.m_NumNames > 0:
           for i in range(self.m_NumNames):
               nsr.seek(self.m_pNames[i], os.SEEK_SET)
               self.ResourceNames.append(nsr.read_null_terminated_string())
        
        if self.SourceAssetPathCount > 0:
           for i in range(self.SourceAssetPathCount):
               sar.seek(self.SourceAssetPathOffsets[i], os.SEEK_SET)
               self.SourceAssets.append(sar.read_null_terminated_string())
        
        # seek to offset where resource data is begins
        sr.seek(self.m_Offset, os.SEEK_SET)
        
        # read and deserialize each resource's data here
        self.ResourceData                = ResourceData()
        self.ResourceData.m_StreamHeader = StreamHeader(sr.read_bytes(8))
        self.ResourceData.m_Identifier   = ResourceIdentifier(sr.read_uint64())
        
        match self.ResourceData.m_Identifier.Packed.Type:
            case 2:  self.ResourceData.m_StreamFormat = StreamFormat().read(sr)
            case 3:  self.ResourceData.m_VertexBuffer = VertexBuffer().read(sr)
            case 4:  self.ResourceData.m_IndexBuffer  = IndexBuffer().read(sr)
            case 5:  self.ResourceData.m_PixelBuffer  = PixelBuffer().read(sr)
            case 8:  self.ResourceData.m_Mesh         = Mesh().read(sr)
            case 11: self.ResourceData.m_Hierarchy    = Hierarchy().read(sr)
            case 71: self.ResourceData.m_TopMips      = TopMips().read(sr)
            case _:  self.ResourceData.m_Generic      = GenericResource().read(sr, self.m_Size)
        
        # seek back
        sr.seek(cPos, os.SEEK_SET)
        
        return self

