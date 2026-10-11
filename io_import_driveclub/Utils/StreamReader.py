import struct, os
from io import BytesIO, IOBase

class StreamReader:
    def __init__(self, bs: bytes | IOBase):
        if isinstance(bs, IOBase):
            self._stream = bs
        else:
            self._stream = BytesIO(bs)
        
        self._endian = "<"
    
    @property
    def endian(self):
        return self._endian
    
    @endian.setter
    def endian(self, value):
        self._endian = value
    
    @property
    def stream(self):
        return self._stream
    
    @property
    def position(self):
        return self._stream.tell()
    
    @property
    def length(self):
        pos = self._stream.tell()
        self._stream.seek(0, os.SEEK_END)
        size = self._stream.tell()
        self._stream.seek(pos) # back to where we were
        return size
    
    def seek(self, offset, whence):
        return self._stream.seek(offset, whence)
    
    # Common
    def read_bool(self):
        return struct.unpack(f"{self._endian}?", self._stream.read(1))[0]
    
    def read_char(self):
        return struct.unpack(f"{self._endian}c", self._stream.read(1))[0]
    
    def read_string(self, size):
        return struct.unpack(f"{self._endian}{size}s", self._stream.read(size))[0].decode("utf-8", errors="ignore")
    
    def read_null_terminated_string(self):
        retval = bytearray()
        while True:
            ch = self._stream.read(1)
            if ch in (b'', b'\x00'):
                break
            retval.extend(ch)
        return retval.decode()
    
    def read_bytes(self, size):
        return self._stream.read(size)
    
    # Signed
    def read_int8(self):
        return struct.unpack(f"{self._endian}b", self._stream.read(1))[0]
    
    def read_int16(self):
        return struct.unpack(f"{self._endian}h", self._stream.read(2))[0]
    
    def read_int32(self):
        return struct.unpack(f"{self._endian}i", self._stream.read(4))[0]
    
    def read_int64(self):
        return struct.unpack(f"{self._endian}q", self._stream.read(8))[0]
    
    # Unsigned
    def read_uint8(self):
        return struct.unpack(f"{self._endian}B", self._stream.read(1))[0]
    
    def read_uint16(self):
        return struct.unpack(f"{self._endian}H", self._stream.read(2))[0]
    
    def read_uint32(self):
        return struct.unpack(f"{self._endian}I", self._stream.read(4))[0]
    
    def read_uint64(self):
        return struct.unpack(f"{self._endian}Q", self._stream.read(8))[0]
    
    # Floating-point
    def read_float16(self):
        return struct.unpack(f"{self._endian}e", self._stream.read(2))[0]
    
    def read_float32(self):
        return struct.unpack(f"{self._endian}f", self._stream.read(4))[0]
    
    def read_float64(self):
        return struct.unpack(f"{self._endian}d", self._stream.read(8))[0]
    
    # Signed arrays
    def read_int8_array(self, count: int):
        return struct.unpack(f"{self._endian}{count}b", self._stream.read(1 * count))
    
    def read_int16_array(self, count: int):
        return struct.unpack(f"{self._endian}{count}h", self._stream.read(2 * count))
    
    def read_int32_array(self, count: int):
        return struct.unpack(f"{self._endian}{count}i", self._stream.read(4 * count))
    
    def read_int64_array(self, count: int):
        return struct.unpack(f"{self._endian}{count}q", self._stream.read(8 * count))
    
    # Unsigned arrays
    def read_uint8_array(self, count: int):
        return struct.unpack(f"{self._endian}{count}B", self._stream.read(1 * count))
    
    def read_uint16_array(self, count: int):
        return struct.unpack(f"{self._endian}{count}H", self._stream.read(2 * count))
    
    def read_uint32_array(self, count: int):
        return struct.unpack(f"{self._endian}{count}I", self._stream.read(4 * count))
    
    def read_uint64_array(self, count: int):
        return struct.unpack(f"{self._endian}{count}Q", self._stream.read(8 * count))
    
    # Floating-point arrays
    def read_float16_array(self, count: int):
        return struct.unpack(f"{self._endian}{count}e", self._stream.read(2 * count))
    
    def read_float32_array(self, count: int):
        return struct.unpack(f"{self._endian}{count}f", self._stream.read(4 * count))
    
    def read_float64_array(self, count: int):
        return struct.unpack(f"{self._endian}{count}d", self._stream.read(8 * count))
    
    # Console-specific
    def read_11bitN(self):
        packed_value = struct.unpack(f"{self._endian}I", self._stream.read(4))[0]
        
        x = packed_value & 0x7FF
        y = (packed_value >> 11) & 0x7FF
        z = (packed_value >> 22) & 0x3FF
        
        if x > 1023: x -= 2048
        if y > 1023: y -= 2048
        if z > 511: z -= 1024
        
        return [ x / 1023.0, y / 1023.0, z / 511.0, 1.0 ]
    
    def read_dec3n(self):
        packed_value = struct.unpack(f"{self._endian}I", self._stream.read(4))[0]
        
        x = packed_value & 0x3FF
        y = (packed_value >> 10) & 0x3FF
        z = (packed_value >> 20) & 0x3FF
        w = (packed_value >> 30) & 0x3
        
        if x > 511: x -= 1024
        if y > 511: y -= 1024
        if z > 511: z -= 1024
        if w > 1: w -= 4
        
        return [ x / 511.0, y / 511.0, z / 511.0, w ]
