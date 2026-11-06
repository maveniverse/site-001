#  *******************************************************************************
#  Copyright (c) 2026 Eclipse Foundation and others.
#  This program and the accompanying materials are made available
#  under the terms of the Eclipse Public License 2.0
#  which is available at http://www.eclipse.org/legal/epl-v20.html
#  SPDX-License-Identifier: EPL-2.0
#  *******************************************************************************

import re
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

FONT = "/usr/share/fonts/google-noto-vf/NotoSans[wght].ttf"
TEXT = "maveniverse"
SCALE = 0.098  # px per font unit, an x-height of about 52px
TRACKING = 6  # font units between the letters
ICON = 168  # size of the icon in the lockup
GAP = 36  # space between icon and wordmark
ACCENT = "#ffb347"

font = instancer.instantiateVariableFont(TTFont(FONT), {"wght": 640})
cmap = font.getBestCmap()
glyphs = font.getGlyphSet()
hmtx = font["hmtx"]


def glyph_name(ch):
    # the dot of the i is drawn separately, as the missing piece
    return cmap[0x131] if ch == "i" else cmap[ord(ch)]


# the dot of the regular 'i' gives size and position of the piece
rec = DecomposingRecordingPen(glyphs)
glyphs[cmap[ord("i")]].draw(rec)
contours, current = [], []
for op, args in rec.value:
    current.append((op, args))
    if op == "closePath":
        contours.append(current)
        current = []
dot_pen = BoundsPen(glyphs)
for op, args in contours[-1]:
    getattr(dot_pen, op)(*args)
dot_xmin, dot_ymin, dot_xmax, dot_ymax = dot_pen.bounds

x = 0
paths, dot = [], None
for ch in TEXT:
    name = glyph_name(ch)
    pen = SVGPathPen(glyphs)
    # flip y, the font has its origin at the baseline with y going up
    glyphs[name].draw(TransformPen(pen, (SCALE, 0, 0, -SCALE, x * SCALE, 0)))
    paths.append(pen.getCommands())
    if ch == "i":
        cx = x + (dot_xmin + dot_xmax) / 2
        cy = (dot_ymin + dot_ymax) / 2
        side = max(dot_xmax - dot_xmin, dot_ymax - dot_ymin) * 1.32
        dot = (cx * SCALE, -cy * SCALE, side * SCALE)
    x += hmtx[name][0] + TRACKING
text_width = (x - TRACKING) * SCALE

icon_svg = Path("svg/maveniverse-icon.svg").read_text()
inner = re.search(r"<svg[^>]*>(.*)</svg>", icon_svg, re.DOTALL).group(1)


def lockup(text_color, label):
    baseline = ICON / 2 + 26  # centers the x-height of the lowercase letters on the icon
    dx = ICON + GAP
    width = dx + text_width + 8
    piece = ""
    if dot:
        cx, cy, side = dot
        piece = (
            f'<rect x="{-side / 2:.1f}" y="{-side / 2:.1f}" width="{side:.1f}" height="{side:.1f}" '
            f'rx="{side * 0.22:.1f}" fill="{ACCENT}" transform="translate({cx:.1f} {cy:.1f}) rotate(14)"/>'
        )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} {ICON}" width="{width:.0f}" height="{ICON}" role="img" aria-labelledby="t">
  <title id="t">{label}</title>
  <g transform="scale({ICON / 512:.5f})">{inner}</g>
  <g transform="translate({dx} {baseline:.1f})">
    <g fill="{text_color}">
      {"".join(f'<path d="{p}"/>' for p in paths)}
    </g>
    {piece}
  </g>
</svg>
'''


Path("svg/maveniverse-lockup-light.svg").write_text(lockup("#1c1b4d", "Maveniverse"))
Path("svg/maveniverse-lockup-dark.svg").write_text(lockup("#fff7e8", "Maveniverse"))
