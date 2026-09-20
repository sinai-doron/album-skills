# What differs between print services

The workflow is the same everywhere; the details are not. Read the service's own pages for the current numbers —
these change, and an old project is not a source.

## Things to establish before starting

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
