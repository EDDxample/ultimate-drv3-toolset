from PIL import Image, ImageDraw, ImageFont
import fontTools
from utils import ensure_paths
from fontTools.ttLib import TTFont

ttfont = None

def charInFont(char: str, fontname):
    global ttfont
    for cmap in ttfont['cmap'].tables:
        if cmap.isUnicode():
            if ord(char) in cmap.cmap:
                return True
    return False


def getCharBB(char: str, fontname: str, font: ImageFont):
    dx, dy, w, h = font.getbbox(char)
    if not charInFont(char, fontname):
        print('missing char', char)
        char = {
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
        }[char]
        char, dx, dy, w, h = getCharBB(char, fontname, font)
    return char, dx, dy, w, h

def getLowerOffsetY(chars: str, font: ImageFont) -> int:
    lowerOffset = 0
    for char in chars:
        lowerOffset = min(lowerOffset, font.getoffset(char)[1])
    return lowerOffset

def genBaseTexture(font_name, font_size, texture_width, unicode_text, file_name='v3_font00'):

    # sample text and font
    unicode_text = ''.join(sorted(set(unicode_text)))
    font = ImageFont.truetype(f"fonts/{font_name}.otf", font_size, encoding="unic")

    charBBs = [] # char, x, y, (bbx, bby, w, h)

    lower_offsetY = getLowerOffsetY(unicode_text, font)
    px, py = 0, max(0, -lower_offsetY)
    max_h = 0

    # ==== Encode BBs ====
    
    for char in unicode_text:
        dx, dy = font.getoffset(char)
        w, h = font.getsize(char)

        # text wrap
        if px + w > texture_width:
            px, py = 0, max_h - lower_offsetY
        
        # img.drawText coords
        x, y = px - dx, py
        
        # store BBdata as (char, x, y, (px, py, w, h))
        charBBs.append((char, x, y, (px, py + lower_offsetY, w, h - lower_offsetY)))
        
        px += w + 1
        max_h = max(max_h, py + h + 1)


    # ==== Generate texture from BBs ====

    # srdv texture
    texture_canvas = Image.new('RGBA', (texture_width, max_h), "black")
    texture_draw = ImageDraw.Draw(texture_canvas)
    
    # png texture with BBs
    debug_canvas = Image.new('RGBA', (texture_width, max_h), "black")
    debug_draw = ImageDraw.Draw(debug_canvas)


    # draw characters
    for i, item in enumerate(charBBs):
        char, x, y, bb = item
        bbx, bby, w, h = bb
        texture_draw.text((x, y), char, 'white', font)

        debug_draw.text((x, y), char, 'white', font)
        debug_draw.rectangle((bbx, bby, bbx + w, bby + h), outline='orange' if i % 2 else 'blue')
    
    
    # save debug texture as png
    debug_canvas.save(f"output/{font_name}.png", "PNG")
    # debug_canvas.show()

    # save final texture as srdv
    with open(f'output/{file_name}.srdv', 'wb') as ff:
        for dy in range(max_h - 1):
            for dx in range(texture_width):
                r = texture_canvas.getpixel((dx, dy))[0]
                ff.write(bytes((r,r,r,r)))
    return max_h, charBBs


def genNewTexture(fontname, fontsize, texture_width, unicode_text, file_name=None):
    global ttfont
    ttfont = TTFont(f"fonts/{fontname}.otf")

    # sample text and font
    unicode_text = ''.join(sorted(set(unicode_text)))
    font = ImageFont.truetype(f"fonts/{fontname}.otf", fontsize, encoding="unic")

    charBBs = [] # char, x, y, (bbx, bby, w, h)

    lower_offsetY = getLowerOffsetY(unicode_text, font)
    px, py = 0, max(0, -lower_offsetY)
    max_h = 0
    errorFlag = False

    # ==== Encode BBs ====
    
    for char in unicode_text:
        # can potentially change the char if missing in font
        newchar, dx, dy, w, h = getCharBB(char, fontname, font)
        char, inFont = newchar, newchar == char

        # text wrap
        if px + w > texture_width:
            px, py = 0, max_h - lower_offsetY
        
        # img.drawText coords
        x, y = px - dx, py
        
        # store BBdata as (char, x, y, (px, py, w, h))
        charBBs.append((char, x, y, (px, py + lower_offsetY, w, h - lower_offsetY), inFont))
        
        px += w + 1
        max_h = max(max_h, py + h + 1)


    # ==== Generate texture from BBs ====

    # srdv texture
    texture_canvas = Image.new('RGBA', (texture_width, max_h), "black")
    texture_draw = ImageDraw.Draw(texture_canvas)
    
    # png texture with BBs
    debug_canvas = Image.new('RGBA', (texture_width, max_h), "black")
    debug_draw = ImageDraw.Draw(debug_canvas)


    # draw characters
    for i, item in enumerate(charBBs):
        char, x, y, bb, inFont = item
        bbx, bby, w, h = bb

        # draw char on debug texture
        debug_draw.rectangle((bbx, bby, bbx + w, bby + h), outline='cyan' if i % 2 else 'blue')
        debug_draw.text((x, y), char, 'white', font)

        # draw char on final/error texture
        if not inFont:
            texture_draw.line((bbx, bby, bbx + w, bby), fill='cyan' if i % 2 else 'blue')
            errorFlag = True
        
        texture_draw.text((x, y), char, 'white', font)
    
    
    # save debug texture as png
    ensure_paths(f"output/{fontname}/{file_name if file_name else fontname}.png")
    debug_canvas.save(f"output/{fontname}/{file_name if file_name else fontname} [DEBUG].png", "PNG")
    # debug_canvas.show()


    if not errorFlag:
        # save final texture as srdv
        with open(f'output/{fontname}/{file_name if file_name else fontname}.srdv', 'wb') as ff:
            for dy in range(max_h - 1):
                for dx in range(texture_width):
                    r = texture_canvas.getpixel((dx, dy))[0]
                    ff.write(bytes((r,r,r,r)))
    else:
        # save error texture as png
        texture_canvas.save(f"output/{fontname}/{file_name if file_name else fontname} [ERROR].png", "PNG")
        # save BB data
        with open(f'output/{fontname}/{file_name if file_name else fontname} [BB].txt', 'w', encoding='utf-8') as ff:
            for i, item in enumerate(zip(unicode_text, charBBs)):
                char = item[0]
                bbx, bby, w, h = item[1][3] # BB data
                
                if i: ff.write('\n')

                ff.write(f'{char}: {bbx}, {bby}, {w}, {h}')

    return max_h, charBBs


