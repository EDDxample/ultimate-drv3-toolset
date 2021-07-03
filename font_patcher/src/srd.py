from font_patcher.src.utils import read, textureSizeToBytes, write, readBB, charOffset, writeBB
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
    
    # current_charset >= new_charset
    validate_charset(iodata, new_charset)
    
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

def write_texture_size(data: bytearray, width: int, height: int):
    data = bytearray(data)
    for i, byte in enumerate(textureSizeToBytes(width, height)):
        data[TXR_OFFSET + 0x16 + i] = byte
    return data

def write_charBBs(data: bytearray, charBBs):
    data = bytearray(data)

    offset_t3 = read('u4', BytesIO(data[SPFT_OFFSET + 0x18 : SPFT_OFFSET + 0x18 + 4]))
    
    for i, item in enumerate(charBBs):
        bbx, bby, w, h = item[3] # BB data
        left, right, top = 0, 0, 0
        for ii, byte in enumerate(writeBB(bbx, bby, w, h, left, right, top)):
            data[SPFT_OFFSET + offset_t3 + i * 8 + ii] = byte
    return data

def validate_charset(current_data: BufferedReader, new_charset: str):
    """
        The new charset cannot be longer than the one in the base file.
        
        This can be solved by using another base file with more chars or by
        updating the data offsets and lengths that would be affected by increasing its size.

        I'm too lazy to solve that right now. ✌️
    """
    current_charset = get_charset(current_data)
    assert len(current_charset) >= len(new_charset), 'The new charset cannot have more chars than the current one'
    assert current_charset[-1] >= new_charset[-1],   'The new char ordinals cannot be higher than the current ones' 
