import bmesh
import bpy
import bpy_extras
from .byaml_file import ByamlFile

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

    def run(self):
        # Read in the file data.
        with open(self.filepath, "rb") as raw:
            byaml_file = ByamlFile(raw)
        # Import the data into Blender objects.
        self._convert_course_info(byaml_file)
        return {"FINISHED"}

    def _convert_course_info(self, byaml):
        pass
