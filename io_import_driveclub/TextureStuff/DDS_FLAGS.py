from enum import IntFlag

class DDS_FLAGS(IntFlag):
    CAPS        = 0x1      # Required in every .dds file.
    HEIGHT      = 0x2      # Required in every .dds file.
    WIDTH       = 0x4      # Required in every .dds file.
    PITCH       = 0x8      # Required when pitch is provided for an uncompressed texture.
    PIXELFORMAT = 0x1000   # Required in every .dds file.
    MIPMAPCOUNT = 0x20000  # Required in a mipmapped texture.
    LINEARSIZE  = 0x80000  # Required when pitch is provided for a compressed texture.
    DEPTH       = 0x800000 # Required in a depth texture.
    
    TEXTURE    = CAPS | HEIGHT | WIDTH | PIXELFORMAT
