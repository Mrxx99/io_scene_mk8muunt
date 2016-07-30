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

    check_extension = True
    filename_ext = ".byaml"
    filter_glob = bpy.props.StringProperty(default="*.byaml", options={'HIDDEN'})
    filepath = bpy.props.StringProperty(name="File Path", description="Filepath used for exporting the course BYAML file.", maxlen=1024)

    @staticmethod
    def menu_func(self, context):
        self.layout.operator(ExportOperator.bl_idname, text="MK8 Course Info (.byaml)")

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
        file.root = copy.deepcopy(addon.loaded_byaml.root)  # TODO: addon.loaded_byaml is None when addon is reloaded.
        # TODO: Get the objects by type rather than group.
        self._replace_info(file.root)
        areas = self._replace_areas(file.root)
        # TODO: Requires rewrite of the Clip node: clip_areas = self._replace_clip_areas(file.root)
        effect_areas = self._replace_effect_areas(file.root)
        objs = self._replace_objs(file.root, areas)
        # Save course info data to a file.
        file.save_raw(open(self.filepath, "wb"))
        return {'FINISHED'}

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
            root["OBJPrm{}".format(i)] = getattr(mk8, "obj_prm_{}".format(i))
        root["PatternNum"] = mk8.pattern_num

    # ---- Areas ----

    def _replace_areas(self, root):
        # Get the Area objects in Blender.
        group = bpy.data.groups.get("Area", None)
        if not group:
            return
        obs = group.objects.values()
        # Add the Area instances to the Area array.
        areas = []
        for ob in obs:
            mk8 = ob.mk8
            areas.append(self._get_area_node(ob))
        root["Area"] = areas
        return obs

    def _get_area_node(self, ob):
        mk8 = ob.mk8
        area = {}
        # General
        area["UnitIdNum"] = mk8.unit_id_num
        area["AreaShape"] = int(mk8.area_shape)
        area["AreaType"] = int(mk8.area_type)
        if mk8.has_area_path:
            area["Area_Path"] = mk8.area_path
        if mk8.has_area_pull_path:
            area["Area_PullPath"] = mk8.area_pull_path
        area["prm1"] = mk8.float_param_1
        area["prm2"] = mk8.float_param_2
        # Camera Areas
        if len(mk8.camera_areas):
            area["Camera_Area"] = [camera_area.value for camera_area in mk8.camera_areas]
        # Transform
        area["Scale"] = Exporter._dict_from_vector(ob.scale)
        area["Rotate"] = Exporter._dict_from_vector(ob.rotation_euler, invert_z=True)
        area["Translate"] = Exporter._dict_from_vector(ob.location, invert_z=True)
        return area

    # ---- Clip Areas ----

    def _replace_clip_areas(self, root):
        # Get the Clip Area objects in Blender.
        group = bpy.data.groups.get("ClipArea", None)
        if not group:
            return
        obs = group.objects.values()
        # Add the Clip Area instances to the Clip Area array.
        clip_areas = []
        for ob in obs:
            mk8 = ob.mk8
            clip_areas.append(self._get_clip_area_node(ob))
        root["ClipArea"] = clip_areas
        return obs

    def _get_clip_area_node(self, ob):
        mk8 = ob.mk8
        clip_area = {}
        # General
        clip_area["UnitIdNum"] = mk8.unit_id_num
        clip_area["AreaShape"] = int(mk8.clip_area_shape)
        clip_area["AreaType"] = int(mk8.clip_area_type)
        clip_area["prm1"] = mk8.float_param_1
        clip_area["prm2"] = mk8.float_param_2
        # Transform
        clip_area["Scale"] = Exporter._dict_from_vector(ob.scale)
        clip_area["Rotate"] = Exporter._dict_from_vector(ob.rotation_euler, invert_z=True)
        clip_area["Translate"] = Exporter._dict_from_vector(ob.location, invert_z=True)
        return clip_area

    # ---- Effect Areas ----

    def _replace_effect_areas(self, root):
        # Get the Effect Area objects in Blender.
        group = bpy.data.groups.get("EffectArea", None)
        if not group:
            return
        obs = group.objects.values()
        # Add the Effect Area instances to the Effect Area array.
        effect_areas = []
        for ob in obs:
            mk8 = ob.mk8
            effect_areas.append(self._get_effect_area_node(ob))
        root["EffectArea"] = effect_areas
        return obs

    def _get_effect_area_node(self, ob):
        mk8 = ob.mk8
        effect_area = {}
        # General
        effect_area["UnitIdNum"] = mk8.unit_id_num
        effect_area["EffectSW"] = int(mk8.effect_sw)
        effect_area["prm1"] = mk8.float_param_1
        effect_area["prm2"] = mk8.float_param_2
        # Transform
        effect_area["Scale"] = Exporter._dict_from_vector(ob.scale)
        effect_area["Rotate"] = Exporter._dict_from_vector(ob.rotation_euler, invert_z=True)
        effect_area["Translate"] = Exporter._dict_from_vector(ob.location, invert_z=True)
        return effect_area

    # ---- Objs ----

    def _replace_objs(self, root, areas):
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
            map_res_names.extend(objflow.get_res_names_by_id(mk8.obj_id))
            objs.append(self._get_obj_node(areas, obs, ob))
        root["Obj"] = objs
        # Add Objs referenced indirectly through others. Unclear how the original editor knew about these references.
        if "N64RTrain" in map_res_names:
            map_ids.append(1044)  # CmnToad
            map_res_names.append("CmnToad")
        # Create the distinct MapObjIdList and MapObjResList contents.
        root["MapObjIdList"] = list(set(map_ids))
        root["MapObjResList"] = list(set(map_res_names))
        return obs

    def _get_obj_node(self, areas, obs, ob):
        mk8 = ob.mk8
        obj = {}
        # General
        obj["UnitIdNum"] = mk8.unit_id_num
        obj["ObjId"] = mk8.obj_id
        obj["TopView"] = mk8.top_view
        if mk8.no_col:
            obj["NoCol"] = True
        for i in ("Single", "Multi2P", "Multi4P", "WiFi", "WiFi2P"):
            obj[i] = i not in mk8.inclusions
        # Params
        obj["Params"] = []
        for i in range(1, 9):
            obj["Params"].append(getattr(mk8, "float_param_{}".format(i)))
        # Paths
        obj["Speed"] = mk8.speed
        if mk8.has_path:
            obj["Obj_Path"] = mk8.path
        if mk8.has_path_point:
            obj["Obj_PathPoint"] = mk8.path_point
        if mk8.has_lap_path:
            obj["Obj_LapPath"] = mk8.lap_path
        if mk8.has_lap_point:
            obj["Obj_LapPoint"] = mk8.lap_point
        if mk8.has_obj_path:
            obj["Obj_ObjPath"] = mk8.obj_path
        if mk8.has_obj_point:
            obj["Obj_ObjPoint"] = mk8.obj_point
        if mk8.has_enemy_path_1:
            obj["Obj_EnemyPath1"] = mk8.enemy_path_1
        if mk8.has_enemy_path_2:
            obj["Obj_EnemyPath2"] = mk8.enemy_path_2
        if mk8.has_item_path_1:
            obj["Obj_ItemPath1"] = mk8.item_path_1
        if mk8.has_item_path_2:
            obj["Obj_ItemPath2"] = mk8.item_path_2
        # Relations
        if mk8.area:
            for i, ref_area in enumerate(areas):
                if mk8.area == ref_area.name:
                    obj["Area_Obj"] = i
                    break
        if mk8.obj:
            for i, ref_ob in enumerate(obs):
                if mk8.obj == ref_ob.name:
                    obj["Obj_Obj"] = i
                    break
        # Transform
        obj["Scale"] = Exporter._dict_from_vector(ob.scale)
        obj["Rotate"] = Exporter._dict_from_vector(ob.rotation_euler, invert_z=True)
        obj["Translate"] = Exporter._dict_from_vector(ob.location, invert_z=True)
        return obj

    # ---- General ----

    @staticmethod
    def _dict_from_vector(vector, invert_z=False):
        if invert_z:
            return {"X": vector.x, "Z": -vector.y, "Y": vector.z}
        else:
            return {"X": vector.x, "Z": vector.y, "Y": vector.z}
