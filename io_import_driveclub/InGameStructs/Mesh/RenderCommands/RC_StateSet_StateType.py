from enum import IntEnum

class RC_StateSet_StateType(IntEnum):
    WIREFRAME_MODE           = 0x0
    STENCIL_MODE             = 0x1
    ALPHA_TEST_MODE          = 0x2
    ALPHA_BLEND_MODE         = 0x3
    SET_SCISSOR              = 0x4
    AUTO_SAMPLER_ARRAY_BASE  = 0x5
    AUTO_SAMPLER_ARRAY_INDEX = 0x6
    AUTO_SAMPLER_TEXTURE_PTR = 0x7
    WRITE_MASK               = 0x8
    NUM_STATE_TYPES          = 0x9

