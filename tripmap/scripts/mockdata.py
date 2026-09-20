"""Generate a believable trip — Timeline export, photo GPS, and an itinerary — for demos and tests.

Real trip data is the most sensitive file a person owns, so the examples in this repo are not anybody's. This
writes a fictional four days in Stockholm for a traveller who does not exist: the same shapes as a real export
(timelinePath, activity segments with types and distances, visits with coordinates and no names), so every reader
in points.py is exercised for real, and the maps it produces are the maps the code actually draws.

The route follows genuine streets, quays and ferry lanes — waypoints taken from the map, interpolated at roughly
a point a minute and jittered the way a phone jitters, so a walk looks walked rather than ruled. Seeded, so
everyone regenerates the same trip.

    python3 mockdata.py [outdir]        # default: ../example-data

Stockholm because it has everything the five archetypes need: an arrival by air, a sea city whose coastline is
most of the picture, an island day reached by ferry, a regional excursion, and streets narrow enough that GPS
noise shows.
"""
import json, math, os, random, sys
from datetime import datetime, timedelta

SEED = 20240715
random.seed(SEED)

TZ = '+02:00'                      # Stockholm, summer
HOME = 'Berlin'                    # the fictional traveller flies in from here
BER = (52.3667, 13.5033)           # Berlin Brandenburg
ARN = (59.6519, 17.9186)           # Stockholm Arlanda

# Waypoints along real ways. Each leg: (label, [(lat, lon), …], minutes, activity)
# Hand-placed off the map; the interpolator does the rest.
DAYS = {
 '2024-07-15': [
   ('flight',   [BER, ARN], 95, 'FLYING'),
   ('arlanda express', [ARN, (59.6100, 17.9300), (59.4400, 17.9600), (59.3300, 18.0530)], 20, 'IN_TRAIN'),
   ('to the hotel', [(59.3300, 18.0530), (59.3318, 18.0590), (59.3345, 18.0625)], 11, 'WALKING'),
   ('evening, Gamla Stan', [(59.3345, 18.0625), (59.3310, 18.0640), (59.3258, 18.0710),
                            (59.3243, 18.0718), (59.3237, 18.0700), (59.3250, 18.0665),
                            (59.3280, 18.0648), (59.3345, 18.0625)], 78, 'WALKING'),
 ],
 '2024-07-16': [
   ('Gamla Stan morning', [(59.3345, 18.0625), (59.3290, 18.0660), (59.3254, 18.0705),
                           (59.3246, 18.0724), (59.3252, 18.0745), (59.3268, 18.0733)], 64, 'WALKING'),
   ('over to Djurgården', [(59.3268, 18.0733), (59.3280, 18.0810), (59.3288, 18.0900),
                           (59.3277, 18.0960), (59.3266, 18.1015)], 34, 'WALKING'),
   ('Vasa and Skansen',  [(59.3280, 18.0915), (59.3258, 18.1035), (59.3237, 18.1043),
                          (59.3226, 18.0995), (59.3249, 18.0960)], 96, 'WALKING'),
   ('back along Strandvägen', [(59.3249, 18.0960), (59.3300, 18.0860), (59.3320, 18.0780),
                               (59.3345, 18.0700), (59.3345, 18.0625)], 41, 'WALKING'),
 ],
 '2024-07-17': [
   ('to the quay', [(59.3345, 18.0625), (59.3300, 18.0680), (59.3253, 18.0726)], 15, 'WALKING'),
   ('ferry to Vaxholm', [(59.3253, 18.0726), (59.3290, 18.1400), (59.3450, 18.3000),
                         (59.3800, 18.4200), (59.4020, 18.3540)], 72, 'IN_FERRY'),
   ('Vaxholm on foot', [(59.4020, 18.3540), (59.4038, 18.3505), (59.4055, 18.3480),
                        (59.4041, 18.3441), (59.4022, 18.3470), (59.4020, 18.3540)], 88, 'WALKING'),
   ('ferry back', [(59.4020, 18.3540), (59.3800, 18.4200), (59.3450, 18.3000), (59.3253, 18.0726)], 70, 'IN_FERRY'),
 ],
 '2024-07-18': [
   ('boat to Drottningholm', [(59.3253, 18.0726), (59.3230, 18.0400), (59.3230, 17.9800),
                              (59.3260, 17.9300), (59.3222, 17.8860)], 55, 'IN_FERRY'),
   ('the palace park', [(59.3222, 17.8860), (59.3235, 17.8845), (59.3250, 17.8860),
                        (59.3242, 17.8905), (59.3222, 17.8860)], 74, 'WALKING'),
   ('back to town', [(59.3222, 17.8860), (59.3260, 17.9300), (59.3230, 18.0400), (59.3253, 18.0726)], 55, 'IN_FERRY'),
   ('last walk', [(59.3253, 18.0726), (59.3290, 18.0665), (59.3345, 18.0625)], 17, 'WALKING'),
 ],
}

