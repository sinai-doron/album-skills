---
name: tripmap
description: Draw print-quality maps of a real journey from the person's own data — a Google Timeline export, photo EXIF GPS, or just a source and a destination. Produces SVG and 300 DPI PNG with real OpenStreetMap geography, walked routes, named stops, great-circle flight paths, coastlines and labels in any language including Hebrew and Arabic. Use this whenever somebody wants a map of a trip, a walk, a route, a flight, a holiday, a move, a commute or a day out — for a photo book, a poster, a gift, a blog post or a slide — and also whenever they have Timeline/Location History data, a folder of geotagged photos, or a "from X to Y" they want drawn. Prefer it over a screenshot of an online map whenever the output is meant to be printed, styled to match something, or to show where somebody actually went rather than where a road is.
---

# tripmap

A map of a journey is not a screenshot of a map service. It is a drawing with one argument — *this is where we
went* — and everything else on the page exists to make that line legible.

These scripts turn three kinds of personal data into that drawing:

| input | what you get | reader |
|---|---|---|
| **Google Timeline export** | every movement, split by day; walking-only paths; stops of N minutes | `points.py timeline` |
| **Photo EXIF GPS** | the places somebody stood long enough to take a picture | `points.py exif` |
| **Source → destination** | a real great-circle arc and its distance | `points.py route` |

A fourth is worth knowing about because people forget they have it: **named stops**. The Timeline records *where
you stopped and for how long* — and a stop of twenty minutes is the story, while the line between stops is just
transport. `geocode.py visits` names them. Read its privacy note before running it.

## Start here

```bash
S=~/.claude/skills/tripmap/scripts

python3 $S/points.py timeline export.json --tz Europe/Stockholm  # what's in the data, day by day
python3 $S/points.py exif ~/Pictures/trip                         # what the photos know
python3 $S/points.py route "Berlin" "Stockholm"                   # 810 km, 65 points
```

Look at the numbers before drawing anything. A day with 4,000 points and 180 km is a car journey; a day with 300
points and 6 km is a city walk, and they want completely different maps.

Then pick an archetype from `references/recipes.md` — flight, region, city walk, island/coast, or route — and copy
its recipe. Each is a worked example with its own bbox, data source and furniture.

## The pipeline

1. **Get the points.** `points.py` (above). `bbox()` gives you the frame they need.
2. **Get the geography.** `fetch_osm.sh NAME S W N E ['extra']` pulls coastline, water, parks, main roads and rail
   from Overpass into `osm_NAME.json`. For a country-scale map use Natural Earth instead — OSM at that zoom is
   both enormous and wrong-looking.
3. **Draw.** `mapkit.py` gives you `Proj` (equirectangular, cosine-corrected), `basemap`, `sea_land`, `he`/`en`
   text, `label`, `split_jumps`. Compose an SVG in millimetres — the page is the coordinate system, so a 0.34 mm
   line is 0.34 mm on paper whatever the pixel density.
4. **Render.** `render.sh in.svg out.png W_PX H_PX` goes through headless Chrome. For print, W_PX = mm × 300 / 25.4.

## What makes these maps work

**Draw the route from the right source.** The raw `timelinePath` is every movement the phone recorded, and drawn
as-is a city day is a tangle of GPS jitter with spikes out to sea where a ferry was. `walking_points()` keeps only
points inside WALKING activity windows, which is what turns a scribble into a map of where somebody walked.

**Break the line where the GPS jumps.** `split_jumps(pts, km=1.0)` cuts a route wherever two consecutive points
are further apart than a walk could be. Without it a tram ride between two neighbourhoods draws as a straight line
through the buildings, and a ferry draws across the water as if you swam.

**Never sum distance straight down a point list.** Use `track_km()`, which splits at jumps first. Mixing two days,
a photo with a bad fix, or a vehicle leg between two walks all produce one enormous jump, and summing through it
gives numbers like "3,381 km walked" — obviously wrong on a page, quietly wrong in a caption. The same week
through `track_km` reads 45.7 km across 23 separate walks, which is the true and printable figure.

**The sea is not a polygon.** OSM has no sea object — the sea is whatever the coastline leaves over, and a harbour
city drawn without handling it comes out as solid land. `coast.py` clips the coastline ways to the box, polygonises
them with the box edge, and calls a face land when a probe point just to the *left* of a coastline segment falls
inside it (OSM coastline ways keep land on their left, by convention). Islands come out of the same step.

