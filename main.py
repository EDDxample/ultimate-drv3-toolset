from src import stx, spc, utils
import sys, json, os

def stx_to_json(filename, subfilename):
    data = []
    en, gt = stx.read(f'files/1_stx/{filename}/{subfilename}')

    for i in range(len(en)):
        data.append({ 'en': en[i], 'gt': gt[i], 'es': gt[i] })

    utils.ensure_paths(f'files/2_json/{filename}/{subfilename}.json')
    with open(f'files/2_json/{filename}/{subfilename}.json', 'w', encoding='utf-16') as file_json:
        json.dump(data, file_json, indent=2, ensure_ascii=False)

def mega_json_to_stx(filename):

    with open(f'files/3_mega_json/{filename}.json', 'r', encoding='utf-16') as mj_file:
        mj = json.load(mj_file)
        translated_lines = 0
        total_lines = 0
        for key in mj:
            value = mj[key]
            
            # stats
            line_count = len(value['text'])
            total_lines += line_count
            if value['translated']: translated_lines += line_count

            # stx convertion
            lines = list(map(lambda texts: texts['es'], value['text']))
            data = stx.write(lines)
            utils.ensure_paths(f'files/4_stx/{filename}/{key}.stx')
            with open(f'files/4_stx/{filename}/{key}.stx', 'wb') as outfile:
                outfile.write(data)

        print(f'{filename}: {translated_lines} out of {total_lines} lines. {translated_lines / total_lines * 100:.2f}%')


def main():
    if len(sys.argv) == 3:
        step, filename = sys.argv[1:3]
        step = int(step)

        if step == 1: # spc to stx[]
            spc.extract(filename)

        if step == 2: # stx[] to json[]
            stx_path = f'files/1_stx/{filename}/'
            subfiles = [ f for f in os.listdir(stx_path) if os.path.isfile(os.path.join(stx_path, f)) ]
            for i, subfilename in enumerate(subfiles):
                print(f'\n{i+1}/{len(subfiles)} - {subfilename}')
                stx_to_json(filename, subfilename)

        if step == 3: # merge json[]
            json_path = f'files/2_json/{filename}/'
            out = {}
            subfiles = [ f for f in os.listdir(json_path) if os.path.isfile(os.path.join(json_path, f)) ]
            for subfile in subfiles:
                subfilename = subfile.replace('.stx.json', '')
                with open(f'files/2_json/{filename}/{subfile}', 'r', encoding='utf-16') as curfile:
                    text = json.load(curfile)
                    out[subfilename] = { 'text': text, 'translated': False }
            utils.ensure_paths(f'files/3_mega_json/{filename}.json')
            with open(f'files/3_mega_json/{filename}.json', 'w', encoding='utf-16') as file_json:
                json.dump(out, file_json, indent=2, ensure_ascii=False)

        if step == 4: # mega json kto stx[]
            mega_json_to_stx(filename)
        


if __name__ == '__main__':
    main()