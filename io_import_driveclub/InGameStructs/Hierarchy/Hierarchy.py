from ...Utils.StreamReader import StreamReader
from ..Math.float4x4 import float4x4
from .HierarchyNode import HierarchyNode

class Hierarchy:
    def __init__(self):
        # DriveClub or Motorstorm Apocalypse = 0x20000
        self.m_VersionNumber        = None
        self.numNodes               = None
        self.Nodes                  = []
        self._full_path_to_idx      = {} # ["path"] = index
        self._short_name_to_indices = {} # ["shortName"] = faceIndices
        self._root_indices          = []
    
    def _normalize_path(self, path_str):
        if "|" in path_str:
            path_str = path_str.strip("|").replace("|", "/")
        
        if not path_str.startswith("/"):
            path_str = "/" + path_str
        
        return path_str

    def _find_by_full_path(self, path_str):
        idx = self._full_path_to_idx.get(self._normalize_path(path_str))
        
        if idx is not None:
            return self.Nodes[idx]
        
        return None

    def _find_by_short_name(self, short_name):
        return [self.Nodes[i] for i in self._short_name_to_indices.get(short_name, [])]

    def _is_root_by_parent(self, node_idx):
        node = self.Nodes[node_idx]
        return node.defaultParent is None or node.defaultParent == node_idx
    
    def _get_root_nodes(self):
        return [self.Nodes[i] for i in self._root_indices]

    def build_path_index(self):
        self._full_path_to_idx.clear()
        self._short_name_to_indices.clear()
        original_count = len(self.Nodes)

        # index existing nodes by their names first
        node_paths = [] # full node paths
        
        for idx, node in enumerate(self.Nodes):
            node.ensure_short_name()
            norm = self._normalize_path(node.name)
            node_paths.append(norm)
            self._full_path_to_idx[norm] = idx
            self._short_name_to_indices.setdefault(node.shortName, []).append(idx)

        # build all required intermediate paths
        all_paths = set(self._full_path_to_idx.keys())
        needed_virtual = set()
        for p in node_paths:
            parts = p.split("/")
            
            # /A/B -> interm. /A, /A/B
            for i in range(2, len(parts)):  # /A (i = 2 means "parts[0]='', parts[1]='A'")
                interm = "/".join(parts[:i])
                
                if interm not in all_paths:
                    needed_virtual.add(interm)

        # make virtual nodes for required intermediate paths (down from root)
        for interm in sorted(needed_virtual, key=lambda x: x.count("/")):
            parent_path = "/".join(interm.split('/')[:-1])
            if parent_path == "":
                parent_path = "/"
            
            parent_idx = self._full_path_to_idx.get(parent_path)
            
            # make virtual node
            virt_node                      = HierarchyNode(name=interm.replace("/", "|"))
            virt_node.shortName            = interm.split("/")[-1]
            virt_node.is_virtual           = True
            virt_node.defaultParent        = parent_idx if parent_idx is not None else 0
            virt_node.crc                  = 0
            virt_node.defaultLocalToParent = float4x4()
            
            # append to list
            self.Nodes.append(virt_node)
            self._full_path_to_idx[interm] = len(self.Nodes)
            self._short_name_to_indices.setdefault(interm.split("/")[-1], []).append(len(self.Nodes))

    def validate_parent_links(self):
        if not self._full_path_to_idx:
            self._build_path_index()

        discrepancies = []
        for idx, node in enumerate(self.Nodes):
            if node.is_virtual:
                continue
            
            comps = node.get_path_components()
            if len(comps) <= 1:
                expected_parent = None
            
            else:
                expected_parent = self._full_path_to_idx.get(self._normalize_path("|" + "|".join(comps[:-1])))

            actual_parent = node.defaultParent
            if self._is_root_by_parent(idx):
                actual_parent = None

            if expected_parent != actual_parent:
                discrepancies.append((node, expected_parent, actual_parent))
        
        return discrepancies

    def ensure_paths(self, mesh_dict):
        if not self._full_path_to_idx:
            self._build_path_index()
        
        for mesh_fullname in mesh_dict:
            parts = self._normalize_path(mesh_fullname).split('/')
            
            # build all intermediate paths starting from 2nd level (root = "/")
            for i in range(2, len(parts)): # skip empty line and root
                interm = "/".join(parts[:i])
                
                if interm not in self._full_path_to_idx:
                    # get parent index
                    parent_idx                     = self._full_path_to_idx.get("/".join(parts[:i-1]) if i > 2 else "/")
                    
                    # make virtual node
                    virt_node                      = HierarchyNode()
                    virt_node.name                 = interm.replace("/", "|")
                    virt_node.shortName            = parts[i - 1]
                    virt_node.is_virtual           = True
                    virt_node.defaultParent        = parent_idx if parent_idx is not None else 0
                    virt_node.crc                  = 0
                    virt_node.defaultLocalToParent = float4x4()
                    
                    # append to list
                    self.Nodes.append(virt_node)
                    self._full_path_to_idx[interm] = len(self.Nodes)
                    self._short_name_to_indices.setdefault(parts[i - 1], []).append(len(self.Nodes))
        
        # rebuild tree after adding nodes
        self.build_tree(use_parent_index=True)

    def build_tree(self, use_parent_index=True):
        if not self._full_path_to_idx:
            self._build_path_index()

        # clear children node lists
        for node in self.Nodes:
            node.children = []

        if use_parent_index:
            for idx, node in enumerate(self.Nodes):
                if self._is_root_by_parent(idx):
                    self._root_indices.append(idx)
                
                else:
                    parent_idx = node.defaultParent
                    
                    if 0 <= parent_idx < len(self.Nodes) and parent_idx != idx:
                        self.Nodes[parent_idx].children.append(idx)
                    
                    else:
                        self._root_indices.append(idx)
        
        else:
            # build tree by names (define parent by path)
            for idx, node in enumerate(self.Nodes):
                comps = node.get_path_components()
                
                if len(comps) <= 1:
                    self._root_indices.append(idx)
                
                else:
                    parent_idx = self._full_path_to_idx.get(self._normalize_path("|" + "|".join(comps[:-1])))
                    
                    if parent_idx is not None and parent_idx != idx:
                        self.Nodes[parent_idx].children.append(idx)
                    
                    else:
                        # if no parent by name (should never happen) then treat as root
                        self._root_indices.append(idx)

        # remove duplicates in roots
        self._root_indices = list(set(self._root_indices))
    
    def read(self, sr: StreamReader):
        # read base data
        self.m_VersionNumber                   = sr.read_uint32()
        self.numNodes                          = sr.read_uint32()
        
        # fill nodes array
        for i in range(self.numNodes):
            self.Nodes.append(HierarchyNode())
        
        # fill each node
        for i in range(self.numNodes):
            self.Nodes[i].defaultLocalToParent = float4x4().read(sr)
        
        for i in range(self.numNodes):
            self.Nodes[i].defaultParent        = sr.read_uint32()
        
        for i in range(self.numNodes):
            self.Nodes[i].crc                  = sr.read_uint32()
        
        # read names as raw bytes
        namePool                               = StreamReader(sr.read_bytes(sr.read_uint32()))
        shortNamePool                          = StreamReader(sr.read_bytes(sr.read_uint32()))
        
        # add names to nodes
        for i in range(self.numNodes):
            self.Nodes[i].name                 = namePool.read_null_terminated_string()
        
        for i in range(self.numNodes):
            self.Nodes[i].shortName            = shortNamePool.read_null_terminated_string()
        
        return self

