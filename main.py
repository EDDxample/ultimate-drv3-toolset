from font_patcher.src.main import create_base, create_srd_from_font, fix_font
from translation_pipeline.src.main import extract_text, patch_text
import sys

# COMMANDS:
# "py main.py transIN  demo_US" -> extracts the texts into a json file
# "py main.py transOUT demo_US" -> repacks the json into a SPC file

def main():
    if len(sys.argv) == 3:
        
        # generate charset and ensure its sorted and 
        # doesn't have any duplicates
        charset = u" !\"#$€%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_abcdefghijklmnopqrstuvwxyz{|}~¡ª«º»¿ÁÇÉÍÑÓÚÜáçéíñóúüĀāĒēĪīŌōŪū"
        charset = ''.join(sorted(set(charset)))


        key, filename = sys.argv[1:3]

        # extract texts for translation
        if   key == 'transIN':   extract_text(filename)
        
        # get patched SPC
        elif key == 'transOUT':  patch_text(filename)
        
        # generate font base.srd
        elif key == 'fontBASE':  create_base(filename, charset)
        
        # attempt to generate a .srd and .srdv using the given font
        elif key == 'fontGEN':   create_srd_from_font(filename, charset)

        # patch the fonts that missed some characters
        elif key == 'fontPATCH': fix_font(filename)

if __name__ == '__main__':
    main()