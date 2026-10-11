from ..Utils.StreamReader import StreamReader
from .Resource.Header import Header
from .Resource.StreamHeader import StreamHeader
from .Resource.ResourceInfoBlock import ResourceInfoBlock
from .StreamFormat.FORMAT_SIZES import FORMAT_SIZES

class Resource_PacK:
    def __init__(self):
        self.m_Header            = None
        self.DataStreamHeader    = None
        self.m_ResourceInfoBlock = None
    
    # read .rpk header, table of contents, etc.
    def read(self, sr: StreamReader):
        self.m_Header = Header().read(sr)
        self.DataStreamHeader = StreamHeader(sr.read_bytes(8))
        self.m_ResourceInfoBlock = ResourceInfoBlock().read(sr)
        
        return self
    
    # get a resource by given id
    def get_resource_by_id(self, id):
        for res in self.m_ResourceInfoBlock.ResourceInfos:
            if res.m_ResourceId.m_UID == id:
                return res
        
        return None
    
    # get all resources by given type
    def get_resources_by_type(self, res_type):
        return [
            res for res in self.m_ResourceInfoBlock.ResourceInfos
            if res.m_ResourceId.Packed.Type == res_type
        ]
    
    # get all dependancies needed by resource
    # deps is a ResourceInfo.m_pDependancies
    def get_all_dependancies(self, deps):
        return [
            res for dep in deps
            if (res := self.get_resource_by_id(dep.m_UID)) is not None
        ]
    
    # calculate expected stride based on sum of format sizes given from streamformat
    def get_expected_stride(self, formats):
        total = 0
        
        for fmt in formats:
            if fmt not in FORMAT_SIZES:
                raise KeyError(f"Unknown format: {fmt}")
            
            total += FORMAT_SIZES[fmt]
        
        return total

