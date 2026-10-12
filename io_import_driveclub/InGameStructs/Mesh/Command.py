from enum import IntEnum

class Command(IntEnum):
    # evo::renderer::RenderCommandBase::commandSizes - ,, , , , 0x10, 0x50, 0x30, 0x20, 0x10, 0x10
    # ^ these command sizes are from Motorstorm Apocalypse Proto Resource Viewer (Jan 2010)
    #   their sizes are a little different in DriveClub
    
    END                             = 0  # 0x10
    DRAW                            = 1  # 0x10
    DRAW_INDEXED                    = 2  # 0x10
    MATERIAL_SET                    = 3  # 0x10
    VERTEX_STREAM_SET               = 4  # 0x10
    INDEX_STREAM_SET                = 5  # 0x10    
    WORLD_MATRIX_SET                = 6  # 0x10
    OWNED_WORLD_MATRIX_SET          = 7  # 0x50
    PREV_WORLD_MATRIX_SET           = 8  # 0x10        
    OWNED_PREVIOUS_WORLD_MATRIX_SET = 9  # 0x50
    MATERIAL_SET_PARAM              = 10 # 0x30
    STATE_SET                       = 11 # 0x20
    TIMESTAMP_SET                   = 12 # 0x10
    DISPLAYLIST_EXECUTE             = 13 # 0x10
    
    # DriveClub
    UNK_CMD_14                      = 14 # NUM_COMMANDS in Motorstorm Apocalypse

