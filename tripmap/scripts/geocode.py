"""Turn coordinates into place names — with a guard that keeps somebody's home off the internet.

A Timeline export and a photo roll both cover the days either side of a trip, which means they contain the
traveller's home — and a naive script will send that address to a third-party geocoder and print the answer.
So: everything is measured against the trip's own centre — the median of the photographs' GPS — and anything
further away than `--km` (default 300) is never looked up and never named. Home stays a coordinate nobody
resolved.

Nominatim's policy is one request a second and a real User-Agent, so results are cached on disk and the cache is
the point: run it twice and the second run asks for nothing.

    python3 geocode.py visits <export.json> --tz Europe/Stockholm --photos <dir-or-scores.csv>
    python3 geocode.py points <dir-or-scores.csv>
"""
import json, os, sys, csv, math, time, statistics, urllib.parse, urllib.request, zoneinfo
from datetime import datetime

UA = 'tripmap/1.0 (personal trip map)'
CACHE = os.environ.get('TRIPMAP_CACHE', 'geocode_cache.json')


def _photo_gps(src):
    pts = []
    if os.path.isdir(src):
        import subprocess
        j = subprocess.run(['exiftool', '-json', '-n', '-GPSLatitude', '-GPSLongitude', '-r', src],
                           capture_output=True, text=True).stdout
        for r in json.loads(j or '[]'):
            if r.get('GPSLatitude') is not None: pts.append((float(r['GPSLatitude']), float(r['GPSLongitude'])))
    else:
        for r in csv.DictReader(open(src)):
            if r.get('lat'): pts.append((float(r['lat']), float(r['lon'])))
    return pts


def trip_centre(photos):
    """The median of the photographs' own GPS. Photos define the trip because a photo is evidence you were there;
    a Timeline point is only evidence the phone was on."""
    g = _photo_gps(photos)
    if not g: raise SystemExit('no photo has GPS — without it there is no way to tell the trip from home, '
                               'and nothing will be geocoded')
    return statistics.median(a for a, _ in g), statistics.median(b for _, b in g)


def on_trip(lat, lon, centre, km=300):
    return 111.2 * math.hypot(lat - centre[0], (lon - centre[1]) * math.cos(math.radians(centre[0]))) <= km


def _cache():
    return json.load(open(CACHE)) if os.path.exists(CACHE) else {}


def reverse(lat, lon, zoom=18):
    """One cached Nominatim lookup. Names are hints, not facts: an office on the next street is what comes back
    for a café terrace. Check them against the photographs before any of them is printed."""
    c = _cache(); key = f'{float(lat):.5f},{float(lon):.5f},{zoom}'
    if key in c: return c[key]
    u = 'https://nominatim.openstreetmap.org/reverse?' + urllib.parse.urlencode(
        {'lat': lat, 'lon': lon, 'format': 'jsonv2', 'zoom': zoom, 'accept-language': 'en'})
    r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': UA})))
    a = r.get('address', {})
    out = {'name': r.get('name') or a.get('attraction') or a.get('tourism') or a.get('road') or a.get('suburb') or '',
           'city': a.get('city') or a.get('town') or a.get('village') or a.get('municipality') or '',
           'country': a.get('country', ''), 'display': r.get('display_name', '')}
    c[key] = out; json.dump(c, open(CACHE, 'w'), ensure_ascii=False, indent=1); time.sleep(1.1)
    return out


if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import points as P
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    args = sys.argv[2:]
    def opt(n, d=None): return args[args.index(n) + 1] if n in args else d
    photos = opt('--photos')
    lim = float(opt('--km', 300))
    if not photos: raise SystemExit('--photos <dir or scores.csv> is required: it is what defines the trip, '
                                    'and therefore what keeps home off the wire')
    C = trip_centre(photos)
    if cmd == 'visits':
        rows = P.visits(args[0], opt('--tz', 'UTC'), int(opt('--min', 12)))
        kept = skipped = 0
        for a, b, la, lo, m in rows:
            if not on_trip(la, lo, C, lim): skipped += 1; continue
            r = reverse(la, lo, 17); kept += 1
            print(f'{a:%Y-%m-%d %H:%M}–{b:%H:%M}  {m:4d} min  {r["name"] or r["city"]}  ({r["city"]}, {r["country"]})')
        print(f'\n{kept} stops named, {skipped} outside the trip and deliberately not looked up')
    elif cmd == 'points':
        seen = {}
        for la, lo in P.exif_points(args[0]):
            if not on_trip(la, lo, C, lim): continue
            k = f'{la:.3f},{lo:.3f}'            # ~100 m: one lookup per place, not per photograph
            if k not in seen: seen[k] = reverse(la, lo, 17)
        for k, r in seen.items(): print(f'{k}  {r["name"] or r["city"]}  ({r["country"]})')
        print(f'\n{len(seen)} places')
    else:
        print(__doc__)
