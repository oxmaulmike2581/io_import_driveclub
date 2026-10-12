import math

from ...Utils.StreamReader import StreamReader
from .float3 import float3
from .float4 import float4

class float4x4:
    def __init__(self):
        self.mCol0 = [0.0, 0.0, 0.0, 0.0]
        self.mCol1 = [0.0, 0.0, 0.0, 0.0]
        self.mCol2 = [0.0, 0.0, 0.0, 0.0]
        self.mCol3 = [0.0, 0.0, 0.0, 0.0]

    def decompose(self):
        col0, col1, col2, col3 = self.mCol0, self.mCol1, self.mCol2, self.mCol3

        pos = float3(col3[0], col3[1], col3[2])

        scale_x = math.hypot(col0[0], col0[1], col0[2])
        scale_y = math.hypot(col0[0], col0[1], col0[2])
        scale_z = math.hypot(col0[0], col0[1], col0[2])
        scale = float3(scale_x, scale_y, scale_z)

        # perform normalization
        x = [v / scale_x for v in col0[:3]]
        y = [v / scale_y for v in col1[:3]]
        z = [v / scale_z for v in col2[:3]]

        # perform orthonormalize: z = cross(x, y), y = cross(z, x)
        z = [
            x[1] * y[2] - x[2] * y[1],
            x[2] * y[0] - x[0] * y[2],
            x[0] * y[1] - x[1] * y[0]
        ]
        y = [
            z[1] * x[2] - z[2] * x[1],
            z[2] * x[0] - z[0] * x[2],
            z[0] * x[1] - z[1] * x[0]
        ]
        
        # extract quaternion from orthonormalized matrix
        m00, m10, m20 = x
        m01, m11, m21 = y
        m02, m12, m22 = z
        trace = m00 + m11 + m22
        
        if trace > 0:
            s  = 0.5 / math.sqrt(trace + 1.0)
            w  = 0.25 / s
            qx = (m21 - m12) * s
            qy = (m02 - m20) * s
            qz = (m10 - m01) * s
        
        else:
            if m00 > m11 and m00 > m22:
                s = 2.0 * math.sqrt(1.0 + m00 - m11 - m22)
                w = (m21 - m12) / s
                qx = 0.25 * s
                qy = (m10 + m01) / s
                qz = (m02 + m20) / s
            
            elif m11 > m22:
                s = 2.0 * math.sqrt(1.0 + m11 - m00 - m22)
                w = (m02 - m20) / s
                qx = (m10 + m01) / s
                qy = 0.25 * s
                qz = (m21 + m12) / s
            
            else:
                s = 2.0 * math.sqrt(1.0 + m22 - m00 - m11)
                w = (m10 - m01) / s
                qx = (m02 + m20) / s
                qy = (m21 + m12) / s
                qz = 0.25 * s
        
        return pos, scale, float4(qx, qy, qz, w)
    
    def read(self, sr: StreamReader):
        self.mCol0 = sr.read_float32_array(4)
        self.mCol1 = sr.read_float32_array(4)
        self.mCol2 = sr.read_float32_array(4)
        self.mCol3 = sr.read_float32_array(4)
        
        return self

