# Five map archetypes

Every trip map is one of these five. Copy the nearest one and change the numbers. The coordinates below are from a
fictional Stockholm trip and a Berlin–Stockholm flight; `scripts/mockdata.py` generates the data they read.

Common preamble for all of them:

```python
import sys, os; sys.path.insert(0, SCRIPTS)
from mapkit import Proj, load, path, basemap, sea_land, svg_open, he, en, label, split_jumps, INK, GREY, PAPER
import points as P
W, H = 215, 220          # the page, in mm — your coordinate system
ACCENT = '#1F4E8C'       # the one colour that means "us"; everything else is geography
```

---

## 1 · Flight — source → destination

*Berlin → Stockholm, 810 km.* The whole point is the arc and the two names; the geography is background.

```python
s, w, n, e = 29.0, 14.0, 66.0, 42.0
Pj = Proj(s, w, n, e, W, H, fit=True)      # fit: both airports MUST be inside the frame
gj = json.load(open('countries50.geojson'))       # Natural Earth 1:50m — not OSM, see below
body = [svg_open(W, H), f'<rect width="100%" height="100%" fill="#C6D9E0"/>']
for f in gj['features']:
    iso = f['properties'].get('ISO_A3')
    fill = '#DCE5EF' if iso == 'FIN' else '#F1E7D4' if iso == 'ISR' else PAPER   # the two countries that matter
    ...                                            # draw each ring with Pj
pts, km = P.great_circle((32.0114, 34.8867), (60.3172, 24.9633))
body.append(polyline(Pj, pts, stroke=ACCENT, stroke_width=.7, stroke_dasharray='2 1.2'))
body.append(he(*mid, f'{round(km, -1):,.0f} km', size=3.4, color=ACCENT))
```

**Why Natural Earth and not OSM:** at country scale an Overpass query is enormous, slow, and looks wrong — you get
every road in Europe and no sense of a coastline. Natural Earth 1:50m is generalised for exactly this zoom. Get
`ne_50m_admin_0_countries` and credit it.

**The dashed line is doing work.** A solid line reads as a road. A dashed arc reads as a flight, and nobody has to
be told.

**Tint the two countries that matter** and leave every other country the paper colour. The map then answers
"from where to where" before anybody reads a word.

---

## 2 · Region — a whole area, a handful of places

*Airport, city, the day trip out of town.* The map of a week, not a day.

```python
s, w, n, e = 60.10, 24.45, 60.45, 25.25
Pj = Proj(s, w, n, e, W, 120, fit=True)
el = load('osm_region.json')                       # coastline + motorway/trunk + water only
body = [svg_open(W, 120), sea_land(Pj, el, s, w, n, e)]
body.append(basemap(Pj, el, road_w=(('trunk', .5), ('motorway', .7))))
for la, lo, heb, latin, side in PLACES:
    body += [dot(Pj, la, lo), label(Pj, la, lo, heb, latin, side=side)]
body.append(scalebar(Pj, W, 120, km=10))
```

**Ask Overpass for less.** A region box with every secondary road times out or comes back rate-limited. Coastline,
motorway, trunk, water — that is the whole map at this scale.

**`side` per label, chosen by eye.** Automatic label placement is a research problem; five places is a five-minute
job. Put the name on the side with room and move on.

---

## 3 · City walk — a day on foot

*Any dense city centre.* The archetype that carries the most meaning, because it is
literally the route somebody walked.

```python
el = load('osm_helsinki.json')
Pj = Proj(s, w, n, e, W, H, fit=False)             # fill the page; the crop is fine here
body = [svg_open(W, H), sea_land(Pj, el, s, w, n, e), basemap(Pj, el)]
pts = P.walking_points('export.json', tz='Europe/Stockholm', day='2024-07-16')
for run in split_jumps(pts, km=1.0):               # tram and ferry gaps become gaps, not lines
    body.append(polyline(Pj, run, stroke=ACCENT, stroke_width=.8, stroke_linecap='round'))
for la, lo in P.exif_points(photos, day='2024-07-16'):
    body.append(dot(Pj, la, lo, r=.9, fill='#fff', stroke=ACCENT))   # where a picture was taken
```

**Two layers, two meanings:** the line is where you walked, the dots are where you stopped to look. Drawn together
they explain a day better than either alone, and the dots come free from the photographs.

**Filter to WALKING or the map is jitter.** This is the single biggest difference between a good city map and a
scribble. See `walking_points()`.

**Don't label every street.** Three or four names, chosen because somebody in the family would say them.

---

## 4 · Island and coast

*A fortress island, a harbour, an archipelago.* Anywhere the water is most of the picture.

```python
el = load('osm_suomenlinna.json')                  # fetch_osm.sh always asks for coastline
Pj = Proj(s, w, n, e, W, H, fit=True)
body = [svg_open(W, H), sea_land(Pj, el, s, w, n, e)]   # ← does the whole job
body.append(basemap(Pj, el, road_w=()))            # no roads on a small island; footpaths if you asked for them
body.append(polyline(Pj, ferry_pts, stroke=ACCENT, stroke_dasharray='1.6 1.2'))   # the crossing, dashed
```

**`sea_land` is the archetype.** Without it the island is invisible — everything is land. With it you get the
shoreline, every islet, and the holes in between, from the same coastline ways.

**Needs `shapely`.** It is the one non-standard dependency and it is worth it; the alternative is hand-tracing.

---

## 5 · Route — a drive between two places

*A day's drive between two towns.* Longer than a walk, shorter than a flight, and the
shape of the road matters.

```python
pts = [p for d, v in P.timeline_days('export.json', tz).items() if d == '2026-07-26' for p in v]
s, w, n, e = P.bbox(pts, pad=0.15)
Pj = Proj(s, w, n, e, W, 150, fit=True)
el = load('osm_corridor.json')                     # motorway + trunk + water for the corridor bbox
body = [svg_open(W, 150), basemap(Pj, el, road_w=(('motorway', .8), ('trunk', .5)))]
body.append(polyline(Pj, pts, stroke=ACCENT, stroke_width=1.0))
body.append(he(x, y, f'{P.total_km(pts):.0f} km', size=3.6, color=ACCENT))
```

**Use the real recorded track, not a routing engine.** A routing API gives the road somebody *should* have taken;
the Timeline gives the one they did, including the wrong turn and the stop for petrol. On a personal map the
second is the point.

**Label the two ends and nothing in between**, unless something happened in the middle.

---

## Furniture, for all five

```python
body.append(frame(W, H))                                        # a 0.3 mm keyline makes it a map, not a shape
body.append(scalebar(Pj, W, H, km=2, label='2 km'))
body.append(en(W - 2.5, H - 2.2, '© OpenStreetMap contributors', size=1.9, anchor='end', color=GREY))
body.append('</svg>')
save('helsinki', ''.join(body), W, H)                           # → .svg, then render.sh → .png
```

Attribution is required by the ODbL for OSM data and asked for by Natural Earth. It is also the line that makes a
drawing look like it came from somewhere real.
