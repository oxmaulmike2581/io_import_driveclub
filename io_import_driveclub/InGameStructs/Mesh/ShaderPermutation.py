from enum import IntEnum

class ShaderPermutation(IntEnum):
    kShaderPermForward          = 0x0
    kShaderPermForwardTexLM     = 0x1
    kShaderPermForwardVertLM    = 0x2
    kShaderPermShadMapGen       = 0x3
    kShaderPermDepthOnly        = 0x4
    kShaderPermPixelVelocity    = 0x5
    kShaderPermGhost            = 0x6
    kShaderPermOverdraw         = 0x7
    kShaderPermMeshRes          = 0x8
    kShaderPermGBuffer          = 0x9
    kShaderPermNormalOnly       = 0xA
    kShaderPermMaterialLPP      = 0xB
    kShaderPermMaterialLPPTexLM = 0xC
    kNumShaderPermutations      = 0xD
    kShaderPermRoot             = 0xD

