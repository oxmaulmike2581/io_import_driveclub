from enum import IntEnum

class FieldType(IntEnum):
    #                          Size:
    FT_UNKNOWN = 0x0           # 0
    FT_INDEX_16 = 0x1          # 2
    FT_INDEX_32 = 0x2          # 4
    FT_HALF = 0x3              # 2
    FT_HALF2 = 0x4             # 4
    FT_HALF3 = 0x5             # 6
    FT_HALF4 = 0x6             # 8
    FT_FLOAT = 0x7             # 4
    FT_FLOAT2 = 0x8            # 8
    FT_FLOAT3 = 0x9            # 12
    FT_FLOAT4 = 0xA            # 16
    FT_DOUBLE = 0xB            # 8
    FT_DOUBLE2 = 0xC           # 16
    FT_DOUBLE3 = 0xD           # 24
    FT_DOUBLE4 = 0xE           # 32
    FT_NORMAL_10_10_10 = 0xF   # 4
    FT_NORMAL_11_11_10 = 0x10  # 4
    FT_UBYTE4 = 0x11           # 4
    FT_UBYTE4_ARGB = 0x12      # 4
    FT_UBYTE4_RGBA = 0x13      # 4
    FT_BYTE4_NORMALISED = 0x14 # 4
    FT_CUSTOM = 0x15           # 0
    NUM_FIELD_TYPES = 0x16     # 0