# Stops: (day, start HH:MM, minutes, lat, lon). Coordinates only — a real export carries no names either.
VISITS = [
 ('2024-07-15', '09:10', 55, *BER), ('2024-07-15', '13:05', 22, *ARN),
 ('2024-07-15', '14:20', 40, 59.3345, 18.0625), ('2024-07-15', '18:40', 64, 59.3243, 18.0718),
 ('2024-07-16', '10:35', 51, 59.3246, 18.0724), ('2024-07-16', '12:15', 118, 59.3280, 18.0915),
 ('2024-07-16', '15:10', 76, 59.3237, 18.1043), ('2024-07-16', '18:05', 44, 59.3320, 18.0780),
 ('2024-07-17', '10:45', 63, 59.4055, 18.3480), ('2024-07-17', '12:30', 47, 59.4041, 18.3441),
 ('2024-07-18', '11:00', 92, 59.3235, 17.8845), ('2024-07-18', '15:40', 38, 59.3290, 18.0665),
]

# What a photograph was of, for the itinerary file. Not in the Timeline — a phone does not know.
PLACES = {
 (59.3243, 18.0718): ('Stortorget', 'Gamla Stan'),
 (59.3246, 18.0724): ('Kungliga slottet', 'the palace'),
 (59.3280, 18.0915): ('Vasamuseet', 'the ship'),
 (59.3237, 18.1043): ('Skansen', ''),
 (59.3320, 18.0780): ('Strandvägen', ''),
 (59.4055, 18.3480): ('Vaxholms kastell', 'the fortress'),
 (59.4041, 18.3441): ('Vaxholm hamn', 'the harbour'),
 (59.3235, 17.8845): ('Drottningholms slott', ''),
}


def interp(a, b, n):
    return [(a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n) for i in range(n)]


def leg_points(waypoints, minutes, activity):
    """One point a minute along the waypoints, with the noise the mode deserves."""
    segs = list(zip(waypoints, waypoints[1:]))
    lens = [math.dist(a, b) or 1e-9 for a, b in segs]
    total = sum(lens)
    pts = []
    for (a, b), L in zip(segs, lens):
        n = max(1, round(minutes * L / total))
        pts += interp(a, b, n)
    pts.append(waypoints[-1])
    # A phone walking in a street canyon wanders a few metres; a plane does not.
    jitter = {'WALKING': 2.2e-4, 'IN_TRAIN': 1.1e-4, 'IN_FERRY': 1.4e-4, 'FLYING': 0.0}[activity]
    return [(la + random.gauss(0, jitter), lo + random.gauss(0, jitter * 1.9)) for la, lo in pts]


def km(a, b):
    return 111.2 * math.hypot(b[0] - a[0], (b[1] - a[1]) * math.cos(math.radians(a[0])))


