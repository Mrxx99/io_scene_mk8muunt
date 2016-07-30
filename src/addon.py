import addon_utils
import bmesh
import bpy
import mathutils
import os
from . import objflow

# ---- Globals ----

loaded_byaml = None  # The currently loaded BYAML file to reuse when exporting non-visualized objects.


def log(indent, text):
    indent = " " * 2 * indent
    print("MK8MUUNT: {}{}".format(indent, text))


def add_object_to_group(ob, group_name):
    # Get or create the required group.
    group = bpy.data.groups.get(group_name, bpy.data.groups.new(group_name))
    # Link the provided object to it.
    if ob.name not in group.objects:
        group.objects.link(ob)


def mk8_colbox(self, data, expand_property):
    # Creates an expandable and collapsible box for the UILayout.
    box = self.box()
    split = box.split(0.5)
    row = split.row(align=True)
    row.prop(data, expand_property, icon="TRIA_DOWN" if getattr(data, expand_property) else "TRIA_RIGHT",
             icon_only=True, emboss=False)
    row.label(getattr(data.rna_type, expand_property)[1]["name"])
    return box, split


# ---- Preferences ----

class MK8MuuntAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    def _get_game_path(self):
        return self.game_path

    def _set_game_path(self, value):
        # Check if at least a content folder exists as the child.
        if os.path.isdir(os.path.join(value, "content")):
            self.game_path = value
        else:
            raise AssertionError("The selected path does not have a 'content' subfolder. Please select the 'vol' directory of your Mario Kart 8 files.")

    # General
    game_path = bpy.props.StringProperty()
    game_path_ui = bpy.props.StringProperty(name="Mario Kart 8 Vol Directory Path", description="Path to the folder holding game content. 'content' and the DLC directory are children of this.", subtype='FILE_PATH', get=_get_game_path, set=_set_game_path)
    # Visualization
    lod_model_index = bpy.props.IntProperty(name="LoD Model Index", description="The index of the LoD model to use when importing Obj models. Lower means more detail.", min=0, default=1)
    import_all_textures = bpy.props.BoolProperty(name="Import All Textures", description="Additionally imports normal, specular and emissive rather than just diffuse textures.")
    # Interface
    show_unused_obj_params = bpy.props.BoolProperty(name="Show Unused Obj Parameters", description="When checked, all Obj parameters will be displayed, even known unused ones.")
    debug_mode = bpy.props.BoolProperty(name="Debug Mode", description="Displays additional info and adds tools useful to report and analyze errors.")

    def draw(self, context):
        box = self.layout.box()
        box.label("General Options:", icon='FILE_FOLDER')
        box.prop(self, "game_path_ui")
        box.prop(self, "debug_mode")
        box = self.layout.box()
        box.label("Visualization Options:", icon='RESTRICT_VIEW_OFF')
        row = box.row()
        if addon_utils.check("io_scene_bfres")[1]:
            row.prop(self, "lod_model_index")
            row.prop(self, "import_all_textures")
        else:
            row.label("io_scene_bfres not installed.", icon='ERROR')


# ---- App Handlers ----

_disable_handlers = False
_last_scene_ob_count = -1


@bpy.app.handlers.persistent
def scene_update_post(scene):
    # Prevent to get into endless loops when causing scene updates inside of the handler.
    global _disable_handlers
    if _disable_handlers:
        return
    _disable_handlers = True
    if scene.mk8.scene_type == "COURSE":
        # Ensure correct state when objects get added or deleted.
        global _last_scene_ob_count
        scene_ob_count = len(scene.objects)
        if len(scene.objects) != _last_scene_ob_count:
            _last_scene_ob_count = scene_ob_count
            # Iterate through all relevant scene objects.
            for ob in scene.objects:
                ob_type = ob.mk8.object_type
                if ob_type == "NONE":
                    continue
                elif ob_type == "OBJ":
                    # Attach visualizer models when they do not exist yet.
                    set_models(ob, ob.mk8.obj_id)
                elif ob_type == "ADDON_VISUALIZER" and ob.parent is None:
                    # Remove all visualizer mesh objects which lost their parent, as they are not removed when the parents get deleted.
                    bpy.context.scene.objects.unlink(ob)
                    bpy.data.objects.remove(ob)
        # Redirect the selection of an Obj visualizer model to the Obj object.
        if not bpy.context.user_preferences.addons[__package__].preferences.debug_mode:
            ob = scene.objects.active
            if ob and ob.mk8.object_type == "ADDON_VISUALIZER":
                scene.objects.active = ob.parent
                ob.parent.select = True
                ob.select = False
    _disable_handlers = False


# ---- Obj Models ----

