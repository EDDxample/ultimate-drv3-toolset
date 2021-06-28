from translation_pipeline.src.main import spc_to_text

import sys

def main():
    if len(sys.argv) == 3:
        key, filename = sys.argv[1:3]

        if   key == 'transIN':  extract_text(filename)
        elif key == 'transOUT': patch_text(filename)
        elif key == 'srd': pass


def extract_text(filename):
    """
    Extracts the text from the spc to
    ./translation_pipeline/pipeline/3_merged_dialogues/
    """
    spc_to_text(filename)


def patch_text(filename):
    """
    Packs the texts in ./translation_pipeline/pipeline/3_merged_dialogues/
    into a .SPC
    """

if __name__ == '__main__':
    main()