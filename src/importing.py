import bpy
import bpy_extras
import os
from bpy.props import BoolProperty, CollectionProperty, EnumProperty, FloatProperty, IntProperty, StringProperty
from . import byaml
from . import addon

class ImportOperator(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Load a MK8 Course Info file"""
    bl_idname  = "import_scene.mk8muunt"
    bl_label   = "Import MK8 Course Info"
    bl_options = {"UNDO"}

    filename_ext = ".byaml"
    filter_glob  = StringProperty(default="*.byaml", options={"HIDDEN"})
    filepath     = StringProperty(name="File Path", description="Filepath used for importing the course BYAML file.", maxlen=1024, default="")

    import_info        = BoolProperty(name="Import Info",        description="Import general course info like the number of laps.",                                  default=True)
    import_area        = BoolProperty(name="Import Areas",       description="Imports Area instances.",                                                              default=False)
    import_clip_area   = BoolProperty(name="Import Clip Areas",  description="Imports Clip Area instances.",                                                         default=False)
    import_effect_area = BoolProperty(name="Import Effect Area", description="Imports Effect Area instances.",                                                       default=False)
    import_obj         = BoolProperty(name="Import Objs",        description="Imports Obj instances which represent animated or interactive objects on the course.", default=True)

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
        return {"FINISHED"}

    def _convert(self, root):
        # Convert the root properties. TODO: Convert all sub node types.
        addon.log(0, "BYAML " + self.filename)
        if self.operator.import_info:        self._convert_info(root)
        if self.operator.import_area:        self._convert_areas(root)
        if self.operator.import_clip_area:   self._convert_clip_areas(root)
        if self.operator.import_effect_area: self._convert_effect_areas(root)
        if self.operator.import_obj:         self._convert_objs(root)

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
            setattr(mk8, "obj_prm_" + str(i), root.get("OBJPrm" + str(i), 0))
        mk8.pattern_num = root.get("PatternNum", 0)

    # ---- Area ----

    def _convert_areas(self, root):
        areas = root.get("Area")
        if areas:
            addon.log(1, "AREA[" + str(len(areas)) + "]")
            for i, area in enumerate(areas):
                ob = self._convert_area(area)
                ob.mk8.index = i

    def _convert_area(self, area):
        addon.log(2, "AREA")
        # Create a wireframe object with a mesh representing the Area.
        area_shape = str(area["AreaShape"])
        mesh = addon.get_default_mesh(area_shape)
        ob = bpy.data.objects.new("Area", mesh)
        ob.draw_type = "WIRE"
        # General
        ob.mk8.object_type = "AREA"
        ob.mk8.unit_id_num = area["UnitIdNum"]
        ob.mk8.float_param_1 = area["prm1"]
        ob.mk8.float_param_2 = area["prm2"]
        ob.mk8.area_shape = area_shape
        ob.mk8.area_type = str(area["AreaType"])
        ob.mk8.area_path = area.get("Area_Path", 0)
        ob.mk8.area_pull_path = area.get("Area_PullPath", 0)
        # Camera Areas
        camera_areas = area.get("Camera_Area")
        if camera_areas:
            for i in range(0, len(camera_areas)):
                ob.mk8.camera_areas.add().value = camera_areas[i]
        # Transform
        ob.location = Importer.vector_from_dict(area["Translate"], invert_z=True)
        ob.rotation_mode = "XZY"
        ob.rotation_euler = Importer.vector_from_dict(area["Rotate"], invert_z=True)
        ob.scale = Importer.vector_from_dict(area["Scale"])
        # Group and link.
        addon.add_object_to_group(ob, "Area")
        bpy.context.scene.objects.link(ob)
        return ob

    # ---- Clip Area ----

    def _convert_clip_areas(self, root):
        clip_areas = root.get("ClipArea")
        if clip_areas:
            addon.log(1, "CLIPAREA[" + str(len(clip_areas)) + "]")
            for i, clip_area in enumerate(clip_areas):
                ob = self._convert_clip_area(clip_area)
                ob.mk8.index = i

    def _convert_clip_area(self, clip_area):
        addon.log(2, "CLIPAREA")
        # Create a wireframe object with a mesh representing the Clip Area.
        clip_area_shape = str(clip_area["AreaShape"])
        mesh = addon.get_default_mesh(clip_area_shape)
        ob = bpy.data.objects.new("ClipArea", mesh)
        ob.draw_type = "WIRE"
        # General
        ob.mk8.object_type = "CLIPAREA"
        ob.mk8.unit_id_num = clip_area["UnitIdNum"]
        ob.mk8.float_param_1 = clip_area["prm1"]
        ob.mk8.float_param_2 = clip_area["prm2"]
        ob.mk8.area_shape = clip_area_shape
        ob.mk8.clip_area_type = str(clip_area["AreaType"])
        # Transform
        ob.location = Importer.vector_from_dict(clip_area["Translate"], invert_z=True)
        ob.rotation_mode = "XZY"
        ob.rotation_euler = Importer.vector_from_dict(clip_area["Rotate"], invert_z=True)
        ob.scale = Importer.vector_from_dict(clip_area["Scale"])
        # Group and link.
        addon.add_object_to_group(ob, "ClipArea")
        bpy.context.scene.objects.link(ob)
        return ob

    # ---- Effect Area ----

    def _convert_effect_areas(self, root):
        effect_areas = root.get("EffectArea")
        if effect_areas:
            addon.log(1, "EFFECTAREA[" + str(len(effect_areas)) + "]")
            for i, effect_area in enumerate(effect_areas):
                ob = self._convert_effect_area(effect_area)
                ob.mk8.index = ob

    def _convert_effect_area(self, effect_area):
        addon.log(2, "EFFECTAREA")
        # Create a wireframe object with a mesh representing the Effect Area.
        mesh = addon.get_default_mesh("AREACUBE")
        ob = bpy.data.objects.new("EffectArea", mesh)
        ob.draw_type = "WIRE"
        # General
        ob.mk8.object_type = "EFFECTAREA"
        ob.mk8.unit_id_num = effect_area["UnitIdNum"]
        ob.mk8.float_param_1 = effect_area["prm1"]
        ob.mk8.float_param_2 = effect_area["prm2"]
        ob.mk8.effect_sw = effect_area["EffectSW"]
        # Transform
        ob.location = Importer.vector_from_dict(effect_area["Translate"], invert_z=True)
        ob.rotation_mode = "XZY"
        ob.rotation_euler = Importer.vector_from_dict(effect_area["Rotate"], invert_z=True)
        ob.scale = Importer.vector_from_dict(effect_area["Scale"])
        # Group and link.
        addon.add_object_to_group(ob, "EffectArea")
        bpy.context.scene.objects.link(ob)
        return ob

    # ---- Obj ----

    def _convert_objs(self, root):
        objs = root.get("Obj")
        if objs:
            addon.log(1, "OBJ[" + str(len(objs)) + "]")
            # Import instances.
            obs = []
            for obj in objs:
                obs.append(self._convert_obj(obj))
            # Satisfy index references.
            for ob in obs:
                if ob.mk8.obj_idx >= 0:
                    ob.mk8.obj = obs[ob.mk8.obj_idx].name

    def _convert_obj(self, obj):
        def set_optional(name, attribute):
            value = obj.get(name)
            if value is not None:
                setattr(mk8, "has_" + attribute, True)
                setattr(mk8, attribute, value)

        def set_optional_idx(name, attribute):
            value = obj.get(name)
            if value is not None:
                setattr(mk8, attribute + "_idx", value)

        addon.log(2, "OBJ " + str(obj["ObjId"]))
        # Create an object representing the Obj.
        ob = bpy.data.objects.new("Obj", None)
        mk8 = ob.mk8
        # General
        mk8.unit_id_num = obj["UnitIdNum"]
        mk8.obj_id = obj["ObjId"]
        mk8.speed = obj["Speed"]
        mk8.no_col = obj.get("NoCol", False)
        mk8.top_view = obj["TopView"]
        # Relations
        set_optional_idx("Obj_Obj", "obj")
        set_optional("Area_Obj", "area_obj")
        # Paths
        set_optional("Obj_Path",       "path")
        set_optional("Obj_PathPoint",  "path_point")
        set_optional("Obj_LapPath",    "lap_path")
        set_optional("Obj_LapPoint",   "lap_point")
        set_optional("Obj_ObjPath",    "obj_path")
        set_optional("Obj_ObjPoint",   "obj_point")
        set_optional("Obj_EnemyPath1", "enemy_path_1")
        set_optional("Obj_EnemyPath2", "enemy_path_2")
        set_optional("Obj_ItemPath1",  "item_path_1")
        set_optional("Obj_ItemPath2",  "item_path_2")
        # Parameters
        for i, param in enumerate(obj["Params"]):
            setattr(mk8, "float_param_" + str(i + 1), param)
        # Exclusions
        mk8.single = obj.get("Single", False)
        mk8.multi_2p = obj["Multi2P"]
        mk8.multi_4p = obj["Multi4P"]
        mk8.wifi = obj["WiFi"]
        mk8.wifi_2p = obj["WiFi2P"]
        # Transform
        ob.location = Importer.vector_from_dict(obj["Translate"], invert_z=True)
        ob.rotation_mode = "XZY"
        ob.rotation_euler = Importer.vector_from_dict(obj["Rotate"], invert_z=True)
        ob.scale = Importer.vector_from_dict(obj["Scale"])
        # Group, link and update.
        addon.add_object_to_group(ob, "Obj")
        bpy.context.scene.objects.link(ob)
        bpy.context.scene.objects.active = ob
        mk8.object_type = "OBJ"
        return ob

    @staticmethod
    def vector_from_dict(dictionary, invert_z=False):
        if invert_z:
            return dictionary["X"], -dictionary["Z"], dictionary["Y"]
        else:
            return dictionary["X"], dictionary["Z"], dictionary["Y"]
