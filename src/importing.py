import bpy
import bpy_extras
import os
from . import byaml
from . import addon
from . import objflow
from . import editing

class ImportOperator(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    bl_idname = "import_scene.mk8muunt"
    bl_label = "Import MK8 Course Info"
    bl_options = {"UNDO"}

    filename_ext = ".byaml"
    filter_glob = bpy.props.StringProperty(
        default="*_muunt*.byaml",
        options={"HIDDEN"}
    )
    filepath = bpy.props.StringProperty(
        name="File Path",
        description="Filepath used for importing the course BYAML file.",
        maxlen=1024,
        default=""
    )

    import_area = bpy.props.BoolProperty(
        name="Import Areas",
        description="Imports Area instances.",
        default=True
    )
    import_clip_area = bpy.props.BoolProperty(
        name="Import Clip Areas",
        description="Imports Clip Area instances.",
        default=True
    )
    import_effect_area = bpy.props.BoolProperty(
        name="Import Effect Area",
        description="Imports Effect Area instances.",
        default=True
    )
    import_obj = bpy.props.BoolProperty(
        name="Import Objs",
        description="Imports Obj instances which represent animated or interactive objects on the course.",
        default=True
    )

    @staticmethod
    def menu_func(self, context):
        self.layout.operator(ImportOperator.bl_idname, text="MK8 Course Info (muunt.byaml)")

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
            byaml_file = byaml.ByamlFile(raw)
        # Import the data into Blender objects.
        self._convert(byaml_file.root)
        return {"FINISHED"}

    def _convert(self, root):
        # Convert the root properties.
        addon.log(0, "BYAML " + self.filename)
        scn = self.context.scene
        scn.mk8.scene_type = "COURSE"
        scn.mk8_course.effect_sw = root.get_value("EffectSW", 0)
        scn.mk8_course.head_light = editing.MK8PropsSceneCourse.head_light[1]["items"][root.get_value("HeadLight", 0)][0]
        scn.mk8_course.is_first_left = root.get_value("IsFirstLeft", False)
        scn.mk8_course.is_jugem_above = root.get_value("IsJugemAbove", False)
        scn.mk8_course.jugem_above = root.get_value("JugemAbove", 0)
        scn.mk8_course.lap_jugem_pos = root.get_value("LapJugemPos", 0)
        scn.mk8_course.lap_number = root.get_value("LapNumber", 0)
        for i in range(1, 9):
            setattr(scn.mk8_course, "obj_prm_" + str(i), root.get_value("OBJPrm" + str(i), 0))
        scn.mk8_course.pattern_num = root.get_value("PatternNum", 0)
        # TODO: Convert all sub node types.
        if self.operator.import_area:        self._convert_areas(root)
        if self.operator.import_clip_area:   self._convert_clip_areas(root)
        if self.operator.import_effect_area: self._convert_effect_areas(root)
        if self.operator.import_obj:         self._convert_objs(root)

    def _add_to_group(self, ob, group_name):
        # Get or create the required group.
        group = bpy.data.groups.get(group_name, bpy.data.groups.new(group_name))
        # Link the provided object to it.
        if ob.name not in group.objects:
            group.objects.link(ob)

    # ---- Area ----

    def _convert_areas(self, root):
        areas = root.get("Area")
        if areas:
            addon.log(1, "AREA[" + str(len(areas)) + "]")
            for area in areas:
                self._convert_area(area)

    def _convert_area(self, area):
        addon.log(2, "AREA")
        # Create a wireframe object with a mesh representing the Area.
        area_shape = editing.MK8PropsObjectArea.area_shape[1]["items"][area["AreaShape"].value][0]
        mesh = addon.get_default_mesh(area_shape)
        ob = bpy.data.objects.new("Area", mesh)
        ob.draw_type = "WIRE"
        # General
        ob.mk8.object_type = "AREA"
        ob.mk8_area.unit_id_num = area["UnitIdNum"].value
        ob.mk8_area.prm1 = area["prm1"].value
        ob.mk8_area.prm2 = area["prm2"].value
        ob.mk8_area.area_shape = area_shape
        ob.mk8_area.area_type = editing.MK8PropsObjectArea.area_type[1]["items"][area["AreaType"].value][0]
        ob.mk8_area.area_path = area.get_value("Area_Path", 0)
        ob.mk8_area.area_pull_path = area.get_value("Area_PullPath", 0)
        # Camera Areas
        camera_areas = area.get_value("Camera_Area")
        if camera_areas:
            for i in range(0, len(camera_areas)):
                ob.mk8_area.camera_areas.add().value = camera_areas[i].value
        # Transform
        ob.scale = area["Scale"].to_vector()
        ob.rotation_euler = area["Rotate"].to_vector()
        ob.location = area["Translate"].to_vector()
        # Group and link.
        self._add_to_group(ob, "Area")
        bpy.context.scene.objects.link(ob)

    # ---- Clip Area ----

    def _convert_clip_areas(self, root):
        clip_areas = root.get("ClipArea")
        if clip_areas:
            addon.log(1, "CLIPAREA[" + str(len(clip_areas)) + "]")
            for clip_area in clip_areas:
                self._convert_clip_area(clip_area)

    def _convert_clip_area(self, clip_area):
        addon.log(2, "CLIPAREA")
        # Create a wireframe object with a mesh representing the Clip Area.
        area_shape = editing.MK8PropsObjectClipArea.area_shape[1]["items"][clip_area["AreaShape"].value][0]
        mesh = addon.get_default_mesh(area_shape)
        ob = bpy.data.objects.new("ClipArea", mesh)
        ob.draw_type = "WIRE"
        # General
        ob.mk8.object_type = "CLIPAREA"
        ob.mk8_clip_area.unit_id_num = clip_area["UnitIdNum"].value
        ob.mk8_clip_area.prm1 = clip_area["prm1"].value
        ob.mk8_clip_area.prm2 = clip_area["prm2"].value
        ob.mk8_clip_area.area_shape = area_shape
        area_type = clip_area["AreaType"].value
        if    area_type == 5: ob.mk8_clip_area.area_type = "UNKNOWN5"
        else: raise AssertionError("Unknown clip area type.")
        # Transform
        ob.scale = clip_area["Scale"].to_vector()
        ob.rotation_euler = clip_area["Rotate"].to_vector()
        ob.location = clip_area["Translate"].to_vector()
        # Group and link.
        self._add_to_group(ob, "ClipArea")
        bpy.context.scene.objects.link(ob)

    # ---- Effect Area ----

    def _convert_effect_areas(self, root):
        effect_areas = root.get("EffectArea")
        if effect_areas:
            addon.log(1, "EFFECTAREA[" + str(len(effect_areas)) + "]")
            for effect_area in effect_areas:
                self._convert_effect_area(effect_area)

    def _convert_effect_area(self, effect_area):
        addon.log(2, "EFFECTAREA")
        # Create a wireframe object with a mesh representing the Effect Area.
        mesh = addon.get_default_mesh("AREACUBE")
        ob = bpy.data.objects.new("EffectArea", mesh)
        ob.draw_type = "WIRE"
        # General
        ob.mk8.object_type = "EFFECTAREA"
        ob.mk8_effect_area.unit_id_num = effect_area["UnitIdNum"].value
        ob.mk8_effect_area.prm1 = effect_area["prm1"].value
        ob.mk8_effect_area.prm2 = effect_area["prm2"].value
        ob.mk8_effect_area.effect_sw = effect_area["EffectSW"].value
        # Transform
        ob.scale = effect_area["Scale"].to_vector()
        ob.rotation_euler = effect_area["Rotate"].to_vector()
        ob.location = effect_area["Translate"].to_vector()
        # Group and link.
        self._add_to_group(ob, "EffectArea")
        bpy.context.scene.objects.link(ob)

    # ---- Obj ----

    def _convert_objs(self, root):
        objs = root.get("Obj")
        if objs:
            addon.log(1, "OBJ[" + str(len(objs)) + "]")
            for obj in objs:
                self._convert_obj(obj)

    def _convert_obj(self, obj):
        addon.log(2, "OBJ " + str(obj["ObjId"]))
        # Create an object representing the Obj (load the real model later on).
        ob_name = objflow.get_obj_label(self.context, obj["ObjId"].value)
        ob = bpy.data.objects.new(ob_name, None)
        ob.empty_draw_size = 10
        # General
        ob.mk8.object_type = "OBJ"
        ob.mk8_obj.unit_id_num = obj["UnitIdNum"].value
        ob.mk8_obj.multi_2p = obj["Multi2P"].value
        ob.mk8_obj.multi_4p = obj["Multi4P"].value
        ob.mk8_obj.obj_id = obj["ObjId"].value
        ob.mk8_obj.speed = obj["Speed"].value
        ob.mk8_obj.obj_path_point = obj.get_value("Obj_PathPoint", 0)
        ob.mk8_obj.obj_path = obj.get_value("Obj_Path", 0)
        ob.mk8_obj.obj_obj_path = obj.get_value("Obj_ObjPath", 0)
        ob.mk8_obj.obj_enemy_path_1 = obj.get_value("Obj_EnemyPath1", 0)
        ob.mk8_obj.obj_enemy_path_2 = obj.get_value("Obj_EnemyPath2", 0)
        ob.mk8_obj.obj_item_path_1 = obj.get_value("Obj_ItemPath1", 0)
        ob.mk8_obj.obj_item_path_2 = obj.get_value("Obj_ItemPath2", 0)
        ob.mk8_obj.top_view = obj["TopView"].value
        ob.mk8_obj.wifi = obj["WiFi"].value
        ob.mk8_obj.wifi_2p = obj["WiFi2P"].value
        # Parameters
        for i, param in enumerate(obj["Params"]):
            setattr(ob.mk8_obj, "prm_" + str(i), param.value)
        # Transform
        ob.scale = obj["Scale"].to_vector()
        ob.rotation_euler = obj["Rotate"].to_vector()
        ob.location = obj["Translate"].to_vector()
        # Group and link.
        self._add_to_group(ob, "Obj")
        bpy.context.scene.objects.link(ob)
