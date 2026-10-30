"""Automated layout validation for Forest / Sage PDF exports.

Renders the intermediate HTML with WeasyPrint and checks the laid-out pages, so
no page screenshots are needed. Run it with WeasyPrint's own interpreter:

    PY="$(head -1 "$(command -v weasyprint)" | sed 's/^#!//')"
    "$PY" pdf-theme/check_layout.py /tmp/guide.html --write /tmp/guide.pdf

Use --no-cover for self-contained HTML without the theme's cover/index.

Exit code 0 means no failures (warnings may remain); 1 means failures.
"""

import argparse
import re
import sys

from weasyprint import HTML

PAGE_SIZES = {"A4": (793.70, 1122.52), "Letter": (816.0, 1056.0)}
HEADINGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
OVERFLOW_TAGS = {"pre", "code", "table", "img", "svg", "blockquote", "figure"}
CONTENT_TAGS = HEADINGS | {"pre", "table", "blockquote", "img", "figure"}
TOLERANCE = 0.5
PARENT = {}


def text_of(box):
    if hasattr(box, "text"):
        return box.text
    return "".join(text_of(c) for c in getattr(box, "children", []))


def box_label(box):
    el = box.element
    ident = el.get("id") if el is not None else None
    text = " ".join(text_of(box).split())[:60]
    return f"<{box.element_tag}{' #' + ident if ident else ''}> {text!r}"


def content_lines(page_box, bottom):
    """Line and replaced boxes in the page content area (excludes the footer)."""
    for box in page_box.descendants():
        kind = type(box).__name__
        if ((kind == "LineBox" or kind.endswith("ReplacedBox"))
                and box.element is not None
                and box.position_y < bottom + TOLERANCE):
            yield box


def is_stranded_label(el):
    """Paragraph containing only <strong>, followed by a blockquote."""
    if el is None or el.tag != "p" or len(el) != 1 or el[0].tag != "strong":
        return False
    if (el.text or "").strip() or (el[0].tail or "").strip():
        return False
    siblings = list(PARENT.get(el, []))
    index = siblings.index(el) if el in siblings else -1
    nxt = siblings[index + 1] if 0 <= index < len(siblings) - 1 else None
    return nxt is not None and nxt.tag == "blockquote"


