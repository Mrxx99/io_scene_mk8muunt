import bpy
import bpy_extras
import copy
from bpy.props import BoolProperty, CollectionProperty, EnumProperty, FloatProperty, IntProperty, StringProperty
from . import addon
from . import byaml
from . import objflow

class ExportOperator(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """Save a MK8 Course Info file"""
    bl_idname = "export_scene.mk8muunt"
    bl_label  = "Export MK8 Course Info"

    check_extension = True
    filename_ext    = ".byaml"
    filter_glob     = StringProperty(default="*.byaml", options={"HIDDEN"})
    filepath        = StringProperty(name="File Path", description="Filepath used for exporting the course BYAML file.", maxlen=1024, default="")

    replace_info = BoolProperty(name="Replace Info", description="Replace overall course info like the number of laps.",                                 default=True)
    replace_obj  = BoolProperty(name="Replace Objs", description="Replace Obj instances which represent animated or interactive objects on the course.", default=True)

    @staticmethod
    def menu_func(self, context):
        self.layout.operator(ExportOperator.bl_idname, text ="MK8 Course Info (.byaml)")

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
        if self.operator.replace_info: self._replace_info(file.root)
        if self.operator.replace_obj:  self._replace_objs(file.root)
        # Save course info data to a file.
        file.save_raw(open(self.filepath, "wb"))
        return {"FINISHED"}

    # ---- Info ----

    def _replace_info(self, root):
        mk8 = self.context.scene.mk8
        root["EffectSW"] = mk8.effect_sw
        root["HeadLight"] = int(mk8.head_light)
        root["IsFirstLeft"] = mk8.is_first_left
        root["IsJugemAbove"] = mk8.is_jugem_above
        root["JugemAbove"] = mk8.jugem_above
        root["LapJugemPos"] = mk8.lap_jugem_pos
        root["LapNumber"] = mk8.lap_number
        for i in range(1, 9):
            root["OBJPrm" + str(i)] = getattr(mk8, "obj_prm_" + str(i))
        root["PatternNum"] = mk8.pattern_num

    def _replace_objs(self, root):
        # Get the Obj objects in Blender.
        group = bpy.data.groups.get("Obj", None)
        obs = group.objects.values()
        # Add the Obj instances to the Obj array and remember ID and ResNames.
        objs = []
        map_ids = []
        map_res_names = []
        for ob in obs:
            mk8 = ob.mk8
            map_ids.append(mk8.obj_id)
            map_res_names.extend(objflow.get_obj_res_names(self.context, mk8.obj_id))
            objs.append(self._get_obj_node(obs, ob))
        root["Obj"] = objs
        # Add Objs referenced indirectly through others. Unclear how the original editor knew about these references.
        if "N64RTrain" in map_res_names:
            map_ids.append(1044) # CmnToad
            map_res_names.append("CmnToad")
        # Create the distinct MapObjIdList and MapObjResList contents.
        root["MapObjIdList"] = list(set(map_ids))
        root["MapObjIdList"].sort(reverse=True) # Probably unrequired, but nice.
        root["MapObjResList"] = list(set(map_res_names))

    def _get_obj_node(self, obs, ob):
        mk8 = ob.mk8
        # General
        obj = {}
        obj["UnitIdNum"] = mk8.unit_id_num # 0 might seem to work too without any issues.
        obj["ObjId"] = mk8.obj_id
        obj["TopView"] = mk8.top_view
        if mk8.no_col:
            obj["NoCol"] = True
        # Params
        obj["Params"] = []
        for i in range(1, 9):
            obj["Params"].append(getattr(mk8, "float_param_" + str(i)))
        # Relations
        if mk8.obj:
            for i, related_ob in enumerate(obs):
                if mk8.obj == related_ob.name:
                    obj["Obj_Obj"] = i
                    break
        if mk8.has_area_obj: obj["Area_Obj"] = mk8.area_obj
        # Paths
        obj["Speed"] = mk8.speed
        if mk8.has_path:         obj["Obj_Path"]       = mk8.path
        if mk8.has_path_point:   obj["Obj_PathPoint"]  = mk8.path_point
        if mk8.has_lap_path:     obj["Obj_LapPath"]    = mk8.lap_path
        if mk8.has_lap_point:    obj["Obj_LapPoint"]   = mk8.lap_point
        if mk8.has_obj_path:     obj["Obj_ObjPath"]    = mk8.obj_path
        if mk8.has_obj_point:    obj["Obj_ObjPoint"]   = mk8.obj_point
        if mk8.has_enemy_path_1: obj["Obj_EnemyPath1"] = mk8.enemy_path_1
        if mk8.has_enemy_path_2: obj["Obj_EnemyPath2"] = mk8.enemy_path_2
        if mk8.has_item_path_1:  obj["Obj_ItemPath1"]  = mk8.item_path_1
        if mk8.has_item_path_2:  obj["Obj_ItemPath2"]  = mk8.item_path_2
        # Exclusions
        obj["Single"]  = mk8.single # Normally not set except in 200cc tracks. Probably doesn't matter.
        obj["Multi2P"] = mk8.multi_2p
        obj["Multi4P"] = mk8.multi_4p
        obj["WiFi"]    = mk8.wifi
        obj["WiFi2P"]  = mk8.wifi_2p
        # Transform
        obj["Scale"] = Exporter._dict_from_vector(ob.scale)
        obj["Rotate"] = Exporter._dict_from_vector(ob.rotation_euler, invert_z=True)
        obj["Translate"] = Exporter._dict_from_vector(ob.location, invert_z=True)
        return obj

    @staticmethod
    def _dict_from_vector(vector, invert_z=False):
        if invert_z:
            return { "X": vector.x, "Z": -vector.y, "Y": vector.z }
        else:
            return { "X": vector.x, "Z": vector.y, "Y": vector.z }
