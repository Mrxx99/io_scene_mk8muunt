import bpy
import bpy_extras
import os
from . import byaml
from . import addon
from . import objflow
from . import editing

class ImportOperator(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    bl_idname = "import_scene.mk8muunt"
    bl_label = "Import Mario Kart 8 Course Info"
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

    @staticmethod
    def menu_func(self, context):
        self.layout.operator(ImportOperator.bl_idname, text="Mario Kart 8 Course Info (muunt.byaml)")

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
        scn.mk8.scene_type = str(int(editing.MK8PropsScene.SceneType.Course))
        scn.mk8course.effect_sw = root.get_value("EffectSW", 0)
        scn.mk8course.head_light = str(root.get_value("HeadLight", 0))
        scn.mk8course.is_first_left = root.get_value("IsFirstLeft", False)
        scn.mk8course.is_jugem_above = root.get_value("IsJugemAbove", False)
        scn.mk8course.jugem_above = root.get_value("JugemAbove", 0)
        scn.mk8course.lap_jugem_pos = root.get_value("LapJugemPos", 0)
        scn.mk8course.lap_number = root.get_value("LapNumber", 0)
        for i in range(1, 9):
            setattr(scn.mk8course, "obj_prm_" + str(i), root.get_value("OBJPrm" + str(i), 0))
        scn.mk8course.pattern_num = root.get_value("PatternNum", 0)
        # TODO: Convert all sub node types.
        self._convert_areas(root)
        self._convert_objs(root)
        # alias existing group, or generate new group and alias that

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
        area_shape = editing.MK8PropsObjectArea.AreaShape(area["AreaShape"].value)
        if area_shape == editing.MK8PropsObjectArea.AreaShape.Cube:
            mesh = addon.get_default_model(addon.DefaultModel.AreaCube)
        elif area_shape == editing.MK8PropsObjectArea.AreaShape.Sphere:
            mesh = addon.get_default_model(addon.DefaultModel.AreaSphere)
        ob = bpy.data.objects.new("Area", mesh)
        ob.draw_type = "WIRE"
        # General
        ob.mk8.object_type = str(int(editing.MK8PropsObject.ObjectType.Area))
        ob.mk8area.unit_id_num = area["UnitIdNum"].value
        ob.mk8area.area_shape = str(area["AreaShape"].value)
        if ob.mk8area.area_shape == "0":
            ob.empty_draw_type = "CUBE"
        elif ob.mk8area.area_shape == "1":
            ob.empty_draw_type = "SPHERE"
        ob.mk8area.area_type = str(area["AreaType"].value)
        ob.mk8area.area_path = area.get_value("Area_Path", 0)
        ob.mk8area.area_pull_path = area.get_value("Area_PullPath", 0)
        ob.mk8area.prm1 = area["prm1"].value
        ob.mk8area.prm2 = area["prm2"].value
        # Camera Areas
        camera_areas = area.get_value("Camera_Area")
        if camera_areas:
            for i in range(0, len(camera_areas)):
                ob.mk8area.camera_areas.add().value = camera_areas[i].value
        # Transform
        ob.scale = area["Scale"].to_vector()
        ob.rotation_euler = area["Rotate"].to_vector()
        ob.location = area["Translate"].to_vector()
        # Group and link.
        self._add_to_group(ob, "Areas")
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
        ob.mk8.object_type = str(int(editing.MK8PropsObject.ObjectType.Obj))
        ob.mk8obj.unit_id_num = obj["UnitIdNum"].value
        ob.mk8obj.multi_2p = obj["Multi2P"].value
        ob.mk8obj.multi_4p = obj["Multi4P"].value
        ob.mk8obj.obj_id = obj["ObjId"].value
        ob.mk8obj.speed = obj["Speed"].value
        ob.mk8obj.obj_path_point = obj.get_value("Obj_PathPoint", 0)
        ob.mk8obj.obj_path = obj.get_value("Obj_Path", 0)
        ob.mk8obj.obj_obj_path = obj.get_value("Obj_ObjPath", 0)
        ob.mk8obj.obj_enemy_path_1 = obj.get_value("Obj_EnemyPath1", 0)
        ob.mk8obj.obj_enemy_path_2 = obj.get_value("Obj_EnemyPath2", 0)
        ob.mk8obj.obj_item_path_1 = obj.get_value("Obj_ItemPath1", 0)
        ob.mk8obj.obj_item_path_2 = obj.get_value("Obj_ItemPath2", 0)
        ob.mk8obj.top_view = obj["TopView"].value
        ob.mk8obj.wifi = obj["WiFi"].value
        ob.mk8obj.wifi_2p = obj["WiFi2P"].value
        # Parameters
        for i, param in enumerate(obj["Params"]):
            setattr(ob.mk8obj, "prm_" + str(i), param.value)
        # Transform
        ob.scale = obj["Scale"].to_vector()
        ob.rotation_euler = obj["Rotate"].to_vector()
        ob.location = obj["Translate"].to_vector()
        # Group and link.
        self._add_to_group(ob, "Objs")
        bpy.context.scene.objects.link(ob)