def genNewTexture2(gamefontname, fontname, fontsize, texture_width, unicode_text, foldername):
    global ttfont
    ttfont = TTFont(f"fonts/fr/{fontname}")

    # sample text and font
    unicode_text = ''.join(sorted(set(unicode_text)))
    font = ImageFont.truetype(f"fonts/fr/{fontname}", fontsize, encoding="unic")

    charBBs = [] # char, x, y, (bbx, bby, w, h)

    lower_offsetY = getLowerOffsetY(unicode_text, font)
    px, py = 0, max(0, -lower_offsetY)
    max_h = 0
    errorFlag = False

    # ==== Encode BBs ====
    
    for char in unicode_text:
        # can potentially change the char if missing in font
        newchar, dx, dy, w, h = getCharBB(char, fontname, font)
        char, inFont = newchar, newchar == char

        # text wrap
        if px + w > texture_width:
            px, py = 0, max_h - lower_offsetY
        
        # img.drawText coords
        x, y = px - dx, py
        
        # store BBdata as (char, x, y, (px, py, w, h))
        charBBs.append((char, x, y, (px, py + lower_offsetY, w, h - lower_offsetY), inFont))
        
        px += w + 1
        max_h = max(max_h, py + h + 1)


    # ==== Generate texture from BBs ====

    # srdv texture
    texture_canvas = Image.new('RGBA', (texture_width, max_h), "black")
    texture_draw = ImageDraw.Draw(texture_canvas)
    
    # png texture with BBs
    debug_canvas = Image.new('RGBA', (texture_width, max_h), "black")
    debug_draw = ImageDraw.Draw(debug_canvas)


    # draw characters
    for i, item in enumerate(charBBs):
        char, x, y, bb, inFont = item
        bbx, bby, w, h = bb

        # draw char on debug texture
        debug_draw.rectangle((bbx, bby, bbx + w, bby + h), outline='cyan' if i % 2 else 'blue')
        debug_draw.text((x, y), char, 'white', font)

        # draw char on final/error texture
        if not inFont:
            texture_draw.line((bbx, bby, bbx + w, bby), fill='cyan' if i % 2 else 'blue')
            errorFlag = True
        
        texture_draw.text((x, y), char, 'white', font)
    
    
    # save debug texture as png
    ensure_paths(f"output/{foldername}/{gamefontname}/{fontname}.png")
    debug_canvas.save(f"output/{foldername}/{gamefontname}/{fontname} [DEBUG].png", "PNG")
    # debug_canvas.show()


    if not errorFlag:

        tempname = gamefontname.replace('game', 'v3').replace('_FR', '')
        # save final texture as srdv
        with open(f'output/{foldername}/{gamefontname}/{tempname}.srdv', 'wb') as ff:
            for dy in range(max_h - 1):
                for dx in range(texture_width):
                    r = texture_canvas.getpixel((dx, dy))[0]
                    ff.write(bytes((r,r,r,r)))
    else:
        # save error texture as png
        texture_canvas.save(f"output/{foldername}/{gamefontname}/{fontname} [ERROR].png", "PNG")
        # save BB data
        with open(f'output/{foldername}/{gamefontname}/{fontname} [BB].txt', 'w', encoding='utf-8') as ff:
            for i, item in enumerate(zip(unicode_text, charBBs)):
                char = item[0]
                bbx, bby, w, h = item[1][3] # BB data
                
                if i: ff.write('\n')

                ff.write(f'{char}: {bbx}, {bby}, {w}, {h}')

    return max_h, charBBs
