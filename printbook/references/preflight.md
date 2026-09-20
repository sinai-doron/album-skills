# Preflight — what to check before a browser is opened

Fixing a page after it is placed in an editor costs roughly ten times what fixing it on disk costs. Everything
here is cheap and catches the failures that are invisible on screen.

## The files

| check | why |
|---|---|
| **Every file is the exact pixel size** — trim + bleed × 300 DPI | One wrong page is silently resampled and prints soft. A whole set at the wrong size means re-rendering after upload. |
| **Count matches the page count** and the sequence has no gaps | `page-1 … page-48` with `page-31` missing is not obvious in a tray of thumbnails. |
| **No page is blank or half-rendered** | Measure brightness variance per file: a blank page has almost none. Headless renders fail silently under load. |
| **Contact sheet, looked at by a person** | The only check that catches "this is the right size and completely wrong". |
| **Colour space is sRGB, 8-bit** | A stray CMYK or 16-bit file may be rejected or converted unpredictably. |
| **File size is plausible** | A 40 KB "page" is a rendering failure wearing the right filename. |

```sh
# size and blankness, quickly
for f in print/page-*.jpg; do
  sips -g pixelWidth -g pixelHeight "$f" | tr '\n' ' '; echo " $f"
done
python3 - <<'PY'
from PIL import Image, ImageStat
import glob
for f in sorted(glob.glob('print/page-*.jpg')):
    s = ImageStat.Stat(Image.open(f).convert('L'))
    if s.stddev[0] < 6: print('SUSPECT (nearly flat):', f, round(s.stddev[0], 1))
PY
```

## The design, at printed size

- **Nothing important within ~14 mm of the edge.** Services trim a little off each side and the amount varies
  between copies. Text, faces and stamps live inside that.
- **Nothing important crosses the spine.** The binding eats a few millimetres and no two copies agree.
- **Type not below about 7 pt**, and small type at full black — grey small type plus dot gain prints muddy.
- **Prints come back darker than the screen.** Images can take a 10–15% lift; a texture that is barely visible on
  a monitor may disappear entirely or band.
- **Check one page at 1:1** in the rendered file, not in the design tool. A page can look right in the builder and
  contain an upscaled asset.

## The cover

The cover is not a page. It is a single sheet whose width depends on the page count and the paper, so its aspect
is different from every other file you have rendered.

- Get its exact size from the service's own cover step, after the page count is set.
- Re-render the cover to that size rather than stretching a page-shaped file.
- Check the spine text fits the spine width with room — a thin book has a narrow spine and the text will not
  shrink itself.
