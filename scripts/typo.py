"""CoreText + Quartz typography-to-SVG-path engine.

Converts refined serif and calligraphic text into crisp, self-contained SVG <path>
elements with exact kerning and OpenType ligatures so GitHub <img> SVGs render
identically across all platforms without external font requests.
"""

from __future__ import annotations

import CoreText
import Quartz
from Cocoa import NSAttributedString, NSFont


def _cgpath_to_svg_d(cgpath, tx: float, ty: float) -> str:
    """Convert a Quartz CGPath (y-up) into an SVG path string (y-down) at (tx, ty)."""
    segs: list[str] = []

    def _cb(_info, element):
        t = element.type
        pts = element.points
        if t == Quartz.kCGPathElementMoveToPoint:
            segs.append(f"M{tx + pts[0].x:.2f},{ty - pts[0].y:.2f}")
        elif t == Quartz.kCGPathElementAddLineToPoint:
            segs.append(f"L{tx + pts[0].x:.2f},{ty - pts[0].y:.2f}")
        elif t == Quartz.kCGPathElementAddQuadCurveToPoint:
            segs.append(
                f"Q{tx + pts[0].x:.2f},{ty - pts[0].y:.2f} "
                f"{tx + pts[1].x:.2f},{ty - pts[1].y:.2f}"
            )
        elif t == Quartz.kCGPathElementAddCurveToPoint:
            segs.append(
                f"C{tx + pts[0].x:.2f},{ty - pts[0].y:.2f} "
                f"{tx + pts[1].x:.2f},{ty - pts[1].y:.2f} "
                f"{tx + pts[2].x:.2f},{ty - pts[2].y:.2f}"
            )
        elif t == Quartz.kCGPathElementCloseSubpath:
            segs.append("Z")

    Quartz.CGPathApply(cgpath, None, _cb)
    return "".join(segs)


def measure_text(text: str, font_name: str, size: float, letter_spacing: float = 0.0) -> float:
    """Return total typographic width of a string rendered with CoreText."""
    font = NSFont.fontWithName_size_(font_name, float(size))
    if font is None:
        raise ValueError(f"Font not found: {font_name}")
    attrs = {"NSFont": font}
    if letter_spacing:
        attrs["NSKern"] = float(letter_spacing)
    astr = NSAttributedString.alloc().initWithString_attributes_(text, attrs)
    line = CoreText.CTLineCreateWithAttributedString(astr)
    width, _asc, _desc, _lead = CoreText.CTLineGetTypographicBounds(line, None, None, None)
    return float(width)


def text_path(
    text: str,
    font_name: str,
    size: float,
    x: float,
    y: float,
    anchor: str = "middle",
    fill: str = "#453427",
    opacity: float = 1.0,
    letter_spacing: float = 0.0,
    extra_attrs: str = "",
) -> str:
    """Render a line of text as a single crisp SVG <path> element."""
    font = NSFont.fontWithName_size_(font_name, float(size))
    if font is None:
        raise ValueError(f"Font not found: {font_name}")
    attrs: dict = {"NSFont": font}
    if letter_spacing:
        attrs["NSKern"] = float(letter_spacing)
    astr = NSAttributedString.alloc().initWithString_attributes_(text, attrs)
    line = CoreText.CTLineCreateWithAttributedString(astr)
    total_w, _asc, _desc, _lead = CoreText.CTLineGetTypographicBounds(line, None, None, None)

    if anchor == "middle":
        origin_x = x - total_w * 0.5
    elif anchor == "end":
        origin_x = x - total_w
    else:
        origin_x = x

    all_d: list[str] = []
    for run in CoreText.CTLineGetGlyphRuns(line):
        count = CoreText.CTRunGetGlyphCount(run)
        glyphs = CoreText.CTRunGetGlyphs(run, (0, count), None)
        positions = CoreText.CTRunGetPositions(run, (0, count), None)
        ctfont = CoreText.CTRunGetAttributes(run)["NSFont"]
        for g, pos in zip(glyphs, positions):
            gpath = CoreText.CTFontCreatePathForGlyph(ctfont, g, None)
            if gpath is not None:
                d = _cgpath_to_svg_d(gpath, origin_x + pos.x, y - pos.y)
                if d:
                    all_d.append(d)

    op_attr = f' fill-opacity="{opacity:.3f}"' if opacity < 0.999 else ""
    extra = f" {extra_attrs.strip()}" if extra_attrs.strip() else ""
    return f'<path d="{"".join(all_d)}" fill="{fill}"{op_attr}{extra}/>'


def text_glyph_paths(
    text: str,
    font_name: str,
    size: float,
    x: float,
    y: float,
    anchor: str = "middle",
    letter_spacing: float = 0.0,
) -> list[str]:
    """Return individual glyph SVG d-strings (useful for staggered ink-reveal animations)."""
    font = NSFont.fontWithName_size_(font_name, float(size))
    if font is None:
        raise ValueError(f"Font not found: {font_name}")
    attrs: dict = {"NSFont": font}
    if letter_spacing:
        attrs["NSKern"] = float(letter_spacing)
    astr = NSAttributedString.alloc().initWithString_attributes_(text, attrs)
    line = CoreText.CTLineCreateWithAttributedString(astr)
    total_w, _asc, _desc, _lead = CoreText.CTLineGetTypographicBounds(line, None, None, None)

    if anchor == "middle":
        origin_x = x - total_w * 0.5
    elif anchor == "end":
        origin_x = x - total_w
    else:
        origin_x = x

    glyph_ds: list[str] = []
    for run in CoreText.CTLineGetGlyphRuns(line):
        count = CoreText.CTRunGetGlyphCount(run)
        glyphs = CoreText.CTRunGetGlyphs(run, (0, count), None)
        positions = CoreText.CTRunGetPositions(run, (0, count), None)
        ctfont = CoreText.CTRunGetAttributes(run)["NSFont"]
        for g, pos in zip(glyphs, positions):
            gpath = CoreText.CTFontCreatePathForGlyph(ctfont, g, None)
            if gpath is not None:
                d = _cgpath_to_svg_d(gpath, origin_x + pos.x, y - pos.y)
                if d:
                    glyph_ds.append(d)
    return glyph_ds


def paragraph_paths(
    text: str,
    font_name: str,
    size: float,
    x: float,
    y: float,
    max_width: float,
    line_height: float,
    anchor: str = "start",
    fill: str = "#453427",
    opacity: float = 1.0,
) -> list[str]:
    """Wrap text greedily by CoreText width and return SVG <path> elements per line."""
    words = text.split()
    lines: list[str] = []
    current = ""
    for w in words:
        trial = f"{current} {w}".strip()
        if current and measure_text(trial, font_name, size) > max_width:
            lines.append(current)
            current = w
        else:
            current = trial
    if current:
        lines.append(current)

    return [
        text_path(line, font_name, size, x, y + i * line_height, anchor=anchor, fill=fill, opacity=opacity)
        for i, line in enumerate(lines)
    ]
