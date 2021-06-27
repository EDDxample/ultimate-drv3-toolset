from src.utils import read_string, read_null_terminated_string, read_u32, read_u16, read_ubyte, padding
from src.utils import write_null_terminated_string, write_u32, write_u16, write_ubyte
from src.utils import ensure_paths
from PIL import Image
import os, cv2, numpy as np


srdv_image: Image = None

def read(filename):
    global srdv_image

    with open(f'files/srd/0_font/{filename}.srd', 'rb') as f:
        filength = os.stat(f'files/srd/0_font/{filename}.srd').st_size
        while f.tell() < filength:
            print('=================================')
            magic       = read_string(f, 4);           print('Magic', magic)
            data_len    = read_u32(f, bigendian=True); print('Data Length', data_len)
            subdata_len = read_u32(f, bigendian=True); print('Sub Data Length', subdata_len)
            idk00       = read_u32(f, bigendian=True); print('idk00', idk00)

            if   magic == '$CFH': pass


            elif magic == '$TXR':
                idk10          = read_u32(f);               print('idk10', idk10)
                swizzle        = read_u16(f);               print('Swizzle', swizzle)
                print(f'= width offset = ${f.tell():04x}')
                display_width  = read_u16(f);               print('Display Width', display_width)
                display_height = read_u16(f);               print('Display Height', display_height)
                scan_line      = read_u16(f);               print('Scan Line', scan_line)
                pic_format     = get_format(read_ubyte(f)); print('Pic Format', pic_format)
                idk1D          = read_ubyte(f);             print('idk1D', idk1D)
                palette        = read_ubyte(f);             print('Palette', idk1D)
                pallete_id     = read_ubyte(f);             print('Palette ID', idk1D)

                srdv_image = get_img(f'files/srd/0_font/{filename}.srdv', display_width, display_height)
                
                
            elif magic == '$RSI':
                RSI_header_pos = f.tell(); print('RSI Header Pos', RSI_header_pos)

                idk10 = read_ubyte(f); print('idk10', idk10)
                idk11 = read_ubyte(f); print('idk11', idk11)
                idk12 = read_ubyte(f); print('idk12', idk12)

                fallback_resource_info_count = read_ubyte(f); print('Fallback Resource Info Count', fallback_resource_info_count)
                resource_info_count          = read_u16(f);   print('Resource Info Count', resource_info_count)
                fallback_resource_info_size  = read_u16(f);   print('Fallback Resource Info Size', fallback_resource_info_size)
                resource_info_size           = read_u16(f);   print('Resource Info Size', resource_info_size)
                idk1A                        = read_u16(f);   print('idk1A', idk1A)
                resource_string_list_offset  = read_u32(f);   print('Resource String List Offset', resource_string_list_offset)

                _resource_info_count         = resource_info_count if resource_info_count else fallback_resource_info_count

                _size = 4
                if   resource_info_size:
                    _size = resource_info_size // 4
                elif fallback_resource_info_size:
                    _size = fallback_resource_info_size // 4

                resource_info = []
                print(f'Resource Info Index ${f.tell():04x}')
                for r in range(resource_info_count):
                    info = []
                    for i in range(_size):
                        info.append(read_u32(f))
                    resource_info.append(info)
                print('Resource Info:', resource_info)
                

                # SPIKE FONT FILE

                # read resource data
                resource_data_len = resource_string_list_offset - (f.tell() - RSI_header_pos)
                print(f'Resource Data Index ${f.tell():04x}') # $0070
                print('Resource Data Length', resource_data_len)
                # resource_data = f.read(resource_data_len)
                # padding(f, resource_data_len)


                # BB DATA

                print('----------------------------------- BB DATA')

                f.seek(0x84, 0)
                character_count = read_u32(f)
                print('Character Count', character_count)
                bb_offset = read_u32(f) # BB Offset Index $0088 = $4004
                print(f'BB Data Offset ${bb_offset:04x} / {bb_offset} (relative to $0070, start of SpFt)', )

                f.seek(0x70 + bb_offset, 0)
                print(f'BB Data Index ${f.tell():04x}') # $4074
                get_bb_positions(f, character_count, filename)
                return
                print(f'Afer BB table Index ${f.tell():04x}') # $4242

                print('\n----------------------------------- BB DATA END')

                # read resource strings
                # f.seek(0x457e, 0)
                # print(f'Resource String Index ${f.tell():04x}') # $457e
                # resource_string_list = []
                # while (f.tell() - RSI_header_pos) < data_len:
                #     resource_string_list.append(read_null_terminated_string(f, 'shift-jis'))
                # print(resource_string_list)

                print('----------------------------------- SRDV DATA')
                # SRDV data
                # get_texture_data(filename, resource_info[0])
                print('\n----------------------------------- SRDV DATA END')



            padding(f, (16 - data_len % 16) % 16) # blocks are aligned to 16 bytes

def get_format(i):
    if  i == 0x00: return 'Unknown'
    if  i == 0x01: return 'ARGB8888'
    if  i == 0x02: return 'BGR565'
    if  i == 0x05: return 'BGRA4444'
    if  i == 0x0F: return 'DXT1RGB'
    if  i == 0x11: return 'DXT5'
    if  i == 0x14: return 'BC5'
    if  i == 0x16: return 'BC4'
    if  i == 0x1A: return 'Indexed8'
    if  i == 0x1C: return 'BPTC'
    return 'IDK'


def get_bb_positions(f, chars, filename):
    global srdv_image
    # with open('positions.txt', 'w') as out:

    for i in range(chars):
        byteA = read_ubyte(f)
        byteB = read_ubyte(f)
        byteC = read_ubyte(f)

        b1 = byteB & 0xF
        b2 = (byteB >> 4) & 0xF
        # print(f'\nBytes: {byteA:02x} {byteB:02x} {byteC:02x}\nDecoded: {b1:01x}{byteA:02x}, {byteC:02x}{b2:01x}')
        
        posX = (b1 << 8) | byteA
        posY = (byteC << 4) | b2
        # print('BB pos:', posX, posY)
        char_width = read_ubyte(f)
        char_height = read_ubyte(f)

        # IDKs
        a = read_ubyte(f)
        b = read_ubyte(f)
        c = read_ubyte(f)
        
        ensure_paths(f'files/srd/1_pictures/{filename}/{i}_{posY}_{a}_{b}_{c}.png')
        srdv_image.crop((posX, posY, posX+char_width, posY+char_height)).save(f'files/srd/1_pictures/{filename}/{i}_{posY}_{a}_{b}_{c}.png')
        # print('BB size:', char_width, char_height)
        # out.write(f'{posX} {posY} {char_width} {char_height} {a} {b} {c}\n')


def get_texture_data(filename, resource_info):
    external_file_type = resource_info[0] >> 28
    offset = resource_info[0] & 0x1FFFFFFF
    data_length = resource_info[1]
    print(f'{resource_info[0]:04x}')
    print(f'data length: {data_length}')

    if external_file_type == 0x004:
        with open(f'files/srd/{filename}v', 'rb') as extf:
            data = extf.read(data_length)


def get_img(path, width, height):
    data = open(path, 'rb')
    srdv_image = Image.frombytes('L', (width, height), data.read(), 'bcn', 4)
    data.close()
    return srdv_image
