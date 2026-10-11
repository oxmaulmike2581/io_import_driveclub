from enum import IntEnum

class PixelBufferBase_ServerUsage(IntEnum):
    READ_WRITE        = 0
    READ_ONLY         = 1
    READLOTS_WRITE    = 2
    READ_WRITELOTS    = 3
    NUM_SERVER_USAGES = 4

