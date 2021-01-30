from src import stx, utils

def main():
    extract_stx('ch0/c00_000_001')
    # build_stx('ch0/c00_000_001')


def extract_stx(filename):
    lines = stx.read(f'input/{filename}.stx')
    out = []
    for line in lines:
        out.append({'id': line[0], 'text': line[1] })
    
    utils.ensure_paths(f'out/text/{filename}.txt')

    with open(f'out/text/{filename}.txt', 'w', encoding='utf-16') as file_txt:
        for line in lines:
            file_txt.writelines([line[1] + '\n\n'])


def build_stx(filename):
    with open(filename + '.txt', 'r', encoding='utf-16') as infile:
        out = stx.write(infile.read().split('\n\n'))

        with open(f'build/{filename}', 'wb') as outfile:
            outfile.write(out)

if __name__ == '__main__': main()