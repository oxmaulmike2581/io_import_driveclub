from .RC_Draw import RC_Draw
from .RC_DrawIndexed import RC_DrawIndexed
from .RC_MaterialSet import RC_MaterialSet
from .RC_VertexStreamSet import RC_VertexStreamSet
from .RC_StateSet import RC_StateSet
from .RC_14 import RC_14

class RenderCommand:
    def __init__(self):
        self.Command_ = None
        self.RenderCommandDraw            = RC_Draw()
        self.RenderCommandDrawIndexed     = RC_DrawIndexed()
        self.RenderCommandMaterialSet     = RC_MaterialSet()
        self.RenderCommandVertexStreamSet = RC_VertexStreamSet()
        self.RenderCommandIndexStreamSet  = RC_VertexStreamSet() # same for vertex and index buffers
        self.RenderCommandStateSet        = RC_StateSet()
        self.RenderCommand14              = RC_14()

