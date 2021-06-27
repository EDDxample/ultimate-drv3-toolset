import cv2, numpy as np, struct, math
from PIL import Image

# img = np.zeros((101, 4096, 4))
# img = cv2.imread('files/pics/db_font00_US_win.bmp.png', cv2.IMREAD_UNCHANGED)

# with open('positions.txt', 'r') as f:
#     for i, line in enumerate(f.readlines()):
#         try:
#             x, y, w, h, a, b, c = list(map(int, line.strip().split(' ')))
#             print(f'{x:04} {y:02}, {w:02} {h:02}, {a} {b} {c}')
#             color = (255,0,0,255) if i % 2 else (0, 255, 0, 255)

#             cv2.rectangle(img, (x, y), (x + w, y + h), color=color, thickness=1)
#         except: pass

# test = cv2.imwrite('test.png', img)


""" BC4 FORMAT

2x 1byte ENDPOINTS 0 - 255

"""
def Compact1By1(x):
    x &= 0x55555555 # x = -f-e -d-c -b-a -9-8 -7-6 -5-4 -3-2 -1-0
    x = (x ^ (x >> 1)) & 0x33333333 # x = --fe --dc --ba --98 --76 --54 --32 --10
    x = (x ^ (x >> 2)) & 0x0f0f0f0f # x = ---- fedc ---- ba98 ---- 7654 ---- 3210
    x = (x ^ (x >> 4)) & 0x00ff00ff # x = ---- ---- fedc ba98 ---- ---- 7654 3210
    x = (x ^ (x >> 8)) & 0x0000ffff # x = ---- ---- ---- ---- fedc ba98 7654 3210
    return x
def DecodeMorton2X(code):
    return Compact1By1(code >> 0)
def DecodeMorton2Y(code):
    return Compact1By1(code >> 1)
def PostProcessMortonUnswizzle(data, width, height, bytespp):
    data = bytearray(data)
    return data
    unswizzled = bytearray(len(data))
    
    width = int(width)
    height = int(height)
    
    min = width if width < height else height
    k = int(math.log(min, 2))
    
    for i in range(width * height):
        
        if height < width:
            j = i >> (2 * k) << (2 * k) \
                | (DecodeMorton2Y(i) & (min - 1)) << k \
                | (DecodeMorton2X(i) & (min - 1)) << 0
            
            x = j / height
            y = j % height
        
        else:
            j = i >> (2 * k) << (2 * k) \
                | (DecodeMorton2X(i) & (min - 1)) << k \
                | (DecodeMorton2Y(i) & (min - 1)) << 0
            
            x = j % width
            y = j / width
        
        p = int(((y * width) + x) * bytespp)
        unswizzled[p : p + bytespp] = data[i * bytespp : (i + 1) * bytespp]
    
    return unswizzled


def bc4_attempt():

    pic = np.zeros((101, 4096, 4))
    pic_x = 0
    pic_y = 0
    pic_w = 4096
    pic_h = 101
    with open('files/srd/0_font/fr.srdv', 'rb') as data:
        # Display Width 4096
        # Display Height 101
        raw_data = data.read()
        img_data = raw_data
        # print(len(img_data))
        for block in range(0, len(img_data), 8):

            A, B, *idx = img_data[block:block+8]
            


            # if A<=B, the last 2 items are left for black and white
            palette_length = 8 if A > B else 6
            palette = [
                    A, B,
                    (6 * A + 1 * B) // 7,
                    (5 * A + 2 * B) // 7,
                    (4 * A + 3 * B) // 7,
                    (3 * A + 4 * B) // 7,
                    (2 * A + 5 * B) // 7,
                    (1 * A + 6 * B) // 7,
                ] if A > B else [
                    A, B,
                    (4 * A + 1 * B) // 5,
                    (3 * A + 2 * B) // 5,
                    (2 * A + 3 * B) // 5,
                    (1 * A + 4 * B) // 5,
                    0, 255
                ]         

            # image
            # the indices are stored like this:
            # h g f e d c b a
            # p o n m l k j i
            for row in range(2):
                bo = row * 3 # byte offset
                ro = row * 2 # row offset
                idx_array = idx[0 + bo] | (idx[1 + bo] << 8) | (idx[2 + bo] << 16)

                for i in range(8):
                    palette_id = 7 & (idx_array >> (3 * i))
                    color = palette[palette_id]
                    block_x = i % 4
                    block_y = i // 4 + ro
                    

                    if pic_y+block_y < pic_h and pic_x+block_x < pic_w:
                        pic[pic_y+block_y, pic_x+block_x] = [color,color,color,255]
            
            # for i in range(8):
            #     palette_id = 7 & (indices_long_B >> (3 * i))
            #     color = palette[palette_id]
            #     block_x = (i + 8) % 4
            #     block_y = (i + 8) // 4
                
            #     if pic_x+block_x < pic_w and pic_y+3-block_y < pic_h:
            #         pic[pic_y+3-block_y, pic_x+block_x] = [color,color,color,255]
                
    
            # update pic pos
            pic_x += 4
            if pic_x >= pic_w:
                pic_x = 0
                pic_y += 4
            if pic_y >= pic_h: break
            

        # cv2.imshow('textureread.png', pic)
        # cv2.waitKey()
        cv2.imwrite('textureread.png', pic)


