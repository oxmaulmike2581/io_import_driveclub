from enum import IntEnum

class PrimType(IntEnum):
    PT_POINT_LIST  = 0x0
    PT_LINE_LIST   = 0x1
    PT_LINE_STRIP  = 0x2
    PT_TRI_LIST    = 0x3
    PT_TRI_FAN     = 0x4
    PT_TRI_STRIP   = 0x5
    PT_QUAD_LIST   = 0x6
    NUM_PRIM_TYPES = 0x7

