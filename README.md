# io_scene_mk8muunt

This is a Blender add-on to import and export Mario Kart 8 Course Info BYAML files (those with "muunt" in their name).

It is currently in the alpha stage and supports the following features:

- Load all Areas, ClipAreas, EffectAreas, Objs and SoundObjs, visualizing them in the 3D view and their parameters in panels.
- Allow editing of Area, ClipArea, EffectArea, Obj and SoundObj configurations.
- Export (modified) Areas, EffectAreas, Objs and SoundObjs to a new BYAML file written from scratch.

![alt tag](https://raw.githubusercontent.com/Syroot/io_scene_mk8muunt/master/doc/readme/example.png)

Installation
============

You require a full dump of the Mario Kart 8 game files.

- Install the latest version of <a href="https://github.com/Syroot/io_scene_bfres">io_scene_bfres</a> first, as that addon will be used to load Obj models which appear on the track.
- Go to your Blender installation directory inside the version folder, and then to `scripts` > `addons`.
- Create a new folder called "io_scene_mk8muunt".
- Copy in all `*.py` files from the `src` folder of this repository.
- In the Blender user preferences, enable the 'Import-Export: Mario Kart 8 Course Info format' add-on.
- You have to provide the path to your Mario Kart 8 `vol` directory (in which the DLC and the `content` folder resides in) so that the add-on can find the path to the `objflow.byaml` (and later on, load models from the `mapobj` folder accordingly). You can set this path in the add-on preferences by expanding the add-on's section there.

License
=======

<a href="http://www.wtfpl.net/"><img src="http://www.wtfpl.net/wp-content/uploads/2012/12/wtfpl.svg" height="20" alt="WTFPL" /></a> WTFPL

    Copyright © 2016 syroot.com <admin@syroot.com>
    This work is free. You can redistribute it and/or modify it under the
    terms of the Do What The Fuck You Want To Public License, Version 2,
    as published by Sam Hocevar. See the COPYING file for more details.
