# aces helper [blender addon]

> this is a simple addon for changing colorspace for aces
>**v0.2: support cycles and eevee now,support custom colorspace as preset**

![img](README.assets/img.png)

## How to use

right click on the **image / environment texture** node to change it to aces color space 

+ for hdr texture, you should choose "Utility - Linear - sRGB"
+ for color texture, you should choose "Utility - sRGB - Texture"
+ for normal/roughtness/metallic/... texture,you should "Utility - Raw"

### Custom Preset

go to the addon preference and enable **preset mode**, then you can add preset with your selected node.

then disable the **preset mode**,now you will get your own preset in the menu