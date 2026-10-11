#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["fonttools", "brotli", "uharfbuzz"]
# ///
"""The banner of github.com/FFD-Labs, drawn from the brand's own files.

    uv run scripts/banner.py <lockup svg> <Host Grotesk woff2> <Spline Sans Mono woff2>

The lockup is a file of the Fair Food Data brand kit, the dark one: the animated loop or the still one. It goes into the
banner as it is, in a canvas of its own, so the mark, its gradient and its motion are the kit's and nothing is redrawn.
The two typefaces are the brand's variable fonts. An image on GitHub cannot load a font, so the two lines of text are
turned into outlines, the way the wordmark of the lockup was: shaped with HarfBuzz and drawn with fontTools.

None of the three files is in this repository. The banner is written to profile/banner.svg.
"""
import re
import sys
from io import BytesIO
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

OUT = Path(__file__).resolve().parent.parent / "profile" / "banner.svg"

# The canvas and what sits on it. Colours are the dark mode of the brand's tokens.
W, H = 1280, 440
BG, LINE, ACCENT = "#0b0e14", "#222b38", "#2CB3C9"
INK_DIM, INK_FAINT = "#9AA7B5", "#76838F"
GRAD_A, GRAD_B = "#1199A8", "#00E676"
GRID, CORNER_INSET, CORNER_LEG = 40, 36, 32

# The lockup: its canvas is 255 x 64 and the mark's cells begin 10 units in, so the canvas starts that much to the left
# of the text under it.
LOCKUP_W, LOCKUP_H, LOCKUP_SCALE = 255, 64, 3
LEFT, LOCKUP_TOP = 104, 62

TAGLINE = dict(text="Proof, not paper.", accent="Proof", size=56, weight=600, tracking=-1.4, baseline=300)
LABEL = dict(text="THE VERIFIABLE RECORD FOR RECOVERED FOOD", size=19, weight=400, tracking=2.6, baseline=352)


def num(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def outlines(woff2, weight, text, size, tracking, x0, baseline):
    """The glyphs of a line as SVG path data, one entry per glyph: (index of its character, path, x where it ends)."""
    plain = BytesIO()
    font = TTFont(woff2)
    font.flavor = None
    font.save(plain)
    instance = instantiateVariableFont(TTFont(BytesIO(plain.getvalue())), {"wght": weight})
    glyphs, order = instance.getGlyphSet(), instance.getGlyphOrder()
    k = size / instance["head"].unitsPerEm

    shaper = hb.Font(hb.Face(hb.Blob(plain.getvalue())))
    shaper.set_variations({"wght": weight})
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(shaper, buf, {"kern": True, "liga": False})

    x, out = x0, []
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        pen = SVGPathPen(glyphs, ntos=num)
        glyphs[order[info.codepoint]].draw(
            TransformPen(pen, (k, 0, 0, -k, x + pos.x_offset * k, baseline - pos.y_offset * k))
        )
        x += pos.x_advance * k
        out.append((info.cluster, pen.getCommands(), x))
        x += tracking
    return out


def path(parts):
    return " ".join(d for _, d, _ in parts if d)


def main(lockup, display, mono):
    source = Path(lockup).read_text()
    inner = re.search(r"<svg[^>]*>(.*)</svg>", source, re.S).group(1).strip()
    if f'viewBox="0 0 {LOCKUP_W} {LOCKUP_H}"' not in source:
        sys.exit(f"{lockup} is not a lockup of the brand kit: its canvas is not {LOCKUP_W} x {LOCKUP_H}")

    lockup_x = LEFT - 10 * LOCKUP_SCALE
    t = TAGLINE
    line = outlines(display, t["weight"], t["text"], t["size"], t["tracking"], LEFT, t["baseline"])
    cut = len(t["accent"])
    accent, rest = [g for g in line if g[0] < cut], [g for g in line if g[0] >= cut]
    accent_end = accent[-1][2]
    label = outlines(mono, LABEL["weight"], LABEL["text"], LABEL["size"], LABEL["tracking"], LEFT, LABEL["baseline"])

    a, b, leg = CORNER_INSET, CORNER_INSET + CORNER_LEG, CORNER_LEG
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Fair Food Data. Proof, not paper. The verifiable record for recovered food.">
  <!-- The banner of github.com/FFD-Labs. Written by scripts/banner.py from the files of the brand kit: change it there. -->
  <defs>
    <pattern id="field" width="{GRID}" height="{GRID}" patternUnits="userSpaceOnUse">
      <path d="M{GRID} 0H0V{GRID}" fill="none" stroke="{ACCENT}" stroke-opacity=".05"/>
    </pattern>
    <linearGradient id="accent" gradientUnits="userSpaceOnUse" x1="{num(LEFT)}" y1="{num(t['baseline'] - 0.7 * t['size'])}" x2="{num(accent_end)}" y2="{num(t['baseline'] + 0.25 * t['size'])}">
      <stop offset="0" stop-color="{GRAD_A}"/><stop offset="1" stop-color="{GRAD_B}"/>
    </linearGradient>
    <clipPath id="edge"><rect width="{W}" height="{H}" rx="6"/></clipPath>
  </defs>
  <g clip-path="url(#edge)">
    <rect width="{W}" height="{H}" fill="{BG}"/>
    <rect width="{W}" height="{H}" fill="url(#field)"/>
  </g>
  <rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="5.5" fill="none" stroke="{LINE}"/>
  <g fill="none" stroke="{ACCENT}" stroke-opacity=".45" stroke-width="2">
    <path d="M{a} {b}V{a}H{b}"/><path d="M{W - b} {a}H{W - a}V{b}"/>
    <path d="M{a} {H - b}V{H - a}H{b}"/><path d="M{W - a} {H - b}V{H - a}H{W - b}"/>
  </g>

  <!-- The lockup of the brand kit, as it is. -->
  <svg x="{num(lockup_x)}" y="{LOCKUP_TOP}" width="{num(LOCKUP_W * LOCKUP_SCALE)}" height="{num(LOCKUP_H * LOCKUP_SCALE)}" viewBox="0 0 {LOCKUP_W} {LOCKUP_H}">
  {inner}
  </svg>

  <!-- {t['text']} Host Grotesk {t['weight']}, in outlines. -->
  <path fill="url(#accent)" d="{path(accent)}"/>
  <path fill="{INK_DIM}" d="{path(rest)}"/>

  <!-- {LABEL['text']}. Spline Sans Mono {LABEL['weight']}, in outlines. -->
  <path fill="{INK_FAINT}" d="{path(label)}"/>
</svg>
"""
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(svg)
    print(f"{OUT.relative_to(OUT.parent.parent)}  {len(svg.encode())} bytes  lockup {Path(lockup).name}")
    print(f"tagline ends at x {num(line[-1][2])}, label at x {num(label[-1][2])}, of {W}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
