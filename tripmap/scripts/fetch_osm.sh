#!/bin/zsh
# fetch_osm.sh NAME S W N E ['extra overpass statements']  →  osm_NAME.json next to this script
# Coastline, water, parks, main roads and rail for a bbox, plus EXTRA (buildings, footpaths, one named place…).
# Coastline is always asked for: in OSM the sea is not a polygon, it is whatever the coastline leaves over, and a
# harbour city drawn without it comes out as solid land (coast.py builds the land from these ways).
# Overpass rate-limits (HTML "rate_limited") and times out on big boxes ("too busy"): pause 30–60 s between calls,
# and for a region-scale box ask for less — coastline, motorway/trunk, lakes — not every secondary road.
set -e
name=$1; s=$2; w=$3; n=$4; e=$5; extra=$6
b="($s,$w,$n,$e)"
q="[out:json][timeout:240];
(
  way[\"natural\"=\"coastline\"]$b;
  way[\"natural\"=\"water\"]$b; relation[\"natural\"=\"water\"]$b;
  way[\"leisure\"=\"park\"]$b; relation[\"leisure\"=\"park\"]$b;
  way[\"highway\"~\"^(motorway|trunk|primary|secondary)$\"]$b;
  way[\"railway\"=\"rail\"]$b;
  $extra
);
out geom;"
out=$(dirname $0)/osm_$name.json
curl -s --max-time 300 -A "photobook/1.0 (personal photo album)" --data-urlencode "data=$q" https://overpass-api.de/api/interpreter -o "$out"
python3 -c "
import json,sys,collections
try: d=json.load(open('$out'))
except Exception: print('NOT JSON (rate-limited or timed out):', open('$out').read()[:300]); sys.exit(1)
print('$out', len(d['elements']), collections.Counter(e['type'] for e in d['elements']))"
