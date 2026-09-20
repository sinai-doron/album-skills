"""Shared map drawing: OSM json → SVG in mm, plus timeline paths.
Colours come from the album accent; text is Hebrew-safe because rendering goes through Chrome."""
import json, math, os, zoneinfo
from datetime import datetime
R=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..'))
PAPER='#F6F4EF'; INK='#23292d'; GREY='#4d565c'   # not a true grey: small type prints muddy below ~60% ink, so the
                                                 # 'quiet' label colour is a dark slate, not the old #8f9599
def load(osm):
    return json.load(open(os.path.join(os.path.dirname(__file__),osm)))['elements']
class Proj:
    def __init__(self, s,w,n,e, W_MM,H_MM, fit=True, margin=0.0):
        self.s,self.w,self.n,self.e=s,w,n,e
        kx=math.cos(math.radians((s+n)/2))
        span_x=(e-w)*kx; span_y=n-s
        f=min if fit else max
        self.sc=(1-margin)*f(W_MM/span_x, H_MM/span_y)
        self.kx=kx
        self.ox=(W_MM-span_x*self.sc)/2; self.oy=(H_MM-span_y*self.sc)/2
    def __call__(self, lat, lon):
        return ((lon-self.w)*self.kx*self.sc+self.ox, (self.n-lat)*self.sc+self.oy)
def path(P, pts, close=False):
    d='M'+' L'.join(f'{x:.2f},{y:.2f}' for x,y in (P(p['lat'],p['lon']) for p in pts))
    return d+(' Z' if close else '')
def rings(ways):
    segs=[w[:] for w in ways if len(w)>1]; out=[]
    key=lambda p:(round(p['lat'],7),round(p['lon'],7))
    while segs:
        ring=segs.pop(); changed=True
        while key(ring[0])!=key(ring[-1]) and changed:
            changed=False
            for i,sg in enumerate(segs):
                if key(sg[0])==key(ring[-1]): ring+=sg[1:]
                elif key(sg[-1])==key(ring[-1]): ring+=sg[::-1][1:]
                elif key(sg[-1])==key(ring[0]): ring=sg+ring[1:]
                elif key(sg[0])==key(ring[0]): ring=sg[::-1]+ring[1:]
                else: continue
                segs.pop(i); changed=True; break
        out.append(ring)
    return out
def basemap(P, elements, road_w=(('secondary',.35),('primary',.6),('trunk',.8),('motorway',.9))):
    water=[];parks=[];roads={}
    for el in elements:
        t=el.get('tags',{})
        if el['type']=='way':
            g=el['geometry']
            if t.get('natural')=='water' or t.get('waterway')=='riverbank': water.append(path(P,g,True))
            elif t.get('leisure')=='park': parks.append(path(P,g,True))
            elif 'highway' in t: roads.setdefault(t['highway'],[]).append(path(P,g))
        else:
            outer=[m['geometry'] for m in el.get('members',[]) if m.get('role')=='outer' and 'geometry' in m]
            inner=[m['geometry'] for m in el.get('members',[]) if m.get('role')=='inner' and 'geometry' in m]
            d=' '.join(path(P,r,True) for r in rings(outer)+rings(inner))
            (water if t.get('natural')=='water' else parks).append(d)
    out=[f'<g fill="#E3E9DD" fill-rule="evenodd">'+''.join(f'<path d="{d}"/>' for d in parks)+'</g>',
         f'<g fill="#C6D9E0" fill-rule="evenodd">'+''.join(f'<path d="{d}"/>' for d in water)+'</g>']
    for hw,wd in road_w:
        if hw in roads:
            out.append(f'<g fill="none" stroke="#E2DDD3" stroke-width="{wd}" stroke-linecap="round">'+''.join(f'<path d="{d}"/>' for d in roads[hw])+'</g>')
    return ''.join(out)
