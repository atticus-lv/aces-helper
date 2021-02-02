# aces helper [blender addon]

> this is a simple addon for changing colorspace for aces
>
>**v0.2: support cycles and eevee now,support custom colorspace as preset**
>
>**v0.3: add properties panel/open foler button**

![img](README.assets/img.png)

## How to use

right click on the **image / environment texture** node to change it to aces color space 

+ for hdr texture, you should choose "Utility - Linear - sRGB"
+ for color texture, you should choose "Utility - sRGB - Texture"
+ for normal/roughtness/metallic/... texture,you should "Utility - Raw"

### Custom Preset

Properties panel/ACES Helper and enable **preset mode**, then you can add preset with your selected node.

Disable the **preset mode**,now you will get your own preset in the menu