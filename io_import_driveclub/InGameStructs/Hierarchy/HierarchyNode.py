from ..Math.float4x4 import float4x4

class HierarchyNode:
    def __init__(self, name="", defaultLocalToParent=None, defaultParent=0, crc=0):
        self.defaultLocalToParent = defaultLocalToParent if defaultLocalToParent else float4x4()
        self.defaultParent        = defaultParent
        self.crc                  = crc
        self.name                 = name
        self.shortName            = ""
        self.is_virtual           = False
        self.children             = []
    
    def get_path_components(self):
        return [comp for comp in self.name.split("|") if comp]

    def ensure_short_name(self):
        if not self.shortName:
            comps = self.get_path_components()
            
            if comps:
                self.shortName = comps[-1]
        
        return self.shortName

