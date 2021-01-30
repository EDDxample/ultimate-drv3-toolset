from src import stx, utils

def main():
    # extract_stx('demo')
    build_stx('demo')


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

if __name__ == '__main__': main()