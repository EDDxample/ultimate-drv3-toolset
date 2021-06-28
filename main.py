from translation_pipeline.src.main import extract_text, patch_text
import sys

# COMMANDS:
# "py main.py transIN  demo_US" -> extracts the texts into a json file
# "py main.py transOUT demo_US" -> repacks the json into a SPC file

def main():
    if len(sys.argv) == 3:
        key, filename = sys.argv[1:3]

        if   key == 'transIN':  extract_text(filename)
        elif key == 'transOUT': patch_text(filename)
        elif key == 'srd': pass


if __name__ == '__main__':
    main()