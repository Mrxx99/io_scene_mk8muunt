import bpy
from . import addon
from . import objflow

# ==== Scene ===========================================================================================================

class MK8PropsScene(bpy.types.PropertyGroup):
    scene_type = bpy.props.EnumProperty(
        name="Scene Type",
        description="Specifies what kind of game content this scene represents.",
        items=(("NONE",   "None",   "Do not handle this scene as game content."),
               ("COURSE", "Course", "Handle this scene as a race track."))
    )

class MK8PanelScene(bpy.types.Panel):
    bl_label = "Mario Kart 8"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        self.layout.prop(context.scene.mk8, "scene_type")

# ---- Scene Course ----------------------------------------------------------------------------------------------------

class MK8PropsSceneCourse(bpy.types.PropertyGroup):
    effect_sw = bpy.props.IntProperty(
        name="EffectSW"
    )
    head_light = bpy.props.EnumProperty(
        name="Headlights",
        description="Controls how headlights are turned on and off throughout the course.",
        items=(("OFF",     "Always Off",  "Headlights are turned off, ignoring any lap path specific settings."),
               ("ON",      "Always On",   "Headlights are turned on, ignoring any lap path specific settings."),
               ("PARTIAL", "By Lap Path", "Headlights are controlled by the lap path."))
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
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    @classmethod
    def poll(cls, context):
        return context.scene.mk8.scene_type == "COURSE"

    def draw(self, context):
        self.layout.prop(context.scene.mk8_course, "lap_number")
        self.layout.prop(context.scene.mk8_course, "head_light")
        row = self.layout.row()
        row.prop(context.scene.mk8_course, "is_jugem_above")
        row.prop(context.scene.mk8_course, "jugem_above")
        row = self.layout.row()
        row.prop(context.scene.mk8_course, "is_first_left")
        row.prop(context.scene.mk8_course, "lap_jugem_pos")
        row = self.layout.row()
        row.prop(context.scene.mk8_course, "effect_sw")
        row.prop(context.scene.mk8_course, "pattern_num")
        # Obj Parameters
        box = self.layout.mk8_colbox(context.scene.mk8_course, "obj_prms_expanded")
        if context.scene.mk8_course.obj_prms_expanded:
            row = box.row()
            row.prop(context.scene.mk8_course, "obj_prm_1")
            row.prop(context.scene.mk8_course, "obj_prm_2")
            row = box.row()
            row.prop(context.scene.mk8_course, "obj_prm_3")
            row.prop(context.scene.mk8_course, "obj_prm_4")
            row = box.row()
            row.prop(context.scene.mk8_course, "obj_prm_5")
            row.prop(context.scene.mk8_course, "obj_prm_6")
            row = box.row()
            row.prop(context.scene.mk8_course, "obj_prm_7")
            row.prop(context.scene.mk8_course, "obj_prm_8")

# ==== Object ==========================================================================================================

class MK8PropsObject(bpy.types.PropertyGroup):
    def update_object(self, context):
        ob = context.object
        if bool(ob):
            if   self.object_type == "NONE":       ob.data = None # Does not seem to have an effect.
            elif self.object_type == "AREA":       ob.mk8_area.update_object(context)
            elif self.object_type == "CLIPAREA":   ob.mk8_clip_area.update_object(context)
            elif self.object_type == "EFFECTAREA": ob.mk8_effect_area.update_object(context)
            elif self.object_type == "OBJ":        ob.mk8_obj.update_object(context)

    object_type = bpy.props.EnumProperty(
        name="Object Type",
        description="Specifies what kind of course content this object represents.",
        items=(("NONE",       "None",        "Do not handle this object as course content."),
               ("AREA",       "Area",        "Handle this object as an area."),
               ("CLIPAREA",   "Clip Area",   "Handle this object as a clip area"),
               ("EFFECTAREA", "Effect Area", "Handle this object as an effect area"),
               ("OBJ",        "Obj",         "Handle this object as a course object.")),
        update=update_object
    )

class MK8PanelObject(bpy.types.Panel):
    bl_label = "Mario Kart 8"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    def draw(self, context):
        self.layout.prop(context.object.mk8, "object_type")

# ---- Object Area -----------------------------------------------------------------------------------------------------

class MK8PropsObjectAreaCameraArea(bpy.types.PropertyGroup):
    value = bpy.props.IntProperty(
        name="Camera Area",
        min=0
    )

class MK8PropsObjectArea(bpy.types.PropertyGroup):
    def update_object(self, context):
        # Ensure the object of the area has the correct mesh.
        ob = context.object
        if bool(ob):
            area = context.object.mk8_area
            ob.data = addon.get_default_mesh(area.area_shape)
            ob.draw_type = "WIRE"

    unit_id_num = bpy.props.IntProperty(
        name="Unit ID",
        min=0
    )
    prm1 = bpy.props.FloatProperty(
        name="Param 1"
    )
    prm2 = bpy.props.FloatProperty(
        name="Param 2"
    )
    area_shape = bpy.props.EnumProperty(
        name="Shape",
        description="Specifies the outer form of the region this area spans.",
        items=(("AREACUBE",   "Cube",   "The area spans a cuboid region."),
               ("AREASPHERE", "Sphere", "The area spans a spherical region.")),
        update=update_object
    )
    area_type = bpy.props.EnumProperty(
        name="Type",
        description="Specifies the action taken for objects inside of this region.",
        items=(("NONE",     "None",        "No special action will be taken."),
               ("UNKNOWN1", "Unknown (1)", "Unknown area type. Appears in Mario Circuit and Twisted Mansion."),
               ("UNKNOWN2", "Unknown (2)", "Unknown area type. Appears almost everywhere."),
               ("PULL",     "Pull",        "Objects are moved along the specified path."),
               ("UNKNOWN4", "Unknown (4)", "Unknown area type. Appears in Mario Kart Stadium, Royal Raceway and Animal Crossing."))
    )
    area_path = bpy.props.IntProperty(
        name="Path",
        min=0
    )
    area_pull_path = bpy.props.IntProperty(
        name="Pull Path",
        min=0
    )
    camera_areas = bpy.props.CollectionProperty(
        type=MK8PropsObjectAreaCameraArea
    )
    camera_areas_active = bpy.props.IntProperty(
    )

class MK8ListObjectAreaCameraArea(bpy.types.UIList):
    layout_type = "GRID"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type == "GRID":
            layout.alignment = "CENTER"
        layout.label(str(item.value), icon="CAMERA_DATA")

class MK8PanelObjectArea(bpy.types.Panel):
    bl_label = "Mario Kart 8 Area"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return context.object.mk8.object_type == "AREA"

    def draw(self, context):
        area = context.object.mk8_area
        self.layout.prop(area, "unit_id_num")
        row = self.layout.row(align=True)
        row.prop(area, "prm1")
        row.prop(area, "prm2")
        self.layout.prop(area, "area_shape")
        # Area Type
        self.layout.prop(area, "area_type")
        if area.area_type == "UNKNOWN2":
            self.layout.prop(area, "area_path")
        elif area.area_type == "PULL":
            self.layout.prop(area, "area_pull_path")
        # Camera Areas
        self.layout.label("Camera Areas")
        self.layout.template_list("MK8ListObjectAreaCameraArea", "", area, "camera_areas", area, "camera_areas_active")

# ---- Object ClipArea -------------------------------------------------------------------------------------------------

class MK8PropsObjectClipArea(bpy.types.PropertyGroup):
    def update_object(self, context):
        # Ensure the object of the clip area has the correct mesh.
        ob = context.object
        if bool(ob):
            clip_area = context.object.mk8_clip_area
            ob.data = addon.get_default_mesh(clip_area.area_shape)
            ob.draw_type = "WIRE"

    unit_id_num = bpy.props.IntProperty(
        name="Unit ID",
        min=0
    )
    prm1 = bpy.props.FloatProperty(
        name="Param 1"
    )
    prm2 = bpy.props.FloatProperty(
        name="Param 2"
    )
    area_shape = bpy.props.EnumProperty(
        name="Shape",
        description="Specifies the outer form of the region this clip area spans.",
        items=(("AREACUBE", "Cube", "The clip area spans a cuboid region."),),
        update=update_object
    )
    area_type = bpy.props.EnumProperty(
        name="Type",
        items=(("UNKNOWN5", "Unknown (5)", "Unknown clip area type. Appears almost everywhere."),)
    )

class MK8PanelObjectClipArea(bpy.types.Panel):
    bl_label = "Mario Kart 8 Clip Area"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return context.object.mk8.object_type == "CLIPAREA"

    def draw(self, context):
        clip_area = context.object.mk8_clip_area
        self.layout.prop(clip_area, "unit_id_num")
        row = self.layout.row(align=True)
        row.prop(clip_area, "prm1")
        row.prop(clip_area, "prm2")
        self.layout.prop(clip_area, "area_type")

# ---- Object EffectArea -----------------------------------------------------------------------------------------------

class MK8PropsObjectEffectArea(bpy.types.PropertyGroup):
    def update_object(self, context):
        # Ensure the object of the area has the correct mesh.
        ob = context.object
        if bool(ob):
            ob.data = addon.get_default_mesh("@AREACUBE")
            ob.draw_type = "WIRE"

    unit_id_num = bpy.props.IntProperty(
        name="Unit ID",
        min=0
    )
    prm1 = bpy.props.FloatProperty(
        name="Param 1"
    )
    prm2 = bpy.props.FloatProperty(
        name="Param 2"
    )
    effect_sw = bpy.props.IntProperty(
        name="EffectSW",
        min=0
    )

class MK8PanelObjectEffectArea(bpy.types.Panel):
    bl_label = "Mario Kart 8 Effect Area"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return context.object.mk8.object_type == "EFFECTAREA"

    def draw(self, context):
        effect_area = context.object.mk8_effect_area
        self.layout.prop(effect_area, "unit_id_num")
        row = self.layout.row(align=True)
        row.prop(effect_area, "prm1")
        row.prop(effect_area, "prm2")
        self.layout.prop(effect_area, "effect_sw")

# ---- Object Obj ------------------------------------------------------------------------------------------------------

class MK8PropsObjectObj(bpy.types.PropertyGroup):
    def update_object(self, context):
        # Ensure the object of the area has the correct mesh.
        ob = context.object
        ob.data = None
        ob.empty_draw_type = "PLAIN_AXES"

    unit_id_num = bpy.props.IntProperty(
        name="Unit ID",
        min=0
    )
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
        description="The ID determining the type of this object (as defined in objflow.byaml).",
        min=1000,
        max=9999
    )
    obj_path = bpy.props.IntProperty(
        name="Path",
        description="The number of the path this obj follows.",
        min=0
    )
    obj_obj_path = bpy.props.IntProperty(
        name="Obj Path",
        min=0
    )
    obj_path_point = bpy.props.IntProperty(
        name="Path Point",
        min=0
    )
    obj_enemy_path_1 = bpy.props.IntProperty(
        name="Enemy Path 1",
        min=0
    )
    obj_enemy_path_2 = bpy.props.IntProperty(
        name="Enemy Path 2",
        min=0
    )
    obj_item_path_1 = bpy.props.IntProperty(
        name="Item Path 1",
        min=0
    )
    obj_item_path_2 = bpy.props.IntProperty(
        name="Item Path 2",
        min=0
    )
    speed = bpy.props.FloatProperty(
        name="Path Speed",
        description="The speed in which the obj follows its path."
    )
    top_view = bpy.props.BoolProperty(
        name="Top View"
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
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return context.object.mk8.object_type == "OBJ"

    def draw(self, context):
        obj = context.object.mk8_obj
        self.layout.prop(obj, "unit_id_num")
        row = self.layout.row(align=True)
        row.prop(obj, "obj_id")
        obj_name = objflow.get_obj_label(context, obj.obj_id)
        if obj_name:
            row.label(obj_name)
        else:
            row.label("Unknown", icon="ERROR")
        self.layout.prop(obj, "top_view")
        row = self.layout.row(align=True)
        row.prop(obj, "multi_2p")
        row.prop(obj, "multi_4p")
        row = self.layout.row(align=True)
        row.prop(obj, "wifi")
        row.prop(obj, "wifi_2p")
        row = self.layout.row(align=True)
        row.prop(obj, "speed")
        row.prop(obj, "obj_path_point")
        row = self.layout.row(align=True)
        row.prop(obj, "obj_path")
        row.prop(obj, "obj_obj_path")
        row = self.layout.row(align=True)
        row.prop(obj, "obj_enemy_path_1")
        row.prop(obj, "obj_enemy_path_2")
        row = self.layout.row(align=True)
        row.prop(obj, "obj_item_path_1")
        row.prop(obj, "obj_item_path_2")
        box = self.layout.mk8_colbox(obj, "params_expanded")
        if obj.params_expanded:
            row = box.row()
            row.prop(obj, "prm_1")
            row.prop(obj, "prm_2")
            row = box.row()
            row.prop(obj, "prm_3")
            row.prop(obj, "prm_4")
            row = box.row()
            row.prop(obj, "prm_5")
            row.prop(obj, "prm_6")
            row = box.row()
            row.prop(obj, "prm_7")
            row.prop(obj, "prm_8")
