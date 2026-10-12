from enum import IntFlag

class PF_FLAGS(IntFlag):
    ALPHAPIXELS = 0x1     # Texture contains alpha data; dwRGBAlphaBitMask contains valid data.
    ALPHA       = 0x2     # Used in some older DDS files for alpha channel only uncompressed data
    FOURCC      = 0x4     # dwFourCC contains valid data.
    RGB         = 0x40    # Texture contains uncompressed RGB data; dwRGBBitCount and the RGB masks (dwRBitMask, dwGBitMask, dwBBitMask) contain valid data.
    YUV         = 0x200   # Used in some older DDS files for YUV uncompressed data
    LUMINANCE   = 0x20000 # Used in some older DDS files for single channel color uncompressed data. Can be combined with DDPF_ALPHAPIXELS for a two channel DDS file.

