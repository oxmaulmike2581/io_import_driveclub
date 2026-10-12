from ....Utils.StreamReader import StreamReader
from ...Resource.ResourceIdentifier import ResourceIdentifier
from ..Command import Command
from ..PrimType import PrimType
from ..StateArg import StateArg
from .RenderCommand import RenderCommand
from .RC_StateSet_StateType import RC_StateSet_StateType

class RenderCommandList:
    def __init__(self):
        self.RuntimeRenderCommandListSize = None
        self.RenderCommands               = []
    
    def read(self, sr: StreamReader, ver: int):
        # Use command sizes above to calculate this
        # This is used to allocate the command object list (cpp object)
        self.RuntimeRenderCommandListSize = sr.read_uint16()
        
        if self.RuntimeRenderCommandListSize == 0:
            return None
        
        stop = False
        while True:
            # read each command
            cmd = RenderCommand()
            cmd.Command_ = Command(sr.read_uint8())

            match cmd.Command_:
                case Command.END:
                    stop = True
                    break
                
                case Command.DRAW:
                    # also never seen
                    cmd.RenderCommandDraw.PrimType    = PrimType(sr.read_uint8())                          # m_PrimType
                    cmd.RenderCommandDraw.StartVertex = sr.read_int32()                                    # m_StartVertex
                    cmd.RenderCommandDraw.NumVertices = sr.read_int32()                                    # m_NumVertices
                
                case Command.DRAW_INDEXED:
                    # for unknown reason (resource version?) in Motorstorm Apocalypse Proto Resource Viewer
                    # first 2 fields are "m_PrimType" (8 bit) and "m_NumIndices" (24 bit)
                    # but for DriveClub it's a 8 bit for "m_PrimType" and 32 bit for 2nd field, which is actually "m_BaseVertexOffset"
                    # 1st field is not a "VertexInfoCount" (as defined in Nenkai's template), it's a "m_PrimType"
                    # which points to index buffer type
                    # DriveClub meshes are mostly have PrimType = 3 (TRIANGLE_LIST)
                    # so all field names in comments are mostly guessed
                    # my code for index buffer converting was written when didn't know that
                    # but it works so I will not edit it
                    cmd.RenderCommandDrawIndexed.VertexInfoCount = PrimType(sr.read_uint8())               # m_PrimType
                    cmd.RenderCommandDrawIndexed.VertexOffset    = sr.read_int32()                         # m_BaseVertexOffset
                    cmd.RenderCommandDrawIndexed.VertexCount     = sr.read_int32()                         # m_StartVertex
                    cmd.RenderCommandDrawIndexed.IndexOffset     = sr.read_int32()                         # m_BaseIndexOffset
                    cmd.RenderCommandDrawIndexed.IndexCount      = sr.read_int32()                         # m_StartIndex
                    cmd.RenderCommandDrawIndexed.Empty           = sr.read_int32()                         # idk
                
                case Command.MATERIAL_SET:
                    # material resources for DriveClub has not been researched yet
                    # only for Motorstorm...
                    # and I think that these resources are more complex and points to shaders
                    # so if I'm right then I have to find a Orbis Shader decompiler
                    # or disassembler, or parser...
                    cmd.RenderCommandMaterialSet.m_UID = ResourceIdentifier(sr.read_uint64())
                    
                    if ver < 0xB0000:
                        cmd.RenderCommandMaterialSet.PermutationIndex = sr.read_uint16()                   # m_permutationIdx
                
                case Command.VERTEX_STREAM_SET:
                    cmd.RenderCommandVertexStreamSet.StreamID       = sr.read_uint8()                      # m_StreamId
                    cmd.RenderCommandVertexStreamSet.VertexBufferID = ResourceIdentifier(sr.read_uint64()) # m_spuVertexBufferID
                
                case Command.INDEX_STREAM_SET:
                    cmd.RenderCommandIndexStreamSet.IndexBufferID = ResourceIdentifier(sr.read_uint64())   # m_spuIndexBufferID
                
                case Command.STATE_SET:
                    # I don't know why it's parsed haha, just ported from template as is
                    cmd.RenderCommandStateSet.StateType = RenderCommandStateSet_StateType(sr.read_uint8()) # m_StateType
                    cmd.RenderCommandStateSet.Arg1 = StateArg(m_int=sr.read_int32())                       # m_arg1
                    cmd.RenderCommandStateSet.Arg2 = StateArg(m_int=sr.read_int32())                       # m_arg2
                    cmd.RenderCommandStateSet.Arg3 = StateArg(m_int=sr.read_int32())                       # m_arg3
                
                case Command.UNK_CMD_14:
                    # same
                    cmd.RenderCommand14.Unk1 = sr.read_uint32()
                    cmd.RenderCommand14.Unk2 = sr.read_uint32()
                    cmd.RenderCommand14.Unk3 = sr.read_uint32()
                    cmd.RenderCommand14.Unk4 = sr.read_uint32()
            
            if stop:
                break
            
            self.RenderCommands.append(cmd)
        
        return self
