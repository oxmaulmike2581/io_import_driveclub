from enum import IntFlag

class DDSCAPS(IntFlag):
    COMPLEX = 0x8      # Optional; must be used on any file that contains more than one surface (a mipmap, a cubic environment map, or mipmapped volume texture).
    MIPMAP  = 0x400000 # Optional; should be used for a mipmap.
    TEXTURE = 0x1000   # Required

