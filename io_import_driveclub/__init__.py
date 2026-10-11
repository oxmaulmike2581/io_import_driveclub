from pathlib import Path

from .InGameStructs.Resource.ResourceTypeId import ResourceTypeId
from .SceneContext import SceneContext

# Blender-specific
import bpy
import bpy.utils.previews
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty
from bpy.types import Operator

bl_info = {
    "name":        "DriveClub Model Importer",
    "author":      "oxmaulmike2581",
    "version":     (1, 0, 0),
    "blender":     (4, 1, 0),
    "location":    "File > Import",
    "description": "Import 3D models from DriveClub",
    "category":    "Import-Export",
}

# global variables
_registered_classes = []
_menu_handler_added = False
preview_collections = {}

# custom icons management
def load_custom_icons():
    global preview_collections
    
    old = preview_collections.pop("main", None)
    if old is not None:
        bpy.utils.previews.remove(old)

    pcoll = bpy.utils.previews.new()
    icons_dir = Path(__file__).parent / "UI"

    if icons_dir.is_dir():
        for icon_path in icons_dir.iterdir():
            if icon_path.suffix.lower() == ".png":
                pcoll.load(icon_path.stem, str(icon_path), "IMAGE")

    preview_collections["main"] = pcoll

def unload_custom_icons():
    global preview_collections
    
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    
    preview_collections.clear()

class IMPORT_SCENE_OT_rpk(Operator, ImportHelper):
    bl_idname      = "import_scene.rpk"
    bl_label       = "Import"
    bl_description = "Import 3D models from DriveClub"
    bl_options     = {"REGISTER", "UNDO"}

    filename_ext = ".rpk"
    filter_glob: StringProperty(
        default="*.rpk",
        options={"HIDDEN"},
        maxlen=255,
    )
    
    import_lod0_only: BoolProperty(
        name="Import LOD0 only",
        description="Import only the highest detail level (LOD0)",
        default=True,
    )
    
    export_textures: BoolProperty(
        name="Export textures",
        description="Export textures to DDS (DX10) when import",
        default=True,
    )
    
    def draw(self, context):
        layout = self.layout
        
        layout.prop(self, "import_lod0_only")
        layout.prop(self, "export_textures")

    def execute(self, context):
        in_path = Path(self.filepath)
    
        # build scene context
        scene = SceneContext()
        
        # load main rpk first
        scene.load(in_path)
        
        # try to load top mips rpk as shared rpk
        topmips_rpk_path = in_path.parent / f"{in_path.stem}_top_mips.rpk"
        
        # trying suffix used for track rpks
        if not topmips_rpk_path.exists():
            topmips_rpk_path = in_path.parent / f"{in_path.stem}_topmips.rpk"
        
        if topmips_rpk_path.exists():
            scene.add_shared_rpk(topmips_rpk_path)
            scene.load_shared_rpks()
        
        # get hierarchy resource
        hier = scene.get_resources_by_type(ResourceTypeId.RTUID_HIERARCHY)[0].ResourceData.m_Hierarchy
        
        # build hierarchy data
        hier.build_path_index()
        disc = hier.validate_parent_links()
        hier.ensure_paths(scene.scene)
        hier.build_tree()
        
        # get scene meta information
        scene.build_scene()
        
        # read geometry data for meshes
        scene.read_scene(self.import_lod0_only)
        
        # import into Blender
        result = None
        try:
            # create hierarchy
            scene.create_hierarchy_empties(hier, self.import_lod0_only)
            
            # validate parent nodes for meshes
            scene.ensure_parent_empties(self.import_lod0_only)
            
            # import meshes
            result = scene.build_meshes(self.import_lod0_only)
            
        except Exception as e:
            self.report({"ERROR"}, f"[ERROR]: {e}")
        
        if result == {"FINISHED"}:
            self.report({"INFO"}, f"Imported: {self.filepath}")
        else:
            self.report({"ERROR"}, "Mesh import failed.")
        
        # export textures
        if self.export_textures:
            self.report({"INFO"}, "Exporting textures...")
            scene.export_textures(in_path)
        
        return result

def menu_func_import(self, context):
    # get icon or fallback to empty
    pcoll = preview_collections.get("main")
    icon_value = pcoll["icon"].icon_id if pcoll and "icon" in pcoll else 0
    
    # add to menu
    self.layout.operator(IMPORT_SCENE_OT_rpk.bl_idname, text="DriveClub (.rpk)", icon_value=icon_value)

def register():
    global _menu_handler_added
    
    # load icons
    load_custom_icons()
    
    # check if already registered to prevent errors on hot reload
    if IMPORT_SCENE_OT_rpk.is_registered:
        try:
            bpy.utils.unregister_class(IMPORT_SCENE_OT_rpk)
        except RuntimeError:
            pass
    
    # then try to register
    try:
        bpy.utils.register_class(IMPORT_SCENE_OT_rpk)
    except Exception as e:
        print(f"[ERROR] Failed to register {IMPORT_SCENE_OT_rpk.__name__}: {e}")
    
    # mark as registered only if class was really registered
    if IMPORT_SCENE_OT_rpk.is_registered:
        _registered_classes.append(IMPORT_SCENE_OT_rpk)
    else:
        print(f"[WARNING] {IMPORT_SCENE_OT_rpk.__name__} reported no error but is not registered")
    
    # add our menu to list
    if not _menu_handler_added:
        bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
        _menu_handler_added = True
    
def unregister():
    global _menu_handler_added

    # remove menu from list
    if _menu_handler_added:
        try:
            bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
        except ValueError:
            pass
        _menu_handler_added = False

    # try to unregister
    while _registered_classes:
        cls = _registered_classes.pop()
        if cls.is_registered:
            try:
                bpy.utils.unregister_class(cls)
            except RuntimeError:
                pass
    
    # unload icons
    unload_custom_icons()

