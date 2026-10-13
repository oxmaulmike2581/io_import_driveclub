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
    "version":     (1, 0, 2),
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
class UIManager:
    def __init__(self):
        pass
    
    @staticmethod
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

    @staticmethod
    def unload_custom_icons():
        global preview_collections
        
        for pcoll in preview_collections.values():
            bpy.utils.previews.remove(pcoll)
        
        preview_collections.clear()

class IMPORT_SCENE_OT_dc_rpk(Operator, ImportHelper):
    bl_idname      = "import_scene.dc_rpk"
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
        description="Export textures to DDS (DX10) when import.\nThey'll be saved in a separate directory near .rpk!",
        default=True,
    )
    
    use_collection: BoolProperty(
        name="Create per-file collection",
        description="If enabled, will create a collection with input file name\nand place all scene entries into it,\notherwise will use a default collection.",
        default=False,
    )
    
    def draw(self, context):
        layout = self.layout
        
        layout.prop(self, "import_lod0_only")
        layout.prop(self, "export_textures")
        layout.prop(self, "use_collection")

    def execute(self, context):
        v = bl_info["version"]
        print(f"DriveClub Model Importer {v[0]}.{v[1]}.{v[2]}\n")
        
        in_path = Path(self.filepath)
        
        # protection against loading topmips as main
        if in_path.stem.endswith(("_top_mips", "_topmips")):
            print(f"[ERROR] Trying to load TopMips RPK as main RPK, exiting...")
            self.report({"ERROR"}, "Trying to load TopMips RPK as main RPK, exiting...")
            return {"CANCELLED"}
        
        # initial log
        print(f"[INFO] Processing {in_path.name}...\n")
    
        # build scene context
        scene = SceneContext(use_collection=self.use_collection, coll_name=in_path.stem)
        
        # load main rpk first
        scene.load(in_path)
        
        # try to load top mips rpk as shared rpk
        topmips_rpk_path = in_path.parent / f"{in_path.stem}_top_mips.rpk"
    
        # trying suffix used for track rpks
        if not topmips_rpk_path.exists():
            topmips_rpk_path = in_path.parent / f"{in_path.stem}_topmips.rpk"
        
        # add topmips rpk if file exists
        if topmips_rpk_path.exists():
            scene.add_shared_rpk(topmips_rpk_path)
        
        # load all shared RPKs
        scene.load_shared_rpks()
        
        # try to get hierarchy resources
        hier = None
        try:
            # this is valid only for vehicles
            # tracks have several hierarchies and of them should be loaded
            # so in theory my addon support tracks but it needs to be tweaked a bit
            # otherwise it will import only first part of the track
            # btw I found a hierarchy and material named "weedKiller" - OH GOD PLEASE NO!!
            #
            # UPD.:
            # - I've modified the script to load all hierarchy resources from rpk
            # - It loaded them fine but it has a bug:
            #   - for each hierarchy script will read and import ALL meshes from the RPK
            #   - I've tried to find the list of meshes needed to load but only I found are CRCs
            #   - I don't know the algorithm to calculate such checksum and don't know the source:
            #     - it can be a full mesh name, shortened mesh name, mesh raw data, resource id, etc.
            #   - I think that these CRCs can solve the problem but I need to (re)calculate them to verify the data
            # - Another problem is instancing: it's not implemented at all because it's not needed for vehicles
            # - So I need to implement instancing to proper load tracks without unneccessary memory wasting
            # - So I revert back this change and return default behavior - load only first hierarchy
            # - But ofc you can export the textures :)
            hier = scene.get_resources_by_type(ResourceTypeId.RTUID_HIERARCHY)[0].ResourceData.m_Hierarchy
        except Exception as e:
            print(f"[INFO] {in_path.name} seems to be a non-mesh package. Exception message: {e}.")
        
        # return value
        result = None
        
        # build hierarchy data
        if hier:
            hier.build_path_index()
            disc = hier.validate_parent_links()
            hier.ensure_paths(scene.scene)
            hier.build_tree()
        
            # get scene meta information
            scene.build_scene()
        
            # read geometry data for meshes
            scene.read_scene(self.import_lod0_only)
        
            # import into Blender
            try:
                # create hierarchy
                scene.create_hierarchy_empties(hier, self.import_lod0_only)
                
                # validate parent nodes for meshes
                scene.ensure_parent_empties(self.import_lod0_only)
                
                # import meshes
                result = scene.build_meshes(self.import_lod0_only)
                
                # activate collection
                scene.activate_target_collection(context)
                
            except Exception as e:
                self.report({"ERROR"}, f"[ERROR]: {e}")
        
        # export textures
        if self.export_textures:
            self.report({"INFO"}, "Exporting textures...")
            result = scene.export_textures(in_path)
        
        # report to blender
        if result == {"FINISHED"}:
            self.report({"INFO"}, f"Imported: {self.filepath}")
            print(f"[INFO] Successfully imported.")
        else:
            self.report({"ERROR"}, f"Import failed: {self.filepath}")
            print(f"[ERROR] Import failed.")
        
        # finish
        return result

def menu_func_dc_import(self, context):
    # get icon or fallback to empty
    pcoll = preview_collections.get("main")
    icon_value = pcoll["icon"].icon_id if pcoll and "icon" in pcoll else 0
    
    # add to menu
    self.layout.operator(IMPORT_SCENE_OT_dc_rpk.bl_idname, text="DriveClub (.rpk)", icon_value=icon_value)

def register():
    global _menu_handler_added
    
    # load icons
    UIManager.load_custom_icons()
    
    # define list of classes
    classes = (
        IMPORT_SCENE_OT_dc_rpk,
    )
    
    # check if already registered to prevent errors on hot reload
    for cls in classes:
        if cls.is_registered:
            try:
                bpy.utils.unregister_class(cls)
            except RuntimeError:
                pass
        
        # then try to register
        try:
            bpy.utils.register_class(cls)
        except Exception as e:
            print(f"[ERROR] Failed to register {cls.__name__}: {e}")
        
        # mark as registered only if class was really registered
        if cls.is_registered:
            _registered_classes.append(cls)
        else:
            print(f"[WARNING] {cls.__name__} reported no error but is not registered")
    
    # add our menu to list
    if not _menu_handler_added:
        bpy.types.TOPBAR_MT_file_import.append(menu_func_dc_import)
        _menu_handler_added = True

def unregister():
    global _menu_handler_added

    # remove menu from list
    if _menu_handler_added:
        try:
            bpy.types.TOPBAR_MT_file_import.remove(menu_func_dc_import)
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
    UIManager.unload_custom_icons()

