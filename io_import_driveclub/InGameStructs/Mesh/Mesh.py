from ...Utils.StreamReader import StreamReader
from .BoundingVolume.BVAABB import BVAABB
from .BoundingVolume.BVOBB import BVOBB
from .BoundingVolume.BVSphere import BVSphere
from .RenderCommands.RenderCommandList import RenderCommandList

class Mesh:
    def __init__(self):
        self.m_Header                     = None
        self.m_Identifier                 = None
        self.m_VersionNumber              = None
        self.NumReservedVertexBuffers     = None
        self.NumVertexBuffers             = None
        self.NumMeshMaterials             = None
        self.UnkCommandList1              = None
        self.UnkCommandList2              = None
        self.UnkCommandList3              = None
        self.UnkCommandList4              = None
        self.NumCommandLists              = None
        self.CommandLists                 = []
        self.DefaultCommandList           = None
        self.m_MeshBlendingState          = None
        self.m_bHasAlphaToCoverageInZPass = None
        self.count3                       = None
        self.BVAABB                       = BVAABB()
        self.BVOBB                        = BVOBB()
        self.BVSphere                     = BVSphere()
        self.m_AverageTriangleArea        = None
        self.m_TriangleCount              = None
        self.HasUnk                       = None
        self.Unks                         = []
    
    def read(self, sr: StreamReader):
        # read base data
        self.m_VersionNumber              = sr.read_uint32()
        
        self.NumReservedVertexBuffers     = sr.read_uint16() # sets the size of std::vector<evo::renderer::VertexBuffer>
        self.NumVertexBuffers             = sr.read_uint16()
        self.NumMeshMaterials             = sr.read_uint16()
        
        if (self.m_VersionNumber >= 0xB0000):
            self.UnkCommandList1 = RenderCommandList().read(sr, self.m_VersionNumber)
            self.UnkCommandList2 = RenderCommandList().read(sr, self.m_VersionNumber)
            self.UnkCommandList3 = RenderCommandList().read(sr, self.m_VersionNumber)
            self.UnkCommandList4 = RenderCommandList().read(sr, self.m_VersionNumber)
            
            self.NumCommandLists = sr.read_int32()
            for i in range(self.NumCommandLists):
                self.CommandLists.append(RenderCommandList().read(sr, self.m_VersionNumber))
        else:
            if self.NumMeshMaterials is None:
                self.DefaultCommandList = RenderCommandList().read(sr, self.m_VersionNumber)
            else:
                self.NumCommandLists = sr.read_int32()
                for i in range(self.NumCommandLists):
                    self.CommandLists.append(RenderCommandList().read(sr, self.m_VersionNumber))
        
        self.m_MeshBlendingState          = sr.read_uint8()
        self.m_bHasAlphaToCoverageInZPass = sr.read_uint8()
        self.count3                       = sr.read_int32()
        
        # Actual game check
        if self.m_VersionNumber >= 0x90000:
            self.BVAABB.m_v3Centre        = sr.read_float32_array(3)
            self.BVAABB.m_v3Extent        = sr.read_float32_array(3)
            
            self.BVOBB.m_v3Centre         = sr.read_float32_array(3)
            for i in range(3):
                self.BVOBB.m_v4AxisAndExtentsInW.append(sr.read_float32_array(3))
            for i in range(3):
                self.BVOBB.test.append(sr.read_float32())
            self.BVOBB.what               = sr.read_uint32()
            
            self.BVSphere.m_v4Centre      = sr.read_float32_array(4)
        
        self.m_AverageTriangleArea        = sr.read_float32()
        self.m_TriangleCount              = sr.read_uint32()
        
        if self.m_VersionNumber >= 0xB0000:
            self.HasUnk                   = sr.read_uint8()
            
            for i in range(self.NumMeshMaterials):
                self.Unks.append(sr.read_bytes(0x40))
        
        return self

