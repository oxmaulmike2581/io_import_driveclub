import os, math, random, re, struct

from pathlib import Path

from .Utils.StreamReader import StreamReader
from .InGameStructs.StreamFormat.StreamFormat import StreamFormat
from .InGameStructs.StreamFormat.StreamFormatBase import StreamFormatBase
from .InGameStructs.StreamFormat.StreamFormatEntry import StreamFormatEntry
from .InGameStructs.StreamFormat.FieldSemantic import FieldSemantic
from .InGameStructs.StreamFormat.FieldType import FieldType
from .InGameStructs.PixelBuffer.PixelFormat import PixelFormat
from .InGameStructs.PixelBuffer.PixelBufferBase_Type import PixelBufferBase_Type
from .InGameStructs.Resource.GenericResource import GenericResource
from .InGameStructs.Resource.ResourceInfo import ResourceInfo
from .InGameStructs.Resource.ResourceIdentifier import ResourceIdentifier
from .InGameStructs.Resource.ResourceTypeId import ResourceTypeId
from .InGameStructs.Resource_PacK import Resource_PacK
from .TextureStuff.PS4Texture import PS4Texture
from .TextureStuff.DDS_FLAGS import DDS_FLAGS
from .TextureStuff.PF_FLAGS import PF_FLAGS
from .TextureStuff.DDSCAPS import DDSCAPS
from .TextureStuff.D3D11_RESOURCE_DIMENSION import D3D11_RESOURCE_DIMENSION

# Blender-specific
import bpy
from mathutils import Matrix, Vector, Quaternion, Euler

