from io import BytesIO
from font_patcher.src import srd
from PIL import Image, ImageDraw, ImageFont
import fontTools
from font_patcher.src.utils import ensure_paths
from fontTools.ttLib import TTFont

TEXTURE_WIDTH     = 2048 # max 4096
TEXTURE_FONT_SIZE = 75

def charInFont(char: str, ttfont: TTFont):
    """Returns whether the char is in the font's cmap or not"""
    for cmap in ttfont['cmap'].tables:
        if cmap.isUnicode():
            if ord(char) in cmap.cmap:
                return True
    return False

def getCharBB(char: str, ttfont: TTFont, imgfont: ImageFont, error: bool = False):
    """
        Returns the character bounding box if found in the font,
        otherwise, it uses a fallback character.
    """

    dx, dy, w, h = imgfont.getbbox(char)
    if not charInFont(char, ttfont):
        error = True
        print('missing char', char)
        mappings = {
            'ā':'ä',
            'ä':'a',
            'ē':'ë',
            'ë':'e',
            'ī':'ï',
            'ï':'i',
            'ō':'ö',
            'ö':'o',
            'ū':'ü',
            'ü':'u',
            'Ā':'Ä',
            'Ä':'A',
            'Ē':'Ë',
            'Ë':'E',
            'Ī':'Ï',
            'Ï':'I',
            'Ō':'Ö',
            'Ö':'O',
            'Ū':'Ü',
            'Ü':'U',
        }
        if char in mappings:
            char = mappings[char]
            char, dx, dy, w, h, error = getCharBB(char, ttfont, imgfont, True)
    return char, dx, dy, w, h, error

def getLowerOffsetY(chars: str, font: ImageFont) -> int:
    """
        Computes the height of the tallest character in the charset
        to align them all when drawing the final texture
    """
    lowerOffset = 0
    for char in chars:
        lowerOffset = min(lowerOffset, font.getoffset(char)[1])
    return lowerOffset


def getCharsetBBs(charset: str, ttfont: TTFont, imgfont: ImageFont):
    """
        Computes the bounding boxes of all the chars, 
        using a given font, within TEXTURE_WIDTH
    """

    charBBs = []
    lower_offsetY = getLowerOffsetY(charset, imgfont)
    px, py = 0, max(0, -lower_offsetY)
    max_h = 0

    for char in charset:
        # can potentially change the char if missing in font
        newchar, dx, dy, w, h, error = getCharBB(char, ttfont, imgfont)
        char, inFont = newchar, not error

        # text wrap
        if px + w > TEXTURE_WIDTH:
            px, py = 0, max_h - lower_offsetY
        
        # img.drawText coords
        x, y = px - dx, py
        
        # store BBdata as (char, x, y, (px, py, w, h))
        charBBs.append((char, x, y, (px, py + lower_offsetY, w, h - lower_offsetY), inFont))
        
        px += w + 1
        max_h = max(max_h, py + h + 1)
    
    return charBBs, max_h

def genTextureAndBBs(data: bytearray, fontname: str, charset: str):
    """
        Generates:
        - .srdv:       Gamefont data, stored as ARGB
        - [DEBUG].png: Debug texture showing the charset and their bounding boxes

        If at least 1 char is not found in the font:
        - [BB].txt:    Text file with the character fonts that can be edited (not implemented for now)
        - [ERROR].png: Texture that marks the missing chars to be edited
    """

    srd.validate_charset(BytesIO(bytearray(data)), charset)
    
    # font objects
    ttfont = TTFont(f"font_patcher/fonts/{fontname}")
    imgfont = ImageFont.truetype(f"font_patcher/fonts/{fontname}", TEXTURE_FONT_SIZE, encoding="unic")

    # compute BBs
    charBBs, texture_height = getCharsetBBs(charset, ttfont, imgfont)


    # srdv texture
    texture_canvas = Image.new('RGBA', (TEXTURE_WIDTH, texture_height), "black")
    texture_draw = ImageDraw.Draw(texture_canvas)
    
    # png texture with BBs
    debug_canvas = Image.new('RGBA', (TEXTURE_WIDTH, texture_height), "black")
    debug_draw = ImageDraw.Draw(debug_canvas)


    # flag that triggers when a characters is not found in the given font
    error_flag = False

    # draw characters
    for i, item in enumerate(charBBs):
        char, x, y, bb, inFont = item
        bbx, bby, w, h = bb

        # mark char if missing in font
        if not inFont:
            texture_draw.line((bbx, bby, bbx + w, bby), fill='cyan' if i % 2 else 'blue')
            error_flag = True

        # draw chars and rects
        debug_draw.rectangle((bbx, bby, bbx + w, bby + h), outline='cyan' if i % 2 else 'blue')
        debug_draw.text((x, y), char, 'white', imgfont)
        texture_draw.text((x, y), char, 'white', imgfont)
    

    # save debug texture as png
    ensure_paths(f"font_patcher/pipeline/{fontname}/{fontname}.png")
    debug_canvas.save(f"font_patcher/pipeline/{fontname}/{fontname} [DEBUG].png", "PNG")


    # save final texture as srdv
    if not error_flag:
        with open(f'font_patcher/pipeline/{fontname}/{fontname}.srdv', 'wb') as ff:
            for dy in range(texture_height - 1):
                for dx in range(TEXTURE_WIDTH):
                    r = texture_canvas.getpixel((dx, dy))[0]
                    ff.write(bytes((r,r,r,r)))
    

    # save error texture as png
    else:
        texture_canvas.save(f"font_patcher/pipeline/{fontname}/{fontname} [ERROR].png", "PNG")
        
        # save BB data
        with open(f'font_patcher/pipeline/{fontname}/{fontname} [BB].txt', 'w', encoding='utf-8') as ff:  
            for i, item in enumerate(zip(charset, charBBs)):
                char = item[0]
                bbx, bby, w, h = item[1][3] # BB data
                
                if i: ff.write('\n')

                ff.write(f'{char}: {bbx}, {bby}, {w}, {h}')

    return charBBs, TEXTURE_WIDTH, texture_height