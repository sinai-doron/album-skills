"""The three ways a trip becomes points on a map: a Timeline export, photo EXIF, and a pair of place names.

Each returns plain [(lat, lon)] or {date: [(lat, lon)]}, so the drawing code never cares where a route came from.
Neither source is exact and both are real: the Timeline is a phone's best guess, EXIF is where the camera thought
it was. Drawn together they agree often enough to be worth trusting, and where they disagree the photos win —
a photo has a picture attached to prove it.

    python3 points.py timeline <export.json> --tz Europe/Stockholm [--walking]
    python3 points.py exif <photo-dir-or-scores.csv> [--day 2023-07-09]
    python3 points.py route "Berlin" "Stockholm"
"""
import json, math, os, sys, csv, glob, subprocess, zoneinfo
from datetime import datetime

EARTH_KM = 6371.0088


# ---------------------------------------------------------------- 1. Google Timeline
def timeline_days(export, tz='UTC'):
    """{date: [(lat, lon), …]} from the timelinePath of every segment.

    This is every movement the phone recorded, which is more than you want: drawn raw, a city day is a tangle of
    GPS jitter and spikes out to sea where a ferry or a tram was. Use walking_points() for a map of walks.
    """
    Z = zoneinfo.ZoneInfo(tz); days = {}
    for sgm in json.load(open(export))['semanticSegments']:
        if 'timelinePath' not in sgm: continue
        day = datetime.fromisoformat(sgm['startTime']).astimezone(Z).strftime('%Y-%m-%d')
        for p in sgm['timelinePath']:
            lat, lon = [float(x.strip().rstrip('°')) for x in p['point'].split(',')]
            days.setdefault(day, []).append((lat, lon))
    return days


def activity_windows(export, kinds=('WALKING',), tz='UTC'):
    """[(start, end, type)] for activities of the given kinds, as local naive datetimes.

    The Timeline labels each segment with how you were moving. Keeping only the points that fall inside WALKING
    windows is what turns a scribble into a map of where somebody actually walked — and the same list answers
    "what shape was this day": train, bus, then 4.1 km on foot.
    """
    Z = zoneinfo.ZoneInfo(tz); out = []
    for s in json.load(open(export))['semanticSegments']:
        t = ((s.get('activity') or {}).get('topCandidate') or {}).get('type')
        if t in kinds:
            out.append((datetime.fromisoformat(s['startTime']).astimezone(Z).replace(tzinfo=None),
                        datetime.fromisoformat(s['endTime']).astimezone(Z).replace(tzinfo=None), t))
    return out


def walking_points(export, tz='UTC', kinds=('WALKING',), day=None):
    """Timeline points that fall inside an activity window of the given kinds."""
    Z = zoneinfo.ZoneInfo(tz)
    wins = activity_windows(export, kinds, tz)
    out = []
    for sgm in json.load(open(export))['semanticSegments']:
        if 'timelinePath' not in sgm: continue
        for p in sgm['timelinePath']:
            t = datetime.fromisoformat(p['time']).astimezone(Z).replace(tzinfo=None)
            if day and t.strftime('%Y-%m-%d') != day: continue
            if any(a <= t <= b for a, b, _ in wins):
                lat, lon = [float(x.strip().rstrip('°')) for x in p['point'].split(',')]
                out.append((lat, lon))
    return out


def visits(export, tz='UTC', min_minutes=12):
    """[(start, end, lat, lon, minutes)] for stops — the places the day was actually spent.

    A stop is where the story is; the path between stops is just transport. The export carries coordinates and no
    names — see geocode.py to name them, and read its privacy note before you do.
    """
    Z = zoneinfo.ZoneInfo(tz); out = []
    for s in json.load(open(export))['semanticSegments']:
        v = s.get('visit')
        if not v: continue
        p = ((v.get('topCandidate') or {}).get('placeLocation') or {}).get('latLng')
        if not p: continue
        lat, lon = [float(x.strip().rstrip('°')) for x in p.split(',')]
        a = datetime.fromisoformat(s['startTime']).astimezone(Z).replace(tzinfo=None)
        b = datetime.fromisoformat(s['endTime']).astimezone(Z).replace(tzinfo=None)
        mins = (b - a).total_seconds() / 60
        if mins >= min_minutes: out.append((a, b, lat, lon, round(mins)))
    return out


