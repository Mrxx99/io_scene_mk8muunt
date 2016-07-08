import bpy
import bpy_extras
from . import binary_io

class ExportOperator(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    bl_idname = "export_scene.mk8muunt"
    bl_label = "Export MK8 Course Info"

    filename_ext = ".byaml"
    filter_glob = bpy.props.StringProperty(
        default = "*_muunt*.byaml",
        options = {"HIDDEN"}
    )
    filepath = bpy.props.StringProperty(
        name = "File Path",
        description = "Filepath used for exporting the course BYAML file.",
        maxlen = 1024,
        default = ""
    )
    check_extension = True

    @staticmethod
    def menu_func(self, context):
        self.layout.operator(ExportOperator.bl_idname, text ="MK8 Course Info (muunt.byaml)")

    def execute(self, context):
        exporter = Exporter(self, context, self.properties.filepath)
        return exporter.run()

class Exporter:
    def __init__(self, operator, context, filepath):
        self.operator = operator
        self.context = context
        self.filepath = filepath

    def run(self):
        # TODO: Prepare the course info data.
        # TODO: Export the course info data with a big-endian binary writer on the file.
        with binary_io.BinaryWriter(open(self.filepath, "wb")) as writer:
            writer.endianness = ">"
            # TODO: Write the header.
