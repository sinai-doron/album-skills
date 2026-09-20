# Data sources — schemas, etiquette, and what each licence makes you print

## Google Timeline export

Get it from the phone (Settings → Location → Timeline → Export) or Google Takeout. The phone export is the useful
one: it is a single JSON, and Takeout splits it by month in a different shape.

```json
{ "semanticSegments": [
  { "startTime": "2023-07-09T08:14:00.000+03:00",
    "endTime":   "2023-07-09T09:02:00.000+03:00",
    "timelinePath": [ { "point": "60.1699°, 24.9384°", "time": "2023-07-09T08:15:00.000+03:00" } ],
    "activity": { "topCandidate": { "type": "WALKING" }, "distanceMeters": 3120 },
    "visit":    { "topCandidate": { "placeLocation": { "latLng": "60.1699°, 24.9384°" } } } } ] }
```

Three things live in here and they are not the same:

- **`timelinePath`** — every recorded position. Noisy. Everything, including the bus.
- **`activity`** — how you were moving for that segment: `WALKING`, `IN_PASSENGER_VEHICLE`, `IN_SUBWAY`, `IN_BUS`,
  `IN_FERRY`, `IN_TRAIN`, `FLYING`, `CYCLING`. Also `distanceMeters`, which is Google's own figure and is more
  trustworthy than summing the jittery path.
- **`visit`** — a stop, with coordinates and no name. This is where the day actually happened.

Note the degree signs inside the coordinate strings, and that times carry an offset. Convert to the trip's local
zone once, at the door, or days will land on the wrong date — a photo at 00:30 belongs to the night before.

**It is the most sensitive file most people own.** Filter to the trip window, keep it out of git, do not upload it.

## Photo EXIF

```bash
exiftool -json -n -GPSLatitude -GPSLongitude -DateTimeOriginal -r ~/Pictures/trip
```

`-n` gives signed decimal degrees instead of `57 deg 38' 56.83" N`, which is what you want. `DateTimeOriginal` is
local clock with no zone — so it agrees with the Timeline only after you have converted the Timeline to the same
zone. **Videos are different**: many cameras write video creation time in UTC, so a video and a photo taken in the
same minute can be hours apart in the file. Offset the videos, not the photos.

Not every photo has GPS: indoor shots, screenshots, anything sent through a messaging app (which strips it), and
anything from a camera without a radio. Sparse is fine — you want the places, not a track.

## Overpass / OpenStreetMap

`fetch_osm.sh NAME S W N E ['extra statements']` does one call. What it asks for by default: coastline, water,
parks, motorway/trunk/primary/secondary, rail.

**Etiquette, and it is enforced.** One call at a time, 30–60 s between calls, a real User-Agent, and `[timeout:240]`
in the query. A too-big box returns HTML that says "rate_limited" or "too busy" — which is why the script checks
the response parses as JSON before claiming success. Parsing an HTML error page as JSON is how you get a map with
no roads and no error.

**Ask for less as the box grows.** City: everything above. Region: coastline, motorway, trunk, water. Country:
don't — use Natural Earth.

Useful extras:

```
way["highway"~"^(footway|path|pedestrian)$"]BBOX;    # a park or an island
way["building"]BBOX;                                  # only for a few blocks; enormous otherwise
node["place"~"^(city|town)$"]BBOX;                    # to label without hard-coding coordinates
relation["route"="ferry"]BBOX;
```

**Licence: ODbL.** Print "© OpenStreetMap contributors" on the map. Not in a credits file — on the map.

## Natural Earth

`ne_50m_admin_0_countries` as GeoJSON, for anything at country scale. Public domain, no restriction, but the
project asks for a credit and it costs one 2 mm line.

`ISO_A3` is the property to key on, though some features carry `ADM0_A3` instead — check both, as the recipe does.

## Nominatim (reverse geocoding)

**Policy, not suggestion:** maximum one request per second, a genuine User-Agent identifying your application, and
no bulk geocoding. Cache on disk — `geocode.py` does, and the cache means a second run asks for nothing.

`zoom` controls granularity: 18 is a building, 17 a street or a named place, 14 a neighbourhood. For "where was
this photo" 17 is usually right; 18 gives you a specific building that is often the one next door.

**The names are hints.** An office on the next street is what comes back for a café terrace. Check them against
the photographs before printing any of them, and prefer what the family actually calls the place.

**And read the privacy note in `geocode.py`.** The trip-centre guard exists because a real home address was once
sent to this service and printed.

## Fonts

Whatever you use, declare it in the renderer. `render.sh` declares the fonts it finds beside it. A missing
`@font-face` substitutes a serif silently, and at map-label sizes that reads as a blurry map, not a wrong font —
five maps shipped that way before anybody worked out what they were looking at.

For Hebrew: Heebo (UI) and Arimo (Helvetica metrics, has Hebrew). Both are open-licensed. Hebrew is never
italicised; use weight or letter-spacing.
