---
name: printbook
description: Get a finished book design into Picabook (picabook.co.il) and ready to order — render each page to a full-bleed image at 2587x2646 px, drive editor.picabook.co.il in a real browser to upload and place them, then verify every page before handing back for the customer to order. Written from a complete 48-page Picabook album and specific to that service: its full-page template, its upload tray, its cover step, its Hebrew right-to-left products. Use it whenever somebody mentions Picabook or פיקאבוק, has a designed album to get into their editor, or asks "how do I get this to print" about an Israeli photo book. Much of the method transfers to Shutterfly, Mixbook, Blurb or Cewe, but every number and every trap here was observed on Picabook and is a hypothesis anywhere else. Never place the order — that is always the customer's own action.
---

# printbook

**This is a Picabook skill.** It was written from placing a complete 48-page album plus cover into
`editor.picabook.co.il`, and every measurement, template name and trap below was observed there. The general
shape — render pages, upload, place, verify, stop before ordering — transfers to Shutterfly, Mixbook, Blurb or
Cewe, but treat anything specific as unverified elsewhere and check it against that service's own pages first.
`references/services.md` lists what to establish before trusting any of it somewhere new.

Picabook's editor is a web application built for a person dragging photos around. Driving it is slow, stateful and
easy to get subtly wrong — a page can end up holding the right-looking image from the wrong file and nothing will
warn you. This skill is about doing it accurately and proving it afterwards.

## Picabook, concretely

| | |
|---|---|
| Editor | `editor.picabook.co.il` — the customer signs in themselves |
| Product used | **Prizma small** (פריזמה קטן), 21.5 × 22 cm hardcover |
| Page image | trim 215 × 220 mm **+ 2 mm bleed every side** = **2587 × 2646 px at 300 DPI**, sRGB JPEG |
| Template | **עמוד מלא** — the full-page template, one frame covering the page. Set the frame to 21.5 × 22 cm at position 0,0 |
| Page count | even, from 24; the diamond-print paper caps around 100–121 pages |
| Extra page | Picabook adds its own **uncounted white logo page** at the end |
| Save | returns a confirmation reading "Sucessful save" — their spelling, not a typo to fix |
| Fetching | `picabook.co.il` returns **403 to automated fetches**; read and drive it in a real browser |
| Lead time | roughly 10 business days |

Their marketing and help pages change. Re-read the size and page-count rules at the start of every album rather
than trusting this table — one series changed dimensions after an equipment upgrade between two orders.

## The decision that shapes everything: objects or images

**Route A — build each page inside the editor** from its own objects: photo frames, text boxes, stickers. The
customer can edit text later in the editor. But you are re-implementing a layout you already have, in a tool with
no undo you can trust, over a browser connection; type and spacing will not match your design, the editor's fonts
are not your fonts, and every page is dozens of interactions.

**Route B — render each page to one finished image** and place it in the editor's full-page template. Everything
is baked in: crops, type, graphics, texture. The service cannot mangle the layout and does not need your fonts.
One upload and one placement per page.

**Choose B unless the customer specifically needs to edit text in the editor later.** Say that trade-off out loud
before starting, because it is the one thing Route B gives up and it cannot be undone without re-rendering.

Route B is also what makes verification possible: a page either holds the right picture or it does not.

## Before touching the browser

1. **Get the exact trim size and bleed from the service**, not from memory or an old project. Sizes change; one
   album series changed after an equipment upgrade between two orders.
2. **Render at the printer's pixel size.** trim + bleed on every side, at 300 DPI. For a 215 × 220 mm page with
   2 mm bleed: (215+4) × (220+4) mm = **2587 × 2646 px**. Get this wrong and every page is silently resampled.
3. **Check the rendered files before uploading anything.** Build a contact sheet and look at it: no blank pages,
   no half-rendered pages, right count, right order. Fixing a bad page after it is placed costs ten times more.
