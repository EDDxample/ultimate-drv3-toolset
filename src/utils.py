import struct
import os, errno
from io import BufferedReader
from googletrans import Translator

def padding(data: BufferedReader, length):
    data.seek(length, 1)

def read_string(data: BufferedReader, length, encoding='utf-8'):
    return data.read(length).decode(encoding)
    
def read_null_terminated_string(data: BufferedReader, encoding='utf-16'):
    string = bytes()
    while True:
        if encoding == 'utf-16':
            char = data.read(2)
            if char == b'\x00\x00' or not char:
                return string.decode(encoding)
            else: string += char
        else:
            char = data.read(1)
            if char == b'\x00' or not char:
                return string.decode(encoding)
            else: string += char
            

def read_u32(data: BufferedReader, bigendian=False):
    endianness = '>' if bigendian else '<'
    return struct.unpack(endianness + 'I', data.read(4))[0]

def read_u16(data: BufferedReader, bigendian=False):
    endianness = '>' if bigendian else '<'
    return struct.unpack(endianness + 'H', data.read(2))[0]

def read_ubyte(data: BufferedReader, bigendian=False):
    endianness = '>' if bigendian else '<'
    return struct.unpack(endianness + 'B', data.read(1))[0]

def write_null_terminated_string(string: str) -> bytes:
    return string.encode('utf-16')[2:] + b'\x00\x00' # remove endianness mark 0xFFFE

def write_u32(n: int, bigendian=False) -> bytes:
    endianness = '>' if bigendian else '<'
    return struct.pack(endianness + 'I', n)

def write_u16(n: int, bigendian=False) -> bytes:
    endianness = '>' if bigendian else '<'
    return struct.pack(endianness + 'H', n)

def write_ubyte(n: int, bigendian=False):
    endianness = '>' if bigendian else '<'
    return struct.pack(endianness + 'B', n)



def ensure_paths(filename):
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise


def translate(text):
    return text
    try:
        translator = Translator()
        translation = translator.translate(text, dest='es')

        return translation.text
    except:
        print('translate failed!')
        return text