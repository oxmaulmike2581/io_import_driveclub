from enum import IntEnum

class PixelFormatOld(IntEnum):
    PF_UNDEFINED_PIXEL_FORMAT = 0
    PF_RGBA_32_I              = 1
    PF_RGBA_64_F              = 2
    PF_RGBA_128_F             = 3
    PF_Z_16                   = 4
    PF_Z_24                   = 5
    PF_Z_24_S_8               = 6
    PF_Z_32                   = 7
    PF_STENCIL                = 8
    PF_DXT1                   = 10
    PF_DXT3                   = 10
    PF_DXT5                   = 11
    PF_LUM_8                  = 12 # 1 byte luminance
    PF_RG_32_F                = 13
    PF_RGBA_16_I              = 14
    PF_L8A8                   = 15
    PF_A16                    = 16
    PF_L16A16                 = 17
    PF_R_32_F                 = 18

