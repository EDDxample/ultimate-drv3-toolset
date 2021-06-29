from font_patcher.src.utils import read, write, readBB, charOffset
from io import BufferedIOBase, BufferedReader, BytesIO

# Format
#
# $0000 $CFH
# $0010 $TXR
# $0030 $RSI
# 
# $0070 SpFt Format:
#   Consists of a series of tables starting with a header with offsets and sizes.
#   Then a table of bits that enable/disable chars from this font.
#   A second table with index shifts for character glyph selection
#   Then a final table with glyphs' bounding boxes pointing to the .srdv


# these offsets may or may not work with other .srd files
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

def write_charset(data: bytearray, new_charset: str) -> bytearray:
    """Overwrites the first two tables from the srd"""

    data = bytearray(data)
    iodata = BytesIO(data) 

    # get table offsets
    iodata.seek(SPFT_OFFSET + 0x1C)
    offset_t1 = read('u4', iodata)
    offset_t2 = read('u4', iodata)

    # current charset + asserts
    current_charset = get_charset(iodata)

    # Note:
    #   These can be acomplished, but that would mean you have to edit
    #   multiple offsets and data lengths accross the whole file... big nope
    assert len(current_charset) >= len(new_charset), 'The new charset cannot have more chars than the current one'
    assert current_charset[-1] >= new_charset[-1],   'The new char ordinals cannot be higher than the current ones' 
    
    
    # first table
    for i in range(len(new_charset)):
        
        # Set bit for current char to 0
        char = current_charset[i]
        byte, bit = charOffset(SPFT_OFFSET + offset_t1, char)
        data[byte] &= ~(1 << bit) & 0xFF

        # Set bit for new char to 1
        char = new_charset[i]
        byte, bit = charOffset(SPFT_OFFSET + offset_t1, char)
        data[byte] |= 1 << bit
    
    # second table
    last_offset = 0
    for i, c in enumerate(new_charset):
        o = ord(c)

        offset = o // 8
        offset = offset - (offset % 4)

        if offset > last_offset:
            last_offset = offset
            data[SPFT_OFFSET + offset_t2 + offset] = i
    
    return data
    