**Fit or fill, and know which you asked for.** `Proj(..., fit=True)` guarantees both endpoints are inside the
frame — that is what a flight map needs. `fit=False` fills the frame and crops, which is what a background texture
needs. A flight map drawn with `fit=False` loses an airport off the edge and nobody notices until it prints.

**Type is the hard part, not the geography.**
- **A halo must be proportional to the type**, about 0.14 em. A fixed 1.2 mm halo closes the counters of O, G, R
  and e at small sizes, and the labels turn to mush.
- **"Quiet grey" prints muddy.** Small type below roughly 60% ink comes back weak and dirty; use a dark slate.
- **Declare every font you use.** A missing `@font-face` does not fail — it silently substitutes a serif, and at
  9 pt the hairline serifs are sub-pixel at 300 DPI, which reads as "the map is blurry" rather than "wrong font".
  `render.sh` declares every font beside it and refuses to render a drawing naming a family with no file on disk.
- **Right-to-left text flips the anchor.** `he()` already swaps start/end for RTL. Pass the *visual* side you want
  and let it do that once — flipping it a second time in your own code puts every label on top of its own dot.
- **Labels collide.** Two stops a hundred metres apart stack. Try right, left, above, below, and take the first
  placement that does not overlap one already down; see `demo_maps.py`.
- Render SVG through Chrome, not `rsvg-convert`: on macOS rsvg ignores fontconfig and silently swaps the font.

**Give the drawing its furniture.** A scale bar, a thin frame, and the attribution. OpenStreetMap data requires
"© OpenStreetMap contributors" on the map; Natural Earth asks for a credit too. It is one 2 mm line and it also
makes the thing look like a map rather than a diagram.

## Privacy — read this before geocoding anything

A Timeline export and a photo roll both cover the days either side of the trip, which means **they contain the
person's home**. A naive script resolves that address through a third-party geocoder and prints the
answer.

So `geocode.py` measures everything against the trip's own centre — the median of the photographs' GPS — and
anything further than 300 km away is never looked up and never named. Home stays a coordinate nobody resolved.
Keep that guard. If somebody asks for a map that includes home, make them say so explicitly, and still do not send
the address to a third party to have it named.

Timeline exports are among the most sensitive files a person owns: years of everywhere they have been. Work on a
filtered copy covering the trip window only, keep it out of version control, and do not upload it anywhere.

## Beyond a photo book

The same three inputs make a lot of things that are not albums, and the archetypes carry over directly:

- **A poster** of a walk, a hike, a race, or the year's runs — one route, heavy paper, no furniture but a scale bar.
- **A gift**: where two people met, walked, and married; a child's first year of places; the streets of a house
  somebody is leaving.
- **A slide or a blog post** — the same SVG at screen resolution, with the line animated by drawing it in segments.
- **A report** where the point is *coverage*: fieldwork visited, properties viewed, deliveries made, sites
  inspected. Stops matter more than paths here, so start from `visits()`.
- **A recap of a move or a commute** — a year of the same journey, drawn once per month, small multiples.

What makes all of these worth doing is the same thing: the person already owns the data, it is about them, and no
map service will ever draw it. The work is the rendering, the judgment and the restraint — not the geography.

## Try it without any real data

`scripts/mockdata.py` generates a fictional four-day trip with the same shape as a real export, and
`scripts/demo_maps.py` draws three maps from it. Use them to check the toolchain works before pointing it at
somebody's actual movements — and as a worked example of all three readers.

## References

- `references/recipes.md` — the five archetypes, each a worked example: flight, region, city walk, island/coast,
  route. Start by copying the nearest one.
- `references/data-sources.md` — Timeline export schema, EXIF fields, Overpass etiquette and query shapes, Natural
  Earth, Nominatim's usage policy, and what each licence requires you to print.

## Scripts

| file | what |
|---|---|
| `points.py` | the three input readers, plus `bbox`, `runs`, `track_km`; runnable for a quick look at any dataset |
| `geocode.py` | names stops and photo places, with the home guard and an on-disk cache |
| `mapkit.py` | projection, basemap, coastline wrapper, RTL/Latin text, labels, `split_jumps`, activity windows |
| `coast.py` | land polygons from OSM coastline ways, for anywhere with a shore |
| `fetch_osm.sh` | one Overpass call for a bbox → `osm_NAME.json` |
| `render.sh` | SVG → PNG through headless Chrome, fonts declared |

Dependencies: `python3` with `shapely` (coastlines only) and `Pillow`; `exiftool` for reading photo GPS; Google
Chrome for rendering. Everything else is standard library.
