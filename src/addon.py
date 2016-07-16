import bmesh
import bpy
import mathutils

# ---- Globals ---------------------------------------------------------------------------------------------------------

loaded_byaml = None # The currently loaded BYAML file to reuse when exporting non-visualized objects.

# ---- Add-on Preferences ----------------------------------------------------------------------------------------------

class MK8MuuntAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    game_path = bpy.props.StringProperty(
        name="Mario Kart 8 Vol Directory Path",
        description="Path to the folder holding game content. 'content' and the DLC directory are children of this.",
        subtype="FILE_PATH"
    )
    library_path = bpy.props.StringProperty(
        name="Obj Model Library File Path",
        description="Path to the *.blend file caching Obj models.",
        subtype="FILE_PATH"
    )

    def draw(self, context):
        self.layout.prop(self, "game_path")

# ---- App Handlers ----------------------------------------------------------------------------------------------------

ignore_updates = False

@bpy.app.handlers.persistent
def scene_update_post(scene):
    # Required when importing object models so it does not recursively load them.
    if ignore_updates:
        return
    # Remove all Obj meshes which lost their parent.
    for ob in scene.objects:
        if ob.mk8.object_type == "OBJ_MODEL" and ob.parent is None:
            bpy.context.scene.objects.unlink(ob)
            bpy.data.objects.remove(ob)
    # Active object computations.
    ob = scene.objects.active
    if ob:
        # Make sure a newly created Obj has the correct child models.
        if ob.mk8.object_type == "OBJ" and len(ob.children) == 0:
            ob.mk8.update(bpy.context)
        # Redirect the selection of an Obj mesh object to the real Obj object.
        if ob.mk8.object_type == "OBJ_MODEL":
            scene.objects.active = ob.parent
            ob.parent.select = True
            ob.select = False

# ---- Model Manager ---------------------------------------------------------------------------------------------------

def create_default_area_cube():
    # Create a 100x100x100 cube, offset to sit on the XY axis.
    bm = bmesh.new()
    mx = mathutils.Matrix((
        (100,   0,   0,  0),
        (  0, 100,   0,  0),
        (  0,   0, 100, 50),
        (  0,   0,   0,  1)
    ))
    bmesh.ops.create_cube(bm, matrix=mx)
    # Create a mesh out of it and return it.
    mesh = bpy.data.meshes.new("@AREACUBE")
    bm.to_mesh(mesh)
    bm.free()
    return mesh

def create_default_area_sphere():
    # Create a 100x100x100 sphere , offset to sit on the XY axis.
    bm = bmesh.new()
    mx = mathutils.Matrix((
        (100,   0,   0,  0),
        (  0, 100,   0,  0),
        (  0,   0, 100, 50),
        (  0,   0,   0,  1)
    ))
    bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, diameter=0.5, matrix=mx)
    # Create a mesh out of it and return it.
    mesh = bpy.data.meshes.new("@AREASPHERE")
    bm.to_mesh(mesh)
    bm.free()
    return mesh

default_mesh_creators = {
    "AREACUBE": create_default_area_cube,
    "AREASPHERE": create_default_area_sphere
}

def get_default_mesh(mesh_name):
    # Get a cached mesh or create a new one.
    mesh = bpy.data.meshes.get("@" + mesh_name)
    if not mesh:
        mesh = default_mesh_creators[mesh_name]()
        mesh.use_fake_user = True
    return mesh

# ---- Methods & Mixins ------------------------------------------------------------------------------------------------

def log(indent, text):
    indent = " " * 2 * indent
    print("MK8MUUNT: " + indent + text)

def add_object_to_group(ob, group_name):
    # Get or create the required group.
    group = bpy.data.groups.get(group_name, bpy.data.groups.new(group_name))
    # Link the provided object to it.
    if ob.name not in group.objects:
        group.objects.link(ob)

def mk8_colbox(self, data, expand_property):
    # Creates an expandable and collapsible box for the UILayout.
    box = self.box()
    row = box.row()
    row.prop(data, expand_property,
        icon="TRIA_DOWN" if getattr(data, expand_property) else "TRIA_RIGHT",
        icon_only=True,
        emboss=False
    )
    row.label(getattr(data.rna_type, expand_property)[1]["name"])
    return box

