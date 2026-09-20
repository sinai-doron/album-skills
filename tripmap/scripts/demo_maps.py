"""Draw the example maps in this repo from the fictional Stockholm trip.

This is the worked example the recipes describe, end to end: mock Timeline in, printable maps out. Run it and you
get the same PNGs that are committed under examples/ — which is the point, since nothing here depends on anybody's
real movements.

    python3 scripts/mockdata.py                       # the trip
    ./scripts/fetch_osm.sh stockholm 59.310 18.020 59.350 18.130
    mv scripts/osm_stockholm.json example-data/
    python3 scripts/demo_maps.py                      # the maps

Natural Earth 1:50m countries (public domain) is needed for the flight map:
  https://www.naturalearthdata.com/downloads/50m-cultural-vectors/  → example-data/countries50.geojson
"""
import json, math, os, sys, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, '..'))
DATA = os.path.join(ROOT, 'example-data')
OUT = os.path.join(ROOT, 'examples')
os.makedirs(OUT, exist_ok=True)

from mapkit import Proj, path as spath, basemap, svg_open, en, INK, GREY, PAPER
import points as P
import coast

TZ = 'Europe/Stockholm'
ACCENT = '#1F6FB2'          # one colour means "us"; everything else is geography
SEA = '#C6D9E0'
TL = os.path.join(DATA, 'timeline.json')


def polyline(Pj, pts, **kw):
    d = 'M' + ' L'.join(f'{x:.2f},{y:.2f}' for x, y in (Pj(la, lo) for la, lo in pts))
    a = ' '.join(f'{k.replace("_", "-")}="{v}"' for k, v in kw.items())
    return f'<path d="{d}" fill="none" {a}/>'


def dot(Pj, la, lo, r=1.0, fill=ACCENT, stroke='none', sw=0):
    x, y = Pj(la, lo)
    return f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def scalebar(Pj, x, y, km_len, label):
    x0, y0 = Pj(*Pj.inv(x, y)) if hasattr(Pj, 'inv') else (x, y)
    # a bar of km_len at this latitude, in mm
    lat = Pj.s + (Pj.n - Pj.s) / 2
    mm = km_len / 111.2 * Pj.kx * Pj.sc
    return (f'<g stroke="{INK}" stroke-width=".35" fill="none">'
            f'<path d="M{x},{y} h{mm:.2f}"/><path d="M{x},{y-1} v2"/><path d="M{x+mm:.2f},{y-1} v2"/></g>'
            + en(x + mm / 2, y - 2.2, label, size=2.8, anchor='middle', color=INK))


def frame(W, H):
    return f'<rect x=".3" y=".3" width="{W-.6}" height="{H-.6}" fill="none" stroke="{INK}" stroke-width=".3"/>'


def save(name, svg, W, H, px_per_mm=300 / 25.4):
    p = os.path.join(OUT, name + '.svg')
    open(p, 'w').write(svg)
    png = os.path.join(OUT, name + '.png')
    subprocess.run([os.path.join(HERE, 'render.sh'), p, png,
                    str(round(W * px_per_mm)), str(round(H * px_per_mm))], check=True)
    print(f'  {name}.png  {round(W*px_per_mm)}×{round(H*px_per_mm)} px  ({W}×{H} mm at 300 DPI)')


