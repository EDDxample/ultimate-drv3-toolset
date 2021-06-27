# Ultimate DRv3 Toolset

Tools I'm using to translate the game to spanish

🚧 Refactor in progress 🚧

## Translation Pipeline
- Extract the .stx files (dialogues) from the .spc file
- Convert (and translate) the .stx files into .json files
- Merge all the .json files (and correct the translations)
- Convert back the .json files to .stx
- Pack everything back into a new .spc file


## Font Patcher

Fonts are split in 2 files: a .srd with character data (misnamed as .stx for some reason) and a .srdv with the glyph texture data.

Right now it's just a set of scripts I call as needed, the output folders are hardcoded and so on.
As I'm too lazy to refactor and generalize the code, let me just explain the process:

- Create a base.srd file with the characters bitflags and offsets you want (1st and 2nd table of the .srd)
- Create the font's .png, srdv and fill base's 3rd table with char bounding boxes (BBs)
- If the character is not in the target font, you'll get an `[ERROR].png` highlighting the missing chars and a text file with all the character BBs
- Finally, by replacing the `[ERROR]` images with `[FIX]` and readjusting the char BBs as needed, you can patch the missing fonts

First of all, as my target font uses ~126 characters, I'm using v3_font03 which has 130 characters as a base, 
so you just have to edit the tables and not the headers / content sizes 
(as long as your highest character is not higher than your base font, otherwise there's a bit count in the first table you should update)




## Inspired by these tools
[yukinogatari/Danganronpa-Tools](https://github.com/yukinogatari/Danganronpa-Tools)

[jpmac26/DRV3-Tools](https://github.com/jpmac26/DRV3-Tools)

[jpmac26/DRV3-Sharp](https://github.com/jpmac26/DRV3-Sharp)

[ThunderGemios10/The-Super-Duper-Script-Editor](https://github.com/ThunderGemios10/The-Super-Duper-Script-Editor)