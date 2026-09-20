# Fonts

Two open-licensed families, here so the renderer never has to fall back.

| file | family | licence | why |
|---|---|---|---|
| `Arimo.ttf` | Arimo | Apache 2.0 | Helvetica metrics, and it carries Hebrew as well as Latin — the Latin labels |
| `Heebo.ttf` | Heebo | SIL Open Font License 1.1 (`OFL-Heebo.txt`) | the Hebrew labels |

`render.sh` declares an `@font-face` for every file in this folder, under its own basename, and **refuses to
render** if the drawing names a family with no file here. That check exists because a missing `@font-face` does
not fail — it silently substitutes a serif, and at 9 pt the hairline serifs are sub-pixel at 300 DPI. Five maps
reached a printed proof that way, and the complaint was not "wrong typeface" but "the map is blurry".

To use another family, drop the `.ttf` in this folder and name it in the SVG.
