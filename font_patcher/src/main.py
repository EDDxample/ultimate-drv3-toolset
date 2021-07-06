from font_patcher.src import srd, srdv, spc, utils
from io import BufferedReader, BytesIO
import cv2,  os, re, numpy as np, shutil
from PIL import Image

def create_base(filename: str, charset: str):
    """Creates a base.stx starting from another gamefont"""
    
    file = open(f'font_patcher/pipeline/{filename}', 'rb')
    data = bytearray(file.read())
    file.close()

    # update texture mode to ARGB
    data[srd.TXR_OFFSET + 0x1C] = 0x01
    
    # fill first 2 tables
    data = srd.write_charset(data, charset)

    file = open(f'font_patcher/files/base.srd', 'wb')
    file.write(data)
    file.close()

def create_srd_from_font(fontname: str, charset: str):
    """
        Generates the game fonts using the given font and charset.

        If the given font doesn't support any character from the charset,
        it will generate a .png and a text file with the bounding boxes that 
        can be edited to then execute fix_font()
    """

    assert os.path.isfile('font_patcher/files/base.srd'), 'Please generate the base.stx before executing this function'

    file = open(f'font_patcher/files/base.srd', 'rb')
    data = file.read()
    file.close()

    # generate textures and compute BBs
    charBBs, texture_width, texture_height = srdv.genTextureAndBBs(data, fontname, charset)

    # write texture size and 3rd table
    data = srd.write_texture_size(data, texture_width, texture_height)
    data = srd.write_charBBs(data, charBBs)

    file = open(f'font_patcher/pipeline/{fontname}/{fontname}.srd', 'wb')
    file.write(data)
    file.close()

def fix_font(fontname):
    for file in os.listdir(f'font_patcher/pipeline/{fontname}'):
        if file.endswith('[FIX].png'):
            
            # update srd
            with open(f'font_patcher/pipeline/{fontname}/{fontname} [BB].txt') as ff:
                pass

            # update srdv
            pic = cv2.imread(f'font_patcher/pipeline/{fontname}/{file}', cv2.IMREAD_UNCHANGED)
            with open(f'font_patcher/pipeline/{fontname}/{fontname}.srdv', 'wb') as ff:
                for dy in range(pic.shape[0]):
                    for dx in range(pic.shape[1]):
                        r = pic[dy, dx][0]
                        ff.write(bytes((r,r,r,r)))


def testA(charset: str):
    """
        Create base and attempt to translate all the fonts.
        Generate [ERROR].png if charset is not covered by the font.
        (Fix them and their bounding boxes inside [BB].txt before the next step)
    """

    create_base('v3_font01_8.srd', charset)

    pattern = re.compile(r'(\w+)\s+->\s+([a-zA-Z-_.]+)')

    with open('font_patcher/files/fontnames FR.txt') as ff:
        for groups in pattern.findall(ff.read()):
            create_srd_from_font(groups[1], charset)

def testB(charset: str):
    """
        Patch all the fonts that contain a [FIX].png,
        then rename them by chapter and compile them back to SPC
    """

    pattern = re.compile(r'(\w+)\s+->\s+([a-zA-Z-_.]+)')

    maps = []

    with open('font_patcher/files/fontnames FR.txt') as ff:
        print('\n=== Fixing Fonts ===\n')
        for groups in pattern.findall(ff.read()):
            maps.append(groups)
            print(groups[1])
            fix_font(groups[1])

    utils.ensure_paths('font_patcher/pipeline/out/')
    utils.ensure_paths('font_patcher/pipeline/temp/')

    print('\n=== Packing SPCs ===\n')
    for chaptername, fontname in maps:
        spcname = chaptername.replace('FR', 'US')
        chaptername = chaptername.replace('game', 'v3').replace('_FR', '')
        print(spcname)
        folder = f'font_patcher/pipeline/{fontname}'

        shutil.copyfile(f'{folder}/{fontname}.srd',  f'font_patcher/pipeline/temp/{chaptername}.stx')
        shutil.copyfile(f'{folder}/{fontname}.srdv', f'font_patcher/pipeline/temp/{chaptername}.srdv')

        # copy font00 as it can't be compiled to spc
        if chaptername == 'v3_font00':
            shutil.copyfile(f'font_patcher/pipeline/temp/{chaptername}.stx',  f'font_patcher/pipeline/out/{chaptername}.stx')
            shutil.copyfile(f'font_patcher/pipeline/temp/{chaptername}.srdv', f'font_patcher/pipeline/out/{chaptername}.srdv')
        
        # compile the rest of the files to spc
        else:
            data = spc.repack('font_patcher/pipeline/temp', [f'{chaptername}.stx', f'{chaptername}.srdv'])
            
            with open(f'font_patcher/pipeline/out/{spcname}.spc', 'wb') as ff:
                ff.write(data)
    
    shutil.rmtree('font_patcher/pipeline/temp/')

