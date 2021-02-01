from src.utils import read_string, read_null_terminated_string, read_u32, read_u16, padding
from src.utils import write_null_terminated_string, write_u32, read_u16

# SPC Format:
#    4B  utf-8 magic word = 'CPS.'
#   36B  x24  padding
#   u32  file count
#   u32  unknown
#   16B  x10  padding
#    4B  utf-8 table magic word = 'Root'
#   12B  padding
#   
#   File Table:
#      u16  cmp flag
#      u16  unknown
#      u32  cmp size 
#      u32  dec size
#      u32  name length
#   
#   


def read(dir):
    lines = []
    with open(dir, 'rb') as obj:
        magic = read_string(obj, 4); #print(magic) # CPS.
        padding(obj, 36)
        file_count = read_u32(obj)
        idk0 = read_u32(obj)
        padding(obj, 16)
        table_magic = read_string(obj, 4)
        padding(obj, 12)

        for file_i in range(file_count):
            compression_flag = read_u16(obj)
            idk0 = read_u16(obj)
            compressed_size = read_u32(obj)
            decompressed_size = read_u32(obj)
            name_length = read_u32(obj) + 1 # null terminated
            padding(obj, 16)

            # alligned to 16B blocks
            file_padding = (16 - compressed_size % 16) % 16
            name_padding = (16 - name_length % 16) % 16

            filename = read_string(obj, name_length - 1)
            padding(obj, 1 + name_padding) # null terminated + padding

            file_data = decomp(obj.read(compressed_size))
            padding(obj, file_padding) # null terminated + padding
            print(filename)

            with open('output/stx/' + filename, 'wb') as current_file:
                current_file.write(file_data)





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
        dataout += write_u32(i) # string ID
        if line in string_set:
            dataout += write_u32(string_set[line]) # string offset
        else:
            string_set[line] = 32 + index_table_bytesize + len(string_table)
            dataout += write_u32(32 + index_table_bytesize + len(string_table)) # string offset
            string_table += write_null_terminated_string(line)

    dataout += string_table

    return dataout
    



    
# IMPORTS ################################################################################

# From: https://github.com/yukinogatari/Danganronpa-Tools

def bit_reverse(b):
  return (b * 0x0202020202 & 0x010884422010) % 1023


# This is the compression scheme used for individual files in an spc archive.
def decomp(data) -> bytes:
  
  data = bytearray(data)
  res = bytearray()
  
  flag = 1
  p = 0
  
  while p < len(data):
    
    # We use an 8-bit flag to determine whether something's raw data
    # or if we pull from the buffer, going from most to least significant bit.
    # Reverse the bit order to make it easier to work with.
    if flag == 1:
      flag = 0x100 | bit_reverse(data[p])
      p += 1
    
    if p >= len(data):
      break
    
    # Raw byte.
    if flag & 1:
      res.append(data[p])
      p += 1
    
    # Read from the buffer.
    # xxxxxxyy yyyyyyyy
    # Count  -> x + 2
    # Offset -> y (from the beginning of a 1024-byte sliding window)
    else:
      b = (data[p + 1] << 8) | data[p]
      p += 2
      
      count  = (b >> 10) + 2
      offset = b & 0b1111111111
      
      for i in range(count):
        res.append(res[offset - 1024])
    
    flag >>= 1
  
  return res

################################################################################