# ---------------------------------------------------------------- 2. photo EXIF
def exif_points(src, day=None, tz=None):
    """[(lat, lon)] from the photographs themselves, in time order.

    `src` is a folder of photos, or a CSV with lat/lon/time columns (e.g. one you already built while culling).
    Photo GPS is sparse — one point per picture — but every point is a place somebody stood long enough to take
    a picture, which is exactly the set of places worth drawing. Where the Timeline and the photos disagree,
    believe the photos.
    """
    rows = []
    if os.path.isdir(src):
        j = subprocess.run(['exiftool', '-json', '-n', '-GPSLatitude', '-GPSLongitude',
                            '-DateTimeOriginal', '-r', src], capture_output=True, text=True).stdout
        for r in json.loads(j or '[]'):
            if r.get('GPSLatitude') is None: continue
            rows.append((r.get('DateTimeOriginal', ''), float(r['GPSLatitude']), float(r['GPSLongitude'])))
    else:
        for r in csv.DictReader(open(src)):
            if not r.get('lat'): continue
            rows.append((r.get('time', ''), float(r['lat']), float(r['lon'])))
    rows.sort()
    if day:
        d = day.replace('-', ':')
        rows = [r for r in rows if r[0][:10] == d or r[0][:10] == day]
    return [(la, lo) for _, la, lo in rows]


def exif_days(src):
    """{date: [(lat, lon)]} — the same, split by day."""
    out = {}
    if os.path.isdir(src):
        j = subprocess.run(['exiftool', '-json', '-n', '-GPSLatitude', '-GPSLongitude',
                            '-DateTimeOriginal', '-r', src], capture_output=True, text=True).stdout
        src_rows = [(r.get('DateTimeOriginal', ''), r.get('GPSLatitude'), r.get('GPSLongitude'))
                    for r in json.loads(j or '[]')]
    else:
        src_rows = [(r.get('time', ''), r.get('lat'), r.get('lon')) for r in csv.DictReader(open(src))]
    for t, la, lo in sorted(src_rows):
        if la in (None, '') or not t: continue
        out.setdefault(t[:10].replace(':', '-'), []).append((float(la), float(lo)))
    return out


# ---------------------------------------------------------------- 3. source → destination
def great_circle(a, b, k=64):
    """([(lat, lon)], km) — the real path between two points on a sphere.

    A straight line between two places on a flat map is not the way anything travels, and over any distance worth
    drawing it looks wrong: the arc bends toward the pole. Draw the arc and label the distance; both come from the
    same call, so the number on the page can never disagree with the line.
    """
    la1, lo1, la2, lo2 = map(math.radians, (*a, *b))
    d = 2 * math.asin(math.sqrt(math.sin((la2 - la1) / 2) ** 2 +
                                math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2))
    if d == 0: return [a, b], 0.0
    pts = []
    for i in range(k + 1):
        f = i / k
        A = math.sin((1 - f) * d) / math.sin(d); B = math.sin(f * d) / math.sin(d)
        x = A * math.cos(la1) * math.cos(lo1) + B * math.cos(la2) * math.cos(lo2)
        y = A * math.cos(la1) * math.sin(lo1) + B * math.cos(la2) * math.sin(lo2)
        z = A * math.sin(la1) + B * math.sin(la2)
        pts.append((math.degrees(math.atan2(z, math.hypot(x, y))), math.degrees(math.atan2(y, x))))
    return pts, d * EARTH_KM


