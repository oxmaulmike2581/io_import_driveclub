# DriveClub Model Importer
[img]dc_logo.png[/img]
---
## Features
* import vehicle .rpk files with all LODs, UVs, normals, colors, etc.
* partial support for materials
* export textures to .dds (DX10) with all mipmaps

## Installation
* Edit -> Preferences -> Addons -> Install from Disk - select io_import_driveclub.zip file
* (on Blender 4.1) tick the checkbox at the left side to activate the addon

## Compatibility
Addon has been initially written on Blender 4.4.3 but also was successfully tested on:
* 4.1.1
* 4.2.23
* 4.3.2
* 4.4.3
* 4.5.14
* 5.0.1
* 5.1.2
* 5.2.2
* 5.3.0-beta
* 5.4.0-alpha

## Limitations
* Material support is partial *(no auto-assigning of textures and properties due to unresearched format)*
* No skeletal animation at all *(because of same problem)*
* Some textures *(like occ.dds)* can't be opened in some editors and old versions of Microsoft's DirectXTex can fail on them.

## Credits
* [RPK_ResourcePack.bt](https://github.com/Nenkai/010GameTemplates/blob/main/Evolution%20Studios/RPK_ResourcePack.bt) by [Nenkai](https://github.com/nenkai)
* [DriveClubFS](https://github.com/Nenkai/DriveClubFS) by [Nenkai](https://github.com/nenkai)
* Information about DDS files from Microsoft's site

## License
* MIT
