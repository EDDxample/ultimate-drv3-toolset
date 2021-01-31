# Ultimate DRv3 Toolset

Tools I'm using to translate the game to spanish

## Notes so far
- .stx files = script files, investigation and debate *should* be in there too, only alter those in /007/
- ideal file structure:
  - /input/ch0/0_000_000.stx
  - /output/text/ch0/0_000_000.txt
  - /output/packed/ch0/0_000_000.stx
- this text clips, so about 50 chars is enough:
> Estaba caminando por mi ruta habitual a la escuela cuando

> de repente, alguien me empujó a un coche.

## TODO
- fix font, missing áíóú ñ, é is there for some reason...
- write tests stx -> txt -> stx
- rephrase ~50 chars long comments to multi-line


## Inspired by these tools
[yukinogatari/Danganronpa-Tools](https://github.com/yukinogatari/Danganronpa-Tools)

[jpmac26/DRV3-Tools](https://github.com/jpmac26/DRV3-Tools)

[ThunderGemios10/The-Super-Duper-Script-Editor](https://github.com/ThunderGemios10/The-Super-Duper-Script-Editor)