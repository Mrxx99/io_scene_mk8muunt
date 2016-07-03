import bpy
import bpy_extras
import os
from .editing import MK8PropsScene
from .byaml_file import ByamlFile
from .log import Log

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
        description="Filepath used for importing the course BYAML file",
        maxlen=1024,
        default=""
    )

    @staticmethod
    def menu_func_import(self, context):
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
            byaml = ByamlFile(raw)
        # Import the data into Blender objects.
        self._convert_byaml(byaml)
        return {"FINISHED"}

    def _convert_byaml(self, byaml):
        # Convert the root properties.
        Log.write(0, "BYAML " + self.filename)
        scn = self.context.scene
        scn.mk8.scene_type = str(int(MK8PropsScene.SceneType.Course))
        scn.mk8course.effect_sw = byaml.root["EffectSW"].value
        scn.mk8course.head_light = str(byaml.root["HeadLight"].value)
        scn.mk8course.is_first_left = byaml.root["IsFirstLeft"].value
        scn.mk8course.is_jugem_above = byaml.root["IsJugemAbove"].value
        scn.mk8course.jugem_above = byaml.root["JugemAbove"].value
        scn.mk8course.lap_jugem_pos = byaml.root["LapJugemPos"].value
        scn.mk8course.lap_number = byaml.root["LapNumber"].value
        scn.mk8course.obj_prm_1 = byaml.root["OBJPrm1"].value
        scn.mk8course.obj_prm_2 = byaml.root["OBJPrm2"].value
        scn.mk8course.obj_prm_3 = byaml.root["OBJPrm3"].value
        scn.mk8course.obj_prm_4 = byaml.root["OBJPrm4"].value
        scn.mk8course.obj_prm_5 = byaml.root["OBJPrm5"].value
        scn.mk8course.obj_prm_6 = byaml.root["OBJPrm6"].value
        scn.mk8course.obj_prm_7 = byaml.root["OBJPrm7"].value
        scn.mk8course.obj_prm_8 = byaml.root["OBJPrm8"].value
        # Convert the Obj instances.
        Log.write(1, "OBJ[]")
        self._convert_byaml_obj(byaml)

    def _convert_byaml_obj(self, byaml):
        for obj in byaml.root["Obj"]:
            Log.write(2, str(obj["ObjId"]))
