import bpy
nt = bpy.context.space_data.edit_tree
node = nt.nodes.active
node.image.colorspace_settings.name = 'Utility - sRGB - Texture'