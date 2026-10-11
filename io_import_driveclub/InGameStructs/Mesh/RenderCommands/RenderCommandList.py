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
                case 0:
                    stop = True
                    break
                
                case 1:
                    cmd.RenderCommandDraw.PrimType    = PrimType(sr.read_uint8())
                    cmd.RenderCommandDraw.StartVertex = sr.read_int32()
                    cmd.RenderCommandDraw.NumVertices = sr.read_int32()
                
                case 2:
                    cmd.RenderCommandDrawIndexed.VertexInfoCount = sr.read_uint8()
                    cmd.RenderCommandDrawIndexed.VertexOffset    = sr.read_int32() # most probably vertex count * stride
                    cmd.RenderCommandDrawIndexed.VertexCount     = sr.read_int32()
                    cmd.RenderCommandDrawIndexed.IndexOffset     = sr.read_int32() # * 2 + 28 bytes header
                    cmd.RenderCommandDrawIndexed.IndexCount      = sr.read_int32() # * 2
                    cmd.RenderCommandDrawIndexed.Empty           = sr.read_int32()
                
                case 3:
                    cmd.RenderCommandMaterialSet.m_UID = ResourceIdentifier(sr.read_uint64())
                    
                    if ver < 0xB0000:
                        cmd.RenderCommandMaterialSet.PermutationIndex = sr.read_uint16()
                
                case 4:
                    cmd.RenderCommandVertexStreamSet.StreamID = sr.read_uint8()
                    cmd.RenderCommandVertexStreamSet.VertexBufferID = ResourceIdentifier(sr.read_uint64())
                
                case 5:
                    cmd.RenderCommandIndexStreamSet.IndexBufferID = ResourceIdentifier(sr.read_uint64())
                
                case 11:
                    cmd.RenderCommandStateSet.StateType = RenderCommandStateSet_StateType(sr.read_uint8())
                    cmd.RenderCommandStateSet.Arg1 = StateArg(m_int=sr.read_int32())
                    cmd.RenderCommandStateSet.Arg2 = StateArg(m_int=sr.read_int32())
                    cmd.RenderCommandStateSet.Arg3 = StateArg(m_int=sr.read_int32())
                
                case 14:
                    cmd.RenderCommand14.Unk1 = sr.read_uint32()
                    cmd.RenderCommand14.Unk2 = sr.read_uint32()
                    cmd.RenderCommand14.Unk3 = sr.read_uint32()
                    cmd.RenderCommand14.Unk4 = sr.read_uint32()
            
            if stop:
                break
            
            self.RenderCommands.append(cmd)
        
        return self
