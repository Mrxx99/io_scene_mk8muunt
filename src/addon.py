import bpy

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
