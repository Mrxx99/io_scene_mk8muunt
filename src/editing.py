import addon_utils
import bpy
import bmesh
import mathutils
import os
from . import idproperty
from . import addon
from . import objflow


# ---- Properties ----

class MK8PropsScene(bpy.types.PropertyGroup):
    scene_type = bpy.props.EnumProperty(name="Scene Type", description="Specifies what kind of game content this scene represents.", items=(
        ("NONE", "None", "Do not handle this scene as game content."),
        ("COURSE", "Course", "Handle this scene as a race track.")))

    # ---- Course ----

    effect_sw = bpy.props.IntProperty(name="Global FX", description="Specifies a global effect type seen on the whole course.", min=0)
    head_light = bpy.props.EnumProperty(name="Headlights", description="Controls how headlights are turned on and off throughout the course.", items=(
        ("0", "Always Off", "Headlights are turned off, ignoring any lap path specific settings."),
        ("1", "Always On", "Headlights are turned on, ignoring any lap path specific settings."),
        ("2", "By Lap Path", "Headlights are controlled by the lap path.")))
    is_first_left = bpy.props.BoolProperty(name="First Curve Left", description="Optimizes game behavior if the first curve after the start turns left.")
    is_jugem_above = bpy.props.BoolProperty(name="Lakitu Above")
    jugem_above = bpy.props.IntProperty(name="Lakitu Above")
    lap_jugem_pos = bpy.props.IntProperty(name="Lap Lakitu Pos.")
    lap_number = bpy.props.IntProperty(name="Lap Count", description="The amount of total laps which have to be driven to finish this track.", min=0, max=7, default=3)
    pattern_num = bpy.props.IntProperty(name="Pattern Count", description="The amount of random object sets of which one is picked at the race start.", min=0)
    obj_prm_1 = bpy.props.IntProperty(name="Param 1")
    obj_prm_2 = bpy.props.IntProperty(name="Param 2")
    obj_prm_3 = bpy.props.IntProperty(name="Param 3")
    obj_prm_4 = bpy.props.IntProperty(name="Param 4")
    obj_prm_5 = bpy.props.IntProperty(name="Param 5")
    obj_prm_6 = bpy.props.IntProperty(name="Param 6")
    obj_prm_7 = bpy.props.IntProperty(name="Param 7")
    obj_prm_8 = bpy.props.IntProperty(name="Param 8")
    # UI
    obj_prms_expanded = bpy.props.BoolProperty(name="Obj Params", description="Expand the Obj Params section or collapse it.")


class MK8PropsObjectAreaCameraArea(bpy.types.PropertyGroup):
    value = bpy.props.IntProperty(name="Camera Area", min=0)


