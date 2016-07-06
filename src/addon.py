import bmesh
import bpy
import enum
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

cached_models = {}

def get_model(obj_id):
    pass

cached_default_models = {}

def creator_default_area_cube():
    # Create a 20x20x20 cube (size of those areas), offset to sit on the floor.
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

def creator_default_area_sphere():
    # Create a 20x20x20 sphere (size of those areas), offset to sit on the floor.
    bm = bmesh.new()
    mx = mathutils.Matrix((
        (100,   0,   0,  0),
        (  0, 100,   0,  0),
        (  0,   0, 100, 50),
        (  0,   0,   0,  1)
    ))
    bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, diameter=1, matrix=mx)
    # Create a mesh out of it and return it.
    mesh = bpy.data.meshes.new("@AreaSphere")
    bm.to_mesh(mesh)
    bm.free()
    return mesh

class DefaultModel(enum.IntEnum):
    AreaCube = 0
    AreaSphere = 1

default_model_creators = (
    creator_default_area_cube,
    creator_default_area_sphere
)

def get_default_model(model):
    # Get a cached model or create a new one.
    mesh = cached_default_models.get(model)
    if not mesh:
        mesh = default_model_creators[model]()
        cached_default_models[model] = mesh
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
