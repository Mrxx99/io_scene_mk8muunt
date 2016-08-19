# io_scene_mk8muunt

This is a Blender add-on to import and export Mario Kart 8 Course Info BYAML files (those with "muunt" in their name).

It is currently in the alpha stage and supports the following Course BYAML sections:

| Feature                        | Import | Edit   | Export | Status |
| ------------------------------ | :----: | :----: | :----: | ------ |
| Main Information               | Yes    | Yes    | Yes    |        |
| Area                           | Yes    | Yes    | Yes    |        |
| Clip / ClipArea / ClipPattern  | Yes    | Yes    | No     | Unclear how to compute the information. |
| EffectArea                     | Yes    | Yes    | Yes    |        |
| EnemyPath                      | No     | No     | No     |        |
| GlidePath                      | No     | No     | No     |        |
| GravityPath                    | No     | No     | No     |        |
| IntroCamera                    | No     | No     | No     |        |
| ItemPath                       | No     | No     | No     |        |
| JugemPath                      | No     | No     | No     |        |
| LapPath                        | No     | No     | No     |        |
| Obj                            | Yes    | Yes    | Yes    |        |
| Path                           | Partly | Partly | No     | Unclear how to solve custom curve point data. |
| ReplayCamera                   | No     | No     | No     |        |
| SoundObj                       | Yes    | Yes    | Yes    |        |

If supported sections reference others not imported yet (like an Obj a Path), they are referenced by index. This is okay, as those sections are not rewritten on export anyway and order is kept. Otherwise, real Blender ID references are used.

![alt tag](https://raw.githubusercontent.com/Syroot/io_scene_mk8muunt/master/doc/readme/example.png)

S. the wiki for [help and more information](https://github.com/Syroot/io_scene_mk8muunt/wiki).

License
=======

<a href="http://www.wtfpl.net/"><img src="http://www.wtfpl.net/wp-content/uploads/2012/12/wtfpl.svg" height="20" alt="WTFPL" /></a> WTFPL

    Copyright © 2016 syroot.com <admin@syroot.com>
    This work is free. You can redistribute it and/or modify it under the
    terms of the Do What The Fuck You Want To Public License, Version 2,
    as published by Sam Hocevar. See the COPYING file for more details.
