from enum import IntEnum

class PixelFormat(IntEnum):
    # Driveclub Proto
    UNDEFINED_PIXEL_FORMAT = 0
    RGBA_32_I_LIN          = 1
    RGBA_32_I_SRGB         = 2
    RGBA_64_F              = 3
    RGBA_128_F             = 4
    Z_16                   = 5
    Z_32                   = 6
    Z32_S8                 = 7
    STENCIL                = 8
    DXT1_LIN               = 9
    DXT1_SRGB              = 10
    DXT3_LIN               = 11
    DXT3_SRGB              = 12
    DXT5_LIN               = 13
    DXT5_SRGB              = 14
    A8_UNORM               = 15
    RG_16_F                = 16
    RG_32_F                = 17
    RGBA_16_I              = 18
    R8G8                   = 19
    A16                    = 20
    L16A16                 = 21
    R_16_F                 = 22
    R_32_F                 = 23
    R11G11B10_F            = 24
    R9G9B9E5               = 25
    R10G10B10A2_UNORM      = 26
    R8_UNORM               = 27
    BGRA_32_I_SRGB         = 28
    BC4_UNORM              = 29
    BC4_SNORM              = 30
    BC5_UNORM              = 31
    BC5_SNORM              = 32
    BC6H_UF                = 33
    BC6H_SF                = 34
    BC7_UNORM              = 35
    BC7_SRGB               = 36
    RGBA_64_UNORM          = 37
    RGBA_32_SNORM          = 38

    # Driveclub retail
    UNK_39                 = 39
    UNK_40                 = 40
    UNK_41                 = 41

    NUM_PIXEL_FORMATS      = 39