class MK8PropsObject(bpy.types.PropertyGroup):
    # ---- General ----

    object_type = bpy.props.EnumProperty(items=(  # Used internally by the addon.
        ("NONE", "", ""),
        ("AREA", "", "."),
        ("CLIPAREA", "", ""),
        ("EFFECTAREA", "", ""),
        ("OBJ", "", ""),
        ("SOUNDOBJ", "", ""),
        ("ADDON_VISUALIZER", "", "")))
    unit_id_num = bpy.props.IntProperty(name="Unit ID", description="Number identifying this object, can be non-unique 0 without issues.", min=0)
    top_view = bpy.props.BoolProperty(name="Top View", description="Unknown setting, never used in the original courses.")
    inclusions = bpy.props.EnumProperty(name="Inclusions", options={'ENUM_FLAG'}, items=(
        ("Single", "1P", "Include this object in 1 player offline games."),
        ("Multi2P", "2P", "Include this object in 2 player offline games."),
        ("Multi4P", "3/4P", "Include this object in 3 or 4 player offline games."),
        ("WiFi", "WiFi 1P", "Include this object in 1 player online games."),
        ("WiFi2P", "WiFi 2P", "Include this object in 2 player online games.")))
    float_param_1 = bpy.props.FloatProperty(name="Param 1")
    float_param_2 = bpy.props.FloatProperty(name="Param 2")
    float_param_3 = bpy.props.FloatProperty(name="Param 3")
    float_param_4 = bpy.props.FloatProperty(name="Param 4")
    float_param_5 = bpy.props.FloatProperty(name="Param 5")
    float_param_6 = bpy.props.FloatProperty(name="Param 6")
    float_param_7 = bpy.props.FloatProperty(name="Param 7")
    float_param_8 = bpy.props.FloatProperty(name="Param 8")

    # ---- Area ----

    def _update_area_shape(self, context):
        ob = context.object
        if self.area_shape == "0":
            ob.data = addon.get_default_mesh("AREACUBE")
        elif self.area_shape == "1":
            ob.data = addon.get_default_mesh("AREASPHERE")

    area_shape = bpy.props.EnumProperty(name="Shape", description="Specifies the outer form of the region this area spans.", update=_update_area_shape, items=(
        ("0", "Cube", "The area spans a cuboid region."),
        ("1", "Sphere", "The area spans a spherical region.")))
    area_type = bpy.props.EnumProperty(name="Type", description="Specifies the action taken for objects inside of this region.", items=(
        ("0", "None", "No special action will be taken."),
        ("1", "Unknown (1)", "Unknown area type. Appears in Mario Circuit and Twisted Mansion."),
        ("2", "Unknown (2)", "Unknown area type. Appears almost everywhere."),
        ("3", "Pull", "Objects are moved along the specified path."),
        ("4", "Roam", "Objects will roam randomly inside of this area.")))
    has_area_path = bpy.props.BoolProperty(name="Has Path", description="Determines whether a Path will be used.")
    has_area_pull_path = bpy.props.BoolProperty(name="Has Pull Path", description="Determines whether a Pull Path will be used.")
    area_path = bpy.props.IntProperty(name="Path", min=0)
    area_pull_path = bpy.props.IntProperty(name="Pull Path", min=0)
    camera_areas = bpy.props.CollectionProperty(type=MK8PropsObjectAreaCameraArea)

    camera_areas_active = bpy.props.IntProperty()

    # ---- Clip Area ----

    def _update_clip_area(self, context):
        pass

    clip_area_shape = bpy.props.EnumProperty(name="Shape", description="Specifies the outer form of the region this clip area spans.", update=_update_clip_area, items=(
        ("0", "Cube", "The clip area spans a cuboid region."),))
    clip_area_type = bpy.props.EnumProperty(name="Type", items=(
        ("5", "Clip", "Specifies a clip area."),))

    # ---- Effect Area ----

    effect_sw = bpy.props.IntProperty(name="FX", description="Specifies the effect type to be seen inside this area.", min=0)

    # ---- Obj ----

    def _update_obj_id(self, context):
        ob = context.object
        # Update the general Obj properties
        ob.empty_draw_type = 'ARROWS'
        ob.empty_draw_size = 20
        obj = objflow.get_obj_by_id(ob.mk8.obj_id)
        ob.name = obj["Label"] if obj else "Unknown"
        # Remove all the children, they will be added in the scene_update_post app handler.
        for ob_child in ob.children:
            context.scene.objects.unlink(ob_child)
            bpy.data.objects.remove(ob_child)

    def _get_obj_id_name(self):
        obj = objflow.get_obj_by_id(self.obj_id)
        return obj["Label"] if obj else "Unknown"

    def _set_obj_id_name(self, value):
        obj = objflow.get_obj_by_label(value)
        if obj:
            self.obj_id = obj["ObjId"]
        else:
            raise AssertionError("No Obj found with the label '{}'.".format(value))

    def _validator_area(ob):
        return ob.mk8.object_type == "AREA"

    def _validator_obj(ob):
        return ob.mk8.object_type == "OBJ"

    obj_id = bpy.props.IntProperty(name="Obj ID", description="The ID determining the type of this object (as defined in objflow.byaml).", min=1000, max=9999, update=_update_obj_id)
    obj_id_name = bpy.props.StringProperty(name="Type", description="The name of the Obj determining its type.", get=_get_obj_id_name, set=_set_obj_id_name)
    no_col = bpy.props.BoolProperty(name="No Collisions", description="Removes collision detection with this Obj when set.")
    # Paths
    speed = bpy.props.FloatProperty(name="Speed", description="The speed in which the Obj follows its path.")
    has_path = bpy.props.BoolProperty(name="Has Path", description="Determines whether a Path will be used.")
    has_path_point = bpy.props.BoolProperty(name="Has Path Point", description="Determines whether a Path Point will be used.")
    has_lap_path = bpy.props.BoolProperty(name="Has Lap Point", description="Determines whether a Lap Path will be used.")
    has_lap_point = bpy.props.BoolProperty(name="Has Lap Path Point", description="Determines whether a Lap Path Point will be used.")
    has_obj_path = bpy.props.BoolProperty(name="Has Obj Path", description="Determines whether an Obj Path will be used.")
    has_obj_point = bpy.props.BoolProperty(name="Has Obj Path Point", description="Determines whether an Obj Path Point will be used.")
    has_enemy_path_1 = bpy.props.BoolProperty(name="Has Enemy Path 1", description="Determines whether an Enemy Path 1 will be used.")
    has_enemy_path_2 = bpy.props.BoolProperty(name="Has Enemy Path 2", description="Determines whether an Enemy Path 2 will be used.")
    has_item_path_1 = bpy.props.BoolProperty(name="Has Item Path 1", description="Determines whether an Item Path 1 will be used.")
    has_item_path_2 = bpy.props.BoolProperty(name="Has Item Path 2", description="Determines whether an Item Path 2 will be used.")
    path = bpy.props.IntProperty(name="Path", description="The index of the path this Obj follows.", min=0)
    path_point = bpy.props.IntProperty(name="Path Point", min=0)
    lap_path = bpy.props.IntProperty(name="Lap", min=0)
    lap_point = bpy.props.IntProperty(name="Lap Point", min=0)
    obj_path = bpy.props.IntProperty(name="Obj", min=0)
    obj_point = bpy.props.IntProperty(name="Obj Point", min=0)
    enemy_path_1 = bpy.props.IntProperty(name="Enemy 1", min=0)
    enemy_path_2 = bpy.props.IntProperty(name="Enemy 2", min=0)
    item_path_1 = bpy.props.IntProperty(name="Item 1", min=0)
    item_path_2 = bpy.props.IntProperty(name="Item 2", min=0)
    # Relations
    area_idx = bpy.props.IntProperty(default=-1)
    area = idproperty.ObjectIDProperty(name="Area", description="The Area this Obj has relations to.", validator=_validator_area)
    obj_idx = bpy.props.IntProperty(default=-1)
    obj = idproperty.ObjectIDProperty(name="Obj", description="The Obj this Obj has relations to.", validator=_validator_obj)
    # UI
    params_expanded = bpy.props.BoolProperty(name="Params", description="Expand the Params section or collapse it.", default=True)
    paths_expanded = bpy.props.BoolProperty(name="Paths", description="Expand the Paths section or collapse it.", default=True)
    relations_expanded = bpy.props.BoolProperty(name="Relations", description="Expand the Relations section or collapse it.", default=True)

    # ---- Sound Obj ----

    sound_index = bpy.props.IntProperty(name="Sound Index", description="The index of the sound to be played.", min=0)
    int_param_2 = bpy.props.IntProperty(name="Param 2", description="Unknown meaning, always -1 in the original courses.", default=-1)


