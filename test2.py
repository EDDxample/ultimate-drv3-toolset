from io import BufferedReader
from struct import unpack, pack

PRINT_PADDING = ''
def padin():
    global PRINT_PADDING
    PRINT_PADDING += '  '
def padout():
    global PRINT_PADDING
    if len(PRINT_PADDING) > len('  '):
        PRINT_PADDING = PRINT_PADDING[0: -len('  ')]
    else:
        PRINT_PADDING = ''


pic_formats = {
    0x00: 'Unknown',
    0x01: 'ARGB8888',
    0x02: 'BGR565',
    0x05: 'BGRA4444',
    0x0F: 'DXT1RGB',
    0x11: 'DXT5',
    0x14: 'BC5',
    0x16: 'BC4',
    0x1A: 'Indexed8',
    0x1C: 'BPTC',
}

def PRINT(*args, **kwargs)  :
    if PRINT_PADDING:
        print(PRINT_PADDING, *args, **kwargs)
    else: print(*args, **kwargs)

def padding(data: BufferedReader, length):
    data.seek(length, 1)

def read(datatype: str, data: BufferedReader, bigendian=False, length=0, encoding='utf-8', name=''):
    endianness = '>' if bigendian else '<'
    numberic_datatypes = {
        'u1':  lambda data: unpack(f'{endianness}B', data.read(1))[0],
        'u2': lambda data: unpack(f'{endianness}H', data.read(2))[0],
        'u4': lambda data: unpack(f'{endianness}I', data.read(4))[0],
        'string':     lambda _: None,
        'nullstring': lambda _: None,
    }

    out = numberic_datatypes[datatype](data)

    if datatype == 'string' and length > 0:
        out = data.read(length).decode(encoding)
        PRINT('str', name, out)
        return out
    elif datatype == 'nullstring':
        out = bytes()
        while True:
            if encoding == 'utf-16':
                char = data.read(2)
                if char == b'\x00\x00' or not char:
                    return out.decode(encoding)
                else: out += char
            else:
                char = data.read(1)
                if char == b'\x00' or not char:
                    PRINT(datatype, name, out.decode(encoding))
                    return out.decode(encoding)
                else: out += char 

    PRINT(datatype, name, out)
    return out

def write(datatype: str, data: BufferedReader, n, bigendian=False, length=0, encoding='utf-8'):
    pass

# srd format:
# 
# $CFH
# $TXR
#   $RSI
#     SpFt
#   $CT0
# $CT0


def main():
    with open('files/srd/0_font/fr.srd', 'rb') as data:
        readCFH(data)
        readTXR(data)
        readCT0(data)

def readTagHeader(data: BufferedReader):
    PRINT('-- header --')
    padin()
    magic          = read('string', data, name='magic', length=4)
    data_length    = read('u4', data, name='data_length', bigendian=True)
    subdata_length = read('u4', data, name='subdata_length', bigendian=True)
    idk            = read('u4', data, name='idk', bigendian=True)
    padout()

def readCFH(data: BufferedReader):
    bytepos = data.tell()
    PRINT('=== $CFH ===', f'@{bytepos:04x}')
    padin()
    readTagHeader(data)
    padout()

def readCT0(data: BufferedReader):
    bytepos = data.tell()
    PRINT('=== $CT0 ===', f'@{bytepos:04x}')
    padin()
    readTagHeader(data)
    padout()

def readTXR(data: BufferedReader):
    bytepos = data.tell()
    PRINT('=== $TRX ===', f'@{bytepos:04x}')
    padin()
    readTagHeader(data)

    PRINT('-- data --')
    padin()
    idk1      = read('u4', data, name='idk1')
    swizzle   = read('u2', data, name='swizzle')
    width     = read('u2', data, name='width')
    height    = read('u2', data, name='height')
    # PRINT(f'texture ({width} x {height})')
    scanline  = read('u2', data, name='scanline')
    formatID  = read('u1', data, name='formatID')
    picformat = pic_formats[formatID] if formatID in pic_formats else 'IDK'
    idk2      = read('u1', data, name='idk2')
    palette   = read('u1', data, name='palette')
    paletteID = read('u1', data, name='paletteID')
    # PRINT((idk1, swizzle, width, height, scanline, picformat, idk2, palette, paletteID))
    padout()

    PRINT('-- subdata --')
    padin()
    readRSI(data)
    readCT0(data)
    padout()

    padout()

def readRSI(data: BufferedReader):
    bytepos = data.tell()
    PRINT('=== $RSI ===', f'@{bytepos:04x}')
    padin()
    readTagHeader(data)
    
    PRINT('-- data --')
    padin()
    idk10 = read('u1', data, name='idk10')
    idk11 = read('u1', data, name='idk11')
    idk12 = read('u1', data, name='idk12')

    fallback_resource_info_count = read('u1', data, name='fallback_resource_info_count')
    resource_info_count          = read('u2', data, name='resource_info_count'         )
    fallback_resource_info_size  = read('u2', data, name='fallback_resource_info_size' )
    resource_info_size           = read('u2', data, name='resource_info_size'          )
    idk1A                        = read('u2', data, name='idk1A'                       )
    resource_string_list_offset  = read('u4', data, name='resource_string_list_offset' )
    PRINT(f'(@{resource_string_list_offset:04x})')
    
    _resource_info_count         = resource_info_count if resource_info_count else fallback_resource_info_count
    _size = 4

    if   resource_info_size: _size = resource_info_size // 4
    elif fallback_resource_info_size: _size = fallback_resource_info_size // 4
    
    readRSIResourceInfo(data, resource_info_count, _size)
    padout()
    
    padout()

def readRSIResourceInfo(data: BufferedReader, count: int, size: int):
    bytepos = data.tell()
    PRINT('=== Resource Info ===', f'@{bytepos:04x}')
    padin()
    resource_info = []
    for resource in range(count):
        info = []
        for i in range(size):
            info.append(read('u4', data))
        resource_info.append(info)
    PRINT('resource info list', resource_info)

    readRSISpFt(data)

    padout()

def readRSISpFt(data: BufferedReader):
    bytepos = data.tell() # @0070
    PRINT('=== Spike Font ===', f'@{bytepos:04x}')
    padin()
    magic = read('string', data, name='magic', length=4)
    data.seek(bytepos + 0x14) # @0084
    character_count = read('u4', data, name='character_count')
    bb_data_offset  = read('u4', data, name='bb_data_offset')
    PRINT(f'(@{bb_data_offset:04x})')
    padout()
if __name__ == '__main__': main()