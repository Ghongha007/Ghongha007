#!/usr/bin/env python3
"""Generates assets/header.svg, the animated profile banner. Pure SVG animation (no scripts, no external files),
so GitHub renders it. Text is converted to outlines, so it looks the same whatever fonts the viewer has.
Needs: pip install fonttools, and JetBrains Mono (SIL Open Font License) as a variable .ttf.
Run: python3 make_header.py /path/to/JetBrainsMono.ttf"""
import math, os, sys
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
FONT_FILE = sys.argv[1] if len(sys.argv) > 1 else "JetBrainsMono.ttf"
_fonts = {}
def outline(text, x, y, size, weight=400, spacing=0.0):
    """Return (path data, width in px) for text set with its baseline starting at x, y."""
    if weight not in _fonts:
        ft = instantiateVariableFont(TTFont(FONT_FILE), {"wght": weight})
        _fonts[weight] = (ft.getGlyphSet(), ft.getBestCmap(), ft["hmtx"])
    gs, cmap, hmtx = _fonts[weight]
    k, pen, cx = size / 1000, SVGPathPen(gs, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip(".")), x
    for ch in text:
        name = cmap[ord(ch)]
        gs[name].draw(TransformPen(pen, (k, 0, 0, -k, cx, y)))
        cx += hmtx[name][0] * k + spacing
    return pen.getCommands(), cx - x - spacing
W, H = 1200, 340
CX, CY, R = 190, 170, 118
SWEEP = 6.0                     # seconds per radar turn
LINES = ["geolocation and chronolocation", "satellite imagery analysis", "maritime and aviation tracking",
         "sanctions evasion and shadow fleets", "conflict and information operations", "open tools for investigators"]
SLOT = 3.6                      # seconds per line
TX, TY = 412, 196
BG, GRID, TEAL, AMBER, TEXT, DIM = "#0b1016", "#16202b", "#2dd4bf", "#fbbf24", "#e6edf3", "#7d8b99"

def f(x): return f"{x:.4f}".rstrip("0").rstrip(".")
o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
     f'aria-label="OSINT JOURNO: independent open-source investigations">',
     '<title>OSINT JOURNO: independent open-source investigations</title>',
     f'''<defs>
<clipPath id="card"><rect width="{W}" height="{H}" rx="18"/></clipPath>
<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="{GRID}" stroke-width="1"/></pattern>
<radialGradient id="glow" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="{TEAL}" stop-opacity=".16"/><stop offset="1" stop-color="{TEAL}" stop-opacity="0"/></radialGradient>
<linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="{BG}" stop-opacity="0"/><stop offset=".25" stop-color="{BG}" stop-opacity="0"/><stop offset="1" stop-color="{BG}" stop-opacity=".9"/></linearGradient>
</defs>''',
     f'<g clip-path="url(#card)"><rect width="{W}" height="{H}" fill="{BG}"/><rect width="{W}" height="{H}" fill="url(#grid)"/>'
     f'<rect width="{W}" height="{H}" fill="url(#fade)"/>',
     f'<circle cx="{CX}" cy="{CY}" r="{R + 40}" fill="url(#glow)"/>']
# radar
for r in (R, R * 2 / 3, R / 3):
    o.append(f'<circle cx="{CX}" cy="{CY}" r="{f(r)}" fill="none" stroke="{TEAL}" stroke-opacity=".35" stroke-width="1"/>')
o.append(f'<path d="M{CX - R} {CY}H{CX + R}M{CX} {CY - R}V{CY + R}" stroke="{TEAL}" stroke-opacity=".22" stroke-width="1"/>')
steps = 14                       # the sweep's fading tail, drawn as thin wedges behind the leading edge
tail = []
for i in range(steps):
    a0, a1 = -math.radians(i * 4.5), -math.radians((i + 1) * 4.5)
    p0 = (CX + R * math.cos(a0), CY + R * math.sin(a0)); p1 = (CX + R * math.cos(a1), CY + R * math.sin(a1))
    tail.append(f'<path d="M{CX} {CY}L{f(p0[0])} {f(p0[1])}A{R} {R} 0 0 0 {f(p1[0])} {f(p1[1])}Z" fill="{TEAL}" fill-opacity="{f(0.30 * (1 - i / steps) ** 1.6)}"/>')
o.append(f'<g>{"".join(tail)}<path d="M{CX} {CY}H{CX + R}" stroke="{TEAL}" stroke-width="2"/>'
         f'<animateTransform attributeName="transform" type="rotate" from="0 {CX} {CY}" to="360 {CX} {CY}" dur="{SWEEP}s" repeatCount="indefinite"/></g>')