########################################################################
# OLD STUFF BEFORE THE REFACTOR, I'LL LEAVE IT HERE FOR NOW
########################################################################

# from utils import charOffset, read, textureSizeToBytes, writeBB
# from textureUtils import genBaseTexture, genNewTexture, genNewTexture2

# def getfontpicture(fontname):
#     with open(f'output/{fontname}.stx', 'rb') as srd:

#         srd.seek(0x26)
#         width  = read('u2', srd)
#         height = read('u2', srd)
#         srd.seek(0x2C)
#         mode = read('u1', srd)


#         with open(f'output/FOT-RodinPro-EB.png', 'rb') as picdata:
#             data = picdata.read()
#             if   mode == 0x01:
#                 pic = cv2.imread(f'output/FOT-RodinPro-EB.png', cv2.IMREAD_UNCHANGED)

#                 srd.seek(0x70 + 0x14) # font name offset + character BB count & offset
#                 char_count       = read('u4', srd)
#                 char_bb_offset   = read('u4', srd)

#                 srd.seek(0x70 + char_bb_offset)

#                 for i in range(char_count):
#                     x, y, w, h, a, b, c = read('charbb', srd)
#                     # print(f'{x:04} {y:02}, {w:02} {h:02}, {a} {b} {c}')
#                     color = (255,0,0,255) if i % 2 else (0, 255, 0, 255)

#                     cv2.rectangle(pic, (x, y), (x + w, y + h), color=color, thickness=1)

#                 cv2.imshow('read from srdv', pic)
#                 cv2.waitKey()
#                 # cv2.imwrite('idk.png', pic)

#             elif mode == 0x16:
#                 pic = Image.frombytes('L', (width, height), data, 'bcn', 4)
#                 # pic.save(f'{fontname}.png')
#                 pic.show()

# def readfont(fontname):
#     """
#         returns charlist, bblist,
#     """
#     with open(f'{fontname}.srd', 'rb') as ff:
#         # srd.seek(0x70 + 0x2C)

#         ff.seek(0x70) # SpFt ====================

#         ff.seek(0x70 + 0x08) # character flag count
#         flag_count = read('u4', ff)

#         ff.seek(0x70 + 0x10) # font name offset + character BB count & offset
#         font_name_offset = read('u4', ff)
#         char_count       = read('u4', ff)
#         char_bb_offset   = read('u4', ff)
        
#         ff.seek(0x70 + 0x2C) # list of character flags -------------------------

#         charlist = ''

#         for byte in range((flag_count >> 3)):
#             current_byte = read('u1', ff)
#             chars = ''
            
#             for bit in range(8):
#                 if (current_byte >> bit) & 1 == 1:
#                     ordinal = byte * 8 + bit
#                     chars += chr(ordinal)
#             charlist += chars

#         s = u' !"#$%&\'()*+,-./0123456789:;<=>?ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_abcdefghijlmnopqrstuvwxyz{|}~ª«º»ÁÇÉÍÑÓÚÜáçéíñóúüĀāĒēĪīŌōŪū麼！（）１７９？'
#         print(len(charlist), len(s))
#         print(charlist)
#         print(s)
#         assert char_count == len(charlist)

#         ff.seek(0x70 + char_bb_offset) # list of character BBs -------------------------
#         bblist = {}
#         print(f'${0x70 + char_bb_offset:04x}')

#         for i in range(char_count):
#             x, y, w, h, left, right, top = read('charbb', ff)
            
#             bblist[charlist[i]] = (x, y, w, h, left, right, top)
#             print(f'{charlist[i]}: {x}, {y}; {w}, {h} ({left},{right},{top})')

#         ff.seek(0x70 + font_name_offset) # font name -------------------------
#         fontname = read('nullstring', ff, encoding='utf-16')

#     return {
#         'charlist': charlist,
#         'bblist': bblist,
#         'fontname': fontname,
#     }


# def createBaseFont():
#     """
#         Steps:
#         - Update bit flags
#         - Update texture mode to ARGB
#         - Generate new texture from font
#         - Update texture's width and height
#         - Update BBs
#     """
#     data = None
    
#     TXR_OFFSET  = 0x10
#     SpFt_OFFSET = 0x70


#     with open('v3_font01_8.srd', 'rb') as ff:
#         data = bytearray(ff.read())

#     # ==== Update bit flags ====
#     FlagList_offset = SpFt_OFFSET + 0x2C
    
