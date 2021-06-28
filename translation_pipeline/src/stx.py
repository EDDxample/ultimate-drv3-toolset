from translation_pipeline.src.utils import read, write, ensure_paths, padding, translate

# Format:
#   4B   utf-8 magic word = 'STXT'
#   4B   utf-8 lang = 'JPLL'
# 
#   u4  unknown value (usually 1)
#   u4  table offset (usually 32)
#   u4  unknown value (usually 8)
#   u4  table length
# 
#   String Offset Table:
#     u4 string ID
#     u4 string offset
#     null-terminated utf-16 string at said offset


def extract(file):
    lines = []
    with open(file, 'rb') as obj:
        magic = read('string', obj, length=4);  #print(magic) # STXT
        lang  = read('string', obj, length=4);  #print(lang)  # JPLL (JP and US)

        idk0         = read('u4', obj); #print(idk0)
        table_offset = read('u4', obj); #print('table offset:', table_offset)
        idk2         = read('u4', obj); #print(idk2)
        table_len    = read('u4', obj); #print('table length:', table_len)

        for i in range(table_len):
            obj.seek(table_offset + i * 8, 0)

            text_id     = read('u4', obj); #print('text ID:', text_id)
            text_offset = read('u4', obj); #print('text offset:', text_offset, f'{text_offset:x}') # 4c4

            obj.seek(text_offset, 0)
            text = read('nullstring', obj, encoding='utf-16'); #print(text_id, text)
            lines.append(text)
    
    joint_lines = '\n\n'.join(lines)
    # print('batches:', len(lines))
    # print('lines length:', len(joint_lines))
    batch_count = len(joint_lines) // 4000 + 1
    batch_size  = len(lines) // batch_count + 1

    # print('batch count:', batch_count)
    # print('batch size:', batch_size)

    translation = ''

    if batch_count == 1:
        translation = translate(joint_lines)
        return lines, translation.split('\n\n')
        
    else:
        for i in range(batch_count):
            batch_from = i * batch_size
            batch_to   = min(batch_from + batch_size, len(lines))
            # print(f'batch from {batch_from} to {batch_to}')
            batch = lines[batch_from:batch_to]
            translation += translate('\n\n'.join(batch)) + '\n\n'
        return lines, translation.split('\n\n')[:-1]


def repack(lines):
    dataout =  b'\x53\x54\x58\x54'   # STXT
    dataout += b'\x4A\x50\x4C\x4C'   # JPLL
    dataout += b'\x01\x00\x00\x00'   # unknown value: 1
    dataout += b'\x20\x00\x00\x00'   # table offset: 32
    dataout += b'\x08\x00\x00\x00'   # unknown value: 8
    dataout += write('u4', len(lines)) # table length

    dataout += b'\x00\x00\x00\x00\x00\x00\x00\x00' # filler to 32

    index_table_bytesize = len(lines) * 4 * 2 # N x 2 x u32 numbers
    string_table = b''
    string_set = {}


    for i, line in enumerate(lines):
        # line = adapt_to_font(line)
        dataout += write('u4', i) # string ID
        if line in string_set:
            dataout += write('u4', string_set[line]) # string offset
        else:
            string_set[line] = 32 + index_table_bytesize + len(string_table)
            dataout += write('u4', 32 + index_table_bytesize + len(string_table)) # string offset
            string_table += write('nullstring', line, encoding='utf-16')

    dataout += string_table

    return dataout
    

# same used by https://twitter.com/v3ducciones
def adapt_to_font(line: str):
    return line.replace('¡', '&').replace('¿', '$').replace('ñ', 'û').replace('á', 'à').replace('í', 'î').replace('ó', 'ô').replace('ú', 'ù')

def adapt_from_font(line: str):
    return line.replace('&', '¡').replace('$', '¿').replace('û', 'ñ').replace('à', 'á').replace('î', 'í').replace('ô', 'ó').replace('ù', 'ú')
    
