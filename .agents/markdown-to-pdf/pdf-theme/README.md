# PDF theme: Forest / Sage v1

All future project PDFs use [print.css](print.css) as the styling source of truth. Do not invent a new palette, cover
design, font stack, or spacing system per guide. Existing PDFs and archived sources remain unchanged.

## Fixed design

| Role                            | Color     |
|---------------------------------|-----------|
| Headings                        | `#183328` |
| Accents, links, rules           | `#116845` |
| Table headers and callouts      | `#E8F4EC` |
| Code background                 | `#F1F7F3` |
| Borders                         | `#D3E3D9` |
| Body text                       | `#202D26` |
| Secondary text and page numbers | `#526B5E` |
| Paper                           | `#FFFFFF` |

Use Palatino (regular and bold) for body text, headings, and page numbers, with Palatino Linotype as the Windows family
name. If neither is available, use the system default UI font (`system-ui`, then `sans-serif` for renderers that do not
support `system-ui`). Code uses the system default `monospace` font to preserve alignment. No font installation is
required. Body text is 10pt at 1.45 line height; headings are 23/16/12/10.5pt; code is 8pt at 1.35; tables and source
labels are 8pt. The stylesheet fixes spacing and component treatment. Default paper is portrait A4 with 18mm top, 17mm
side, and 20mm bottom margins.

Use white pages, restrained sage fills, and green accents. Page 1 is a restrained cover with the guide title and a
compact **Index** of main sections/modules, including linked, right-aligned page numbers and dot leaders. Guide content
starts on page 2; count the cover as page 1 without resetting numbering. No gradients, dark code panels, additional
title-only pages, or per-document theme overrides. Diagrams created during conversion must use the same palette;
preserve existing assets and any semantic colors needed to understand them. A warning/error may retain its semantic
color only with a textual label, never color alone.

## Reproducible conversion

1. Read the Markdown without altering content. Generate a semantic HTML intermediate using [guide.html](guide.html):
   title and main-section index together on the first page, followed by the complete guide on page 2. Include only main
   sections/modules in the cover index, not individual lessons. Preserve stable heading anchors, source labels,
   answer-key sections, and references. The template requires a title and a generated table of contents.
2. Disable converter-provided document styles and load this stylesheet instead. For Pandoc, use boolean metadata
   `--metadata=document-css:false` and `--syntax-highlighting=none`. If converter styles cannot be disabled, remove
   their conflicting rules before export; loading this CSS last alone cannot override more-specific selectors. Do not
   add a second print theme.
3. Keep the stylesheet link local and resolvable relative to the generated HTML, not the original Markdown. Absolute
   local paths are suitable for temporary HTML.
4. Check the actual resolved fonts before rendering, including bold. For example, `fc-match 'Palatino'` should name
   Palatino when it is installed; a different family indicates substitution. If Palatino/Palatino Linotype is
   unavailable, the system default fallback is expected and permitted. Record the resolved text and monospace families
   in the rendering profile rather than requiring additional fonts to be installed.
5. Use the same renderer and version, font files, input assets, and settings for repeat exports. WeasyPrint with
   Pandoc-generated HTML is the reference path when already available. Browser Save PDF is also supported, but is a
   distinct rendering profile: select CSS paper size, 100% scale, background graphics on, and browser headers/footers
   off. Do not add browser margins over CSS margins. The index uses CSS `target-counter()` to resolve final page
   numbers. Browser print engines without this support are preview-only: use WeasyPrint or another supporting paged
   renderer for the final PDF, or a renderer-specific two-pass index that resolves and rechecks page numbers after final
   pagination. Never ship blank, guessed, stale, or placeholder index page numbers.
6. Use the CSS `Page N` footer where margin boxes are supported. If an engine does not support it, configure an
   equivalent 8pt muted footer through that engine, reserving the bottom margin. Do not enable a second footer or accept
   missing page numbers for a long guide.
7. Record the theme version, renderer and converter versions, resolved font files/versions, page size, settings, and
   exact conversion command in the generation handoff. Reuse that profile next time. Changing renderers or fonts can
   change pagination; matching colors does not guarantee identical pagination or byte-identical PDFs.

The oral-drill HTML loads the theme only for print; keep its screen design and interactive behavior separate. Its
question navigation becomes the cover index for print. Use its **Print / Save PDF** button to expand details and include
all questions, even after a search. For final indexed PDFs, render the expanded HTML with an engine supporting
`target-counter()`; browser previews may lack numbers.

For example, from the project root with Pandoc and WeasyPrint already available, after checking the resolved fonts:

```sh
pandoc path/to/guide.project-narratives --standalone --toc --toc-depth=2 \
  --template="$PWD/pdf-theme/guide.html" --metadata title="Guide title" \
  --syntax-highlighting=none \
  --css="$PWD/pdf-theme/print.css" --output=/tmp/guide.html
weasyprint /tmp/guide.html /tmp/guide.pdf
```

Use an unused output path and resolve embedded asset paths relative to the generated HTML before rendering. The example
assumes a source with an H1 document title and H2 main sections; use `--toc-depth=1` for H1 main sections. Exclude a
redundant document-title entry from the generated index when preparing the intermediate HTML, without removing original
source content. Do not include H3 lessons in the cover index. Confirm the cover fits exactly one page before accepting
the PDF. If main-section entries do not fit at the standard 10pt size, report the layout conflict rather than clipping
entries, shrinking to illegibility, or silently spilling the index onto page 2.

## Content and layout safeguards

- Allow tall code blocks, callouts, and tables to span pages; avoid keeping an entire lesson or question together.
  Repeat table headers where supported.
- Wrap long code lines visually, preserving source text and indentation. Mark ASCII/text diagrams with `class="diagram"`
  on `pre` so they do not wrap. Inspect width before exporting: use a vector rendering or an explicitly documented
  landscape-page exception if needed, never crop or shrink to illegibility. Preserve the original diagram's meaning.
- Keep heading navigation, internal links, exercise/answer numbering, answer keys, coverage matrices, and
  source-verification labels intact.
- Validate layout with automated checks, not page screenshots: never rasterize pages or read PNG/JPEG renders.
  Run [check_layout.py](check_layout.py) with WeasyPrint's own interpreter on the generated HTML, using `--write` so the
  validated rendering is the delivered PDF:

  ```sh
  PY="$(head -1 "$(command -v weasyprint)" | sed 's/^#!//')"
  "$PY" pdf-theme/check_layout.py /tmp/guide.html --write /tmp/guide.pdf
  ```

  It checks page size, cover/index spill, index numbers against actual target pages, content starting on page 2, broken
  internal links, right-edge overflow and bottom clipping, stranded headings and bold labels, sparse pages, content
  missing from the layout, and embedded fonts. It checks A4 by default; pass `--page-size Letter` only for an explicitly
  Letter-size export. Fix every `FAIL`; review `WARN` lines. Palette, backgrounds, and footer appearance follow from the
  unmodified theme; report them as not visually inspected rather than passed.
- Verify page 1 contains both the title and complete main-section index, content begins on page 2, and every index
  number matches its actual destination page in the final PDF, including the answer key and other indexed end matter.
- Verify actual PDF page dimensions (A4 or the explicit Letter exception), fonts, and the fixed palette. Existing
  generated PDFs are not evidence that a new export meets this contract.
