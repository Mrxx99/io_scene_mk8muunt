import bpy
import bpy_extras
import copy
from . import addon
from . import byaml
from . import objflow

class ExportOperator(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """Save a MK8 Course Info file"""
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

    replace_obj = bpy.props.BoolProperty(
        name="Replace Objs",
        description="Replace Obj instances which represent animated or interactive objects on the course.",
        default=True
    )
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
        # Create a copy of the loaded BYAML and replace only parts set to be replaced.
        file = byaml.File()
        file.root = copy.deepcopy(addon.loaded_byaml.root) # TODO: addon.loaded_byaml is None when addon is reloaded.
        if self.operator.replace_obj: self.replace_objs(file.root)
        # Save course info data to a file.
        file.save_raw(open(self.filepath, "wb"))
        return {"FINISHED"}

    def replace_objs(self, root):
        # Create the Obj array.
        objs = []
        map_ids = []
        map_res_names = []
        group = bpy.data.groups.get("Obj", None)
        for ob in group.objects:
            # Add the instance to the Obj list and remember ID and ResNames.
            obj = ob.mk8
            map_ids.append(obj.obj_id)
            map_res_names.extend(objflow.get_obj_res_names(self.context, obj.obj_id))
            objs.append(self.get_obj_node(ob))
        # Sort descending by ObjID
        objs.sort(key=lambda o: o["ObjId"], reverse=True)
        root["Obj"] = objs
        # Create the distinct MapObjIdList and MapObjResList contents.
        root["MapObjIdList"] = list(set(map_ids))
        root["MapObjIdList"].sort(reverse=True)
        root["MapObjResList"] = list(set(map_res_names))

    def get_obj_node(self, ob):
        mk8 = ob.mk8
        # General
        obj = {
            "UnitIdNum": mk8.unit_id_num, # 0 might seem to work without any issues.
            "ObjId": mk8.obj_id,
            "Multi2P": mk8.multi_2p,
            "Multi4P": mk8.multi_4p,
            "WiFi": mk8.wifi,
            "WiFi2P": mk8.wifi_2p,
            "TopView": mk8.top_view,
            "Speed": mk8.speed,
            "Params": []
        }
        if mk8.no_col:
            obj["NoCol"] = True
        # Params
        for i in range(1, 9):
            obj["Params"].append(getattr(mk8, "float_param_" + str(i)))
        # Relations
        if mk8.has_obj_obj:          obj["Obj_Obj"]        = mk8.obj_obj
        # Paths
        if mk8.has_obj_path:         obj["Obj_Path"]       = mk8.obj_path
        if mk8.has_obj_path_point:   obj["Obj_PathPoint"]  = mk8.obj_path_point
        if mk8.has_obj_obj_path:     obj["Obj_ObjPath"]    = mk8.obj_obj_path
        if mk8.has_obj_obj_point:    obj["Obj_ObjPoint"]   = mk8.obj_obj_point
        if mk8.has_obj_enemy_path_1: obj["Obj_EnemyPath1"] = mk8.obj_enemy_path_1
        if mk8.has_obj_enemy_path_2: obj["Obj_EnemyPath2"] = mk8.obj_enemy_path_2
        if mk8.has_obj_item_path_1:  obj["Obj_ItemPath1"]  = mk8.obj_item_path_1
        if mk8.has_obj_item_path_2:  obj["Obj_ItemPath2"]  = mk8.obj_item_path_2
        # Exclusions
        obj["Multi2P"] = mk8.multi_2p
        obj["Multi4P"] = mk8.multi_4p
        obj["WiFi"]    = mk8.wifi
        obj["WiFi2P"]  = mk8.wifi_2p
        # Transform
        obj["Translate"] = Exporter.dict_from_vector(ob.location)
        obj["Rotate"] = Exporter.dict_from_vector(ob.rotation_euler)
        obj["Scale"] = Exporter.dict_from_vector(ob.scale)
        return obj

    @staticmethod
    def dict_from_vector(vector):
        return { "X": vector.x, "Z": -vector.y, "Y": vector.z }