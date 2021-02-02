from src.utils import read_string, read_null_terminated_string, read_u32, write_u32, write_null_terminated_string

# Format:
#   4B   utf-8 magic word = 'STXT'
#   4B   utf-8 lang = 'JPLL'
# 
#   u32  unknown value (usually 1)
#   u32  table offset (usually 32)
#   u32  unknown value (usually 8)
#   u32  table length
# 
#   String Offset Table:
#     u32 string ID
#     u32 string offset
#     null-terminated utf-16 string at said offset


def read(dir):
    lines = []
    with open(dir, 'rb') as obj:
        magic = read_string(obj, 4); #print(magic) # STXT
        lang  = read_string(obj, 4); #print(lang)  # JPLL (JP and US)

        idk0         = read_u32(obj); print(idk0)
        table_offset = read_u32(obj); print('table offset:', table_offset)
        idk2         = read_u32(obj); print(idk2)
        table_len    = read_u32(obj); print('table length:', table_len)

        print()

        for i in range(table_len):
            obj.seek(table_offset + i * 8, 0)

            text_id     = read_u32(obj); #print('text ID:', text_id)
            text_offset = read_u32(obj); #print('text offset:', text_offset, f'{text_offset:x}') # 4c4

            obj.seek(text_offset, 0)
            text = read_null_terminated_string(obj); #print(text_id, text)
            lines.append(text)
    return lines


def write(lines):
    dataout =  b'\x53\x54\x58\x54'   # STXT
    dataout += b'\x4A\x50\x4C\x4C'   # JPLL
    dataout += b'\x01\x00\x00\x00'   # unknown value: 1
    dataout += b'\x20\x00\x00\x00'   # table offset: 32
    dataout += b'\x08\x00\x00\x00'   # unknown value: 8
    dataout += write_u32(len(lines)) # table length

    dataout += b'\x00\x00\x00\x00\x00\x00\x00\x00' # filler to 32

    index_table_bytesize = len(lines) * 4 * 2 # N x 2 x u32 numbers
    string_table = b''
    string_set = {}


    for i, line in enumerate(lines):
        line = adapt_to_font(line)
        dataout += write_u32(i) # string ID
        if line in string_set:
            dataout += write_u32(string_set[line]) # string offset
        else:
            string_set[line] = 32 + index_table_bytesize + len(string_table)
            dataout += write_u32(32 + index_table_bytesize + len(string_table)) # string offset
            string_table += write_null_terminated_string(line)

    dataout += string_table

    return dataout
    

# same used by https://twitter.com/v3ducciones
def adapt_to_font(line: str):
    return line.replace('¡', '&').replace('¿', '$').replace('ñ', 'û').replace('á', 'à').replace('í', 'î').replace('ó', 'ô').replace('ú', 'ù')
    
