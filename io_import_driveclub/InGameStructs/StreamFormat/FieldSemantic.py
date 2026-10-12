from enum import IntEnum

class FieldSemantic(IntEnum):
    FS_UNKNOWN = 0
    FS_POSITION = 1
    FS_NORMAL = 2
    FS_BINORMAL = 3
    FS_TANGENT = 4
    FS_TEXCOORD = 5
    FS_COLOR = 6
    FS_BLENDWEIGHTS = 7
    FS_BLENDINDICES = 8
    FS_INDEX = 9