# ---- UI ----

class MK8PanelScene(bpy.types.Panel):
    bl_label = "Mario Kart 8"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        mk8 = context.scene.mk8
        self.layout.prop(mk8, "scene_type")
        if mk8.scene_type == "COURSE":
            self.draw_scene(context, mk8)

    def draw_scene(self, context, mk8):
        self.layout.prop(mk8, "lap_number")
        self.layout.prop(mk8, "effect_sw")
        self.layout.prop(mk8, "head_light")
        self.layout.prop(mk8, "pattern_num")
        row = self.layout.row()
        row.prop(mk8, "is_jugem_above")
        row.prop(mk8, "jugem_above")
        row = self.layout.row()
        row.prop(mk8, "is_first_left")
        row.prop(mk8, "lap_jugem_pos")
        # Obj Parameters
        box, header = self.layout.mk8_colbox(mk8, "obj_prms_expanded")
        if mk8.obj_prms_expanded:
            col = box.column(align=True)
            for i in range(1, 9):
                col.prop(mk8, "obj_prm_{}".format(i))


class MK8PanelObject(bpy.types.Panel):
    bl_label = "Mario Kart 8"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        # The panel is displayed if this is a valid MK8 object.
        return context.object.mk8.object_type not in ("NONE", "ADDON_VISUALIZER")

    def draw(self, context):
        self.bl_label = "Mario Kart 8"
        mk8 = context.object.mk8
        # Debug information.
        if bpy.context.user_preferences.addons[__package__].preferences.debug_mode:
            self.layout.prop(mk8, "unit_id_num")
        # Type specific properties.
        if mk8.object_type == "AREA":
            self._draw_area(context, mk8)
        elif mk8.object_type == "CLIPAREA":
            self._draw_clip_area(context, mk8)
        elif mk8.object_type == "EFFECTAREA":
            self._draw_effect_area(context, mk8)
        elif mk8.object_type == "OBJ":
            self._draw_obj(context, mk8)
        elif mk8.object_type == "SOUNDOBJ":
            self._draw_sound_obj(context, mk8)

    def _draw_area(self, context, mk8):
        self.bl_label += " Area"
        # Area Type
        self.layout.prop(mk8, "area_type")
        if mk8.area_type in ("0", "2"):
            self._optional_prop(mk8, self.layout.row(), "area_path")
        elif mk8.area_type == "3":
            self._optional_prop(mk8, self.layout.row(), "area_pull_path")
        # Shape
        self.layout.prop(mk8, "area_shape")
        # Parameters
        col = self.layout.column(align=True)
        col.prop(mk8, "float_param_1")
        col.prop(mk8, "float_param_2")
        # Camera Areas
        self.layout.label("Camera Areas")
        self.layout.template_list("MK8ListObjectAreaCameraArea", "", mk8, "camera_areas", mk8, "camera_areas_active")

    def _draw_clip_area(self, context, mk8):
        self.bl_label += " Clip Area"
        self.layout.prop(mk8, "clip_area_type")
        col = self.layout.column(align=True)
        col.prop(mk8, "float_param_1")
        col.prop(mk8, "float_param_2")

    def _draw_effect_area(self, context, mk8):
        self.bl_label += " Effect Area"
        self.layout.prop(mk8, "effect_sw")
        col = self.layout.column(align=True)
        col.prop(mk8, "float_param_1")
        col.prop(mk8, "float_param_2")

    def _draw_obj(self, context, mk8):
        self.bl_label += " Obj"
        # General
        row = self.layout.row(align=True)
        if objflow.get_obj_by_id(mk8.obj_id):
            row.prop(mk8, "obj_id_name")
        else:
            row.prop(mk8, "obj_id_name", icon='ERROR')
        row.operator("object.mk8_obj_id_search", text="", icon='VIEWZOOM')
        row = self.layout.row()
        row.prop(mk8, "no_col")
        row.prop(mk8, "top_view")
        self.layout.prop(mk8, "inclusions")
        # Params
        box, header = self.layout.mk8_colbox(mk8, "params_expanded")
        header.prop(context.user_preferences.addons[__package__].preferences, "show_unused_obj_params", text="Show Unused")
        if mk8.params_expanded:
            col = box.column(align=True)
            for i in range(1, 9):
                name = objflow.get_param_names(mk8.obj_id, i)
                if name:
                    col.prop(mk8, "float_param_{}".format(i), text=name)
        # Paths
        box, header = self.layout.mk8_colbox(mk8, "paths_expanded")
        header.prop(mk8, "speed")
        if mk8.paths_expanded:
            row = box.row()
            self._optional_prop(mk8, row, "path")
            self._optional_prop(mk8, row, "path_point")
            row = box.row()
            self._optional_prop(mk8, row, "lap_path")
            self._optional_prop(mk8, row, "lap_point")
            row = box.row()
            self._optional_prop(mk8, row, "obj_path")
            self._optional_prop(mk8, row, "obj_point")
            row = box.row()
            self._optional_prop(mk8, row, "enemy_path_1")
            self._optional_prop(mk8, row, "enemy_path_2")
            row = box.row()
            self._optional_prop(mk8, row, "item_path_1")
            self._optional_prop(mk8, row, "item_path_2")
        # Relations
        box, header = self.layout.mk8_colbox(mk8, "relations_expanded")
        if mk8.relations_expanded:
            idproperty.layout_id_prop(box.row(), mk8, "area")
            idproperty.layout_id_prop(box.row(), mk8, "obj")

    def _draw_sound_obj(self, context, mk8):
        self.bl_label += " Sound Obj"
        self.layout.prop(mk8, "sound_index")
        self.layout.prop(mk8, "int_param_2")
        self.layout.prop(mk8, "inclusions")

    def _optional_prop(self, mk8, layout, path):
        # Checkbox
        row = layout.row(align=True)
        row.prop(mk8, "has_{}".format(path), text="")
        # Property
        sub = row.row(align=True)
        sub.active = getattr(mk8, "has_{}".format(path))
        sub.prop(mk8, path)


