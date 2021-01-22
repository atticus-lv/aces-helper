bl_info = {
    "name"       : "aces helper",
    "author"     : "Atticus",
    "version"    : (0, 1),
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
from bpy.types import Operator, AddonPreferences, Menu

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


class AH_MT_CSMenu(Menu):
    bl_idname = 'AH_MT_CSMenu'
    bl_label = 'aces helper'

    def draw(self, context):
        layout = self.layout
        layout.menu('AH_MT_UtilityCSMenu', text='Utility')


class AH_MT_UtilityCSMenu(Menu):
    bl_idname = 'AH_MT_UtilityCSMenu'
    bl_label = 'Utility'

    def draw(self, context):
        layout = self.layout
        for s in tex_cs:
            layout.operator('ah.set_image_cs', text=s).cs_name = s


class AH_OT_SetImageCS(Operator):
    bl_idname = 'ah.set_image_cs'
    bl_label = 'Set Image ColorSpace'
    bl_options = {'REGISTER', 'UNDO'}

    cs_name: StringProperty()

    def execute(self, context):
        nt = context.space_data.edit_tree
        node = nt.nodes.active
        if node.bl_idname in tex_nodes and node.image:
            try:
                node.image.colorspace_settings.name = self.cs_name
            except Exception as e:
                self.report({'ERROR'}, f'{e}')
        else:
            self.report({'WARNING'}, 'Select Node with image in Environment Texture,Image Texture!')
        return {'FINISHED'}

def fill_cs_folder(self,context):
    self.cs_folder_path = get_blender_cs_folder() + '\\'

class AH_Preference(AddonPreferences):
    bl_idname = __name__

    zip_file_path: StringProperty()
    cs_folder_path: StringProperty(update=fill_cs_folder)

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=1)
        row.prop(self,'cs_folder_path',text='')
        row.operator('buttons.file_browse', icon='FILEBROWSER', text='')
        # row = layout.row(align=1)
        # row.prop(self, 'zip_file_path', text='ACES Zip File')
        # row.operator('buttons.file_browse', icon='FILEBROWSER', text='')
        # layout.separator()
        # row = layout.row(align=1)
        # row.operator('ah.switch_cs',text = 'Insatll').action = 'INSTALL'
        # row.operator('ah.switch_cs',text = 'Switch ACES').action = 'ACES'
        # row.operator('ah.switch_cs',text = 'Switch Filmic').action = 'Filmic'
        pass


class AH_OT_SwitchCS(Operator):
    bl_idname = 'ah.switch_cs'
    bl_label = 'Switch ColorSpace'
    bl_options = {'REGISTER', 'UNDO'}

    action: EnumProperty(items=[
        ('INSTALL', 'Insatll', ''),
        ('ACES', 'Switch ACES', ''),
        ('Filmic', 'Switch Filmic', '')
    ], default='ACES')

    def execute(self, context):
        pref = bpy.context.preferences.addons.get('aces helper').preferences
        zip_file_path = pref.zip_file_path
        if self.action == 'INSTALL' and zip_file_path != '':
            install_aces(use_zip_file=True, zip_file=zip_file_path)
        elif self.action == 'ACES':
            install_aces()
        else:
            rollback_filmic()

        return {'FINISHED'}


classes = [
    AH_MT_CSMenu,
    AH_OT_SetImageCS,
    AH_MT_UtilityCSMenu,
    # AH_OT_SwitchCS,
    AH_Preference,

]


def draw_menu(self, context):
    layout = self.layout
    # layout.menu('AH_MT_CSMenu')
    layout.menu('AH_MT_UtilityCSMenu', text='ACES Utility')


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.NODE_MT_context_menu.prepend(draw_menu)


def unregister():
    bpy.types.NODE_MT_context_menu.remove(draw_menu)
    for cls in classes:
        bpy.utils.unregister_class(cls)