# ---------------------------------------------------------------- 1 · flight
def flight():
    gj = os.path.join(DATA, 'countries50.geojson')
    if not os.path.exists(gj):
        print('  (skipping flight: put Natural Earth countries50.geojson in example-data/ — see the docstring)')
        return
    W, H = 180, 200
    s, w, n, e = 44.0, 2.0, 66.0, 32.0
    Pj = Proj(s, w, n, e, W, H, fit=True)      # fit: BOTH airports must be inside the frame
    body = [svg_open(W, H), f'<rect width="100%" height="100%" fill="{SEA}"/>']
    for f in json.load(open(gj))['features']:
        g = f['geometry']; iso = f['properties'].get('ISO_A3') or f['properties'].get('ADM0_A3')
        polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
        fill = '#DCE5EF' if iso == 'SWE' else '#F1E7D4' if iso == 'DEU' else PAPER
        d = ''.join('M' + ' L'.join(f'{Pj(la, lo)[0]:.2f},{Pj(la, lo)[1]:.2f}' for lo, la in ring) + 'Z'
                    for poly in polys for ring in poly)
        body.append(f'<path d="{d}" fill="{fill}" stroke="#C9C2B4" stroke-width=".18" fill-rule="evenodd"/>')
    ber, arn = (52.3667, 13.5033), (59.6519, 17.9186)
    pts, km = P.great_circle(ber, arn)
    body.append(polyline(Pj, pts, stroke=ACCENT, stroke_width=.7, stroke_dasharray='2 1.2', stroke_linecap='round'))
    for p, name in ((ber, 'BERLIN'), (arn, 'STOCKHOLM')):
        body.append(dot(Pj, *p, r=1.5))
        x, y = Pj(*p)
        body.append(en(x + 3, y + .8, name, size=3.6, weight=700, color=INK, ls=.6))
    mx, my = Pj(*pts[len(pts) // 2])
    body.append(en(mx + 3, my, f'{km:,.0f} km', size=3.0, color=ACCENT, weight=600))
    body += [frame(W, H), en(W - 2.5, H - 2.2, 'Natural Earth', size=1.9, anchor='end', color=GREY), '</svg>']
    save('mock-01-flight-berlin-stockholm', ''.join(body), W, H)


# ---------------------------------------------------------------- 2 · city walk
def city():
    osm = os.path.join(DATA, 'osm_stockholm.json')
    if not os.path.exists(osm):
        print('  (skipping city: run fetch_osm.sh — see the docstring)')
        return
    W, H = 200, 150
    s, w, n, e = 59.313, 18.032, 59.345, 18.125
    Pj = Proj(s, w, n, e, W, H, fit=False)     # fill the page; a city map may crop
    el = json.load(open(osm))['elements']
    body = [svg_open(W, H), f'<rect width="100%" height="100%" fill="{SEA}"/>']
    # the sea is whatever the coastline leaves over — without this, Stockholm is solid land
    body.append(f'<g fill="{PAPER}">' + ''.join(
        f'<path d="{coast.poly_path(Pj, p)}"/>' for p in coast.land(el, s, w, n, e)) + '</g>')
    body.append(basemap(Pj, el))
    walked = 0.0
    for day in ('2024-07-15', '2024-07-16', '2024-07-18'):
        pts = P.walking_points(TL, tz=TZ, day=day)
        for run in P.runs(pts, 1.0):           # break where the GPS jumps: a ferry is not a walk
            body.append(polyline(Pj, run, stroke=ACCENT, stroke_width=.75,
                                 stroke_linecap='round', stroke_linejoin='round', opacity=.85))
        walked += P.track_km(pts, 1.0)
    for la, lo in P.exif_points(os.path.join(DATA, 'photos.csv')):
        if s < la < n and w < lo < e:
            body.append(dot(Pj, la, lo, r=.75, fill='#fff', stroke=ACCENT, sw=.3))
    body.append(en(5, 9, 'STOCKHOLM', size=6.5, weight=700, color=INK, ls=1.4))
    body.append(en(5, 14, f'three days on foot · {walked:.1f} km · dots are photographs', size=3.0, color=GREY))
    body.append(scalebar(Pj, 5, H - 8, 1, '1 km'))
    body += [frame(W, H), en(W - 2.5, H - 2.2, '© OpenStreetMap contributors', size=1.9, anchor='end', color=GREY), '</svg>']
    save('mock-02-citywalk-stockholm', ''.join(body), W, H)


# ---------------------------------------------------------------- 3 · the day, as stops
def day_stops():
    W, H = 200, 150
    s, w, n, e = 59.313, 18.032, 59.345, 18.125
    osm = os.path.join(DATA, 'osm_stockholm.json')
    if not os.path.exists(osm): return
    Pj = Proj(s, w, n, e, W, H, fit=False)
    el = json.load(open(osm))['elements']
    body = [svg_open(W, H), f'<rect width="100%" height="100%" fill="{SEA}"/>',
            f'<g fill="{PAPER}">' + ''.join(f'<path d="{coast.poly_path(Pj, p)}"/>'
                                            for p in coast.land(el, s, w, n, e)) + '</g>',
            basemap(Pj, el)]
    names = {(round(p['lat'], 4), round(p['lon'], 4)): p['name']
             for p in json.load(open(os.path.join(DATA, 'itinerary.json')))['places_photographed']}
    # Two stops 150 m apart put their labels on top of each other. Nothing clever here — try the right, then the
    # left, then above and below, and take the first placement that does not overlap a label already down. Five
    # labels is a five-minute problem; automatic label placement in general is a research field.
    placed = []
    def free(bx):
        return all(not (bx[0] < q[2] and q[0] < bx[2] and bx[1] < q[3] and q[1] < bx[3]) for q in placed)
    for a, b, la, lo, mins in sorted(P.visits(TL, tz=TZ, min_minutes=20), key=lambda v: -v[4]):
        if not (s < la < n and w < lo < e): continue
        r = 1.1 + min(mins, 120) / 120 * 2.2        # a longer stop is a bigger dot: time made visible
        body.append(dot(Pj, la, lo, r=r, fill=ACCENT, stroke='#fff', sw=.4))
        nm = names.get((round(la, 4), round(lo, 4)), '')
        if not nm: continue
        x, y = Pj(la, lo)
        wmm = len(nm) * 1.6 + 2                      # rough advance width at 3 mm type
        for anchor, ox, oy in (('start', r + 1.4, 0), ('end', -(r + 1.4), 0),
                               ('start', r + 1.4, -5.5), ('end', -(r + 1.4), -5.5),
                               ('start', r + 1.4, 5.5), ('end', -(r + 1.4), 5.5)):
            bx = (x + ox - (wmm if anchor == 'end' else 0), y + oy - 3.2,
                  x + ox + (0 if anchor == 'end' else wmm), y + oy + 3.6)
            if free(bx): break
        placed.append(bx)
        body.append(en(x + ox, y + oy - .4, nm, size=3.0, weight=600, color=INK, anchor=anchor))
        body.append(en(x + ox, y + oy + 3.0, f'{mins} min', size=2.5, color=GREY, anchor=anchor))
    body.append(en(5, 9, 'WHERE THE TIME WENT', size=5.5, weight=700, color=INK, ls=1.2))
    body.append(en(5, 14, 'every stop of twenty minutes or more · the circle is how long', size=3.0, color=GREY))
    body += [frame(W, H), en(W - 2.5, H - 2.2, '© OpenStreetMap contributors', size=1.9, anchor='end', color=GREY), '</svg>']
    save('mock-03-stops-stockholm', ''.join(body), W, H)


if __name__ == '__main__':
    print('drawing from the fictional Stockholm trip:')
    flight(); city(); day_stops()