def build():
    segments, photos, itinerary = [], [], []
    for day, legs in DAYS.items():
        clock = datetime.fromisoformat(f'{day}T08:30:00')
        for label, waypoints, minutes, activity in legs:
            pts = leg_points(waypoints, minutes, activity)
            start, end = clock, clock + timedelta(minutes=minutes)
            segments.append({
                'startTime': start.isoformat() + '.000' + TZ,
                'endTime': end.isoformat() + '.000' + TZ,
                'timelinePath': [
                    {'point': f'{la:.6f}°, {lo:.6f}°',
                     'time': (start + timedelta(minutes=i * minutes / max(1, len(pts) - 1))).isoformat() + '.000' + TZ}
                    for i, (la, lo) in enumerate(pts)],
                'activity': {'topCandidate': {'type': activity},
                             'distanceMeters': round(sum(km(a, b) for a, b in zip(pts, pts[1:])) * 1000)},
            })
            itinerary.append({'day': day, 'leg': label, 'mode': activity, 'minutes': minutes,
                              'km': round(sum(km(a, b) for a, b in zip(pts, pts[1:])), 1)})
            # photographs: taken while walking, in bursts, never on the plane
            if activity == 'WALKING':
                for i, (la, lo) in enumerate(pts):
                    if random.random() < 0.18:
                        t = start + timedelta(minutes=i * minutes / max(1, len(pts) - 1))
                        photos.append({'time': t.strftime('%Y:%m:%d %H:%M:%S'),
                                       'lat': f'{la + random.gauss(0, 8e-5):.6f}',
                                       'lon': f'{lo + random.gauss(0, 1.3e-4):.6f}'})
            clock = end + timedelta(minutes=random.choice([18, 24, 31, 45, 52]))

    for day, hhmm, mins, la, lo in VISITS:
        s = datetime.fromisoformat(f'{day}T{hhmm}:00')
        segments.append({
            'startTime': s.isoformat() + '.000' + TZ,
            'endTime': (s + timedelta(minutes=mins)).isoformat() + '.000' + TZ,
            'visit': {'topCandidate': {'placeLocation': {'latLng': f'{la:.6f}°, {lo:.6f}°'},
                                       'probability': round(random.uniform(0.72, 0.98), 2)},
                      'probability': round(random.uniform(0.7, 0.95), 2)},
        })
    segments.sort(key=lambda s: s['startTime'])
    return segments, photos, itinerary


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'example-data')
    out = os.path.abspath(out); os.makedirs(out, exist_ok=True)
    segments, photos, itinerary = build()

    json.dump({'semanticSegments': segments}, open(os.path.join(out, 'timeline.json'), 'w'), indent=1)
    with open(os.path.join(out, 'photos.csv'), 'w') as f:
        f.write('time,lat,lon\n')
        for p in photos: f.write(f"{p['time']},{p['lat']},{p['lon']}\n")
    json.dump({
        'title': 'Four days in Stockholm',
        'note': 'Entirely fictional. Generated by scripts/mockdata.py (seed %d) so the examples in this repo are '
                'nobody\'s real movements. The waypoints follow real streets and ferry lanes; the traveller does not exist.' % SEED,
        'from': HOME, 'legs': itinerary,
        'places_photographed': [{'lat': k[0], 'lon': k[1], 'name': v[0], 'note': v[1]} for k, v in PLACES.items()],
    }, open(os.path.join(out, 'itinerary.json'), 'w'), indent=1, ensure_ascii=False)

    walk = sum(l['km'] for l in itinerary if l['mode'] == 'WALKING')
    print(f"{out}\n  timeline.json  {len(segments)} segments "
          f"({sum('timelinePath' in s for s in segments)} paths, {sum('visit' in s for s in segments)} visits)")
    print(f"  photos.csv     {len(photos)} photographs with GPS")
    print(f"  itinerary.json {len(itinerary)} legs, {walk:.1f} km on foot over {len(DAYS)} days")