def timeline_days(extract, tz='America/New_York'):
    """{date: [(lat,lon), …]} from timelinePath segments"""
    Z=zoneinfo.ZoneInfo(tz); days={}
    for sgm in json.load(open(extract))['semanticSegments']:
        if 'timelinePath' not in sgm: continue
        day=datetime.fromisoformat(sgm['startTime']).astimezone(Z).strftime('%Y-%m-%d')
        pts=[]
        for p in sgm['timelinePath']:
            lat,lon=[float(x.strip().rstrip('°')) for x in p['point'].split(',')]
            pts.append((lat,lon))
        days.setdefault(day,[]).extend(pts)
    return days
def svg_open(W,H): return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}"><rect width="100%" height="100%" fill="{PAPER}"/>'
def he(x,y,txt,size=4.2,color=INK,anchor='start',weight=500,halo=PAPER):
    a={'start':'end','end':'start','middle':'middle'}[anchor]   # RTL flips start/end
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="Heebo" font-weight="{weight}" font-size="{size}" fill="{color}" '
            f'text-anchor="{a}" direction="rtl" paint-order="stroke" stroke="{halo}" stroke-width="{size*0.14:.2f}" stroke-linejoin="round">{txt}</text>')
def en(x,y,txt,size=4.2,color=GREY,anchor='start',weight=500,ls=0,halo=PAPER):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="Arimo" font-weight="{weight}" font-size="{size}" fill="{color}" '
            f'text-anchor="{anchor}" letter-spacing="{ls}" paint-order="stroke" stroke="{halo}" stroke-width="{size*0.14:.2f}">{txt}</text>')

# ---- sea cities, labels beside dots, and walks that are actually walks ----
def label(P, la, lo, heb, latin='', side='right', dx=2.4, size=3.6, color=INK):
    """Hebrew name with a small Latin name under it, beside a dot. side is where the text sits VISUALLY.
    he() already flips start/end for RTL — pass the visual anchor straight through. Flipping it a second time here
    put every right-to-left label on top of its own dot."""
    x, y = P(la, lo)
    anchor = {'right': 'start', 'left': 'end', 'middle': 'middle'}[side]
    x += dx if side == 'right' else -dx if side == 'left' else 0
    return he(x, y, heb, size=size, anchor=anchor, weight=600, color=color) + \
        (en(x, y + size * .95, latin, size=size * .62, anchor=anchor) if latin else '')
def sea_land(P, elements, s, w, n, e, sea='#C6D9E0', land=PAPER):
    """Sea background + land polygons built from coastline ways (coast.py). Fetch with fetch_osm.sh (asks for coastline)."""
    from coast import land as _land, poly_path
    return f'<rect width="100%" height="100%" fill="{sea}"/><g fill="{land}">' + \
        ''.join(f'<path d="{poly_path(P, p)}"/>' for p in _land(elements, s, w, n, e)) + '</g>'
def split_jumps(pts, km=1.0):
    """[(lat,lon)] → runs, broken wherever two consecutive points are further apart than km: a ferry or a tram
    between two walks is not drawn as a line across the water."""
    runs = [[pts[0]]] if pts else []
    for a, b in zip(pts, pts[1:]):
        d = 111.2 * math.hypot(b[0] - a[0], (b[1] - a[1]) * math.cos(math.radians(a[0])))
        (runs[-1].append(b) if d < km else runs.append([b]))
    return [r for r in runs if len(r) > 1]
def activity_windows(extract, kinds=('WALKING',), tz='UTC'):
    """[(start, end, type)] of Timeline activities, local naive datetimes. The raw timelinePath is every movement —
    drawn as-is, a city map was a tangle of GPS jitter and ferry spikes; keeping only points inside WALKING windows
    made it a map of walks. The same list settles a day's shape: train, bus, then 4.1 km on foot."""
    Z = zoneinfo.ZoneInfo(tz); out = []
    for s in json.load(open(extract))['semanticSegments']:
        t = ((s.get('activity') or {}).get('topCandidate') or {}).get('type')
        if t in kinds:
            out.append((datetime.fromisoformat(s['startTime']).astimezone(Z).replace(tzinfo=None),
                        datetime.fromisoformat(s['endTime']).astimezone(Z).replace(tzinfo=None), t))
    return out