#     eng_chars = sorted(set(u" !'*,-.179?ABCDEFGHIKLMNOPRSTUWYabcdefghijklmnopqrstuvwxyz…　。一之什他以來們候兇到動即去可吧因圖在天太好存定室將屍式我所手打把是時暗書會櫃正殺海為獨現當發的知給自蘭被趁超過道郎門開限體麼！（）１７９？"))
#     esp_chars = sorted(set(u" !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_abcdefghijklmnopqrstuvwxyz{|}~¡ª«º»¿ÁÇÉÍÑÓÚÜáçéíñóúüĀāĒēĪīŌōŪū"))

    
#     for i in range(len(esp_chars)):
        
#         # Set bit from eng char to 0
#         char = eng_chars[i]
#         byte, bit = charOffset(FlagList_offset, char)
#         data[byte] &= ~(1 << bit) & 0xFF

#         # Set bit from esp char to 1
#         char = esp_chars[i]
#         byte, bit = charOffset(FlagList_offset, char)
#         data[byte] |= 1 << bit
    

#     # ==== Update texture mode to ARGB ====
#     data[TXR_OFFSET + 0x1C] = 0x01
    
#     # ==== Generate new texture from font ====
#     width = 2048
#     font_size = 75
#     height, charbbs = genBaseTexture('FOT-RodinPro-EB', font_size, width, esp_chars)

#     # ==== Update texture's width and height ====
#     for i, byte in enumerate(textureSizeToBytes(width, height)):
#         data[TXR_OFFSET + 0x16 + i] = byte

#     # ==== Update 2nd table ==== (test)
#     start = 0x2080
#     last_offset = 0
#     for i, c in enumerate(esp_chars):
#         o = ord(c)

#         offset = o // 8
#         offset = offset - (offset % 4)

#         if offset > last_offset:
#             last_offset = offset
#             data[start + offset] = i

#     # ==== Update BBs ====
#     CHAR_BBs_OFFSET   = read('u4', BytesIO(data[SpFt_OFFSET + 0x18 : SpFt_OFFSET + 0x18 + 4]))

#     for i, item in enumerate(charbbs):
#         c, x, y, bb = item
#         bbx, bby, w, h = bb
#         left, right, top = 0, 0, 0
#         for ii, byte in enumerate(writeBB(bbx, bby, w, h, left, right, top)):
#             # print(f'${SpFt_OFFSET + CHAR_BBs_OFFSET:04x}', byte)
#             data[SpFt_OFFSET + CHAR_BBs_OFFSET + i * 8 + ii] = byte

#     with open('output/v3_font00.stx', 'wb') as ff:
#         ff.write(data)

# def createFromBaseFont(fontname):
#     TXR_OFFSET  = 0x10
#     SpFt_OFFSET = 0x70

#     esp_chars = sorted(set(u" !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_abcdefghijklmnopqrstuvwxyz{|}~¡ª«º»¿ÁÇÉÍÑÓÚÜáçéíñóúüĀāĒēĪīŌōŪū"))
    
#     # ==== Copy data from base file ====
#     data = None
#     with open('base/base.stx', 'rb') as ff:
#         data = bytearray(ff.read())

#     # ==== Generate new texture from font ====
#     width = 2048
#     font_size = 75
#     height, charbbs = genNewTexture(fontname, font_size, width, esp_chars)

#     # ==== Update texture's width and height ====
#     for i, byte in enumerate(textureSizeToBytes(width, height)):
#         data[TXR_OFFSET + 0x16 + i] = byte

#     # ==== Update BBs ====
#     CHAR_BBs_OFFSET   = read('u4', BytesIO(data[SpFt_OFFSET + 0x18 : SpFt_OFFSET + 0x18 + 4]))
    
#     for i, item in enumerate(charbbs):
#         bbx, bby, w, h = item[3] # BB data
#         left, right, top = 0, 0, 0
#         for ii, byte in enumerate(writeBB(bbx, bby, w, h, left, right, top)):
#             data[SpFt_OFFSET + CHAR_BBs_OFFSET + i * 8 + ii] = byte

#     # ==== Save new Font file ====
#     with open(f'output/{fontname}/{fontname}.stx', 'wb') as ff:
#         ff.write(data)

#     print(fontname,'done!')


# ### extracts font names from srd files

# def extractFontName():
#     for foldername in os.listdir('gamefonts'):
#         srdname = '_'.join(foldername.split('_')[1:-1])
#         with open(f'gamefonts/{foldername}/v3_{srdname}.stx', 'rb') as ff:
#             ff.seek(0x70 + 0x10)
#             font_name_offset = read('u4', ff)
#             ff.seek(0x70 + font_name_offset)
#             fontname = read('nullstring', ff, encoding='utf-16')

#             print(foldername, '->', fontname)


# ### patches fonts from (gamefont, font) list

# def createFromBaseFont2(gamefontname: str, fontname: str, foldername='game'):
#     TXR_OFFSET  = 0x10
#     SpFt_OFFSET = 0x70

#     esp_chars = sorted(set(u" !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_abcdefghijklmnopqrstuvwxyz{|}~¡ª«º»¿ÁÇÉÍÑÓÚÜáçéíñóúüĀāĒēĪīŌōŪū"))
    
