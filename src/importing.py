import bpy
import bpy_extras
import os
from . import byaml
from . import addon


class ImportOperator(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Load a MK8 Course Info file"""
    bl_idname = "import_scene.mk8muunt"
    bl_label = "Import MK8 Course Info"
    bl_options = {'UNDO'}

    filename_ext = ".byaml"
    filter_glob = bpy.props.StringProperty(default="*.byaml", options={'HIDDEN'})
    filepath = bpy.props.StringProperty(name="File Path", description="Filepath used for importing the course BYAML file.", maxlen=1024, default="")

    show_areas = bpy.props.BoolProperty(name="Show Areas", description="Makes Areas visible after loading.")
    show_clip_areas = bpy.props.BoolProperty(name="Show Clip Areas", description="Makes Clip Areas visible after loading.")
    show_effect_areas = bpy.props.BoolProperty(name="Show Effect Areas", description="Makes Effect Areas visible after loading.")

    @staticmethod
    def menu_func(self, context):
        self.layout.operator(ImportOperator.bl_idname, text="MK8 Course Info (.byaml)")

    def execute(self, context):
        importer = Importer(self, context, self.properties.filepath)
        return importer.run()


class Importer:
    def __init__(self, operator, context, filepath):
        self.operator = operator
        self.context = context
        self.filepath = filepath
        self.filename = os.path.basename(self.filepath)

    def run(self):
        # Read in the file data.
        with open(self.filepath, "rb") as raw:
            addon.loaded_byaml = byaml.File()
            addon.loaded_byaml.load_raw(raw)
        # Import the data into Blender objects.
        self._convert(addon.loaded_byaml.root)
        return {'FINISHED'}

    def _convert(self, root):
        # TODO: Convert all sub node types.
        addon.log(0, "BYAML {}".format(self.filename))
        self._convert_info(root)
        areas = self._convert_areas(root)
        clip_areas = self._convert_clip_areas(root)
        effect_areas = self._convert_effect_areas(root)
        objs = self._convert_objs(root, areas)

    # ---- Info ----

    def _convert_info(self, root):
        mk8 = self.context.scene.mk8
        mk8.scene_type = "COURSE"
        mk8.effect_sw = root.get("EffectSW", 0)
        mk8.head_light = str(root.get("HeadLight", 0))
        mk8.is_first_left = root.get("IsFirstLeft", False)
        mk8.is_jugem_above = root.get("IsJugemAbove", False)
        mk8.jugem_above = root.get("JugemAbove", 0)
        mk8.lap_jugem_pos = root.get("LapJugemPos", 0)
        mk8.lap_number = root.get("LapNumber", 0)
        for i in range(1, 9):
            setattr(mk8, "obj_prm_{}".format(i), root.get("OBJPrm{}".format(i), 0))
        mk8.pattern_num = root.get("PatternNum", 0)

    # ---- Area ----

    def _convert_areas(self, root):
        obs = []
        areas = root.get("Area")
        if areas:
            addon.log(1, "AREA[{}]".format(len(areas)))
            # Import instances.
            for area in areas:
                ob = self._convert_area(area)
                ob.hide = not self.operator.show_areas
                obs.append(ob)
        return obs

    def _convert_area(self, area):
        # Create a wireframe object with a mesh representing the Area.
        addon.log(2, "AREA")
        ob = bpy.data.objects.new("Area", addon.get_default_mesh("AREACUBE"))
        ob.draw_type = 'WIRE'
        addon.add_object_to_group(ob, "Area")
        self.context.scene.objects.link(ob)
        self.context.scene.objects.active = ob
        # General
        mk8 = ob.mk8
        mk8.object_type = "AREA"
        mk8.unit_id_num = area["UnitIdNum"]
        mk8.float_param_1 = area["prm1"]
        mk8.float_param_2 = area["prm2"]
        mk8.area_type = str(area["AreaType"])
        mk8.area_shape = str(area["AreaShape"])
        Importer.set_optional(area, mk8, "Area_Path", "area_path")
        Importer.set_optional(area, mk8, "Area_PullPath", "area_pull_path")
        # Camera Areas
        camera_areas = area.get("Camera_Area")
        if camera_areas:
            for i in range(0, len(camera_areas)):
                mk8.camera_areas.add().value = camera_areas[i]
        # Transform
        ob.location = Importer.vector_from_dict(area["Translate"], invert_z=True)
        ob.rotation_mode = 'XZY'
        ob.rotation_euler = Importer.vector_from_dict(area["Rotate"], invert_z=True)
        ob.scale = Importer.vector_from_dict(area["Scale"])
        return ob

    # ---- Clip Area ----

    def _convert_clip_areas(self, root):
        obs = []
        clip_areas = root.get("ClipArea")
        if clip_areas:
            addon.log(1, "CLIPAREA[{}]".format(len(clip_areas)))
            # Import instances.
            for clip_area in clip_areas:
                ob = self._convert_clip_area(clip_area)
                ob.hide = not self.operator.show_clip_areas
                obs.append(ob)
        return obs

    def _convert_clip_area(self, clip_area):
        # Create a wireframe object with a mesh representing the Clip Area.
        addon.log(2, "CLIPAREA")
        ob = bpy.data.objects.new("ClipArea", addon.get_default_mesh("AREACUBE"))
        ob.draw_type = 'WIRE'
        addon.add_object_to_group(ob, "ClipArea")
        self.context.scene.objects.link(ob)
        self.context.scene.objects.active = ob
        # General
        mk8 = ob.mk8
        mk8.object_type = "CLIPAREA"
        mk8.unit_id_num = clip_area["UnitIdNum"]
        mk8.float_param_1 = clip_area["prm1"]
        mk8.float_param_2 = clip_area["prm2"]
        mk8.area_shape = str(clip_area["AreaShape"])
        mk8.clip_area_type = str(clip_area["AreaType"])
        # Transform
        ob.location = Importer.vector_from_dict(clip_area["Translate"], invert_z=True)
        ob.rotation_mode = 'XZY'
        ob.rotation_euler = Importer.vector_from_dict(clip_area["Rotate"], invert_z=True)
        ob.scale = Importer.vector_from_dict(clip_area["Scale"])
        return ob

    # ---- Effect Area ----

    def _convert_effect_areas(self, root):
        obs = []
        effect_areas = root.get("EffectArea")
        if effect_areas:
            addon.log(1, "EFFECTAREA[{}]".format(len(effect_areas)))
            # Import instances.
            for effect_area in effect_areas:
                ob = self._convert_effect_area(effect_area)
                ob.hide = not self.operator.show_effect_areas
                obs.append(ob)
        return obs

    def _convert_effect_area(self, effect_area):
        # Create a wireframe object with a mesh representing the Effect Area.
        addon.log(2, "EFFECTAREA")
        ob = bpy.data.objects.new("EffectArea", addon.get_default_mesh("AREACUBE"))
        ob.draw_type = 'WIRE'
        addon.add_object_to_group(ob, "EffectArea")
        self.context.scene.objects.link(ob)
        self.context.scene.objects.active = ob
        # General
        ob.mk8.object_type = "EFFECTAREA"
        ob.mk8.unit_id_num = effect_area["UnitIdNum"]
        ob.mk8.float_param_1 = effect_area["prm1"]
        ob.mk8.float_param_2 = effect_area["prm2"]
        ob.mk8.effect_sw = effect_area["EffectSW"]
        # Transform
        ob.location = Importer.vector_from_dict(effect_area["Translate"], invert_z=True)
        ob.rotation_mode = 'XZY'
        ob.rotation_euler = Importer.vector_from_dict(effect_area["Rotate"], invert_z=True)
        ob.scale = Importer.vector_from_dict(effect_area["Scale"])
        return ob

    # ---- Obj ----

    def _convert_objs(self, root, areas):
        obs = []
        objs = root.get("Obj")
        if objs:
            addon.log(1, "OBJ[{}]".format(len(objs)))
            # Import instances.
            for obj in objs:
                obs.append(self._convert_obj(obj))
            # Satisfy references.
            for ob in obs:
                if ob.mk8.area_idx >= 0:
                    ob.mk8.area = areas[ob.mk8.area_idx].name
                if ob.mk8.obj_idx >= 0:
                    ob.mk8.obj = obs[ob.mk8.obj_idx].name
        return obs

    def _convert_obj(self, obj):
        # Create an object representing the Obj.
        addon.log(2, "OBJ {}".format(obj["ObjId"]))
        ob = bpy.data.objects.new("Obj", None)
        addon.add_object_to_group(ob, "Obj")
        self.context.scene.objects.link(ob)
        self.context.scene.objects.active = ob
        # General
        mk8 = ob.mk8
        mk8.object_type = "OBJ"
        mk8.unit_id_num = obj["UnitIdNum"]
        mk8.obj_id = obj["ObjId"]
        mk8.speed = obj["Speed"]
        mk8.no_col = obj.get("NoCol", False)
        mk8.top_view = obj["TopView"]
        for i in ("Single", "Multi2P", "Multi4P", "WiFi", "WiFi2P"):
            if not obj.get(i, False):
                mk8.inclusions |= {i}
        # Paths
        Importer.set_optional(obj, mk8, "Obj_Path", "path")
        Importer.set_optional(obj, mk8, "Obj_PathPoint", "path_point")
        Importer.set_optional(obj, mk8, "Obj_LapPath", "lap_path")
        Importer.set_optional(obj, mk8, "Obj_LapPoint", "lap_point")
        Importer.set_optional(obj, mk8, "Obj_ObjPath", "obj_path")
        Importer.set_optional(obj, mk8, "Obj_ObjPoint", "obj_point")
        Importer.set_optional(obj, mk8, "Obj_EnemyPath1", "enemy_path_1")
        Importer.set_optional(obj, mk8, "Obj_EnemyPath2", "enemy_path_2")
        Importer.set_optional(obj, mk8, "Obj_ItemPath1", "item_path_1")
        Importer.set_optional(obj, mk8, "Obj_ItemPath2", "item_path_2")
        # Relations
        Importer.set_optional_idx(obj, mk8, "Area_Obj", "area")
        Importer.set_optional_idx(obj, mk8, "Obj_Obj", "obj")
        # Parameters
        for i, param in enumerate(obj["Params"]):
            setattr(mk8, "float_param_{}".format(i + 1), param)
        # Transform
        ob.location = Importer.vector_from_dict(obj["Translate"], invert_z=True)
        ob.rotation_mode = "XZY"
        ob.rotation_euler = Importer.vector_from_dict(obj["Rotate"], invert_z=True)
        ob.scale = Importer.vector_from_dict(obj["Scale"])
        return ob

    # ---- General ----

    @staticmethod
    def set_optional(node, mk8, name, attribute):
        value = node.get(name)
        if value is not None:
            setattr(mk8, "has_{}".format(attribute), True)
            setattr(mk8, attribute, value)

    @staticmethod
    def set_optional_idx(node, mk8, name, attribute):
        value = node.get(name)
        if value is not None:
            setattr(mk8, "{}_idx".format(attribute), value)

    @staticmethod
    def vector_from_dict(dictionary, invert_z=False):
        if invert_z:
            return dictionary["X"], -dictionary["Z"], dictionary["Y"]
        else:
            return dictionary["X"], dictionary["Z"], dictionary["Y"]
