from src import stx, spc, utils
import sys, json, os

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

    # utils.ensure_paths(f'files/1_stx/{filename}/{subfilename}.json')

    # with open(f'files/1_stx/{filename}/{subfilename}.json', 'w', encoding='utf-16') as file_txt:
        # file_txt.write('\n\n'.join(lines))

def build_stx(filename):
    utils.ensure_paths(f'output/build/{filename}.stx')

    with open(f'output/text/{filename}.txt', 'r', encoding='utf-16') as infile:
        out = stx.write(infile.read().split('\n\n'))

        with open(f'output/build/{filename}.stx', 'wb') as outfile:
            outfile.write(out)

def stx_to_json(filename, subfilename):
    data = []
    en, gt = stx.read(f'files/1_stx/{filename}/{subfilename}')

    for i in range(len(en)):
        data.append({ 'en': en[i], 'gt': gt[i], 'es': gt[i] })

    utils.ensure_paths(f'files/2_json/{filename}/{subfilename}.json')
    with open(f'files/2_json/{filename}/{subfilename}.json', 'w', encoding='utf-16') as file_json:
        json.dump(data, file_json, indent=2, ensure_ascii=False)


def tests():
    if len(sys.argv) == 3:
        step, filename = sys.argv[1:3]
        step = int(step)

        if step == 1: # spc to stx[]
            spc.extract(filename)

        if step == 2: # stx[] to json
            stx_path = f'files/1_stx/{filename}/'
            subfiles = [ f for f in os.listdir(stx_path) if os.path.isfile(os.path.join(stx_path, f)) ]
            for i, subfilename in enumerate(subfiles):
                print(f'\n{i+1}/{len(subfiles)} - {subfilename}')
                stx_to_json(filename, subfilename)

def translate(text):
    translator = Translator()
    translation = translator.translate(text, dest='es')
    print(translation.text)
    return translation.text

if __name__ == '__main__':
    tests()
    # en, gt = stx.read(f'files/1_stx/chap0_text_US/c00_004_007.stx')
    # print(len(en), len(gt))