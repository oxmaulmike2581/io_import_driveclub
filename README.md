# DriveClub Model Importer
<p align="center">
 <img width="50%" src="https://github.com/oxmaulmike2581/io_import_driveclub/blob/master/dc_logo.png" alt="DriveClub Logo" />
</p>
<hr />

## Features
* import vehicle .rpk files with all LODs, UVs, normals, colors, etc.
* import only LOD0 meshes *(faster)*
* partial support for materials
* export textures to .dds (DX10) with all mipmaps

## Installation
* Edit -> Preferences -> Addons -> Install from Disk -> select **io_import_driveclub.zip** file
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

## WARNING
I'm not responsible for changes in the code in any forks. If you have an error / you broke the functionality / etc. after you (or maybe your AI) changed something - it's only your way now.
I'm maintain only version released here.

## Limitations
* **Only DriveClub is supported now.** Motorstorm Apocalypse or other games on this engine will not officially supported *(may be it can be changed in the future)*
* Material support is partial *(no auto-assigning of textures and properties due to unresearched format for DriveClub)*
* No track/world/location support *(in theory it can be supported but partially, without proper placement)*
* No skeletal animation at all *(because of same problem)*

## Credits
* [RPK_ResourcePack.bt](https://github.com/Nenkai/010GameTemplates/blob/main/Evolution%20Studios/RPK_ResourcePack.bt) by [Nenkai](https://github.com/nenkai)
* [DriveClubFS](https://github.com/Nenkai/DriveClubFS) by [Nenkai](https://github.com/nenkai)
* Information about DDS files from Microsoft's site

## License
* [MIT](https://github.com/oxmaulmike2581/io_import_driveclub/blob/master/LICENSE)
