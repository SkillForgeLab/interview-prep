## PDF Generation Prompt

Convert the Markdown guide into a polished, publication-quality A4 size PDF while preserving **all original content**, including code examples, diagrams, exercises, interview answers, the answer key, coverage matrix, and source labels.

### Requirements

1. **Inspect the source**
   - Review the guide's structure, module and lesson hierarchy, formatting, dependencies, and embedded assets.
   - Identify potential layout issues, including wide code blocks, complex tables, diagrams, and long sections.

2. **Design the PDF**
   - Follow [`../../pdf-theme/README.md`](../../pdf-theme/README.md) and load [`../../pdf-theme/print.css`](../../pdf-theme/print.css) as the single styling source of truth.
   - Use the fixed Forest / Sage v1 theme: white paper, forest headings (`#183328`), green accents (`#116845`), sage fills (`#E8F4EC`), and the exact fonts, sizes, spacing, margins, and component styles in the shared theme.
   - Do not invent or substitute a palette, font stack, syntax-highlighting theme, cover design, or layout on each run.
   - Use portrait A4. Resolve local CSS/imports correctly. Use Palatino (or Palatino Linotype) when available, otherwise the system default font; keep code in the system default monospace font. Record the resolved fonts.
   - Use the shared `../../pdf-theme/guide.html` template: page 1 must contain the title and a compact Index of main sections/modules with links, dot leaders, and actual destination page numbers.
   - Start guide content on page 2. Count the cover as page 1; do not reset page numbering. Keep lesson-level navigation out of the cover index so it fits on one page at a readable size.
   - Resolve index numbers from the final rendered layout using `target-counter()` or a verified two-pass equivalent. Do not use guessed numbers or a browser export that omits index numbers.
   - Style code blocks, tables, diagrams, exercises, and interview answers for easy reading.
   - For glossary and definition sections, prefer a clean sequence of standalone paragraphs: bold the term, follow it with its definition, and leave enough vertical space to distinguish entries. Do not use tables, bullets, or numbered lists for glossary entries.
   - For question-and-answer or weak/strong-example sections, use readable labeled text blocks or paragraphs rather than tables or nested lists. Keep labels such as **Question**, **Answer**, **Weak answer**, and **Clearer answer** visually distinct using the shared theme.
   - Avoid unnecessary bullets and dense list styling in reference material. Retain numbering where it conveys a meaningful sequence, such as steps, exercises, or ordered procedures. These are PDF layout rules; do not change the Markdown source or remove, summarize, or reorder its content.
   - Keep the answer key in a dedicated, clearly labeled section.
   - Preserve the original source labels distinguishing verified facts from fictional assumptions.

3. **Preserve content integrity**
   - Do not omit, summarize, rewrite, or alter technical content.
   - Preserve code syntax, indentation, diagrams, exercise numbering, answer references, and coverage matrix entries.
   - Ensure long code examples and wide tables remain readable without clipping or unintended truncation.

4. **Validate the final output**
   - Render and visually inspect the completed PDF.
   - Check typography, alignment, page breaks, section transitions, and code block widths.
   - Prevent orphaned headings, awkward page splits, overlapping elements, and excessive whitespace.
   - Verify that all content, internal references, and navigation elements are preserved and correctly rendered.
   - Verify the fixed palette, actual fonts, A4 dimensions, print backgrounds, and page numbers against the shared theme.
   - Confirm the title and complete main-section index fit on page 1, content starts on page 2, and all index page numbers match their destinations. Report a cover overflow rather than silently adding index pages.
   - Record the theme version, renderer/converter versions, resolved font files/versions, page size, settings, and exact conversion command in the handoff. Reuse that profile for repeat exports; do not redesign the document.

### Deliverable

Provide the final, print-ready PDF with a consistent editorial layout, complete content coverage, and verified rendering quality.

**Acceptance criteria:** No missing content, no clipped code or tables, no broken diagrams, no misplaced answer keys, and no loss of source-verification labels. All new exports must use the shared Forest / Sage v1 styling; existing PDFs and archived material remain unchanged unless regeneration is explicitly requested.