class SceneContext:
    # rotate X by 90° (game's Y-up -> blender's Z-up). det = +1.
    _GAME_TO_BLENDER = Matrix([
        [ 1,  0,  0,  0],
        [ 0,  0, -1,  0],
        [ 0,  1,  0,  0],
        [ 0,  0,  0,  1]
    ])
    
    def __init__(self, use_collection=False, coll_name=""):
        self.main_rpk     = None
        self.shared_paths = []
        self.shared_rpks  = []
        self.scene        = {}
        self._path_to_obj = {}
        self.use_coll     = use_collection
        self.coll_name    = coll_name
        self._target_coll = None
    
    # load main rpk
    def load(self, in_path):
        if not in_path.exists():
            raise FileNotFoundError("File not found.")
        
        with open(in_path, "rb") as rpk:
            rdr = StreamReader(rpk)
            self.main_rpk = Resource_PacK().read(rdr)
    
    # add shared rpk to the list
    def add_shared_rpk(self, rpk_path):
        if rpk_path is not None and isinstance(self.shared_paths, list):
            self.shared_paths.append(rpk_path)
    
    # load all shared rpks
    def load_shared_rpks(self):
        if isinstance(self.shared_rpks, list):
            for shared in self.shared_paths:
                if shared.exists():
                    with open(shared, "rb") as s:
                        srdr = StreamReader(s)
                        self.shared_rpks.append(Resource_PacK().read(srdr))
    
    # proxy methods to Resource_PacK class
    # find a resource by given id
    def get_resource_by_id(self, id):
        # in main rpk first
        res = self.main_rpk.get_resource_by_id(id)
        if res is not None:
            return res
        
        # not found, try to search in shared rpks
        for pak in self.shared_rpks:
            res = pak.get_resource_by_id(id)
            if res is not None:
                return res
        
        return None
    
    # get all resources by given type
    def get_resources_by_type(self, res_type):
        # in main rpk first
        results = self.main_rpk.get_resources_by_type(res_type)
        
        # then in shared rpks
        for pak in self.shared_rpks:
            results.extend(pak.get_resources_by_type(res_type))
        
        return results
    
    # calculate expected stride based on sum of format sizes given from streamformat
    def get_expected_stride(self, formats):
        return self.main_rpk.get_expected_stride(formats)
    
    # 2-pass heuristic for vertex buffers:
    # search for StreamFormat using deps first,
    # then select a format based on stride and missing semantics for the remaining streams, trying all loaded formats
    # if nothing matches, perform a fallback-guess based on stride
    def _resolve_vertex_formats(self, mat, vo):
        if mat["vb_stream_formats"]:
            return

        vertex_streams = mat["vertex_streams"]
        mat["vb_stream_formats"] = {}

        # FIRST PASS
        # get dependencies
        for stream_idx, vb_res in vertex_streams.items():
            for dep in vb_res.m_pDependancies:
                if dep.Packed.Type == ResourceTypeId.RTUID_STREAM_FORMAT:
                    sf_res = self.get_resource_by_id(dep.m_UID)
                    if sf_res is not None:
                        mat["vb_stream_formats"][stream_idx] = sf_res
                        break

        # get covered semantics from all found formas
        covered_sem = set()
        for fmt in mat["vb_stream_formats"].values():
            if fmt is None:
                continue
            for e in fmt.ResourceData.m_StreamFormat.m_Base.Entries:
                covered_sem.add(e.Semantic)

        all_sf = self.get_resources_by_type(ResourceTypeId.RTUID_STREAM_FORMAT)

        # list of needed semantics
        required = {FieldSemantic.FS_POSITION, FieldSemantic.FS_NORMAL, FieldSemantic.FS_TEXCOORD}
        optional = {FieldSemantic.FS_COLOR, FieldSemantic.FS_TEXCOORD}
        all_desired = required | optional

        # SECOND PASS
        # do a heuristic for a remaining VBs
        for stream_idx, vb_res in vertex_streams.items():
            if stream_idx in mat["vb_stream_formats"]:
                continue

            stride = vb_res.ResourceData.m_VertexBuffer.m_Base.ElementSizeInBytes

            # get missing semantics
            missing_semantics = [sem for sem in all_desired if sem not in covered_sem]

            chosen = None
            
            # get formats which have at least one missing semantic
            candidates_1 = [sf for sf in all_sf
                            if any(e.Semantic in missing_semantics
                                   for e in sf.ResourceData.m_StreamFormat.m_Base.Entries)]

            # find target stride and all missing semantics in candidates
            for sf in candidates_1:
                entries = sf.ResourceData.m_StreamFormat.m_Base.Entries
                
                if self.get_expected_stride([e.Type.name for e in entries]) != stride:
                    continue
                
                if all(sem in {e.Semantic for e in entries} for sem in missing_semantics):
                    chosen = sf
                    break

            if chosen is not None:
                mat["vb_stream_formats"][stream_idx] = chosen
                
                for e in chosen.ResourceData.m_StreamFormat.m_Base.Entries:
                    covered_sem.add(e.Semantic)
            
            else:
                # try to make a fake StreamFormat
                fake = self._generate_fake_format(missing_semantics, stride)
                
                # it fails, make an placeholder
                if fake is None:
                    fake = self._make_fake_format_from_entries([])
                
                mat["vb_stream_formats"][stream_idx] = fake
                
                for e in fake.ResourceData.m_StreamFormat.m_Base.Entries:
                    covered_sem.add(e.Semantic)

        # get expected stride for StreamFormat
        for stream_idx, vb_res in vertex_streams.items():
            fmt = mat["vb_stream_formats"][stream_idx]
            stride = vb_res.ResourceData.m_VertexBuffer.m_Base.ElementSizeInBytes
            byte_start = vo * stride
            entries = fmt.ResourceData.m_StreamFormat.m_Base.Entries
            
            if entries:
                calc = self.get_expected_stride([e.Type.name for e in entries])

    # make a fake StreamFormat node based on missing semantics and stride
    def _generate_fake_format(self, missing_semantics, stride):
        if not missing_semantics:
            return None

        POOLS = {
            FieldSemantic.FS_POSITION: [
                (FieldType.FT_FLOAT3, 12),
                (FieldType.FT_HALF4, 8),
                (FieldType.FT_HALF3, 6),
            ],
            FieldSemantic.FS_NORMAL: [
                (FieldType.FT_NORMAL_10_10_10, 4),
                (FieldType.FT_FLOAT3, 12),
            ],
            FieldSemantic.FS_TEXCOORD: [
                (FieldType.FT_FLOAT2, 8),
                (FieldType.FT_HALF2, 4),
                (FieldType.FT_FLOAT, 4),
            ],
            FieldSemantic.FS_COLOR: [
                (FieldType.FT_UBYTE4_ARGB, 4),
                (FieldType.FT_FLOAT4, 16),
                (FieldType.FT_HALF4, 8),
            ],
        }

        choices_per_sem = [POOLS[sem] for sem in missing_semantics]

        from itertools import product
        for combo in product(*choices_per_sem):
            total = sum(sz for _, sz in combo)
            
            if total == stride:
                entries = []
                
                for sem, (ftype, _) in zip(missing_semantics, combo):
                    e              = StreamFormatEntry()
                    e.Semantic     = sem
                    e.Type         = ftype
                    e.UsageOrdinal = 0
                    entries.append(e)
                
                return self._make_fake_format_from_entries(entries)
        
        return None

    # make a fake StreamFormat node with existing entries
    def _make_fake_format_from_entries(self, entries):
        fake_ri                    = ResourceInfo()
        fake_ri.m_ResourceId       = ResourceIdentifier()
        fake_ri.m_ResourceId.m_UID = 0
        
        sf                         = StreamFormat()
        sf.m_Base                  = StreamFormatBase()
        sf.m_Base.Entries          = entries
        sf.m_Base.EntryCount       = len(entries)
        
        fake_ri.ResourceData       = type("obj", (object,), {"m_StreamFormat": sf})()
        
        return fake_ri
    
    # make a StreamFormat placeholder
    def _make_fake_format(self, *args):
        entries = []
        
        for i in range(0, len(args), 2):
            e              = StreamFormatEntry()
            e.Semantic     = args[i]
            e.Type         = args[i + 1]
            e.UsageOrdinal = 0
            
            entries.append(e)
        
        return self._make_fake_format_from_entries(entries)
    
    # heurstic for index buffer
    def _resolve_index_format(self, mat):
        if mat.get("ib_stream_format") is not None:
            return
        
        ib = mat["index_buffer"]
        if ib is None:
            mat["ib_stream_format"] = False
            return

        # search using deps
        for dep in ib.m_pDependancies:
            if dep.Packed.Type == ResourceTypeId.RTUID_STREAM_FORMAT:
                fmt = self.get_resource_by_id(dep.m_UID)
                if fmt is not None:
                    mat["ib_stream_format"] = fmt
                    return

        # heuristic by stride
        stride = ib.ResourceData.m_IndexBuffer.m_Base.ElementSizeInBytes
        if stride == 2:
            ft = FieldType.FT_INDEX_16
        
        elif stride == 4:
            ft = FieldType.FT_INDEX_32
        
        else:
            mat["ib_stream_format"] = False
            return

        mat["ib_stream_format"] = self._make_fake_format(FieldSemantic.FS_INDEX, ft)
    
    # read all required meta information about meshes and its subresources and collect into scene
    def build_scene(self):
        meshes = self.get_resources_by_type(ResourceTypeId.RTUID_MESH)

        if not meshes:
            return

        for ctr, mesh in enumerate(meshes, 1):
            mesh_name              = mesh.ResourceNames[0]
            mesh_materials         = {}
            current_material_name  = None
            current_vertex_streams = {}
            current_index_stream   = None

            # grab render commands
            all_commands = []
            
            # usually no more 5 commands
            for list_name in [f"UnkCommandList{i}" for i in range(1, 5)]:
                cmd_list_obj = getattr(mesh.ResourceData.m_Mesh, list_name, None)
                
                if cmd_list_obj is not None and hasattr(cmd_list_obj, "RenderCommands"):
                    all_commands.extend(cmd_list_obj.RenderCommands)
            
            if hasattr(mesh.ResourceData.m_Mesh, "CommandLists"):
                for cmd_list in mesh.ResourceData.m_Mesh.CommandLists:
                    if hasattr(cmd_list, "RenderCommands"):
                        all_commands.extend(cmd_list.RenderCommands)

            if not all_commands:
                continue

            # define a format cache for vertex buffer pairs to prevent a repeated call for heuristic
            format_cache = {}

            for cmd in all_commands:
                match cmd.Command_:
                    case 4:  # VERTEX_STREAM_SET
                        current_vertex_streams[cmd.RenderCommandVertexStreamSet.StreamID] = self.get_resource_by_id(cmd.RenderCommandVertexStreamSet.VertexBufferID.m_UID)

                    case 5:  # INDEX_STREAM_SET
                        current_index_stream = self.get_resource_by_id(cmd.RenderCommandIndexStreamSet.IndexBufferID.m_UID)

                    # currently, all materials are now generated placeholders
                    # due to unknown format of Material resource (it's known only for Motorstorm Apocalypse, not for DriveClub, they're different)
                    case 3:  # MATERIAL_SET
                        mat_id = cmd.RenderCommandMaterialSet.m_UID.m_UID
                        mat_res = self.get_resource_by_id(mat_id)
                        
                        if mat_res is not None and mat_res.ResourceNames:
                            current_material_name = mat_res.ResourceNames[0]
                        
                        else:
                            current_material_name = f"0x{mat_id:X}"

                        # add material if not added before
                        if current_material_name not in mesh_materials:
                            mesh_materials[current_material_name] = {"draw_calls": [], "_seen_dc": set()}

                    case 2:  # DRAW_INDEXED
                        if current_material_name is None:
                            continue

                        mat = mesh_materials[current_material_name]

                        if not current_vertex_streams or current_index_stream is None:
                            continue

                        vo = cmd.RenderCommandDrawIndexed.VertexOffset
                        vc = cmd.RenderCommandDrawIndexed.VertexCount
                        io = cmd.RenderCommandDrawIndexed.IndexOffset
                        ic = cmd.RenderCommandDrawIndexed.IndexCount

                        # make a dedup key with streams
                        vb_uids = tuple(
                            (sid, vb_res.m_ResourceId.m_UID)
                            for sid, vb_res in current_vertex_streams.items()
                        )
                        ib_uid = current_index_stream.m_ResourceId.m_UID
                        dc_key = (vo, vc, io, ic, vb_uids, ib_uid)

                        if dc_key in mat["_seen_dc"]:
                            continue
                        
                        mat["_seen_dc"].add(dc_key)

                        # get/calc formats for this set of VB and IB
                        cache_key = (vb_uids, ib_uid)
                        if cache_key not in format_cache:
                            # make a tmp obj to send into heur
                            tmp_mat = {
                                "vertex_streams":    dict(current_vertex_streams),
                                "vb_stream_formats": {},
                                "index_buffer":      current_index_stream,
                                "ib_stream_format":  None
                            }
                            
                            self._resolve_vertex_formats(tmp_mat, vo)
                            self._resolve_index_format(tmp_mat)
                            
                            format_cache[cache_key] = {
                                "vb_stream_formats": tmp_mat["vb_stream_formats"],
                                "ib_stream_format":  tmp_mat["ib_stream_format"]
                            }
                        
                        formats = format_cache[cache_key]

                        # save draw call with full data
                        mat["draw_calls"].append({
                            "vertex_offset":     vo,
                            "vertex_count":      vc,
                            "index_offset":      io,
                            "index_count":       ic,
                            "vertex_streams":    dict(current_vertex_streams),
                            "index_buffer":      current_index_stream,
                            "vb_stream_formats": formats["vb_stream_formats"],
                            "ib_stream_format":  formats["ib_stream_format"]
                        })

                    case 0:  # END
                        pass

                    case _:
                        print(f"  [WARNING] Unknown command {cmd.Command_.name}")

            self.scene[mesh_name] = mesh_materials
    
    # find a LayerCollection which wraps the given Collection
    def _find_layer_collection(self, layer_coll, coll):
        if layer_coll.collection == coll:
            return layer_coll

        for child in layer_coll.children:
            found = self._find_layer_collection(child, coll)
            if found is not None:
                return found

        return None

    # make the per-import collection active in the outliner
    def activate_target_collection(self, context):
        if self._target_coll is None:
            return

        layer_coll = self._find_layer_collection(context.view_layer.layer_collection, self._target_coll)
        if layer_coll is not None:
            context.view_layer.active_layer_collection = layer_coll
    
    # return the per-import collection
    def _get_target_collection(self):
        if not self.use_coll:
            return None

        if self._target_coll is None:
            coll = bpy.data.collections.new(self.coll_name)
            bpy.context.scene.collection.children.link(coll)
            self._target_coll = coll

        return self._target_coll

    # link obj into the per-import collection if needed or into default collection otherwise
    def _link_object(self, obj, fallback_coll):
        coll = self._get_target_collection()
        
        if coll is None:
            coll = fallback_coll

        if obj.name not in coll.objects:
            coll.objects.link(obj)
    
    # create dummies
    def create_hierarchy_empties(self, hier, import_lod0_only=False):
        if not hier._root_indices:
            raise RuntimeError("Hierarchy tree is not built. Call hier.build_tree() first.")

        path_to_obj = {}  # ["path"] = blender object

        G = self._GAME_TO_BLENDER
        G_inv = G.inverted()

        def process_node(node_idx):
            node      = hier.Nodes[node_idx]
            comps     = node.get_path_components()

            # skip other LODs and collision meshes if "Import LOD0 only" is enabled
            if import_lod0_only and re.search(r"_LOD\d|_SHADOW", node.shortName):
                return
            
            # make a object
            obj = bpy.data.objects.new(node.shortName, None)
            obj.empty_display_type = "ARROWS"
            obj.empty_display_size = 0.05

            # get node's local matrix
            m = node.defaultLocalToParent
            mat_game = Matrix((m.mCol0, m.mCol1, m.mCol2, m.mCol3)).transposed()

            # G * M * G^-1
            mat_blender = G @ mat_game @ G_inv

            # find parent
            if len(comps) > 1:
                parent_path = "/" + "/".join(comps[:-1])
                parent_obj = path_to_obj.get(parent_path)
                if parent_obj:
                    obj.parent = parent_obj
                else:
                    print(f"Warning: parent not found for {node.shortName} (path: {parent_path})")

            # set full local matrix
            obj.rotation_mode = "QUATERNION"
            obj.matrix_basis = mat_blender

            # add to scene
            self._link_object(obj, bpy.context.scene.collection)
            path_to_obj["/" + "/".join(comps)] = obj

            # process childrens
            for child_idx in node.children:
                process_node(child_idx)

        # process all children
        for root_idx in hier._root_indices:
            process_node(root_idx)

        self._path_to_obj = path_to_obj
        return path_to_obj
    
    # check if all dummies has parent
    def ensure_parent_empties(self, import_lod0_only=False):
        if not self._path_to_obj:
            raise RuntimeError("path_to_obj is empty. Run create_hierarchy_empties first.")
        
        # grab all required parent paths
        required_parents = set()
        for full_name in self.scene.keys():
            if import_lod0_only and re.search(r"_LOD\d|_SHADOW", full_name):
                continue
            
            norm_name = full_name.strip("|").replace("|", "/")
            if not norm_name.startswith("/"):
                norm_name = "/" + norm_name
            
            parent_path = "/".join(norm_name.split("/")[:-1])
            if parent_path and parent_path != "/":
                required_parents.add(parent_path)

        # check for all components must exist for all parent paths
        for parent_path in sorted(required_parents, key=lambda p: p.count("/")):
            components = parent_path.strip("/").split("/")
            
            # find nearest exisiting parent
            for i in range(len(components)-1, -1, -1):
                ancestor = "/" + "/".join(components[:i+1])
                
                if ancestor in self._path_to_obj:
                    break
            else:
                ancestor = None

            # start from first absent component
            start_idx = i + 1 if ancestor else 0
            current_parent_path = ancestor if ancestor else ""

            for j in range(start_idx, len(components)):
                if current_parent_path:
                    new_path = f"{current_parent_path}/{components[j]}"
                else:
                    new_path = f"/{components[j]}"

                # go to next if exists
                if new_path in self._path_to_obj:
                    current_parent_path = new_path
                    continue

                # make an object
                obj                    = bpy.data.objects.new(components[j], None)
                obj.empty_display_type = "ARROWS"
                obj.empty_display_size = 0.1

                # set parent
                if current_parent_path:
                    parent_obj = self._path_to_obj.get(current_parent_path)
                    if parent_obj:
                        obj.parent = parent_obj

                # link to scene
                self._link_object(obj, bpy.context.scene.collection)
                self._path_to_obj[new_path] = obj
                current_parent_path = new_path

    # create meshes in blender
    def build_meshes(self, import_lod0_only=False):
        if not self.scene:
            return {"CANCELLED"}
        
        # check if scene has hierarchy (it's required to relink the meshes)
        if not self._path_to_obj:
            raise RuntimeError("Path-to-object map not found. Run create_hierarchy_empties first.")
        
        # rotation-only (3x3): convert axis for positions and normals from game's system to blender's system
        G3 = self._GAME_TO_BLENDER.to_3x3()
        
        # process meshes
        print("\n")
        for full_name, mesh_materials in self.scene.items():
            if import_lod0_only and re.search(r"_LOD\d|_SHADOW", full_name):
                continue
            
            # get a short name
            short_name = full_name.split("|")[-1]
            
            print(f"[INFO] Importing: {short_name}")
            
            # define buffers
            all_positions         = []
            all_normals           = []
            all_uv_layers         = {} # uv_ord -> values list for vertices
            all_colors            = {} # same as uv
            all_faces             = []
            face_material_indices = []
            material_slots        = []

            current_vertex_offset = 0

            for mat_name, mat_data in mesh_materials.items():
                if not mat_data.get("triangles"):
                    continue

                positions   = mat_data["vertices"]["positions"]
                normals     = mat_data["vertices"]["normals"]
                uv_dict     = mat_data["vertices"]["uv"]
                colors_dict = mat_data["vertices"]["colors"]

                if not positions:
                    continue
                
                # positions
                clean_pos = []
                for p in positions:
                    clean_pos.append(tuple(G3 @ Vector((p[0], p[1], p[2]))))
                
                # normals
                clean_norm = []
                for n in normals:
                    v = G3 @ Vector((n[0], n[1], n[2]))
                    
                    if v.length > 0.0:
                        v.normalize()
                    
                    clean_norm.append(tuple(v))
                
                # UV
                clean_uv = {}
                for uv_ord, uv_list in uv_dict.items():
                    clean_uv[uv_ord] = []
                    
                    for uv in uv_list:
                        clean_uv[uv_ord].append((uv[0], uv[1]))

                # vertex colors
                clean_col = {}
                for col_ord, col_list in colors_dict.items():
                    clean_col[col_ord] = []
                    
                    for col in col_list:
                        clean_col[col_ord].append((col[0], col[1], col[2], col[3]))
                
                # append to buffers
                all_positions.extend(clean_pos)
                all_normals.extend(clean_norm)
                
                # prepare uv layers
                for uv_ord, uv_data in clean_uv.items():
                    if uv_ord not in all_uv_layers:
                        all_uv_layers[uv_ord] = []
                    
                    all_uv_layers[uv_ord].extend(uv_data)

                # prepare color layers
                for col_ord, col_data in clean_col.items():
                    if col_ord not in all_colors:
                        all_colors[col_ord] = []
                    
                    all_colors[col_ord].extend(col_data)
                
                # prepare face indices
                for tri in mat_data["triangles"]:
                    new_tri = (tri[2] + current_vertex_offset,
                               tri[1] + current_vertex_offset,
                               tri[0] + current_vertex_offset)
                    
                    all_faces.append(new_tri)
                    face_material_indices.append(len(material_slots))

                material_slots.append(mat_name)
                
                current_vertex_offset += len(clean_pos)

            # create mesh
            mesh = bpy.data.meshes.new(short_name)
            mesh.from_pydata(all_positions, [], all_faces, False)
            mesh.validate()
            
            vertex_count = len(all_positions)

            loop_vi = [0] * len(mesh.loops)
            mesh.loops.foreach_get("vertex_index", loop_vi)

            # apply normals
            if all_normals:
                mesh.normals_split_custom_set_from_vertices(all_normals)

            # apply uv
            for uv_ord, uv_data in sorted(all_uv_layers.items()):
                if len(uv_data) < vertex_count:
                    uv_data = uv_data + [(0.0, 0.0)] * (vertex_count - len(uv_data))
                
                uv_layer = mesh.uv_layers.new(name=f"UVMap_{uv_ord}")
                uv_layer.data.foreach_set("uv", [c for vi in loop_vi for c in uv_data[vi]])

            # apply colors
            for col_ord, col_data in sorted(all_colors.items()):
                if len(col_data) < vertex_count:
                    col_data = col_data + [(0.0, 0.0, 0.0, 1.0)] * (vertex_count - len(col_data))
                
                attr = mesh.color_attributes.new(name=f"VCol_{col_ord}", type="FLOAT_COLOR", domain="POINT")
                attr.data.foreach_set("color", [c for col in col_data for c in col])
            
            # fix disrepancies caused by degenerate faces
            num_polygons = len(mesh.polygons)
            if len(face_material_indices) != num_polygons:
                if len(face_material_indices) > num_polygons:
                    face_material_indices = face_material_indices[:num_polygons]
                
                else:
                    face_material_indices.extend([face_material_indices[-1]] * (num_polygons - len(face_material_indices)))
            
            # apply materials
            for mat_name in material_slots:
                mat = bpy.data.materials.get(mat_name)
                
                if not mat:
                    mat = bpy.data.materials.new(mat_name)
                
                mesh.materials.append(mat)

            mesh.polygons.foreach_set("material_index", face_material_indices)
            
            # create object in scene
            mesh.update()
            obj = bpy.data.objects.new(short_name, mesh)
            
            # get parent for mesh
            norm_name = full_name.strip("|").replace("|", "/")
            
            if not norm_name.startswith("/"):
                norm_name = "/" + norm_name
            
            parent_path = "/".join(norm_name.split("/")[:-1])
            parent_obj = self._path_to_obj.get(parent_path)
            
            # relink to parent
            if parent_obj:
                obj.parent = parent_obj

            # relink to collection
            self._link_object(obj, bpy.context.collection)
        
        return {"FINISHED"}
    
    # convert index buffer type
    def convert_indices_to_triangles(self, local_indices, mode='auto', force_strip=False):
        if len(local_indices) < 3:
            return []

        if mode == "auto":
            has_duplicate_pairs = any(
                local_indices[i] == local_indices[i + 1] 
                for i in range(len(local_indices) - 1)
            )
            
            if not has_duplicate_pairs and not force_strip:
                mode = "list"
            else:
                mode = "strip"

        triangles = []

        if mode == "list":
            for i in range(0, len(local_indices) - 2, 3):
                a, b, c = local_indices[i], local_indices[i + 1], local_indices[i + 2]
                
                if a != b and b != c and a != c:
                    triangles.append((a, b, c))

        elif mode == "strip":
            splits = []
            
            for i in range(len(local_indices) - 1):
                if local_indices[i] == local_indices[i + 1]:
                    splits.append(i)
            
            starts = [0]
            
            for sp in splits:
                starts.append(sp + 2)
            
            ends = splits + [len(local_indices)]
            
            for start, end in zip(starts, ends):
                strip = local_indices[start:end]
                
                if len(strip) < 3:
                    continue
                
                for i in range(len(strip) - 2):
                    a, b, c = strip[i], strip[i + 1], strip[i + 2]
                    if a == b or b == c or a == c:
                        continue
                    
                    if i % 2 == 0:
                        triangles.append((a, b, c))
                    
                    else:
                        triangles.append((a, c, b))

        elif mode == "fan":
            for i in range(1, len(local_indices) - 1):
                a = local_indices[0]
                b = local_indices[i]
                c = local_indices[i + 1]
                
                if a != b and b != c and a != c:
                    triangles.append((a, b, c))

        return triangles

    # read data from buffers
    def read_scene(self, import_lod0_only=False):
        if not self.scene:
            return

        all_mesh_names = list(self.scene.keys())
        last_mesh_name = all_mesh_names[-1] if all_mesh_names else None
        
        for mesh_name, mesh_materials in self.scene.items():
            if import_lod0_only and re.search(r"_LOD\d|_SHADOW", mesh_name):
                continue
            
            print(f"[INFO] Reading geometry for mesh: {mesh_name}")
            for mat_name, mat_data in mesh_materials.items():
                draw_calls = mat_data.get("draw_calls", [])
                if not draw_calls:
                    continue

                # define a storage
                mat_data["vertices"] = {
                    "positions": [],
                    "normals":   [],
                    "uv":        {},
                    "colors":    {}
                }
                mat_data["triangles"] = []
                
                base_vertex_index = 0

                # dedup init
                seen_dc = set()
                dc_used = False  # true if first unique draw call is already processed

                for dc_idx, dc in enumerate(draw_calls):
                    if dc_used:
                        break

                    vo = dc["vertex_offset"]
                    vc = dc["vertex_count"]
                    io = dc["index_offset"]
                    ic = dc["index_count"]

                    # make a dedup
                    vb_uids = tuple(
                        (sid, vb_res.m_ResourceId.m_UID)
                        for sid, vb_res in dc.get("vertex_streams", {}).items()
                    )
                    ib_uid = dc.get("index_buffer").m_ResourceId.m_UID if dc.get("index_buffer") else None
                    dc_key = (vo, vc, io, ic, vb_uids, ib_uid)
                    
                    if dc_key in seen_dc:
                        continue
                    
                    seen_dc.add(dc_key)
                    dc_used = True

                    num_verts = vc - vo + 1 if vc >= vo else 0

                    vertex_streams = dc.get("vertex_streams", {})
                    index_buffer   = dc.get("index_buffer")
                    vb_formats     = dc.get("vb_stream_formats", {})
                    ib_format      = dc.get("ib_stream_format")

                    if not vertex_streams or index_buffer is None or not vb_formats or ib_format is None:
                        continue

                    # read vertex buffer data
                    for stream_idx in sorted(vertex_streams.keys()):
                        vb_res = vertex_streams[stream_idx]
                        sf_res = vb_formats.get(stream_idx)
                        
                        if sf_res is None:
                            continue
                        
                        stride = vb_res.ResourceData.m_VertexBuffer.m_Base.ElementSizeInBytes
                        byte_start = vo * stride
                        data_slice = vb_res.ResourceData.m_VertexBuffer.m_Base.Data[byte_start : byte_start + num_verts * stride]
                        raw = StreamReader(data_slice)
                        total_verts = raw.length // stride

                        for _ in range(total_verts):
                            for entry in sf_res.ResourceData.m_StreamFormat.m_Base.Entries:
                                # vertex
                                v = None
                                
                                match entry.Type:
                                    case 3:  v = raw.read_float16()
                                    case 4:  v = raw.read_float16_array(2)
                                    case 5:  v = raw.read_float16_array(3)
                                    case 6:  v = raw.read_float16_array(4)
                                    case 7:  v = raw.read_float32()
                                    case 8:  v = raw.read_float32_array(2)
                                    case 9:  v = raw.read_float32_array(3)
                                    case 10: v = raw.read_float32_array(4)
                                    case 11: v = raw.read_float64()
                                    case 12: v = raw.read_float64_array(2)
                                    case 13: v = raw.read_float64_array(3)
                                    case 14: v = raw.read_float64_array(4)
                                    case 15: v = raw.read_dec3n()
                                    case 16: v = raw.read_11bitN()
                                    case 17: v = raw.read_uint8_array(4)
                                    case 18: v = raw.read_uint8_array(4)
                                    case 19: v = raw.read_uint8_array(4)
                                    case 20: v = raw.read_int8_array(4)

                                match entry.Semantic:
                                    case 1:  # POSITION
                                        mat_data["vertices"]["positions"].append(v)
                                    
                                    case 2:  # NORMAL
                                        mat_data["vertices"]["normals"].append(v)
                                    
                                    case 5:  # TEXCOORD
                                        uv_ord = entry.UsageOrdinal
                                        mat_data["vertices"]["uv"].setdefault(uv_ord, []).append(v)
                                    
                                    case 6:  # COLOR
                                        col_ord = entry.UsageOrdinal
                                        mat_data["vertices"]["colors"].setdefault(col_ord, []).append(v)
                    
                    # read indices
                    ib_stride = index_buffer.ResourceData.m_IndexBuffer.m_Base.ElementSizeInBytes
                    ib_byte_start = io * ib_stride
                    raw_inds = StreamReader(index_buffer.ResourceData.m_IndexBuffer.m_Base.Data[ib_byte_start : ib_byte_start + ic * ib_stride])

                    dc_indices = []
                    for entry in ib_format.ResourceData.m_StreamFormat.m_Base.Entries:
                        if entry.Semantic == 9:  # FS_INDEX
                            for _ in range(ic):
                                match entry.Type:
                                    case 1: raw_idx = raw_inds.read_uint16()
                                    case 2: raw_idx = raw_inds.read_uint32()
                                
                                local_idx = raw_idx - vo
                                dc_indices.append(local_idx + base_vertex_index)
                    
                    # force convert to triangle list
                    tris = self.convert_indices_to_triangles(dc_indices, mode="list")
                    mat_data["triangles"].extend(tris)

                # warn if there's no geometry
                if not mat_data["triangles"]:
                    print(f"[WARNING] There's no geometry for {mat_name}.")
    
    # convert all textures to .dds (DX10) and save to disk
    def export_textures(self, in_path, top_mips_mode=False):
        pbs = self.get_resources_by_type(ResourceTypeId.RTUID_PIXEL_BUFFER)
        
        print(f"\n[INFO] Found {len(pbs)} textures.\n")
        
        for i in range(len(pbs)):
            # shortened call for current PixelBuffer
            pb = pbs[i]
            
            # get topmips data
            top_mips_resid = pb.ResourceData.m_PixelBuffer.m_Base.TopMipsResrcIdentifier.m_UID
            top_mips_res   = self.get_resource_by_id(top_mips_resid)
            
            # get texture name without extension
            tex_name       = Path(pb.ResourceNames[0]).stem
            
            # build output directory path and output file path
            target_dir = in_path.parent / f"{in_path.stem}_textures"
            target_dir.mkdir(parents=True, exist_ok=True)
            target_path = target_dir / f"{tex_name!s}.dds"
            
            # define some vars and check if we have a top mips resource
            tPtr = None
            data = None
            if top_mips_res:
                print(f"[INFO] Found TopMips resource for \"{tex_name}\"")
                
                # define short call to a topmips pointer if exists
                tPtr         = top_mips_res.ResourceData.m_TopMips
            
            else:
                print(f"[WARNING] No TopMips found for \"{tex_name}\"")
            
            if isinstance(pb, GenericResource):
                print(f"[INFO] Found non-parsed texture \"{tex_name}\" (ver=0x{pb.ResourceData.m_Generic.m_VersionNumber}), export as raw data...")
                with open(str(target_dir / f"{tex_name}_rawData.bin"), "wb") as raw:
                    raw.write(pb.ResourceData.m_Generic.m_rawData)
            
            else:
                # define a short call to main pointer
                mPtr             = pb.ResourceData.m_PixelBuffer.m_Base
                print(f"[INFO] Texture \"{tex_name}\" ({mPtr.m_WriteWidth}x{mPtr.m_WriteHeight}, {mPtr.m_PixelFormat.name}, ver=0x{pb.ResourceData.m_PixelBuffer.m_VersionNumber:X})")
                
                dxgi_format      = PS4Texture.pixel_format_to_dxgi_format(mPtr.m_PixelFormat)
                pixels_per_block = PS4Texture.pixels_per_block(dxgi_format)
                bpp              = PS4Texture.bits_per_pixel(dxgi_format)
                block_size       = bpp / 8 if pixels_per_block == 1 else bpp * 2
                
                # if startMip != 0 then the pixel buffer should have a top mips
                # but if it's not then just work with main buffer
                if mPtr.m_StartMip != 0:
                    if top_mips_res:
                        data = PS4Texture.swizzle(tPtr.Data,      mPtr.m_WriteWidth, mPtr.m_WriteHeight, pixels_per_block, block_size)
                        lowd = PS4Texture.swizzle(mPtr.ImageData, mPtr.m_WriteWidth, mPtr.m_WriteHeight, pixels_per_block, block_size)
                    else:
                        data = PS4Texture.swizzle(mPtr.ImageData, mPtr.m_WriteWidth, mPtr.m_WriteHeight, pixels_per_block, block_size)
                
                # no top mips?
                else:
                    data = PS4Texture.swizzle(mPtr.ImageData, mPtr.m_WriteWidth, mPtr.m_WriteHeight, pixels_per_block, block_size)
                
                print(f"[INFO] Exporting texture {i + 1}/{len(pbs)}: {target_path.name!s}...\n")
                
                with open(str(target_path), "wb") as f:
                    # write first part of the header
                    f.write(struct.pack("<I", 0x20534444))                                      # dwMagic
                    f.write(struct.pack("<I", 124))                                             # dwSize
                    
                    if mPtr.m_MipLevels > 1:                                                    # dwFlags
                        f.write(struct.pack("<I", DDS_FLAGS.TEXTURE | DDS_FLAGS.MIPMAPCOUNT | \
                                DDS_FLAGS.LINEARSIZE))
                    else:
                        f.write(struct.pack("<I", DDS_FLAGS.TEXTURE | DDS_FLAGS.LINEARSIZE))
                    
                    f.write(struct.pack("<I", mPtr.m_WriteHeight))                              # dwHeight
                    f.write(struct.pack("<I", mPtr.m_WriteWidth))                               # dwWidth
                    
                    match mPtr.m_PixelFormat:                                                   # dwPitchOrLinearSize
                        case PixelFormat.DXT1_LIN | PixelFormat.DXT1_SRGB | \
                                PixelFormat.BC4_UNORM | PixelFormat.BC4_SNORM | \
                                PixelFormat.DXT3_LIN | PixelFormat.DXT3_SRGB | \
                                PixelFormat.DXT5_LIN | PixelFormat.DXT5_SRGB | \
                                PixelFormat.BC5_UNORM | PixelFormat.BC5_SNORM | \
                                PixelFormat.BC6H_UF | PixelFormat.BC6H_SF | \
                                PixelFormat.BC7_UNORM | PixelFormat.BC7_SRGB:
                            f.write(struct.pack("<I", int(max(1, ((mPtr.m_WriteWidth + 3) // 4)) * bpp)))
                        
                        case _:
                            f.write(struct.pack("<I", int((mPtr.m_WriteWidth * bpp + 7) // 8)))
                    
                    if mPtr.m_Type == PixelBufferBase_Type.TEXTURE_2D:                          # dwDepth
                        f.write(struct.pack("<I", 0))
                    else:
                        f.write(struct.pack("<I", mPtr.m_Depth))
                    
                    f.write(struct.pack("<I", mPtr.m_MipLevels))                                # dwMipMapCount
                    f.write(struct.pack("<11I", *[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]))            # dwReserved1

                    # write DDS_PIXELFORMAT
                    f.write(struct.pack("<I", 32))                                              # dwSize
                    f.write(struct.pack("<I", PF_FLAGS.FOURCC))                                 # dwFlags
                    f.write(struct.pack("<I", 0x30315844))                                      # dwFourCC (DX10)
                    f.write(struct.pack("<I", 0))                                               # dwRGBBitCount
                    f.write(struct.pack("<I", 0))                                               # dwRBitMask
                    f.write(struct.pack("<I", 0))                                               # dwGBitMask
                    f.write(struct.pack("<I", 0))                                               # dwBBitMask
                    f.write(struct.pack("<I", 0))                                               # dwABitMask

                    # write second part of the header
                    if mPtr.m_MipLevels > 1:                                                    # dwCaps
                        f.write(struct.pack("<I", DDSCAPS.COMPLEX | DDSCAPS.MIPMAP | \
                                DDSCAPS.TEXTURE))
                    else:
                        f.write(struct.pack("<I", DDSCAPS.COMPLEX | DDSCAPS.TEXTURE))
                    
                    f.write(struct.pack("<I", 0))                                               # dwCaps2
                    f.write(struct.pack("<I", 0))                                               # dwCaps3
                    f.write(struct.pack("<I", 0))                                               # dwCaps4
                    f.write(struct.pack("<I", 0))                                               # dwReserved2

                    # write DDS_HEADER_DX10
                    f.write(struct.pack("<I", dxgi_format))                                     # dxgiFormat
                    
                    if mPtr.m_Type == PixelBufferBase_Type.TEXTURE_2D:
                        f.write(struct.pack("<I", D3D11_RESOURCE_DIMENSION.TEXTURE2D))          # resourceDimension
                        f.write(struct.pack("<I", 0))                                           # miscFlag
                        f.write(struct.pack("<I", 0))                                           # arraySize
                        f.write(struct.pack("<I", 0))                                           # miscFlags2
                    
                    elif mPtr.m_Type == PixelBufferBase_Type.TEXTURE_3D:
                        f.write(struct.pack("<I", D3D11_RESOURCE_DIMENSION.TEXTURE3D))
                        f.write(struct.pack("<I", 0))
                        f.write(struct.pack("<I", 1))
                        f.write(struct.pack("<I", 0))

                    # write texture data
                    if mPtr.m_StartMip != 0:
                        if top_mips_res:
                            f.write(data + lowd)
                        
                        else:
                            f.write(data)
                    else:
                        f.write(data)

        return {"FINISHED"}

