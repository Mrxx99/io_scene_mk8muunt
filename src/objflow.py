import bpy
import collections
import os

from . import addon
from . import byaml

_objflow = None
_id_dict = None
_no_model_objs = [] # Remembers the ObjIDs to which no model exists.

def get_obj_label(context, obj_id):
    # Returns the label of the object as displayed in the editor.
    _ensure_objflow_loaded(context)
    objflow_entry = _id_dict.get(obj_id)
    return objflow_entry["Label"] if objflow_entry else None

def get_obj_res_names(context, obj_id):
    # Returns the ResName's which need to be loaded by the game to use this object.
    _ensure_objflow_loaded(context)
    objflow_entry = _id_dict.get(obj_id)
    return objflow_entry["ResName"] if objflow_entry else []

def get_obj_id_label_items():
    items = []
    for key, value in _id_dict.items():
        items.append((str(key), value["Label"], ""))
    # Sort them by label.
    items.sort(key=lambda item: item[1].lower())
    return items

def check_if_obj_has_models(obj_id):
    # If this ObjID is known to not have objects, return that.
    return not obj_id in _no_model_objs

def create_obj_models(context, obj_ob):
    # Check first if this ObjID is known to not have models.
    if obj_ob.mk8.obj_id in _no_model_objs:
        return
    addon.ignore_updates = True
    # Get the path of the mapobj and race_common folder.
    addon_prefs = context.user_preferences.addons[__package__].preferences
    mapobj_path = os.path.join(addon_prefs.game_path, "content", "mapobj")
    racecommon_path = os.path.join(addon_prefs.game_path, "content", "race_common")
    # Get the ResName's of the object with the provided ID and go through them.
    _ensure_objflow_loaded(context)
    res_names = get_obj_res_names(context, obj_ob.mk8.obj_id)
    for res_name in res_names:
        # Check if the model is already loaded.
        model_ob_name = "@" + res_name
        model_ob = bpy.data.objects.get(model_ob_name)
        if not model_ob:
            # Load the objects making up the model from file (they are all decompressed BFRES files).
            filepath = os.path.join(mapobj_path, res_name, res_name + ".bfres")
            if not os.path.isfile(filepath):
                # Common race objects are in race_common rather than mapobj. No clue which param tells the game that.
                filepath = os.path.join(racecommon_path, res_name, res_name + ".bfres")
                if not os.path.isfile(filepath):
                    # Model not found at all (probably not dumped).
                    addon.log(0, "Warning: Could not find BFRES for '" + res_name + "'.")
                    _no_model_objs.append(obj_ob.mk8.obj_id)
                    break
            bpy.ops.import_scene.bfres(filepath=filepath, ob_name=model_ob_name)
            model_ob = bpy.data.objects[model_ob_name]
        # Link all the model objects and parent them to the object representing the Obj.
        for model_ob_child in model_ob.children:
            # Create a new object "cloning" the model child object.
            obj_ob_child = bpy.data.objects.new(model_ob_child.name, model_ob_child.data)
            obj_ob_child.mk8.object_type = "OBJ_MODEL"
            obj_ob_child.parent = obj_ob
            # Lock the transformation of the child.
            obj_ob_child.lock_location = [True] * 3
            obj_ob_child.lock_rotation = [True] * 3
            obj_ob_child.lock_scale = [True] * 3
            # Link the object to the scene.
            bpy.context.scene.objects.link(obj_ob_child)
    addon.ignore_updates = False

def _ensure_objflow_loaded(context):
    global _objflow, _id_dict
    if not _objflow:
        # Load the objflow as it has not been loaded yet.
        addon.log(0, "Loading objflow...")
        addon_prefs = context.user_preferences.addons[__package__].preferences
        objflow_path = os.path.join(addon_prefs.game_path, "content", "data", "objflow.byaml")
        if not os.path.isfile(objflow_path):
            raise AssertionError("objflow.byaml does not exist as '" + objflow_path + ". Correct your game directory.")
        _objflow = byaml.File()
        _objflow.load_raw(open(objflow_path, "rb"))
        # Create a dictionary to quickly look up obj's by ObjId.
        _id_dict = collections.OrderedDict()
        for obj in _objflow.root:
            _id_dict[obj["ObjId"]] = obj
