import struct
from struct import pack, unpack
import os, errno
from io import BufferedReader
from typing import Any
from googletrans import Translator

STEP_0_PATH = 'translation_pipeline/pipeline/0_input_SPC'
STEP_1_PATH = 'translation_pipeline/pipeline/1_extracted_STX'
STEP_2_PATH = 'translation_pipeline/pipeline/2_extracted_dialogues'
STEP_3_PATH = 'translation_pipeline/pipeline/3_merged_dialogues'
STEP_4_PATH = 'translation_pipeline/pipeline/4_output_STX'
STEP_5_PATH = 'translation_pipeline/pipeline/5_output_SPC'

def padding(data: BufferedReader, length: int):
    data.seek(length, 1)

def read(mode: str, data: BufferedReader, bigendian: bool = False, length: int = 0, encoding: str = 'utf-8'):
    endianness = '>' if bigendian else '<'
    numeric_datatypes = {
        'u1': lambda data: unpack(endianness + 'B', data.read(1))[0],
        'u2': lambda data: unpack(endianness + 'H', data.read(2))[0],
        'u4': lambda data: unpack(endianness + 'I', data.read(4))[0],
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