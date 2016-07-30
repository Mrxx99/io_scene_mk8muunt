import bpy
import os
from . import addon
from . import byaml

_objflow = None
_id_dict = {}
_label_dict = {}
_label_items = []


def get_label_items(self, context):
    # Returns the list of all textual labels, in a tuple to be used by a Blender search operator.
    _ensure_loaded()
    return _label_items


def get_obj_by_label(label):
    # Returns the Obj definition for the given unique textual label, case-insensitive.
    _ensure_loaded()
    return _label_dict.get(label.lower())


def get_obj_by_id(obj_id):
    # Returns the Obj definition for the given Obj ID.
    _ensure_loaded()
    return _id_dict.get(obj_id)


def get_res_names_by_id(obj_id):
    # Returns the ResName's which need to be loaded by the game to use this object.
    _ensure_loaded()
    objflow_entry = _id_dict.get(obj_id)
    return objflow_entry["ResName"] if objflow_entry else []


_param_names = {  # Tuples must have a length of 8: Either document an object fully or let it.
    1014: ("Initial Delay", "Slam Delay", "?", None, None, None, None, None),  # Dossun
    1036: ("?", "?", None, None, None, None, None, None),  # PcBalloon
    1119: ("Road Index", "Initial Delay", "Slam Delay", None, None, None, None, None),  # CrWanwanB
    4052: ("?", "?", "?", None, None, None, None, "Model Index")  # VolcanoPiece
}


def get_param_names(obj_id, index):
    names = _param_names.get(obj_id)
    if names:
        param_name = names[index - 1]
        # Return "Unused X" when such parameters should be shown.
        if not param_name and bpy.context.user_preferences.addons[__package__].preferences.show_unused_obj_params:
            param_name = "Unused {}".format(index)
    else:
        param_name = "Unknown {}".format(index)
    return param_name


def _ensure_loaded():
    global _objflow
    if not _objflow:
        # Load the objflow as it has not been loaded yet.
        addon.log(0, "Loading objflow...")
        addon_prefs = bpy.context.user_preferences.addons[__package__].preferences
        objflow_path = os.path.join(addon_prefs.game_path, "content", "data", "objflow.byaml")
        if not os.path.isfile(objflow_path):
            raise AssertionError("objflow.byaml does not exist as '{}'. Correct your game directory.".format(objflow_path))
        _objflow = byaml.File()
        _objflow.load_raw(open(objflow_path, "rb"))
        # Create lookup dictionaries and arrays for quick access.
        for obj in _objflow.root:
            obj_id = obj["ObjId"]
            label = obj["Label"]
            _id_dict[obj_id] = obj
            _label_dict[label.lower()] = obj
            _label_items.append((str(obj_id), label, ""))
        _label_items.sort(key=lambda item: item[1].lower())
