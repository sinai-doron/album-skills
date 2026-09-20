# Picabook, and what to establish before trusting any of it elsewhere

**Everything in this skill was observed on Picabook.** This file separates what is known about Picabook from what
you would have to find out about any other service. The workflow shape is the same everywhere; the details are
not, and an old project is never a source — read the service's own pages for the current numbers.

## Picabook — observed

| | |
|---|---|
| Editor | `editor.picabook.co.il`; the main site returns 403 to automated fetches, so use a real browser |
| Product | **Prizma small** / פריזמה קטן, 21.5 × 22 cm hardcover. Other sizes exist; their numbers are not these |
| Bleed | 2 mm every side, up to 5 mm allowed. Page file **2587 × 2646 px at 300 DPI** |
| Full-page template | **עמוד מלא**. Frames or borders on it are warned against — they fall outside the trim |
| Pages | even, from 24; diamond print caps around 100–121 |
| Logo page | an uncounted white page is added at the end |
| Hebrew products | page 1 is a **left** page; the flat cover sheet is [front · spine · back] with **front on the left** |
| Cover | a separate step; the sheet's size depends on the page count, so read it there and re-render to fit |
| Quality indicator | a percentage per placed image; low means the file was scaled |
| Upload tray | a "not used" list that **re-orders when an image is replaced** — the cause of the worst trap in this skill |
| Save | responds "Sucessful save" |
| Lead time | roughly 10 business days |

## Anywhere else — what to establish first

1. **Trim size** of the product, in mm, and **how much bleed** the full-page template expects (commonly 2 mm,
   sometimes up to 5 mm allowed).
2. **Page count rules** — minimum, maximum, and the step. Even counts are usual; some products step in fours.
   Some services add an uncounted logo or colophon page.
3. **Whether the product has a separate cover step** and what sheet size it asks for at your page count.
4. **Opening direction** if the language is right-to-left, and whether the service flips a left-to-right file
   automatically — some do, and it breaks spreads and page numbers.
5. **Whether they publish a quality indicator** per placed image. If so, it is your best in-editor check.

## Templates

Nearly every editor has a **full-page** (single frame, no margin) template. That is the one Route B needs. It is
often not the default, and it is sometimes named in the local language — look for the icon showing one frame
filling the page rather than trusting a label.

Services generally warn that **frames and borders on a full-page template fall outside the trim**. Take the
warning seriously: the frame is drawn inside your bleed.

## Automation notes

- Some services **block automated fetches** — a plain HTTP request gets a 403 while a real browser gets the page.
  Read and drive them in a real browser session rather than scripting HTTP.
- Editors are stateful and server-rendered. Expect multi-second waits after an upload, a page change or a save,
  and confirm each save rather than assuming.
- Uploading many files at once is usually faster and more reliable than one at a time, but the **order they land
  in the tray is not guaranteed** to match the order you sent them.
- Sign-in is the customer's to do. Never handle a password, and never enter payment details.

## Right-to-left products

- Page 1 is a **left** page; place spreads right-hand page first.
- The flat cover sheet reads **[front | spine | back]** — front panel on the **left**.
- Design in final orientation. Flipping a finished left-to-right cover cuts the spine in half.