def bbox(points, pad=0.12):
    """(s, w, n, e) around a set of points, with a margin — what to pass to Proj and to fetch_osm.sh."""
    la = [p[0] for p in points]; lo = [p[1] for p in points]
    dla = (max(la) - min(la)) or 0.01; dlo = (max(lo) - min(lo)) or 0.01
    return (min(la) - dla * pad, min(lo) - dlo * pad, max(la) + dla * pad, max(lo) + dlo * pad)


def km(a, b):
    """Great-circle distance in km between two (lat, lon)."""
    return great_circle(a, b, k=2)[1]


def total_km(pts):
    """Straight sum. Only meaningful for points you know are one continuous track."""
    return sum(km(a, b) for a, b in zip(pts, pts[1:]))


def runs(pts, max_jump_km=1.0):
    """Split a point list wherever the gap is bigger than a person could have moved between samples.

    Mixing two days, or a photo whose GPS is wrong, or a ferry between two walks, all produce one enormous leg.
    Summing straight through it gives distances like "3,381 km walked", which is the kind of number that is
    obviously wrong on a page and quietly wrong in a caption.
    """
    if not pts: return []
    out = [[pts[0]]]
    for a, b in zip(pts, pts[1:]):
        (out[-1].append(b) if km(a, b) <= max_jump_km else out.append([b]))
    return [r for r in out if len(r) > 1]


def track_km(pts, max_jump_km=1.0):
    """Distance actually travelled along the ground, ignoring jumps. This is the number to print."""
    return sum(total_km(r) for r in runs(pts, max_jump_km))


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    args = sys.argv[2:]
    def opt(name, default=None):
        return args[args.index(name) + 1] if name in args else default
    if cmd == 'timeline':
        tz = opt('--tz', 'UTC')
        if '--walking' in args:
            pts = walking_points(args[0], tz)
            r = runs(pts, 1.0)
            print(f'{len(pts)} walking points in {len(r)} separate walks, {track_km(pts, 1.0):.1f} km on foot')
            print('(a straight sum would say %.0f km — it would be counting the gaps between walks)' % total_km(pts))
        else:
            d = timeline_days(args[0], tz)
            for k_, v in sorted(d.items()):
                r = runs(v, 2.0)
                gaps = len(r) - 1
                print(f'{k_}  {len(v):5d} points  {track_km(v, 2.0):7.1f} km on the ground'
                      + (f'   ({gaps} jump{"s" if gaps != 1 else ""} not counted — vehicle, or a bad fix)' if gaps else ''))
        for a, b, la, lo, m in visits(args[0], tz):
            print(f'  stop {a:%Y-%m-%d %H:%M}–{b:%H:%M}  {m:4d} min  {la:.5f},{lo:.5f}')
    elif cmd == 'exif':
        day = opt('--day')
        d = exif_days(args[0]) if not day else {day: exif_points(args[0], day)}
        for k_, v in sorted(d.items()):
            r = runs(v, 5.0)
            gaps = len(r) - 1
            print(f'{k_}  {len(v):5d} photos with GPS  {track_km(v, 5.0):7.1f} km between them'
                  + (f'   ({gaps} jump{"s" if gaps != 1 else ""} — travel, or a photo with a bad fix)' if gaps else ''))
    elif cmd == 'route':
        import urllib.parse, urllib.request
        def find(q):
            u = 'https://nominatim.openstreetmap.org/search?' + urllib.parse.urlencode({'q': q, 'format': 'json', 'limit': 1})
            r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'tripmap/1.0'})))
            if not r: raise SystemExit(f'no such place: {q}')
            return float(r[0]['lat']), float(r[0]['lon'])
        a, b = find(args[0]), find(args[1])
        pts, d = great_circle(a, b)
        print(f'{args[0]} {a[0]:.4f},{a[1]:.4f} → {args[1]} {b[0]:.4f},{b[1]:.4f}   {d:,.0f} km, {len(pts)} points')
    else:
        print(__doc__)
