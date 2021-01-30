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
- fix formatting commands like <CLT = cltMIND>
- fix font, missing áéíóú ñ
- write tests stx -> txt -> stx