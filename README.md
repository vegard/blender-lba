Blender-LBA
===========

This is a Blender script for importing HQR resources (palettes, models, animations) from the game Little Big Adventure.

To get started:

 - You need the data files from the game, obviously. You can buy it from [gog.com](https://www.gog.com/game/little_big_adventure) for cheap.

 - Copy import.py to your `~/.config/blender/<version>/scripts/addons/` directory.

![Import body](https://github.com/vegard/blender-lba/raw/master/1.png)
![Import body](https://github.com/vegard/blender-lba/raw/master/2.png)

 - Import body 0 from `BODY.HQR` (File > Import).
    - This creates two objects: the body itself ("Body") and the rig ("Rig").

![Import palette](https://github.com/vegard/blender-lba/raw/master/3.png)

 - Select *Body* and import palette 0 from `RESS.HQR` (File > Import).

![Import rig](https://github.com/vegard/blender-lba/raw/master/4.png)

 - Select *Rig* and import animation 8 from `ANIM.HQR` (File > Import).
 - Switch to top view (View > Top).
 - Switch to orthographic projection (View > View Persp/Ortho).
 - Press Alt-A to play the animation.

Playing around a bit and you can render something like this:

![Rendered animation](https://github.com/vegard/blender-lba/raw/master/rendered.gif)

I admit that doesn't look half as good as it does in the actual game, and there are several reasons for that. Firstly, Blender doesn't support circle/sphere primitives natively so those are not imported yet -- we could of course create a sphere mesh, but we should ideally be able to export that back out of blender without creating polygonal faces for them. Other things (lines, normals, etc.) may not all be imported correctly either. Secondly, you'll have to play around with lighting and rendering settings to get it more like it is in the game.

Check out the full list of [body numbers](http://chaosfish.free.fr/lbafileinfo/lba1-body.hqr.htm) and [animation numbers](http://chaosfish.free.fr/lbafileinfo/lba1-anim.hqr.htm), but beware that numbering in Blender starts from 0 (so the “Twinsen jumping” animation is not index 6, but index 5).


Bugs/TODO
---------

 - Some animations are weird, e.g. “Twinsen standing (normal mode)” has him swinging on the wrong axis for some reason
 - Switch axes (LBA uses Y up, while Blender uses Z up)
 - Import normals
 - Import lines
 - Import circles
 - Export everything
 - Factor out reading functions into its own library that is reusable outside blender
