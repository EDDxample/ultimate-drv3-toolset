from src.utils import read_string, read_null_terminated_string, read_u32, read_u16, padding
from src.utils import write_null_terminated_string, write_u32, read_u16
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
            # print(subfilename)

            ensure_paths(f'files/1_stx/{filename}/{subfilename}')
            with open(f'files/1_stx/{filename}/{subfilename}', 'wb') as current_file:
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

# CPP version from https://github.com/jpmac26/DRV3-Tools

# First, read from the readahead area into the sequence one byte at a time.
# Then, see if the sequence already exists in the previous 1023 bytes.
# If it does, note its position. Once we encounter a sequence that
# is not duplicated, take the last found duplicate and compress it.
# If we haven't found any duplicate sequences, add the first byte as raw data.
# If we did find a duplicate sequence, and it is adjacent to the readahead area,
# see how many bytes of that sequence can be repeated until we encounter
# a non-duplicate byte or reach the end of the readahead area.
def comp(data) -> bytes:
    raw_size = len(data)
    compressed_data = bytearray(raw_size)
    block = bytearray(16) # block to be analyzed
    pos = 0
    flag = 0
    current_flag_bit = 0
    
    # This repeats until we've stored the final compressed block,
    # after we reach the end of the uncompressed data.
    while True:
        # At the end of each 8-byte block (or the end of the uncompressed data),
        # append the flag and compressed block to the compressed data.
        if current_flag_bit == 8 or pos >= raw_size:
            flag = bit_reverse(flag)
            compressed_data.append(flag)
            compressed_data.append(block)
            block.clear()
            flag = 0
            current_flag_bit = 0
        
        if pos >= raw_size: break

        lookahead_length  = min(raw_size - pos, 65) # hardcoded max length
        lookahead = data[pos : lookahead_length]
        searchback_length = min(pos, 1024)
        window = data[pos - searchback_length, searchback_length + lookahead_length - 1]
        


################################################################################



"""
// First, read from the readahead area into the sequence one byte at a time.
// Then, see if the sequence already exists in the previous 1023 bytes.
// If it does, note its position. Once we encounter a sequence that
// is not duplicated, take the last found duplicate and compress it.
// If we haven't found any duplicate sequences, add the first byte as raw data.
// If we did find a duplicate sequence, and it is adjacent to the readahead area,
// see how many bytes of that sequence can be repeated until we encounter
// a non-duplicate byte or reach the end of the readahead area.
QByteArray spc_cmp(const QByteArray &dec_data) {
    const int dec_size = dec_data.size();
    QByteArray cmp_data;
    cmp_data.reserve(dec_size);
    QByteArray block;
    block.reserve(16);
    int pos = 0;
    int flag = 0;
    char cur_flag_bit = 0;

    // This repeats until we've stored the final compressed block,
    // after we reach the end of the uncompressed data.
    while (true) {
        // At the end of each 8-byte block (or the end of the uncompressed data),
        // append the flag and compressed block to the compressed data.
        if (cur_flag_bit == 8 || pos >= dec_size) {
            flag = bit_reverse(flag);
            cmp_data.append(flag);
            cmp_data.append(block);
            block.clear();
            block.reserve(16);
            flag = 0;
            cur_flag_bit = 0;
        }

        if (pos >= dec_size) break;

        const int lookahead_len = std::min(dec_size - pos, 65);
        const QByteArray lookahead = dec_data.mid(pos, lookahead_len);
        const int searchback_len = std::min(pos, 1024);
        const QByteArray window = dec_data.mid(pos - searchback_len, searchback_len + (lookahead_len - 1));

        // Find the largest matching sequence in the window.
        int s = -1;
        int l = 1;
        QByteArray seq;
        seq.reserve(65);
        seq.append(lookahead.at(0));
        for (l; l <= lookahead_len; ++l) {
            const int last_s = s;
            if (searchback_len < 1) break;

            s = window.lastIndexOf(seq, searchback_len - 1);

            if (s == -1) {
                if (l > 1) {
                    --l;
                    seq.chop(1);
                }
                s = last_s;
                break;
            }

            if (l == lookahead_len) break;
            seq.append(lookahead.at(l));
        }

        // if (seq.size() >= 2)
        if (l >= 2 && s != -1) {
            // We found a duplicate sequence
            ushort repeat_data = 0;
            repeat_data |= 1024 - searchback_len + s;
            repeat_data |= (l - 2) << 10;
            block.append(num_to_bytes<ushort>(repeat_data));
        } else {
            // We found a new raw byte
            flag |= (1 << cur_flag_bit);
            block.append(seq);
        }

        ++cur_flag_bit;
        // Seek forward to the end of the duplicated sequence,
        // in case it continued into the lookahead buffer.
        pos += l;
    }

    return cmp_data;
}
"""