# Ultimate DRv3 Toolset

Tools I'm using to translate the game to spanish

🚧 Refactor in progress 🚧

# Translation Pipeline

- Extract the .stx files (dialogues) from the .spc file
- Convert (and translate) the .stx files into .json files
- Merge all the .json files (and correct the translations)
- Convert back the .json files to .stx
- Pack everything back into a new .spc file

## Instructions

### Extract text:

Put the chapter's .spc into `pipeline/0_input_SPC`, then run `py main.py transIN <file name>` to get a json file with the text in `pipeline/3_merged_texts`. You can replace the texts in the "es" section (as it was initialy meant for a spanish translation).

### Repack text:

Once you edit that json, run `py main.py transOUT <file name>` to get the patched SPC in `5_output_SPC`.

# Font Patcher

Fonts are split in 2 files: a .srd with character data (misnamed as .stx for some reason) and a .srdv with the glyph texture data.

Right now it's just a set of scripts I call as needed, the output folders are hardcoded and so on.
As I'm too lazy to refactor and generalize the code, let me just explain the process:

- Create a base.srd file with the characters bitflags and offsets you want (1st and 2nd table of the .srd)
- Create the font's .png, srdv and fill base's 3rd table with char bounding boxes (BBs)
- If the character is not in the target font, you'll get an `[ERROR].png` highlighting the missing chars and a text file with all the character BBs
- Finally, by replacing the `[ERROR]` images with `[FIX]` and readjusting the char BBs as needed, you can patch the missing fonts

## Notes

The new charset cannot be longer than the one in the base file.

This can be solved by using another base file with more chars or by updating
the data offsets and lengths that would be affected by increasing its size. (not implemented atm)

## Instructions

### Generate Base file:

Put the .stx you want to copy (for example, I used `v3_font01_8.srd`) inside `font_patcher/pipeline`
and edit the charset inside `main.py`, then run `py main.py fontBASE <file name>`.

### Generate SRD from font:

Put the font you want inside `font_patcher/fonts`, then run `py main.py fontGEN <font name>`.
If the font contains all the characters from the charset, it should generate both .srd and .srdv files.
Otherwise, you'll get an `[ERROR].png` and a `[BB].txt` so you will have to run the next command.

### Patch missing font (not ported yet)

Edit the `[ERROR].png` texture with the glyphs you want, and update their bounding boxes in the `[BB].txt` file.
Then run `py main.py fontPATCH <file name>`

# Inspired by these tools

[yukinogatari/Danganronpa-Tools](https://github.com/yukinogatari/Danganronpa-Tools)

[jpmac26/DRV3-Tools](https://github.com/jpmac26/DRV3-Tools)

[jpmac26/DRV3-Sharp](https://github.com/jpmac26/DRV3-Sharp)

[ThunderGemios10/The-Super-Duper-Script-Editor](https://github.com/ThunderGemios10/The-Super-Duper-Script-Editor)