for ang, rr, col in ((38, .62, AMBER), (118, .82, TEAL), (205, .45, TEAL), (292, .74, AMBER), (336, .33, TEAL)):
    x, y = CX + R * rr * math.cos(math.radians(ang)), CY + R * rr * math.sin(math.radians(ang))
    t = ang / 360                                    # fraction of the turn at which the sweep passes this blip
    if t + .45 < 1:
        k = f"0;{f(t - .001)};{f(t)};{f(t + .45)};1"; v = "0;0;1;0;0"; rv = "4;4;4;13;13"
    else:                                            # the fade wraps past the end of the turn
        left = (t + .45) - 1; done = (1 - t) / .45
        k = f"0;{f(left)};{f(t - .001)};{f(t)};1"; v = f"{f(1 - done)};0;0;1;{f(1 - done)}"
        rv = f"{f(4 + 9 * done)};13;4;4;{f(4 + 9 * done)}"
    o.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="4" fill="{col}" opacity="0"><animate attributeName="opacity" values="{v}" keyTimes="{k}" dur="{SWEEP}s" repeatCount="indefinite"/></circle>')
    o.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="4" fill="none" stroke="{col}" opacity="0"><animate attributeName="opacity" values="{v}" keyTimes="{k}" dur="{SWEEP}s" repeatCount="indefinite"/>'
             f'<animate attributeName="r" values="{rv}" keyTimes="{k}" dur="{SWEEP}s" repeatCount="indefinite"/></circle>')
o.append(f'<circle cx="{CX}" cy="{CY}" r="3" fill="{TEAL}"/>')
# text (as outlines)
def T(text, x, y, size, fill, weight=400, spacing=0.0, extra=""):
    d, w = outline(text, x, y, size, weight, spacing)
    return f'<path d="{d}" fill="{fill}"{extra}/>', w
o.append(T("// INDEPENDENT OPEN-SOURCE INVESTIGATIONS", TX - 32, 78, 17, TEAL, 500, 1.6)[0])
o.append(T("OSINT JOURNO", TX - 34, 144, 62, TEXT, 800, 4)[0])
o.append(T(">", TX - 32, TY, 22, AMBER, 700)[0])
total = SLOT * len(LINES)
for i, line in enumerate(LINES):
    el, w = T(line, TX, TY, 22, TEXT, 400, 0, f' clip-path="url(#c{i})"')
    w += 5
    a, b, c, d = i * SLOT, i * SLOT + 1.1, (i + 1) * SLOT - .45, (i + 1) * SLOT - .1   # type in, hold, wipe out
    kt = ";".join(f(x / total) for x in ((0, a, b, c, d, total) if i else (0, b, c, d, total)))
    wv = f"0;0;{f(w)};{f(w)};0;0" if i else f"0;{f(w)};{f(w)};0;0"
    xv = ";".join(f(TX + float(x)) for x in wv.split(";"))
    ov = "0;1;1;1;0;0" if i else "1;1;1;0;0"
    o.append(f'<clipPath id="c{i}"><rect x="{TX}" y="{TY - 24}" height="34" width="0"><animate attributeName="width" values="{wv}" keyTimes="{kt}" dur="{f(total)}s" repeatCount="indefinite"/></rect></clipPath>'
             f'{el}<rect y="{TY - 19}" width="11" height="24" fill="{AMBER}" opacity="0"><animate attributeName="x" values="{xv}" keyTimes="{kt}" dur="{f(total)}s" repeatCount="indefinite"/>'
             f'<animate attributeName="opacity" values="{ov}" keyTimes="{kt}" dur="{f(total)}s" calcMode="discrete" repeatCount="indefinite"/></rect>')
o.append(T("80+ bylined investigations  |  SANS OSINT Summit speaker  |  cited by GIJN", TX - 32, 246, 15.5, DIM)[0])
# a vessel track along the bottom
path = "M380 300 C520 270 640 322 780 296 S1010 268 1160 292"
o.append(f'<path id="trk" d="{path}" fill="none" stroke="{TEAL}" stroke-opacity=".45" stroke-width="1.5" stroke-dasharray="2 9" stroke-linecap="round"/>')
for x, y in ((380, 300), (780, 296), (1160, 292)):
    o.append(f'<circle cx="{x}" cy="{y}" r="3" fill="{BG}" stroke="{TEAL}" stroke-opacity=".7"/>')
o.append(f'<g><path d="M-9 -5L9 0L-9 5L-5 0Z" fill="{AMBER}"/><animateMotion dur="16s" repeatCount="indefinite" rotate="auto"><mpath href="#trk"/></animateMotion></g>')
o.append('</g></svg>')
os.makedirs("assets", exist_ok=True)
open("assets/header.svg", "w", encoding="utf-8").write("\n".join(o) + "\n")
print("assets/header.svg", os.path.getsize("assets/header.svg"), "bytes")
