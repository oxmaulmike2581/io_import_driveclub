import ctypes

class StateArg(ctypes.Union):
    _fields_ = [
        ("m_int", ctypes.c_int),
        ("m_float", ctypes.c_float)
    ]

