# album-skills

Skills for turning a folder of photographs and a phone's location history into something printed.

Each skill is a self-contained folder: instructions Claude Code can read (`SKILL.md`), scripts that run on their
own, reference notes, and worked examples generated from synthetic data so anything here can be reproduced without
private material.

## Skills

| skill | what it does |
|---|---|
| **[tripmap](tripmap/)** | Print-quality maps of a journey, drawn from a location-history export, photo EXIF GPS, or a source and a destination. Five archetypes — flight, region, city walk, island/coast, route — as SVG in millimetres and 300 DPI PNG. Includes a trip generator, so the examples run on data belonging to nobody. |
| **[picabook](picabook/)** | Getting a finished design into **Picabook**, the Israeli photo-book printer, and ready to order: render each page full-bleed at their exact pixel size, drive their editor in a real browser, place and verify every page. Specific to Picabook — every number and trap was observed there — though the shape transfers. Stops short of placing the order. |

Planned, from the same body of work: preflight checks on rendered pages, culling and selection from a large
camera roll, face-safe cropping, and subject-preserving retouch.

## What these are for

Consumer photo tools automate layout. The parts that actually decide whether a printed object is any good are
different: choosing what goes in, checking that what the software produced is what will physically print, and
knowing which mistakes are invisible on screen.

These skills lean on that second half. The recurring failure is not a crash — it is **a build that succeeds while
the printed object is wrong**:

- a page composited at 100 DPI because a helper silently fell back to a web-sized thumbnail
- type rendered in a substitute serif, because a missing `@font-face` does not raise an error
- a layout that crops a face out of frame, passing every check because the checker measured the wrong box
- a distance printed in a caption that is off by two orders of magnitude, because the points were summed straight
  through a gap

None of those raise an exception. All of them are obvious the moment a page is rendered and looked at. So the
method underneath every skill here is the same: **render it, look at the image, fix it** — and where a defect can
be reduced to a measurement, write the checker and keep it.

## Working with personal data

These tools read location history and personal photographs. Two rules apply throughout:

- **A trip's data contains the traveller's home.** An export covers the days either side of the journey, and photo
  GPS covers wherever the camera was. Anything that resolves coordinates to names must exclude home explicitly —
  `tripmap`'s geocoder refuses to look up anything beyond a radius of the trip's own centre, so a home address is
  never sent to a third-party service.
- **Source data stays out of the repository.** `.gitignore` refuses location exports, photo indexes and cached
  geocoder results by name. Example images are generated from synthetic trips, not real ones.

## Checks

`python3 scripts/check_frontmatter.py` validates every `SKILL.md` frontmatter: that it parses as YAML, that the
name matches its folder, and that the description is there. Worth running before a commit — a bare colon inside a
description is read as a nested mapping, which breaks the whole block, and the symptom is a skill that silently
never triggers plus a red error box on GitHub. Nothing shows locally.

## Requirements

`python3`, and per skill: `shapely` and `Pillow`, `exiftool` for reading photo metadata, Google Chrome for
rendering. Each skill's README lists what it actually needs.

## Licence

MIT, see `LICENSE`. Individual data sources carry their own terms and each skill documents them — map data
© OpenStreetMap contributors (ODbL), country outlines from Natural Earth (public domain), geocoding via Nominatim.
Bundled fonts keep their own licences alongside them.
