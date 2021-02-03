from src import stx, spc, utils
import sys, json

from googletrans import Translator

def main():
    if len(sys.argv) == 3:
        mode, filename = sys.argv[1:3]
        
        if filename:
            if mode in ['e', 'extract']:
                extract_stx(filename)
            elif mode in ['b', 'build']:
                build_stx(filename)
    else:
        spc.read('input/ch0/chap0_text_US.SPC')

def extract_stx(filename):
    lines = stx.read(f'input/{filename}.stx')

    utils.ensure_paths(f'output/text/{filename}.txt')

    with open(f'output/text/{filename}.txt', 'w', encoding='utf-16') as file_txt:
        file_txt.write('\n\n'.join(lines))

def build_stx(filename):
    utils.ensure_paths(f'output/build/{filename}.stx')

    with open(f'output/text/{filename}.txt', 'r', encoding='utf-16') as infile:
        out = stx.write(infile.read().split('\n\n'))

        with open(f'output/build/{filename}.stx', 'wb') as outfile:
            outfile.write(out)


def stx_to_json(filename):
    data = []
    en, gt = stx.read(f'input/{filename}.stx')

    for i in range(len(en)):
        data.append({
            'en': en[i],
            'gt': gt[i],
            'es': '',
        })

    utils.ensure_paths(f'output/json/{filename}.json')
    with open(f'output/json/{filename}.json', 'w', encoding='utf-16') as file_json:
        json.dump(data, file_json)


def tests():
    # translate('This is a test, hello world!')
    stx_to_json('ch0/c00_001_018')

def translate(text):
    translator = Translator()
    translation = translator.translate(text, dest='es')
    print(translation.text)
    return translation.text

if __name__ == '__main__': tests()