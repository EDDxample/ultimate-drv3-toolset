from font_patcher.src.utils import read, write, readBB
from io import BufferedReader

# Format
#
# $0000 $CFH
# $0010 $TXR
# $0030 $RSI
# $0070 SpFt


# these offsets may or may not work with other .stx file
TXR_OFFSET  = 0x10
RSI_OFFSET  = 0x30
SPFT_OFFSET = 0x70


def get_charset(fontfile: BufferedReader):
    """Returns the chars that can be used by this fontfile"""
    
    charset = ''

    fontfile.seek(SPFT_OFFSET + 0x08)
    bitflag_list_length = read('u4', fontfile) // 8

    # bit flag list
    fontfile.seek(SPFT_OFFSET + 0x2C)
    
    for byte in range(bitflag_list_length):
        current_byte = read('u1', fontfile)

        for bit in range(8):
            if (current_byte >> bit) & 1 == 1:
                ordinal = byte * 8 + bit
                charset += chr(ordinal)
    
    return charset

def get_fontname(fontfile: BufferedReader):
    """Reads the name of the font used in this fontfile"""

    fontfile.seek(SPFT_OFFSET + 0x10)
    font_name_offset = read('u4', fontfile)

    fontfile.seek(SPFT_OFFSET + font_name_offset)
    fontname = read('nullstring', fontfile, encoding='utf-16')

    return fontname

def get_charBBs(fontfile: BufferedReader):
    """Returns the glyphs' bounding boxes"""

    charBBs = []

    fontfile.seek(SPFT_OFFSET + 0x14)
    char_count     = read('u4', fontfile)
    bb_data_offset = read('u4', fontfile)

    # BB data table
    fontfile.seek(SPFT_OFFSET + bb_data_offset)

    for i in range(char_count):
        charBBs.append(read('charbb', fontfile)) # x, y, w, h, a, b, c
    
    return charBBs

    