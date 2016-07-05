import os
from . import addon
from . import byaml

_objflow      = None
_objflow_dict = None

def get_obj_label(context, obj_id):
    _ensure_objflow_loaded(context)
    objflow_entry = _objflow_dict.get(obj_id)
    return objflow_entry["Label"].value if objflow_entry else None

def _ensure_objflow_loaded(context):
    global _objflow, _objflow_dict
    if not _objflow:
        # Load the objflow as it has not been loaded yet.
        addon.log(0, "Loading objflow...")
        addon_prefs = context.user_preferences.addons[__package__].preferences
        objflow_path = os.path.join(addon_prefs.game_path, "content", "data", "objflow.byaml")
        if not os.path.isfile(objflow_path):
            raise AssertionError("objflow.byaml does not exist as '" + objflow_path + ". Correct your game directory.")
        _objflow = byaml.ByamlFile(open(objflow_path, "rb"))
        # Create a dictionary to quickly look up obj's by ObjId.
        _objflow_dict = {}
        for obj in _objflow.root:
            _objflow_dict[obj["ObjId"].value] = obj