4. **Name files so position is unambiguous** — `page-1.jpg` … `page-48.jpg`, `page-cover.jpg`. You will be
   matching thumbnails to filenames under time pressure.
5. **Confirm the page count is one the service accepts** (often even, often a minimum, sometimes a maximum for a
   particular paper) and whether they add an uncounted logo page.

## Driving the editor

Work in a real browser with the person signed in. Ask them to sign in themselves — never handle their password.

- **Batch actions, but keep them verifiable.** Several clicks and a screenshot in one call is efficient; twenty
  blind actions is a guess. End a batch with a screenshot or a zoom of the region you changed.
- **Wait generously.** These editors save and render server-side; 8–10 seconds after an upload or a page change is
  normal. Acting early is how you click the wrong thing.
- **Zoom to read.** Editor chrome is small. A `zoom` on the region beats a full screenshot for reading a page
  number, a quality indicator or a filename.
- **Set the frame explicitly** to the full page size at position 0,0 rather than dragging to fit. On a full-page
  template the image already contains the bleed the frame expects — do not zoom or nudge it afterwards.
- **Do not add frames or borders to full-page images.** Services warn that these fall outside the trim.
- **Save as you go** and read the confirmation. Do not assume.

## The traps that cost real time

All four were observed on Picabook. The first is the one most likely to exist in any editor with an upload tray;
the rest may well be Picabook's own behaviour.

**The upload tray reshuffles when you replace an image.** This is the worst one. Replacing a page returns the old
image to the "not used" list, which re-orders the tray, so the next drag picks up a neighbour. In one run page 9
silently received page 19's content this way. **Match by what the thumbnail shows, never by its position in the
tray**, and re-verify the page you just changed *and* the one after it.

**The browser connection will drop mid-run.** It dropped twice in one session. Both times the action had actually
gone through. **Check the current state before redoing anything** — blind retries are how a page gets placed twice
or a wrong image lands.

**Single pages behave differently from spreads.** The first and last pages have no facing page, and their tray
slot can hold something unexpected. The last page of one book received an old cover draft for exactly this reason.

**Old drafts stay in the tray.** Superseded images remain in the uploads list. They print nothing, but they are
available to be grabbed by mistake. Either delete them or know they are there.

**Trust the quality indicator.** If the editor reports a low resolution for a page, the file was scaled somewhere —
your image is exactly 300 DPI at printed size, so a low number means something went wrong, not that the file is
poor.

## Right-to-left books — Picabook's Hebrew products

- **Page 1 is a left page.** Place spread by spread, right-hand page first, the way the book reads.
- **The flat cover sheet reads [front | spine | back] — the front panel is on the LEFT**, the opposite of a
  left-to-right book. Design it in final orientation. Never build it the English way round and flip it: flipping
  cuts the spine text in half.
- **The spine usually carries the destination and the year**, not the front. Ask; people have a house style.
- The cover sheet's size depends on the page count, so it is never the same shape as a page. Read its exact size
  from the editor's cover step and re-render the cover to fit rather than stretching a page-shaped file.

## Verify before handing back

Walking the page strip in the editor is necessary but not sufficient — the thumbnails are small.

1. Walk every spread in the editor and confirm each page holds the image its filename says.
2. Open the service's **3D or full preview** and page through the whole book.
3. Check the **full-bleed pages** and anything near an edge: services trim a little off each side.
4. Confirm the **page count** and the **opening direction**.
5. Ask the customer to look at the preview themselves before ordering. What you can see in an editor is small, and
   they know what the book is supposed to be.

## Never place the order

Stop at the point of purchase and hand back. Placing an order spends the customer's money and is theirs to do,
however clear the intent seems — and the same goes for entering card details, which you should never do at all.
Tell them what is ready, what you checked, and what you would look at before they buy.

## References

- `references/services.md` — what differs between services: page templates, cover steps, quality indicators,
  bleed conventions, and which ones block automated fetches so you must use a real browser.
- `references/preflight.md` — the checks worth running on the rendered files before a browser is ever opened.