class MK8ListObjectAreaCameraArea(bpy.types.UIList):
    layout_type = 'GRID'

    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index=0, flt_flag=0):
        if self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
        layout.label(str(item.value), icon='CAMERA_DATA')


# ---- Operators ----

class MK8OpAddObject(bpy.types.Operator):
    """Add a Mario Kart 8 object to the course"""
    bl_idname = "object.mk8_add"
    bl_label = "Add MK8 Obj"

    name = bpy.props.StringProperty()
    type = bpy.props.EnumProperty(name="types", items=[
        ("AREA", "Area", "Section to control objects"),
        ("EFFECTAREA", "Effect Area", "Section with visual effects"),
        ("OBJ", "Obj", "Dynamic, interactive and / or collidable object"),
        ("SOUNDOBJ", "Sound Obj", "Region in which a sound is emitted.")])

    @staticmethod
    def menu_func(self, context):
        self.layout.separator()
        self.layout.operator_menu_enum("object.mk8_add", property="type", text="Mario Kart 8", icon='OBJECT_DATA')

    @classmethod
    def poll(cls, context):
        return bpy.context.mode == 'OBJECT'

    def execute(self, context):
        if self.type == "AREA":
            self._execute_area(context)
        elif self.type == "EFFECTAREA":
            self._execute_effect_area(context)
        elif self.type == "OBJ":
            self._execute_obj(context)
        elif self.type == "SOUNDOBJ":
            self._execute_sound_obj(context)
        return {'FINISHED'}

    def _execute_area(self, context):
        # Create a new object.
        ob = bpy.data.objects.new("Area", addon.get_default_mesh("AREACUBE"))
        ob.location = context.scene.cursor_location
        ob.rotation_mode = 'XZY'
        # Add to the scene.
        addon.add_object_to_group(ob, "Area")
        context.scene.objects.link(ob)
        # Select only the new object.
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.objects.active = ob
        ob.select = True
        # Set up the MK8 specific properties.
        ob.mk8.object_type = "AREA"
        ob.draw_type = 'WIRE'

    def _execute_effect_area(self, context):
        # Create a new object.
        ob = bpy.data.objects.new("Area", addon.get_default_mesh("AREACUBE"))
        ob.location = context.scene.cursor_location
        ob.rotation_mode = 'XZY'
        # Add to the scene.
        addon.add_object_to_group(ob, "EffectArea")
        context.scene.objects.link(ob)
        # Select only the new object.
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.objects.active = ob
        ob.select = True
        # Set up the MK8 specific properties.
        ob.mk8.object_type = "EFFECTAREA"
        ob.draw_type = 'WIRE'

    def _execute_obj(self, context):
        # Create a new object.
        ob = bpy.data.objects.new("Obj", None)
        ob.location = context.scene.cursor_location
        ob.rotation_mode = 'XZY'
        # Add to the scene.
        addon.add_object_to_group(ob, "Obj")
        context.scene.objects.link(ob)
        # Select only the new object.
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.objects.active = ob
        ob.select = True
        # Set up the MK8 specific properties.
        ob.mk8.object_type = "OBJ"
        ob.mk8.obj_id = 1013  # ItemBox
        ob.mk8.inclusions = {"Single", "Multi2P", "Multi4P", "WiFi", "WiFi2P"}
        addon.set_models(ob, ob.mk8.obj_id)

    def _execute_sound_obj(self, context):
        # Create a new object.
        ob = bpy.data.objects.new("SoundObj", None)
        ob.location = context.scene.cursor_location
        ob.rotation_mode = 'XZY'
        # Add to the scene.
        addon.add_object_to_group(ob, "SoundObj")
        context.scene.objects.link(ob)
        # Select only the new object.
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.objects.active = ob
        ob.select = True
        # Set up the MK8 specific properties.
        ob.mk8.object_type = "SOUNDOBJ"
        ob.mk8.inclusions = {"Single", "Multi2P", "Multi4P", "WiFi", "WiFi2P"}
        ob.empty_draw_type = 'SPHERE'
        ob.empty_draw_size = 1000


class MK8OperatorObjectObjIDSearch(bpy.types.Operator):
    """Search for an ObjID by name"""
    bl_idname = "object.mk8_obj_id_search"
    bl_label = "Obj ID Search"
    bl_property = "obj_id_enum"

    obj_id_enum = bpy.props.EnumProperty(items=objflow.get_label_items)

    def execute(self, context):
        context.object.mk8.obj_id = int(self.obj_id_enum)
        addon.force_update = True
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'FINISHED'}
