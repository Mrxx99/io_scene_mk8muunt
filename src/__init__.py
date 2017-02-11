bl_info = {
    "name": "Mario Kart 8 Course Info format",
    "description": "Import-Export Mario Kart 8 Course info",
    "author": "Syroot, IDProperty 1.2.1 by Andrew Moffat",
    "version": (0, 5, 6),
    "blender": (2, 77, 0),
    "location": "File > Import-Export",
    "warning": "This add-on is under development. io_scene_bfres is required for it to work.",
    "wiki_url": "https://github.com/Syroot/io_scene_mk8muunt/wiki",
    "tracker_url": "https://github.com/Syroot/io_scene_mk8muunt/issues",
    "support": 'COMMUNITY',
    "category": "Import-Export"
}

# Reload the package modules when reloading add-ons in Blender with F8.
if "bpy" in locals():
    import importlib
    if "idproperty" in locals():
        importlib.reload(idproperty)
    if "addon" in locals():
        importlib.reload(addon)
    if "binary_io" in locals():
        importlib.reload(binary_io)
    if "byaml" in locals():
        importlib.reload(byaml)
    if "objflow" in locals():
        importlib.reload(objflow)
    if "importing" in locals():
        importlib.reload(importing)
    if "editing" in locals():
        importlib.reload(editing)
    if "exporting" in locals():
        importlib.reload(exporting)
import bpy
from . import idproperty
from . import addon
from . import importing
from . import editing
from . import exporting


def register():
    bpy.utils.register_module(__name__)
    idproperty.register()
    # Addon
    bpy.types.UILayout.mk8_colbox = addon.mk8_colbox
    bpy.app.handlers.scene_update_post.append(addon.scene_update_post)
    # Importing
    bpy.types.INFO_MT_file_import.append(importing.ImportOperator.menu_func)
    # Editing
    bpy.types.INFO_MT_add.append(editing.MK8OpAddObject.menu_func)
    bpy.types.Scene.mk8 = bpy.props.PointerProperty(type=editing.MK8PropsScene)
    bpy.types.Object.mk8 = bpy.props.PointerProperty(type=editing.MK8PropsObject)
    # Exporting
    bpy.types.INFO_MT_file_export.append(exporting.ExportOperator.menu_func)


def unregister():
    bpy.utils.unregister_module(__name__)
    idproperty.unregister()
    # Addon
    del bpy.types.UILayout.mk8_colbox
    bpy.app.handlers.scene_update_post.remove(addon.scene_update_post)
    # Importing
    bpy.types.INFO_MT_file_import.remove(importing.ImportOperator.menu_func)
    # Editing
    bpy.types.INFO_MT_add.remove(editing.MK8OpAddObject.menu_func)
    del bpy.types.Scene.mk8
    del bpy.types.Object.mk8
    # Exporting
    bpy.types.INFO_MT_file_export.remove(exporting.ExportOperator.menu_func)
