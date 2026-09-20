"""Land polygons from OSM coastline ways, for a sea city.

OSM has no sea polygon: the sea is whatever the coastline leaves over, and a coastline way keeps land on its LEFT.
So: clip every coastline way to the bbox, polygonize them together with the bbox edge, and call a face land when a
point just left of one of its coastline segments falls inside it. Closed islands come out of the same step.
A face with no coastline on its boundary is sea. That is wrong only for a box drawn entirely inland, where there is
no coastline at all — use a plain land background there, since inland lakes arrive as natural=water anyway.
Needs shapely. Verified by eye on a harbour city (174 land faces), a fortress island (36) and a stretch of
archipelago coast (958): the counts are a useful smell test, since a wrong left/right test collapses them to one
or two enormous faces.
"""
import math
from shapely.geometry import LineString, Polygon, box, Point
from shapely.ops import polygonize, unary_union, linemerge

def land(elements, s, w, n, e):
    bb = box(w, s, e, n)
    lines = []
    for el in elements:
        if el['type'] == 'way' and el.get('tags', {}).get('natural') == 'coastline':
            pts = [(p['lon'], p['lat']) for p in el['geometry']]
            if len(pts) > 1: lines.append(LineString(pts))
    if not lines: return []
    merged = linemerge(lines)
    parts = list(merged.geoms) if hasattr(merged, 'geoms') else [merged]
    clipped = [g for p in parts for g in (lambda c: list(c.geoms) if hasattr(c, 'geoms') else [c])(p.intersection(bb))
               if g.length > 0 and g.geom_type == 'LineString']
    faces = list(polygonize(unary_union(clipped + [bb.exterior])))
    # probe points just left (land) of each coastline segment
    probes = []
    kx = math.cos(math.radians((s + n) / 2))
    for ln in clipped:
        c = list(ln.coords)
        for i in range(0, len(c) - 1, max(1, (len(c) - 1) // 6 or 1)):
            (x0, y0), (x1, y1) = c[i], c[i + 1]
            dx, dy = (x1 - x0) * kx, y1 - y0; L = math.hypot(dx, dy)
            if L == 0: continue
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2; eps = 2e-6
            probes.append(Point(mx + (-dy / L) * eps / kx, my + (dx / L) * eps))
    out = []
    for f in faces:
        if any(f.contains(p) for p in probes): out.append(f)
    return out

def poly_path(P, poly):
    """shapely polygon (lon,lat) → SVG path via projection P(lat, lon)"""
    def ring(r):
        return 'M' + ' L'.join(f'{x:.2f},{y:.2f}' for x, y in (P(la, lo) for lo, la in r.coords)) + ' Z'
    return ring(poly.exterior) + ''.join(ring(i) for i in poly.interiors)
