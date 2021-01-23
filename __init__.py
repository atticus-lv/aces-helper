# author: Atticus
# update log:
# v0.1
#   2021.1.22 initial commit
# v0.2
#   2021.1.23 use preset operator


bl_info = {
    "name"       : "aces helper",
    "author"     : "Atticus",
    "version"    : (0, 2),
    "blender"    : (2, 90, 0),
    "location"   : "Shader Editor > Right Click Menu",
    "description": "heple changing colorspace with eevee/cycles",
    "warning"    : "",
    "doc_url"    : "",
    "category"   : "Render",
}

import os
import bpy
from bpy.props import *
from bpy.types import Operator, AddonPreferences, Menu, Panel
from bl_operators.presets import AddPresetBase
from bl_ui.utils import PresetPanel

from .swith_cs import *

tex_nodes = {
    'ShaderNodeTexEnvironment',
    'ShaderNodeTexImage',
}

tex_cs = [
    'Utility - Linear - sRGB',
    'Utility - sRGB - Texture',
    'Utility - Raw',
]


# class AH_MT_CSMenu(Menu):
#     bl_idname = 'AH_MT_CSMenu'
#     bl_label = 'aces helper'
#
#     def draw(self, context):
#         layout = self.layout
#         layout.menu('AH_MT_UtilityCSMenu', text='Utility')
#
#
# class AH_MT_UtilityCSMenu(Menu):
#     bl_idname = 'AH_MT_UtilityCSMenu'
#     bl_label = 'Utility'
#
#     def draw(self, context):
#         layout = self.layout
#         for s in tex_cs:
#             layout.operator('ah.set_image_cs', text=s).cs_name = s
#
#
# class AH_OT_SetImageCS(Operator):
#     bl_idname = 'ah.set_image_cs'
#     bl_label = 'Set Image ColorSpace'
#     bl_options = {'REGISTER', 'UNDO'}
#
#     cs_name: StringProperty()
#
#     def execute(self, context):
#         nt = context.space_data.edit_tree
#         node = nt.nodes.active
#         if node.bl_idname in tex_nodes and node.image:
#             try:
#                 node.image.colorspace_settings.name = self.cs_name
#             except Exception as e:
#                 self.report({'ERROR'}, f'{e}')
#         else:
#             self.report({'WARNING'}, 'Select Node with image in Environment Texture,Image Texture!')
#         return {'FINISHED'}


def fill_cs_folder(self, context):
    self.cs_folder_path = get_blender_cs_folder() + '\\'


class AH_Preference(AddonPreferences):
    bl_idname = __name__

    # zip_file_path: StringProperty()
    cs_folder_path: StringProperty(update=fill_cs_folder)
    preset_mode: BoolProperty(name='Use Preset Mode', default=False)

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=1)
        col.label(text='Color Management Folder')
        row = col.row(align=1)
        row.prop(self, 'cs_folder_path', text='')
        row.operator('buttons.file_browse', icon='FILEBROWSER', text='')

        layout.prop(self, 'preset_mode', text='Preset Mode')
        # row = layout.row(align=1)
        # row.prop(self, 'zip_file_path', text='ACES Zip File')
        # row.operator('buttons.file_browse', icon='FILEBROWSER', text='')
        # layout.separator()
        # row = layout.row(align=1)
        # row.operator('ah.switch_cs',text = 'Insatll').action = 'INSTALL'
        # row.operator('ah.switch_cs',text = 'Switch ACES').action = 'ACES'
        # row.operator('ah.switch_cs',text = 'Switch Filmic').action = 'Filmic'


# class AH_OT_SwitchCS(Operator):
#     bl_idname = 'ah.switch_cs'
#     bl_label = 'Switch ColorSpace'
#     bl_options = {'REGISTER', 'UNDO'}
#
#     action: EnumProperty(items=[
#         ('INSTALL', 'Insatll', ''),
#         ('ACES', 'Switch ACES', ''),
#         ('Filmic', 'Switch Filmic', '')
#     ], default='ACES')
#
#     def execute(self, context):
#         pref = bpy.context.preferences.addons.get('aces helper').preferences
#         zip_file_path = pref.zip_file_path
#         if self.action == 'INSTALL' and zip_file_path != '':
#             install_aces(use_zip_file=True, zip_file=zip_file_path)
#         elif self.action == 'ACES':
#             install_aces()
#         else:
#             rollback_filmic()
#
#         return {'FINISHED'}


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
    # AH_MT_CSMenu,
    # AH_OT_SetImageCS,
    AH_MT_UtilityCSMenu,
    # AH_OT_SwitchCS,
    AH_Preference,

    # preset
    AH_MT_CSPresetsMenu,
    AH_PT_CSPresetPanel,
    AH_OT_AddCSPreset,

]


def draw_menu(self, context):
    layout = self.layout
    # layout.menu('AH_MT_CSMenu')
    # layout.menu('AH_MT_UtilityCSMenu', text='ACES Utility')
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
