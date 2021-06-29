from struct import pack, unpack
import os, errno
from io import BufferedReader
from typing import Any

def padding(data: BufferedReader, length: int):
    data.seek(length, 1)

def read(mode: str, data: BufferedReader, bigendian: bool = False, length: int = 0, encoding: str = 'utf-8'):
    endianness = '>' if bigendian else '<'
    numeric_datatypes = {
        'u1': lambda data: unpack(endianness + 'B', data.read(1))[0],
        'u2': lambda data: unpack(endianness + 'H', data.read(2))[0],
        'u4': lambda data: unpack(endianness + 'I', data.read(4))[0],
        'charbb': readBB,
    }
    
    if mode in numeric_datatypes:
        return numeric_datatypes[mode](data)

    elif mode == 'string' and length > 0:
        # usually utf-8
        return data.read(length).decode(encoding)
    
    elif mode == 'nullstring':
        # null-terminated string, usually utf-16
        out = bytes()
        bytes_per_char = 2 if encoding == 'utf-16' else 1
        while True:
            char = data.read(bytes_per_char)
            null_char = b'\x00' * bytes_per_char

            if char == null_char or not char:
                return out.decode(encoding)
            else: out += char

def write(mode: str, data: Any, bigendian: bool = False, encoding: str = 'utf-8'):
    endianness = '>' if bigendian else '<'
    numeric_datatypes = {
        'u1': lambda n: pack(endianness + 'B', n),
        'u2': lambda n: pack(endianness + 'H', n),
        'u4': lambda n: pack(endianness + 'I', n),
    }
    
    if mode in numeric_datatypes:
        return numeric_datatypes[mode](data)

    elif mode == 'string' and type(data) == 'str':
        # usually utf-8
        return data.encode(encoding)
        
    elif mode == 'nullstring':
        # hopefully utf-16
        assert encoding == 'utf-16', f'ERROR, nulstring with encoding {encoding} not implemented yet'

        # remove endianness mark 0xFFFE
        return data.encode(encoding)[2:] + b'\x00\x00'

def abc2xy(a, b, c):
    b1 = b & 0xF
    b2 = (b >> 4) & 0xF
    
    x = (b1 << 8) | a
    y = (c << 4) | b2
    return x, y

def xy2abc(x, y):
    a = x & 0xFF
    c = (y >> 4) & 0xFF
    
    b1 = (x >> 8) & 0xF
    b2 = y & 0xF
    b = (b2 << 4) | b1
    return a, b, c

def textureSizeToBytes(width, height):
    return pack('<H', width) + pack('<H', height)

def readBB(data: BufferedReader):
    a, b, c, w, h, left, right, top = data.read(8)
    x, y = abc2xy(a, b, c)
    return x, y, w, h, left, right, top

def writeBB(x, y, w, h, left, right, top) -> bytes:
    a, b, c = xy2abc(x, y)
    out = bytes([a, b, c, w, h, left, right, top])
    # print(''.join(f'{x:02X} ' for x in out))
    # print((x, y, w, h, left, right, top))
    # print(readBB(BytesIO(out)))
    # print()
    return out

def charOffset(flagListOffset: int, char: str):
    ordinal = ord(char)
    
    file_offset = flagListOffset + (ordinal >> 3)
    bit_pos = ordinal & 0b111
    # print(char, ordinal, f'${file_offset:04x}', bit_pos)
    return file_offset, bit_pos

def ensure_paths(filename):
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise