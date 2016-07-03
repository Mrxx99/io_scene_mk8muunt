import bmesh
import bpy
import enum

# ==== Scene ===========================================================================================================

class MK8PropsScene(bpy.types.PropertyGroup):
    class SceneType(enum.IntEnum):
        No     = 0
        Course = 1

    scene_type = bpy.props.EnumProperty(
        name="Scene Type",
        description="Specifies what kind of game content this scene represents.",
        items=[("0", "None",   "Do not handle this scene as game content."),
               ("1", "Course", "Handle this scene as a race track.")]
    )

class MK8PanelScene(bpy.types.Panel):
    bl_label = "Mario Kart 8"
    bl_idname = "SCENE_PT_mk8"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        self.layout.prop(context.scene.mk8, "scene_type")

# ---- Scene Course ----------------------------------------------------------------------------------------------------

class MK8PropsSceneCourse(bpy.types.PropertyGroup):
    class HeadLights(enum.IntEnum):
        AlwaysOff = 0,
        AlwaysOn  = 1,
        ByLapPath = 2

    effect_sw = bpy.props.IntProperty(
        name="EffectSW"
    )
    head_light = bpy.props.EnumProperty(
        name="Headlights",
        description="Controls how headlights are turned on and off throughout the course.",
        items=[("0", "Always Off",  "Headlights are turned off, ignoring any lap path specific settings."),
               ("1", "Always On",   "Headlights are turned on, ignoring any lap path specific settings."),
               ("2", "By Lap Path", "Headlights are controlled by the lap path.")]
    )
    is_first_left = bpy.props.BoolProperty(
        name="First Curve Left",
        description="Optimizes game behavior if the first curve after the start turns left."
    )
    is_jugem_above = bpy.props.BoolProperty(
        name="Lakitu Above"
    )
    jugem_above = bpy.props.IntProperty(
        name="Lakitu Above"
    )
    lap_jugem_pos = bpy.props.IntProperty(
        name="Lap Lakitu Pos."
    )
    lap_number = bpy.props.IntProperty(
        name="Lap Number",
        description="The number of total laps which have to be driven to finish this track.",
        min=0,
        max=7,
        default=3
    )
    obj_prms_expanded = bpy.props.BoolProperty(
        name="Expand Obj Parameters",
        description="Expand the Obj Parameter section or collapse it."
    )
    obj_prm_1 = bpy.props.IntProperty(
        name="Param 1"
    )
    obj_prm_2 = bpy.props.IntProperty(
        name="Param 2"
    )
    obj_prm_3 = bpy.props.IntProperty(
        name="Param 3"
    )
    obj_prm_4 = bpy.props.IntProperty(
        name="Param 4"
    )
    obj_prm_5 = bpy.props.IntProperty(
        name="Param 5"
    )
    obj_prm_6 = bpy.props.IntProperty(
        name="Param 6"
    )
    obj_prm_7 = bpy.props.IntProperty(
        name="Param 7"
    )
    obj_prm_8 = bpy.props.IntProperty(
        name="Param 8"
    )

class MK8PanelSceneCourse(bpy.types.Panel):
    bl_label = "Mario Kart 8 Course"
    bl_idname = "SCENE_PT_mk8course"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    @classmethod
    def poll(cls, context):
        return context.scene.mk8.scene_type == str(int(MK8PropsScene.SceneType.Course))

    def draw(self, context):
        self.layout.prop(context.scene.mk8course, "lap_number")
        self.layout.prop(context.scene.mk8course, "effect_sw")
        self.layout.prop(context.scene.mk8course, "head_light")
        row = self.layout.row()
        row.prop(context.scene.mk8course, "is_jugem_above")
        row.prop(context.scene.mk8course, "jugem_above")
        row = self.layout.row()
        row.prop(context.scene.mk8course, "is_first_left")
        row.prop(context.scene.mk8course, "lap_jugem_pos")
        box = self.layout.box()
        row = box.row()
        row.prop(context.scene.mk8course, "obj_prms_expanded",
             icon="TRIA_DOWN" if context.scene.mk8course.obj_prms_expanded else "TRIA_RIGHT",
             icon_only=True,
             emboss=False
        )
        row.label("Obj Parameters")
        if context.scene.mk8course.obj_prms_expanded:
            row = box.row()
            row.prop(context.scene.mk8course, "obj_prm_1")
            row.prop(context.scene.mk8course, "obj_prm_2")
            row = box.row()
            row.prop(context.scene.mk8course, "obj_prm_3")
            row.prop(context.scene.mk8course, "obj_prm_4")
            row = box.row()
            row.prop(context.scene.mk8course, "obj_prm_5")
            row.prop(context.scene.mk8course, "obj_prm_6")
            row = box.row()
            row.prop(context.scene.mk8course, "obj_prm_7")
            row.prop(context.scene.mk8course, "obj_prm_8")