def bc4_idk_anymore():
    filee = 'us'
    filee = 'v3_font01_8'
    # filee = 'v3_font07'
    with open(f'files/srd/0_font/{filee}.srd', 'rb') as srd:

        srd.seek(0x0026)
        width  = read_u16(srd)
        height = read_u16(srd)
        with open(f'files/srd/0_font/{filee}.srdv', 'rb') as data:
            pic = []
            pic = Image.frombytes('L', (width, height), data.read(), 'bcn', 4)
            pic.save('idk.png')

# bc4_attempt()

import struct
from io import BufferedReader

def read_u32(data): return struct.unpack('<I', data.read(4))[0]
def read_u16(data): return struct.unpack('<H', data.read(2))[0]
def read_ubyte(data): return struct.unpack('<B', data.read(1))[0]
def write_u32(n) -> bytes: return struct.pack('<I', n)
def write_u16(n) -> bytes: return struct.pack('<H', n)
def write_ubyte(n) -> bytes: return struct.pack('<B', n)
def read_null_terminated_string(data: BufferedReader, encoding='utf-16'):
    string = bytes()
    while True:
        if encoding == 'utf-16':
            char = data.read(2)
            if char == b'\x00\x00' or not char:
                return string.decode(encoding)
            else: string += char
        else:
            char = data.read(1)
            if char == b'\x00' or not char:
                return string.decode(encoding)
            else: string += char

def read_stuff():
    target = 119
    with open('files/srd/0_font/v3_font01_8.srd', 'rb') as srd:
        srd.seek(0x0000) # $CFH
        srd.seek(0x0010) # $TXR
        srd.seek(0x0016, 1)
        width  = read_u16(srd)
        height = read_u16(srd)
        print(f'{width} {height}')
        
        srd.seek(0x0030) # $RSI
        srd.seek(0x0013, 1)
        mipmapCount = read_ubyte(srd)
        read_u32(srd)
        read_u32(srd)

        str_offset = read_u32(srd)
        print(f'str offset ${str_offset:04x}')

        for i in range(mipmapCount):
            for j in range(4):
                read_u32(srd)

        print(f'${srd.tell():04x}')
        srd.seek(0x0040 + str_offset)

        print(f'${srd.tell():04x}')
        
        print(read_null_terminated_string(srd, 'utf-8'))

        srd.seek(0x0070) # SpFt
        srd.seek(0x0010, 1)

        font_name_offset = read_u32(srd)
        # srd.seek(0x0014, 1)
        print(f'Font Name Offset: ${0x70 + font_name_offset:04x}')
        
        # read font name:
        temp = srd.tell()
        srd.seek(0x70 + font_name_offset)
        font_name = read_null_terminated_string(srd)
        print('Font Name:', font_name)
        srd.seek(temp)

        char_count = read_u32(srd) 
        print(char_count, 'characters')
        bb_offset = read_u32(srd) # offset relative to $0070
        print(f'${bb_offset:04x} bb data offset (relative to $0070, start of SpFt)')
        return
        srd.seek(0x0070 + bb_offset)
        for i in range(char_count):
            byteA = read_ubyte(srd)
            byteB = read_ubyte(srd)
            byteC = read_ubyte(srd)

            b1 = byteB & 0xF
            b2 = (byteB >> 4) & 0xF
            
            x = (b1 << 8) | byteA
            y = (byteC << 4) | b2
            w = read_ubyte(srd)
            h = read_ubyte(srd)

            a = read_ubyte(srd) # left padding
            b = read_ubyte(srd) # right
            c = read_ubyte(srd)
            print(f'{x}, {y}; {w}, {h}')

  

# read_stuff()
# bc4_idk_anymore()
bc4_attempt()

def charOffset(char):
    RSI_pos = 0x0070
    CharFlags_pos = RSI_pos + 0x2C
    ordinal = ord(char)
    
    file_offset = CharFlags_pos + (ordinal >> 3)
    bit_pos = ordinal & 0b111
    print(char, ordinal, f'${file_offset:04x}', bit_pos)

# charOffset('a')
# charOffset('之')
# charOffset('什')

unicode = u" !\"#$%&'(){|}~*+,-./:;<=>?[\\]^_0123456789ABCDEFGHIJKLMNÑOPQRSTUVWXYZabcdefghijqlmnñopqrstuvwxyzÁĀÉĒÍĪÓŌÚÜŪÇáāéēíīóōúüūç"
# print(len(unicode))

# 100 100 110 010 010 100 100 100 100 110 010 010 100 100
# 100 100 110 010 010 100 100 100 100 110 010 010 100 100 