def is_inside(el, tag, attr=None):
    while el is not None:
        if el.tag == tag and (attr is None or el.get(attr[0]) == attr[1]):
            return True
        el = PARENT.get(el)
    return False


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("html", help="generated intermediate HTML")
    parser.add_argument("--page-size", choices=PAGE_SIZES, default="A4")
    parser.add_argument("--write", metavar="PDF",
                        help="also write the validated rendering to this PDF")
    parser.add_argument("--no-cover", action="store_true",
                        help="skip cover/index checks for documents without "
                             "a pdf-cover section and nav#TOC")
    parser.add_argument("--min-fill", type=float, default=0.45,
                        help="warn when a non-final page is filled below this")
    args = parser.parse_args()

    doc = HTML(args.html).render()
    pages = doc.pages
    failures, warnings, info = [], [], []

    # Page geometry
    exp_w, exp_h = PAGE_SIZES[args.page_size]
    info.append(f"pages: {len(pages)}")
    for n, page in enumerate(pages, 1):
        if abs(page.width - exp_w) > 1 or abs(page.height - exp_h) > 1:
            failures.append(f"page {n}: size {page.width:.1f}x{page.height:.1f}px "
                            f"is not {args.page_size}")
    if len(pages) < 2 and not args.no_cover:
        failures.append("expected a cover page followed by content")

    anchor_page = {}
    for n, page in enumerate(pages, 1):
        for name in page.anchors:
            anchor_page.setdefault(name, n)

    # Cover, index, and content start
    root = pages[0]._page_box.children[0].element
    PARENT.update({child: parent for parent in root.iter() for child in parent})
    toc_links = [] if args.no_cover else [
        a for a in root.iter("a")
        if is_inside(a, "nav", ("id", "TOC"))
        and (a.get("href") or "").startswith("#")]
    shown = {}
    for page_no, page in enumerate(pages, 1):
        for box in page._page_box.descendants():
            el = box.element
            if el is None:
                continue
            if is_inside(el, "section", ("class", "pdf-cover")) and page_no != 1:
                failures.append(f"cover/index spills onto page {page_no}: "
                                f"{box_label(box)}")
                break
            if (page_no == 1 and el.tag == "a" and el in toc_links
                    and "::after" in repr(box)):
                shown[el] = shown.get(el, "") + text_of(box)
    if not toc_links and not args.no_cover:
        failures.append("cover index (nav#TOC) has no entries")
    for a in toc_links:
        target = a.get("href")[1:]
        label = " ".join("".join(a.itertext()).split())[:50]
        actual = anchor_page.get(target)
        nums = re.findall(r"\d+", shown.get(a, ""))
        if actual is None:
            failures.append(f"index entry {label!r}: target #{target} not found")
        elif not nums:
            failures.append(f"index entry {label!r}: no page number rendered")
        elif int(nums[-1]) != actual:
            failures.append(f"index entry {label!r}: shows {nums[-1]}, "
                            f"target is on page {actual}")
    info.append(f"index entries checked: {len(toc_links)}")
    main_el = next(root.iter("main"), None)
    if main_el is not None and len(pages) > 1 and not args.no_cover:
        if not any(b.element is main_el for b in pages[1]._page_box.descendants()):
            failures.append("guide content does not start on page 2")

    # Broken internal links
    for n, page in enumerate(pages, 1):
        for kind, target, _, _ in page.links:
            if kind == "internal" and target not in anchor_page:
                failures.append(f"page {n}: internal link to missing #{target}")

    # Overflow, stranded headings/labels, whitespace
    seen, reported = set(), set()
    for n, page in enumerate(pages, 1):
        pb = page._page_box
        left, top = pb.content_box_x(), pb.content_box_y()
        right, bottom = left + pb.width, top + pb.height
        for box in pb.descendants():
            if box.element is not None:
                seen.add(box.element)
            tag = box.element_tag
            kind = type(box).__name__
            if box.element is None or not hasattr(box, "margin_width") or not (
                    tag in OVERFLOW_TAGS or kind in ("LineBox", "TextBox")):
                continue
            if kind in ("LineBox", "TextBox"):
                box_right = box.position_x + box.width
            else:
                box_right = box.position_x + box.margin_width()
            box_bottom = box.position_y + box.margin_height()
            if (n, id(box.element)) in reported:
                continue
            if box_right > right + TOLERANCE or (
                    box_bottom > bottom + TOLERANCE and box.is_monolithic()):
                reported.add((n, id(box.element)))
            if box_right > right + TOLERANCE:
                failures.append(f"page {n}: overflows right edge by "
                                f"{box_right - right:.1f}px: {box_label(box)}")
            elif box_bottom > bottom + TOLERANCE and box.is_monolithic():
                failures.append(f"page {n}: clipped at bottom by "
                                f"{box_bottom - bottom:.1f}px: {box_label(box)}")

        if n == 1 and not args.no_cover:
            continue
        blocks = [b for b in content_lines(pb, bottom)
                  if not is_inside(b.element, "section", ("class", "pdf-cover"))]
        if not blocks:
            failures.append(f"page {n}: blank page")
            continue
        last = max(blocks, key=lambda b: b.position_y + b.margin_height())
        if n < len(pages):
            if last.element_tag in HEADINGS:
                failures.append(f"page {n}: heading stranded at page bottom: "
                                f"{box_label(last)}")
            elif is_stranded_label(last.element):
                failures.append(f"page {n}: bold label stranded before its "
                                f"blockquote: {box_label(last)}")
            used = max(b.position_y + b.margin_height() for b in blocks) - top
            fill = used / pb.height
            nxt = pages[n]._page_box
            nxt_lines = list(content_lines(nxt, nxt.content_box_y() + nxt.height))
            nxt_first = min(nxt_lines, key=lambda b: b.position_y, default=None)
            forced = nxt_first is not None and nxt_first.element_tag in {"h1", "h2"}
            if fill < args.min_fill and not forced:
                warnings.append(f"page {n}: only {fill:.0%} filled before a "
                                f"non-section break")

    # Content completeness
    body = next(root.iter("body"))
    for el in body.iter():
        if (isinstance(el.tag, str) and el.tag in CONTENT_TAGS
                and el not in seen and "display:none" not in
                (el.get("style") or "").replace(" ", "")):
            failures.append(f"not laid out (missing from PDF): <{el.tag}> "
                            f"{' '.join(''.join(el.itertext()).split())[:60]!r}")

    # Fonts actually embedded
    pdf = doc.write_pdf(args.write) if args.write else doc.write_pdf()
    fonts = sorted({re.sub(r"^/(?:[A-Z]{6}\+)?", "",
                           font.name.decode("latin-1"))
                    for font in getattr(doc, "fonts", {}).values()})
    if not fonts and pdf:
        fonts = sorted({m.decode("latin-1") for m in re.findall(
            rb"/BaseFont\s*/(?:[A-Z]{6}\+)?([^\s/\[\]<>())]+)", pdf)})
    info.append("embedded fonts: " + (", ".join(fonts) or "none found"))
    if args.write:
        info.append(f"wrote: {args.write}")

    for line in info:
        print(f"INFO  {line}")
    for line in warnings:
        print(f"WARN  {line}")
    for line in failures:
        print(f"FAIL  {line}")
    print(f"RESULT {'FAIL' if failures else 'PASS'}: "
          f"{len(failures)} failure(s), {len(warnings)} warning(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
