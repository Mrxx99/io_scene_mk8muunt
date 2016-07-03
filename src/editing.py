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
        AlwaysOff = 0
        AlwaysOn  = 1
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
    pattern_num = bpy.props.IntProperty(
        name="Pattern Num."
    )

    obj_prms_expanded = bpy.props.BoolProperty(
        name="Obj Params",
        description="Expand the Obj Params section or collapse it."
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
        self.layout.prop(context.scene.mk8course, "head_light")
        row = self.layout.row()
        row.prop(context.scene.mk8course, "is_jugem_above")
        row.prop(context.scene.mk8course, "jugem_above")
        row = self.layout.row()
        row.prop(context.scene.mk8course, "is_first_left")
        row.prop(context.scene.mk8course, "lap_jugem_pos")
        row = self.layout.row()
        row.prop(context.scene.mk8course, "effect_sw")
        row.prop(context.scene.mk8course, "pattern_num")
        # Obj Parameters
        box = self.layout.mk8_colbox(context.scene.mk8course, "obj_prms_expanded")
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


# ==== Object ==========================================================================================================

class MK8PropsObject(bpy.types.PropertyGroup):
    class ObjectType(enum.IntEnum):
        No           = 0
        Area         = 10
        Clip         = 20
        ClipArea     = 30
        EffectArea   = 40
        EnemyPath    = 50
        GCameraPath  = 60
        GlidePath    = 70
        GravityPath  = 80
        IntroCamera  = 90
        ItemPath     = 100
        JugemPath    = 110
        LapPath      = 120
        Obj          = 130
        Path         = 140
        ReplayCamera = 150
        SoundObj     = 160

    object_type = bpy.props.EnumProperty(
        name="Object Type",
        description="Specifies what kind of course content this object represents.",
        items=[("0",   "None", "Do not handle this object as course content."),
               ("130", "Obj",  "Handle this object as a course object.")]
    )

class MK8PanelObject(bpy.types.Panel):
    bl_label = "Mario Kart 8"
    bl_idname = "OBJECT_PT_mk8"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    def draw(self, context):
        self.layout.prop(context.object.mk8, "object_type")

# ---- Object Obj ------------------------------------------------------------------------------------------------------

class MK8PropsObjectObj(bpy.types.PropertyGroup):
    multi_2p = bpy.props.BoolProperty(
        name="Exclude 2P",
        description="Removes this obj in 2 player offline games."
    )
    multi_4p = bpy.props.BoolProperty(
        name="Exclude 4P",
        description="Removes this obj in 4 player offline games."
    )
    obj_id = bpy.props.IntProperty(
        name="Obj ID",
        description="The ID determining the type of this object (as defined in objflow.byaml)."
    )
    obj_path = bpy.props.IntProperty(
        name="Path",
        description="The number of the path this obj follows."
    )
    obj_path_point = bpy.props.IntProperty(
        name="Path Point"
    )
    # TODO: These are actually arrays named like Obj_EnemyPath1
    #obj_enemy_path = bpy.props.IntProperty(
    #    name="Enemy Path"
    #)
    #obj_item_path = bpy.props.IntProperty(
    #    name="Item Path"
    #)
    speed = bpy.props.FloatProperty(
        name="Path Speed",
        description="The speed in which the obj follows its path."
    )
    top_view = bpy.props.BoolProperty(
        name="Top View"
    )
    unit_id_num = bpy.props.IntProperty(
        name="Unit ID"
    )
    wifi = bpy.props.BoolProperty(
        name="Exclude WiFi",
        description="Removes this obj in online games."
    )
    wifi_2p = bpy.props.BoolProperty(
        name="Exclude WiFi 2P",
        description="Removes this obj in 2 player online games."
    )
    prm_1 = bpy.props.IntProperty(
        name="Param 1"
    )
    prm_2 = bpy.props.IntProperty(
        name="Param 2"
    )
    prm_3 = bpy.props.IntProperty(
        name="Param 3"
    )
    prm_4 = bpy.props.IntProperty(
        name="Param 4"
    )
    prm_5 = bpy.props.IntProperty(
        name="Param 5"
    )
    prm_6 = bpy.props.IntProperty(
        name="Param 6"
    )
    prm_7 = bpy.props.IntProperty(
        name="Param 7"
    )
    prm_8 = bpy.props.IntProperty(
        name="Param 8"
    )

    params_expanded = bpy.props.BoolProperty(
        name="Params",
        description="Expand the Params section or collapse it.",
        default=True
    )

class MK8PanelObjectObj(bpy.types.Panel):
    bl_label = "Mario Kart 8 Obj"
    bl_idname = "OBJECT_PT_mk8obj"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return context.object.mk8.object_type == str(int(MK8PropsObject.ObjectType.Obj))

    def draw(self, context):
        row = self.layout.row()
        row.prop(context.object.mk8obj, "obj_id")
        row.prop(context.object.mk8obj, "unit_id_num")
        self.layout.prop(context.object.mk8obj, "top_view")
        row = self.layout.row()
        row.prop(context.object.mk8obj, "multi_2p")
        row.prop(context.object.mk8obj, "multi_4p")
        row = self.layout.row()
        row.prop(context.object.mk8obj, "wifi")
        row.prop(context.object.mk8obj, "wifi_2p")
        self.layout.prop(context.object.mk8obj, "speed")
        row = self.layout.row()
        row.prop(context.object.mk8obj, "obj_path")
        row.prop(context.object.mk8obj, "obj_path_point")
        #self.layout.prop(context.object.mk8obj, "obj_enemy_path")
        #self.layout.prop(context.object.mk8obj, "obj_item_path")
        box = self.layout.mk8_colbox(context.object.mk8obj, "params_expanded")
        if context.object.mk8obj.params_expanded:
            row = box.row()
            row.prop(context.object.mk8obj, "prm_1")
            row.prop(context.object.mk8obj, "prm_2")
            row = box.row()
            row.prop(context.object.mk8obj, "prm_3")
            row.prop(context.object.mk8obj, "prm_4")
            row = box.row()
            row.prop(context.object.mk8obj, "prm_5")
            row.prop(context.object.mk8obj, "prm_6")
            row = box.row()
            row.prop(context.object.mk8obj, "prm_7")
            row.prop(context.object.mk8obj, "prm_8")