def _create_mesh_area_cube():
    # Create a 100x100x100 cube, offset to sit on the XY axis.
    bm = bmesh.new()
    mx = mathutils.Matrix(((100, 0, 0, 0), (0, 100, 0, 0), (0, 0, 100, 50), (0, 0, 0, 1)))
    bmesh.ops.create_cube(bm, matrix=mx)
    # Create a mesh object of it and return it.
    mesh = bpy.data.meshes.new("MK8.AREACUBE")
    bm.to_mesh(mesh)
    bm.free()
    return mesh


def _create_mesh_area_sphere():
    # Create a 100x100x100 sphere, offset to sit on the XY axis.
    bm = bmesh.new()
    mx = mathutils.Matrix(((100, 0, 0, 0), (0, 100, 0, 0), (0, 0, 100, 50), (0, 0, 0, 1)))
    bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=10, diameter=0.5, matrix=mx)
    # Create a mesh object out of it and return it.
    mesh = bpy.data.meshes.new("MK8.AREASPHERE")
    bm.to_mesh(mesh)
    bm.free()
    return mesh


_default_meshes = {
    "AREACUBE": _create_mesh_area_cube,
    "AREASPHERE": _create_mesh_area_sphere
}


def get_default_mesh(name):
    # Get the mesh or load it if it does not exist yet.
    mesh = bpy.data.meshes.get("MK8.{}".format(name))
    if not mesh:
        default_mesh_creator = _default_meshes.get(name)
        if default_mesh_creator:
            mesh = default_mesh_creator()
    return mesh


_empty_models = []


def set_models(ob, name):
    # If possible, attach child mesh objects (requires models to be available, io_scene_bfres and no existing children).
    if name in _empty_models or not addon_utils.check("io_scene_bfres")[1] or len(ob.children):
        return
    # Get the model or load it if it does not exist yet.
    model_ob = bpy.data.objects.get("MK8.{}".format(name))
    if not model_ob:
        model_ob = _load_model(name)
        if not model_ob:
            log(0, "Warning: No model found for '{}'.".format(name))
            _empty_models.append(name)
            return
        model_ob.name = "MK8.{}".format(name)
    # Link-clone the child objects and attach them to the given parent.
    for child in model_ob.children:
        child_ob = bpy.data.objects.new(child.name, child.data)
        child_ob.mk8.object_type = "ADDON_VISUALIZER"
        child_ob.parent = ob
        child_ob.lock_location = [True] * 3
        child_ob.lock_rotation = [True] * 3
        child_ob.lock_scale = [True] * 3
        bpy.context.scene.objects.link(child_ob)
        bpy.context.scene.update()  # Required to find the children at the parent's transform eventually.


def _load_model(name_or_id):
    # Find the path to the BFRES file of the Obj model and load it.
    model_ob = None
    for res_name in objflow.get_res_names_by_id(name_or_id):
        model_path = _get_model_path(res_name)
        if not model_path:
            continue
        # Create the object which will hold all child mesh objects.
        if not model_ob:
            model_ob = bpy.data.objects.new("MK8.{}".format(name_or_id), None)
        # Load the BFRES with the special parent object to which all FSHP mesh objects become children of.
        all_tex = bpy.context.user_preferences.addons[__package__].preferences.import_all_textures
        lod_idx = bpy.context.user_preferences.addons[__package__].preferences.lod_model_index
        bpy.ops.import_scene.bfres(filepath=model_path, parent_ob_name=model_ob.name, mat_name_prefix=res_name, lod_model_index=lod_idx,
                                   tex_import_normal=all_tex, tex_import_specular=all_tex, tex_import_emissive=all_tex)
    return model_ob


def _get_model_path(res_name):
    # Check the base game directories, then the DLC cup ones.
    vol_path = bpy.context.user_preferences.addons[__package__].preferences.game_path
    path = os.path.join(vol_path, "content", "mapobj", res_name, "{}.bfres".format(res_name))
    if os.path.isfile(path):
        return path
    path = os.path.join(vol_path, "content", "race_common", res_name, "{}.bfres".format(res_name))
    if os.path.isfile(path):
        return path
    # Go through the DLC region directories.
    for i in range(ord("b"), ord("e")):  # JAP, USA, EUR
        dlc_path = os.path.join(vol_path, "aoc0005000c1010e{}00".format(chr(i)))
        if os.path.isdir(dlc_path):
            # Go through the Grand Prix indices.
            for j in range(13, 20, 2):  # 13, 15, 17, 19
                gp_path = os.path.join(dlc_path, "{0:04d}".format(j))
                if os.path.isdir(gp_path):
                    # Check if the file exists.
                    path = os.path.join(gp_path, "mapobj", res_name, "{}.bfres".format(res_name))
                    if os.path.isfile(path):
                        return path
