from .DXGI_FORMAT import DXGI_FORMAT
from ..InGameStructs.PixelBuffer.PixelFormat import PixelFormat

class PS4Texture:
    def __init__(self):
        pass
    
    @staticmethod
    def pixels_per_block(fmt):
        match fmt:
            case DXGI_FORMAT.BC1_TYPELESS | DXGI_FORMAT.BC1_UNORM | DXGI_FORMAT.BC1_UNORM_SRGB | \
                    DXGI_FORMAT.BC4_TYPELESS | DXGI_FORMAT.BC4_UNORM | DXGI_FORMAT.BC4_SNORM | \
                    DXGI_FORMAT.BC2_TYPELESS | DXGI_FORMAT.BC2_UNORM | DXGI_FORMAT.BC2_UNORM_SRGB | \
                    DXGI_FORMAT.BC3_TYPELESS | DXGI_FORMAT.BC3_UNORM | DXGI_FORMAT.BC3_UNORM_SRGB | \
                    DXGI_FORMAT.BC5_TYPELESS | DXGI_FORMAT.BC5_UNORM | DXGI_FORMAT.BC5_SNORM | \
                    DXGI_FORMAT.BC6H_TYPELESS | DXGI_FORMAT.BC6H_UF16 | DXGI_FORMAT.BC6H_SF16 | \
                    DXGI_FORMAT.BC7_TYPELESS | DXGI_FORMAT.BC7_UNORM | DXGI_FORMAT.BC7_UNORM_SRGB:
                return 4
        
        return 1
    
    @staticmethod
    def bits_per_pixel(fmt):
        match fmt:
            case DXGI_FORMAT.R32G32B32A32_TYPELESS | DXGI_FORMAT.R32G32B32A32_FLOAT | DXGI_FORMAT.R32G32B32A32_UINT | DXGI_FORMAT.R32G32B32A32_SINT:
                return 128

            case DXGI_FORMAT.R32G32B32_TYPELESS | DXGI_FORMAT.R32G32B32_FLOAT | DXGI_FORMAT.R32G32B32_UINT | DXGI_FORMAT.R32G32B32_SINT:
                 return 96

            case DXGI_FORMAT.R16G16B16A16_TYPELESS | DXGI_FORMAT.R16G16B16A16_FLOAT | DXGI_FORMAT.R16G16B16A16_UNORM | DXGI_FORMAT.R16G16B16A16_UINT | \
                DXGI_FORMAT.R16G16B16A16_SNORM | DXGI_FORMAT.R16G16B16A16_SINT | DXGI_FORMAT.R32G32_TYPELESS | DXGI_FORMAT.R32G32_FLOAT | \
                DXGI_FORMAT.R32G32_UINT | DXGI_FORMAT.R32G32_SINT | DXGI_FORMAT.R32G8X24_TYPELESS | DXGI_FORMAT.D32_FLOAT_S8X24_UINT | \
                DXGI_FORMAT.R32_FLOAT_X8X24_TYPELESS | DXGI_FORMAT.X32_TYPELESS_G8X24_UINT:
                 return 64

            case DXGI_FORMAT.R10G10B10A2_TYPELESS | DXGI_FORMAT.R10G10B10A2_UNORM | DXGI_FORMAT.R10G10B10A2_UINT | DXGI_FORMAT.R11G11B10_FLOAT | \
                DXGI_FORMAT.R8G8B8A8_TYPELESS | DXGI_FORMAT.R8G8B8A8_UNORM | DXGI_FORMAT.R8G8B8A8_UNORM_SRGB | DXGI_FORMAT.R8G8B8A8_UINT | \
                DXGI_FORMAT.R8G8B8A8_SNORM | DXGI_FORMAT.R8G8B8A8_SINT | DXGI_FORMAT.R16G16_TYPELESS | DXGI_FORMAT.R16G16_FLOAT | \
                DXGI_FORMAT.R16G16_UNORM | DXGI_FORMAT.R16G16_UINT | DXGI_FORMAT.R16G16_SNORM | DXGI_FORMAT.R16G16_SINT | \
                DXGI_FORMAT.R32_TYPELESS | DXGI_FORMAT.D32_FLOAT | DXGI_FORMAT.R32_FLOAT | DXGI_FORMAT.R32_UINT | \
                DXGI_FORMAT.R32_SINT | DXGI_FORMAT.R24G8_TYPELESS | DXGI_FORMAT.D24_UNORM_S8_UINT | DXGI_FORMAT.R24_UNORM_X8_TYPELESS | \
                DXGI_FORMAT.X24_TYPELESS_G8_UINT | DXGI_FORMAT.R9G9B9E5_SHAREDEXP | DXGI_FORMAT.R8G8_B8G8_UNORM | DXGI_FORMAT.G8R8_G8B8_UNORM | \
                DXGI_FORMAT.B8G8R8A8_UNORM | DXGI_FORMAT.B8G8R8X8_UNORM | DXGI_FORMAT.R10G10B10_XR_BIAS_A2_UNORM | DXGI_FORMAT.B8G8R8A8_TYPELESS | \
                DXGI_FORMAT.B8G8R8A8_UNORM_SRGB | DXGI_FORMAT.B8G8R8X8_TYPELESS | DXGI_FORMAT.B8G8R8X8_UNORM_SRGB:
                 return 32

            case DXGI_FORMAT.R8G8_TYPELESS | DXGI_FORMAT.R8G8_UNORM | DXGI_FORMAT.R8G8_UINT | DXGI_FORMAT.R8G8_SNORM | \
                DXGI_FORMAT.R8G8_SINT | DXGI_FORMAT.R16_TYPELESS | DXGI_FORMAT.R16_FLOAT | DXGI_FORMAT.D16_UNORM | \
                DXGI_FORMAT.R16_UNORM | DXGI_FORMAT.R16_UINT | DXGI_FORMAT.R16_SNORM | DXGI_FORMAT.R16_SINT | \
                DXGI_FORMAT.B5G6R5_UNORM | DXGI_FORMAT.B5G5R5A1_UNORM:
                 return 16

            case DXGI_FORMAT.R8_TYPELESS | DXGI_FORMAT.R8_UNORM | DXGI_FORMAT.R8_UINT | DXGI_FORMAT.R8_SNORM | \
                DXGI_FORMAT.R8_SINT | DXGI_FORMAT.A8_UNORM:
                 return 8

            case DXGI_FORMAT.R1_UNORM:
                 return 1

            case DXGI_FORMAT.BC1_TYPELESS | DXGI_FORMAT.BC1_UNORM | DXGI_FORMAT.BC1_UNORM_SRGB | DXGI_FORMAT.BC4_TYPELESS | \
                DXGI_FORMAT.BC4_UNORM | DXGI_FORMAT.BC4_SNORM:
                 return 4

            case DXGI_FORMAT.BC2_TYPELESS | DXGI_FORMAT.BC2_UNORM | DXGI_FORMAT.BC2_UNORM_SRGB | DXGI_FORMAT.BC3_TYPELESS | \
                DXGI_FORMAT.BC3_UNORM | DXGI_FORMAT.BC3_UNORM_SRGB | DXGI_FORMAT.BC5_TYPELESS | DXGI_FORMAT.BC5_UNORM | \
                DXGI_FORMAT.BC5_SNORM | DXGI_FORMAT.BC6H_TYPELESS | DXGI_FORMAT.BC6H_UF16 | DXGI_FORMAT.BC6H_SF16 | \
                DXGI_FORMAT.BC7_TYPELESS | DXGI_FORMAT.BC7_UNORM | DXGI_FORMAT.BC7_UNORM_SRGB:
                 return 8

            case _:
                 return 0
    
    @staticmethod
    def pixel_format_to_dxgi_format(pf):
        match pf:
            case PixelFormat.RGBA_32_I_LIN: return DXGI_FORMAT.R8G8B8A8_UNORM
            case PixelFormat.RGBA_32_I_SRGB: return DXGI_FORMAT.R8G8B8A8_UNORM_SRGB
            case PixelFormat.RGBA_64_F: return DXGI_FORMAT.R16G16B16A16_FLOAT
            case PixelFormat.RGBA_128_F: return DXGI_FORMAT.R32G32B32A32_FLOAT

            case PixelFormat.DXT1_LIN: return DXGI_FORMAT.BC1_UNORM
            case PixelFormat.DXT1_SRGB: return DXGI_FORMAT.BC1_UNORM_SRGB
            case PixelFormat.DXT3_LIN: return DXGI_FORMAT.BC3_UNORM
            case PixelFormat.DXT3_SRGB: return DXGI_FORMAT.BC3_UNORM_SRGB
            case PixelFormat.DXT5_LIN: return DXGI_FORMAT.BC5_UNORM
            case PixelFormat.DXT5_SRGB: return DXGI_FORMAT.BC5_SNORM
            case PixelFormat.A8_UNORM: return DXGI_FORMAT.A8_UNORM

            case PixelFormat.R_32_F: return DXGI_FORMAT.R32_FLOAT
            case PixelFormat.BC4_UNORM: return DXGI_FORMAT.BC4_UNORM
            case PixelFormat.BC4_SNORM: return DXGI_FORMAT.BC4_SNORM
            case PixelFormat.BC5_UNORM: return DXGI_FORMAT.BC5_UNORM
            case PixelFormat.BC5_SNORM: return DXGI_FORMAT.BC5_SNORM
            case PixelFormat.BC6H_UF: return DXGI_FORMAT.BC6H_UF16
            case PixelFormat.BC6H_SF: return DXGI_FORMAT.BC6H_SF16
            case PixelFormat.BC7_UNORM: return DXGI_FORMAT.BC7_UNORM
            case PixelFormat.BC7_SRGB: return DXGI_FORMAT.BC7_UNORM_SRGB
            case _: raise TypeError(f"Pixel format {pf} not supported")
    
    @staticmethod
    def swizzle(input, width, height, pixels_per_block, block_size):
        output                = bytearray(len(input))
        block_size            = int(block_size)
        
        height_texels         = int(height) // int(pixels_per_block)
        height_texels_aligned = (height_texels + 7) // 8
        width_texels          = int(width) // int(pixels_per_block)
        width_texels_aligned  = (width_texels + 7) // 8
        data_index            = 0

        for y in range(height_texels_aligned):
            for x in range(width_texels_aligned):
                for t in range(64):
                    pixel_index = PS4Texture.morton_reorder(t, 8, 8)
                    cur_pixel   = pixel_index // 8
                    rem_pixel   = pixel_index % 8
                    y_offset    = y * 8 + cur_pixel
                    x_offset    = x * 8 + rem_pixel

                    if x_offset < width_texels and y_offset < height_texels:
                        dest_pixel_index = y_offset   * width_texels + x_offset
                        dest_index       = block_size * dest_pixel_index

                        output[dest_index:dest_index + block_size] = input[data_index:data_index + block_size]

                    data_index += block_size
        
        return bytes(output)
    
    @staticmethod
    def morton_reorder(i, width, height):
        x = 1
        y = 1

        w = width
        h = height

        index = 0
        index2 = 0

        while w > 1 or h > 1:
            if w > 1:
                index += x * (i & 1)
                i >>= 1
                x *= 2
                w >>= 1
            if h > 1:
                index2 += y * (i & 1)
                i >>= 1
                y *= 2
                h >>= 1

        return index2 * width + index
