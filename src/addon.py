import bmesh
import bpy
import mathutils

# ---- Add-on Preferences ----------------------------------------------------------------------------------------------

class MK8MuuntAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    game_path = bpy.props.StringProperty(
        name="Mario Kart 8 Vol Directory",
        description="Path to the folder holding game content. 'content' and the DLC directory are children of this.",
        subtype="FILE_PATH"
    )

    def draw(self, context):
        self.layout.prop(self, "game_path")

# ---- Model Manager ---------------------------------------------------------------------------------------------------

def get_model(obj_id):
    raise NotImplementedError()

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
    mesh = bpy.data.meshes.new("@AreaCube")
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
    mesh = bpy.data.meshes.new("@AreaSphere")
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
