#!/bin/zsh
# render.sh in.svg out.png WIDTHpx HEIGHTpx [transparent]
# Renders through headless Chrome so the local fonts and Hebrew shaping are used (rsvg on macOS ignores fontconfig).
#
# EVERY file in assets/fonts is declared below, under its own basename — so a new album declares a font by
# dropping Rubik.ttf in that folder and naming Rubik in the SVG. A missing @font-face does not fail, it silently
# substitutes a serif: that is how five maps reached a printed proof in the wrong typeface, and the report was
# not "wrong typeface" but "blurred", because at 9 pt hairline serifs are sub-pixel at 300 DPI.
set -e
svg=$1; out=$2; w=$3; h=$4; bg=${5:-opaque}
dir=$(cd $(dirname $0)/.. && pwd); tmp=$(mktemp -d)   # assets/
faces=""
for f in $dir/fonts/*.ttf(N) $dir/fonts/*.otf(N); do
  fam=${${f:t}:r}
  faces+=$'@font-face{font-family:'$fam$';src:url("file://'$f$'");font-weight:100 900}\n'
done
# Fail loudly rather than printing a serif: any family this drawing names must have a file on disk.
for fam in ${(f)"$(grep -oE 'font-family[:=] ?"?[A-Za-z][A-Za-z0-9 _-]*' $svg | sed -E 's/.*[:=] ?"?//' | sort -u)"}; do
  [[ -z $fam || $fam == (serif|sans-serif|monospace|system-ui|ui-monospace|inherit) ]] && continue
  if [[ ! -f $dir/fonts/$fam.ttf && ! -f $dir/fonts/$fam.otf ]]; then
    print -u2 "render.sh: $svg asks for '$fam' but $dir/fonts/$fam.ttf is missing — it would silently print as a serif"
    exit 1
  fi
done
cat > $tmp/page.html <<HTML
<!doctype html><meta charset="utf-8"><style>
$faces
html,body{margin:0;padding:0;background:transparent;width:${w}px;height:${h}px;overflow:hidden}
img,svg{display:block;width:${w}px;height:${h}px}
</style>
$(sed '1{/^<?xml/d;}' $svg)
HTML
flags=()
[[ $bg == transparent ]] && flags=(--default-background-color=00000000)
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --hide-scrollbars \
  --force-device-scale-factor=1 --window-size=$w,$h $flags --virtual-time-budget=3000 \
  --screenshot=$out "file://$tmp/page.html" >/dev/null 2>&1
rm -rf $tmp