#     # ==== Copy data from base file ====
#     data = None
#     with open('base/base.stx', 'rb') as ff:
#         data = bytearray(ff.read())

#     # ==== Generate new texture from font ====
#     width = 2048
#     font_size = 75
#     height, charbbs = genNewTexture2(gamefontname, fontname, font_size, width, esp_chars, foldername=foldername)

#     # ==== Update texture's width and height ====
#     for i, byte in enumerate(textureSizeToBytes(width, height)):
#         data[TXR_OFFSET + 0x16 + i] = byte

#     # ==== Update BBs ====
#     CHAR_BBs_OFFSET   = read('u4', BytesIO(data[SpFt_OFFSET + 0x18 : SpFt_OFFSET + 0x18 + 4]))
    
#     for i, item in enumerate(charbbs):
#         bbx, bby, w, h = item[3] # BB data
#         left, right, top = 0, 0, 0
#         for ii, byte in enumerate(writeBB(bbx, bby, w, h, left, right, top)):
#             data[SpFt_OFFSET + CHAR_BBs_OFFSET + i * 8 + ii] = byte

#     # ==== Save new Font file ====
#     tempname = gamefontname.replace('game', 'v3').replace('_FR', '')
#     with open(f'output/{foldername}/{gamefontname}/{tempname}.stx', 'wb') as ff:
#         ff.write(data)

#     print(fontname,'done!')

# def readFontnames(listname='fontnames US.txt', foldername='game'):
#     pattern = re.compile(r'(\w+)\s+->\s+([a-zA-Z-_.]+)')

#     with open(listname) as ff:
#         for groups in pattern.findall(ff.read()):
#             print(groups)
#             createFromBaseFont2(*groups, foldername)

#     # createFromBaseFont2('game_font11_US', 'FOT-RowdyStd-EB.otf')


# ### gens srdv from picture

# def patchFonts():

#     for folder in os.listdir('completed/fonts'):
#         for file in os.listdir(f'completed/fonts/{folder}'):
#             if file.endswith('[FIX].png'):
#                 pic = cv2.imread(f'completed/fonts/{folder}/{file}', cv2.IMREAD_UNCHANGED)
#                 # print(f'completed/fonts/{folder}/{file}', pic.shape)

                

#                 with open(f'completed/fonts/{folder}/{folder}.srdv', 'wb') as ff:
#                     for dy in range(pic.shape[0]):
#                         for dx in range(pic.shape[1]):
#                             r = pic[dy, dx][0]
#                             ff.write(bytes((r,r,r,r)))


### AAAAAAAAAAAAAAAAAAAAAAAAAA
# import spcUtils as spc

# def extractSPCs():
#     # ===== step 1 =====
#     # for file in os.listdir('nuevasfonts/US_fonts'):
#     #     spc.extract(file[:-4])

#     # ===== step 2 =====
#     for folder in os.listdir('nuevasfonts/us'):
#         for file in os.listdir(f'nuevasfonts/us/{folder}'):
#             if file.endswith('.stx'):
#                 with open(f'nuevasfonts/us/{folder}/{file}', 'rb') as ff:
#                     ff.seek(0x80)
#                     name_offset = read('u4', ff)
#                     ff.seek(0x70 + name_offset)
#                     name = read('nullstring', ff, encoding='utf-16')
#                     print(folder, '->', name)

#     # ===== step 3 =====
#     # readFontnames('fontnames FR.txt', 'fr')

#     # ===== step 4 =====
#     # for folder in os.listdir('output/fr'):
#     #     for file in os.listdir(f'output/fr/{folder}'):
#     #         if file.endswith('[FIX].png'):
#     #             print(folder)
#     #             pic = cv2.imread(f'output/fr/{folder}/{file}', cv2.IMREAD_UNCHANGED)

                
#     #             tempname = folder.replace('game', 'v3').replace('_FR', '')
#     #             with open(f'output/fr/{folder}/{tempname}.srdv', 'wb') as ff:
#     #                 for dy in range(pic.shape[0]):
#     #                     for dx in range(pic.shape[1]):
#     #                         r = pic[dy, dx][0]
#     #                         ff.write(bytes((r,r,r,r)))








# == Gen base file  ==
# createBaseFont()
# getfontpicture('v3_font00')

# == Gen new font file ==
# createFromBaseFont('FOT-HummingStd-D')
# createFromBaseFont('FOT-NewCezannePro-EB')
# createFromBaseFont('FOT-RodinPro-EB')
# createFromBaseFont('FOT-TsukuQMinLStd-L')
# createFromBaseFont('HOT-SamuraiStd-R')
# createFromBaseFont('ComicSansMS3')


# readFontnames()
# patchFonts()

# extractSPCs()
