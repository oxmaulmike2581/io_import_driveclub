import ctypes

class ResourceIdentifier(ctypes.Union):
    class Packed(ctypes.Structure):
        _fields_ = [
            ("Identifier", ctypes.c_uint64, 48),
            ("Type",       ctypes.c_uint64, 16)
        ]

    _fields_ = [
        ("m_UID",  ctypes.c_uint64),
        ("Packed", Packed)
    ]

    def __init__(self, uid=0):
        super().__init__(m_UID=uid)

