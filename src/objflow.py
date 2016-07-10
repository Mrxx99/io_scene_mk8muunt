import collections
import os

from . import addon
from . import byaml

_objflow = None
_id_dict = None

def get_obj_label(context, obj_id):
    # Returns the label of the object as displayed in the editor.
    _ensure_objflow_loaded(context)
    objflow_entry = _id_dict.get(obj_id)
    return objflow_entry["Label"] if objflow_entry else None

def get_obj_res_names(context, obj_id):
    # Returns the ResName's which need to be loaded by the game to use this object.
    _ensure_objflow_loaded(context)
    objflow_entry = _id_dict.get(obj_id)
    return objflow_entry["ResName"] if objflow_entry else None

def get_id_label_items():
    items = []
    for key, value in _id_dict.items():
        items.append((str(key), value["Label"], ""))
    # Sort them by label.
    items.sort(key=lambda item: item[1])
    return items

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
