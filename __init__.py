# author: Atticus
# update log:
# v0.1
#   2021.1.22 initial commit
# v0.2
#   2021.1.23 use preset operator
#   add support for compositor
# v0.3
#   2021.2.3 add properties panel
#   fix add preset problem

bl_info = {
    "name"       : "aces helper",
    "author"     : "Atticus",
    "version"    : (0, 3, 1),
    "blender"    : (2, 90, 0),
    "location"   : "Shader Editor > Right Click Menu / Properties Panel > ACES Helper",
    "description": "heple changing colorspace with eevee/cycles",
    "warning"    : "",
    "doc_url"    : "",
    "category"   : "Render",
}

import os
import bpy
import shutil
from bpy.props import *
from bpy.types import Operator, AddonPreferences, Menu, Panel

from bl_operators.presets import AddPresetBase
from bl_ui.utils import PresetPanel

from .utils import get_blender_cs_folder

tex_nodes = {
    'ShaderNodeTexEnvironment',
    'ShaderNodeTexImage',
    'CompositorNodeImage',
}


def get_pref():
    return bpy.context.preferences.addons.get(__name__).preferences


class AH_OT_OpenFolder(Operator):
    bl_idname = 'ah.open_folder'
    bl_label = 'Open Folder'

    path: StringProperty(name='Path')

    def execute(self, context):
        if self.path:
            os.startfile(self.path)

        return {'FINISHED'}


class AH_Preference(AddonPreferences):
    bl_idname = __name__

    preset_mode: BoolProperty(name='Use Preset Mode', default=False)

    def draw(self, context):
        layout = self.layout
        row = layout.row()

        row.operator('ah.open_folder').path = get_blender_cs_folder() + '\\'
        row.prop(self, 'preset_mode', text='Preset Mode', toggle=1)


class AH_PT_Panel(Panel):
    bl_label = "ACES Helper"
    bl_idname = "AH_PT_Panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        pref = get_pref()
        layout = self.layout
        row = layout.row()

        row.prop(pref, 'preset_mode', text='Preset Mode', toggle=1)
        row.operator('ah.open_folder').path = get_blender_cs_folder() + '\\'


class AH_MT_CSPresetsMenu(Menu):
    bl_label = 'colorspace Presets'
    preset_subdir = 'AH/colorspace_presets'
    preset_operator = 'script.execute_preset'
    draw = Menu.draw_preset


class AH_PT_CSPresetPanel(PresetPanel, Panel):
    bl_label = 'AH Colorspace Presets'
    preset_subdir = 'AH/colorspace_presets'
    preset_operator = 'script.execute_preset'
    preset_add_operator = 'ah.add_cs_preset'


class AH_OT_AddCSPreset(AddPresetBase, Operator):
    bl_idname = 'ah.add_cs_preset'
    bl_label = 'Add a preset'
    preset_menu = 'AH_MT_CSPresetsMenu'

    preset_defines = [
        'nt = bpy.context.space_data.edit_tree',
        'node = nt.nodes.active',
    ]

    preset_values = [
        'node.image.colorspace_settings.name',
    ]

    preset_subdir = 'AH/colorspace_presets'


def get_files_from_path(path):
    files = []
    for dirName, subdirList, fileList in os.walk(path):
        dir = dirName.replace(path, '')
        for f in fileList:
            files.append(os.path.join(dir, f))
    return files


def add_res_preset_to_user():
    presets_folder = bpy.utils.user_resource('SCRIPTS', "presets")
    ah_presets_folder = os.path.join(presets_folder, 'AH', 'colorspace_presets')

    if not os.path.exists(ah_presets_folder):
        os.makedirs(ah_presets_folder, exist_ok=True)

    destination = get_files_from_path(ah_presets_folder)

    addon_folder = bpy.utils.user_resource('SCRIPTS', "addons")
    bundled_presets_folder = os.path.join(addon_folder, __name__, 'preset')
    source = get_files_from_path(bundled_presets_folder)

    # install difference
    difference = set(source) - set(destination)
    if len(difference) != 0:
        print('aces helper will install bundled colorspace presets:\n' + str(difference))

    for f in difference:
        file = os.path.join(bundled_presets_folder, f)
        dest_file = os.path.join(ah_presets_folder, f)
        dest_folder = os.path.dirname(dest_file)
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder, exist_ok=True)
        shutil.copy2(file, dest_folder)


classes = [
    AH_OT_OpenFolder,
    AH_Preference,
    AH_PT_Panel,
    # preset
    AH_MT_CSPresetsMenu,
    AH_PT_CSPresetPanel,
    AH_OT_AddCSPreset,
]


def draw_menu(self, context):
    layout = self.layout
    pref = bpy.context.preferences.addons.get(__name__).preferences
    nt = context.space_data.edit_tree
    node = nt.nodes.active
    if node.bl_idname in tex_nodes and node.image:
        if not pref.preset_mode:
            layout.menu('AH_MT_CSPresetsMenu', text='ACES Preset')
        else:
            layout.popover(panel='AH_PT_CSPresetPanel')


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.NODE_MT_context_menu.prepend(draw_menu)

    add_res_preset_to_user()


def unregister():
    bpy.types.NODE_MT_context_menu.remove(draw_menu)
    for cls in classes:
        bpy.utils.unregister_class(cls)
