from src.utils import read_string, read_null_terminated_string, read_u32, read_u16, padding
from src.utils import write_null_terminated_string, write_u32, write_u16
from src.utils import ensure_paths

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


def extract(filename):
    lines = []
    with open(f'files/0_spc/{filename}.spc', 'rb') as obj:
        magic = read_string(obj, 4); #print(magic) # CPS.
        if magic != 'CPS.': print(f'{filename}\'s magic isn\'t CPS.', magic)
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

            subfilename = read_string(obj, name_length - 1)
            padding(obj, 1 + name_padding) # null terminated + padding

            file_data = decomp(obj.read(compressed_size))
            padding(obj, file_padding) # null terminated + padding
            print(subfilename)


            recompressed_size = len(comp(file_data))
            print('compressed size:', compressed_size)
            print('decompressed size:', decompressed_size)
            print('recompressed size:', recompressed_size, '(EDD)')
            print()

            ensure_paths(f'files/1_stx/{filename}/{subfilename}')
            with open(f'files/1_stx/{filename}/{subfilename}', 'wb') as current_file:
                current_file.write(file_data)
    

def write(filename, subfiles):
    dataout =  bytes('CPS.', 'utf-8')
    dataout += b'\x00' * 36 # padding
    file_count = len(subfiles)
    dataout += write_u32(file_count)
    dataout += write_u32(0) # idk
    dataout += b'\x00' * 16 # padding
    dataout += bytes('Root', 'utf-8')
    dataout += b'\x00' * 12 # padding

    for subfilename in subfiles:
        file_data = open(f'files/4_stx/{filename}/{subfilename}', 'rb').read()
        dataout += b'\x02\x00\x01\x00' # compression flag + idk
        comp_data = comp(file_data)
        comp_len = len(comp_data)
        raw_len = len(file_data)
        name_len = len(subfilename)

        dataout += write_u32(comp_len)
        dataout += write_u32(raw_len)
        dataout += write_u32(name_len)
        dataout += b'\x00' * 16 # padding

        file_padding = (16 - comp_len % 16) % 16
        name_padding = (16 - name_len % 16) % 16

        dataout += bytes(subfilename, 'utf-8')
        dataout += b'\x00' * name_padding

        dataout += comp_data
        dataout += b'\x00' * file_padding
    
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
        # Count    -> x + 2
        # Offset -> y (from the beginning of a 1024-byte sliding window)
        else:
            b = (data[p + 1] << 8) | data[p]
            p += 2
            
            count    = (b >> 10) + 2
            offset = b & 0b1111111111
            
            for i in range(count):
                res.append(res[offset - 1024])
        
        flag >>= 1
    
    return res

################################################################################
# C# version from https://github.com/jpmac26/DRV3-Sharp

def comp(data: bytes) -> bytes: 
    data_len = len(data)
    out = bytearray() # compressed result container

    # keep trak of the current compression state
    pos  = 0     # current reading position in uncompressed data
    flag = 0     # describes which parts of the current block are compressed/uncompressed
    flag_bit = 0
    block = bytearray() # current block of data that finished being compressed

    # This repeats until we've stored the final compressed block,
    # after we reach the end of the uncompressed data.
    while True:
        # At the end of each compressed block (or the end of the uncompressed data),
        # append the flag and block to the compressed data.
        if flag_bit == 8 or pos >= data_len:
            flag = bit_reverse(flag & 0xFF) & 0xFF
            out.append(flag)
            out.extend(block)

            if pos >= data_len: break

            # prep for next block
            flag = 0
            flag_bit = 0
            block = bytearray()
        
        # Keep track of the current sequence of data we're trying to compress
        seq_len = 1
        found_at = -1
        searchback_len = min(pos, 1024)

        # When we start this loop, we've just started 
        # looking for a new sequence to compress
        while seq_len <= 65:
            # The sliding window is a slice into the uncompressed data that we search for duplicate instances of the sequence
            # The readahead length MUST be at least one byte shorter than the current sequence length
            readahead_len = min(seq_len - 1, data_len - pos)
            window = data[pos - searchback_len : pos + readahead_len]

            # If we've reached the end of the file, don't try to compress any more data, just use what we've got
            # NOTE: We do NOT need to backup/restore foundAt here because it hasn't been touched yet this iteration!
            if pos + seq_len > data_len:
                seq_len -= 1
                break

            seq = data[pos : pos + seq_len]
            last_found_at = found_at        # back up last found value
            found_at = window.rfind(seq)

            # If we fail to find a match, then try and restore the last match we found,
            # which must be one size smaller than the current.
            if found_at == -1:
                found_at = last_found_at
                seq_len -= 1
                break

            seq_len += 1 # increment here bc python

        # If we exit the above loop due to seqLen exceeding 65 then we must decrement seqLen
        if seq_len > 65: seq_len = 65

        
        if seq_len >= 2 and found_at != -1:
            # The sequence was inside the previous window
            repeat_data = 0
            repeat_data |= (1024 - searchback_len + found_at) & 0xFFFF # first 10-12 bits
            repeat_data |= ((seq_len - 2) << 10) & 0xFFFF
            block.extend(write_u16(repeat_data))
        else:
            # The sequence is new, add that byte and move on
            flag |= (1 << flag_bit)
            block.append(data[pos])
        
        # Increment the current read position by the size of
        # whatever sequence we found (even if it's non-compressable)
        pos += max(1, seq_len)
        flag_bit += 1
    
    return out

################################################################################