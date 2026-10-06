import hashlib
import html
import math
import random
import re

from .fonts import STACK, font_face

POSTER = 840
PAD = 10
GAP = 10
W = POSTER - 2 * PAD
HALF = (W - GAP) // 2
INK = "#05060b"
LINE = "#1c2033"
PANEL = "#090b14"
RX = 18
MUTED = "#7d84a6"
TEXT = "#e9ecff"
VIOLET = "#7c5cff"
CYAN = "#22d3ee"
PINK = "#ff4fd8"
AMBER = "#ffb547"
MINT = "#3dffa8"
RED = "#ff4d6d"


def esc(s):
    return html.escape(str(s), quote=True)


def rng(*parts):
    seed = hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest()
    return random.Random(int(seed[:16], 16))


def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb2hex(c):
    return "#" + "".join(f"{max(0, min(255, round(v))):02x}" for v in c)


def mix(a, b, t):
    ca, cb = hex2rgb(a), hex2rgb(b)
    return rgb2hex(tuple(x + (y - x) * t for x, y in zip(ca, cb)))


def ramp(stops, t):
    t = max(0.0, min(1.0, t))
    if t >= 1:
        return stops[-1]
    pos = t * (len(stops) - 1)
    i = int(pos)
    return mix(stops[i], stops[i + 1], pos - i)


def shade(c, k):
    return mix(c, "#000000", k) if k > 0 else mix(c, "#ffffff", -k)


def f(v):
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


def pts(points):
    return " ".join(f"{f(x)},{f(y)}" for x, y in points)


def smooth(points):
    if len(points) < 3:
        return "M" + " L".join(f"{f(x)} {f(y)}" for x, y in points)
    d = [f"M{f(points[0][0])} {f(points[0][1])}"]
    for i in range(len(points) - 1):
        p0 = points[i - 1] if i else points[i]
        p1, p2 = points[i], points[i + 1]
        p3 = points[i + 2] if i + 2 < len(points) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append(f"C{f(c1[0])} {f(c1[1])} {f(c2[0])} {f(c2[1])} {f(p2[0])} {f(p2[1])}")
    return " ".join(d)


def arc(cx, cy, r0, r1, a0, a1):
    def p(r, a):
        return cx + r * math.cos(a), cy + r * math.sin(a)

    large = 1 if (a1 - a0) % (2 * math.pi) > math.pi else 0
    x0, y0 = p(r1, a0)
    x1, y1 = p(r1, a1)
    x2, y2 = p(r0, a1)
    x3, y3 = p(r0, a0)
    return (f"M{f(x0)} {f(y0)}A{f(r1)} {f(r1)} 0 {large} 1 {f(x1)} {f(y1)}"
            f"L{f(x2)} {f(y2)}A{f(r0)} {f(r0)} 0 {large} 0 {f(x3)} {f(y3)}Z")


GRAIN = (
    '<filter id="grain" x="0" y="0" width="100%" height="100%">'
    '<feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" stitchTiles="stitch"/>'
    '<feColorMatrix values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 .55 0"/></filter>'
)

BASE_CSS = (
    "text{{font-family:{stack}}}"
    "text:not([fill]){{fill:{text}}}"
    "text.k:not([fill]){{font-size:11px;letter-spacing:.22em;fill:{muted};font-weight:700}}"
    ".k{{font-size:11px;letter-spacing:.22em;font-weight:700}}"
    "@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}"
).format(stack=STACK, text=TEXT, muted=MUTED)


def scoped(root, css):
    out, i = [], 0
    while i < len(css):
        j = css.index("{", i)
        sel = css[i:j].strip()
        if sel.startswith("@"):
            depth, k = 0, j
            while True:
                depth += {"{": 1, "}": -1}.get(css[k], 0)
                if depth == 0:
                    break
                k += 1
            out.append(css[i:k + 1])
        else:
            k = css.index("}", j)
            out.append(",".join(f".{root} {part.strip()}" for part in sel.split(",")) + css[j:k + 1])
        i = k + 1
    return "".join(out)


def piece(w, h, body, css="", defs=""):
    return {"w": w, "h": h, "body": body, "css": css, "defs": defs}


def card(w, h, uid, index, title, body, meta="", css="", defs="", glow=(VIOLET, CYAN)):
    fdefs = (
        f'<linearGradient id="{uid}-edge" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{glow[0]}" stop-opacity=".5"/>'
        f'<stop offset=".5" stop-color="{LINE}" stop-opacity=".9"/>'
        f'<stop offset="1" stop-color="{glow[1]}" stop-opacity=".5"/></linearGradient>'
        f'<radialGradient id="{uid}-g1" cx="0" cy="0" r="{f(max(1.0, 520 / w))}">'
        f'<stop offset="0" stop-color="{glow[0]}" stop-opacity=".2"/><stop offset="1" stop-color="{glow[0]}" stop-opacity="0"/></radialGradient>'
        f'<radialGradient id="{uid}-g2" cx="1" cy="1" r="{f(max(1.0, 520 / w))}">'
        f'<stop offset="0" stop-color="{glow[1]}" stop-opacity=".14"/><stop offset="1" stop-color="{glow[1]}" stop-opacity="0"/></radialGradient>'
        f'<clipPath id="{uid}-clip"><rect width="{w}" height="{h}" rx="{RX}"/></clipPath>'
    )
    back = (
        f'<rect width="{w}" height="{h}" rx="{RX}" fill="{PANEL}"/>'
        f'<g clip-path="url(#{uid}-clip)"><rect width="{w}" height="{h}" fill="url(#{uid}-g1)"/>'
        f'<rect width="{w}" height="{h}" fill="url(#{uid}-g2)"/></g>'
    )
    head = (
        f'<text x="24" y="36" class="k"><tspan fill="{glow[0]}">N°{index:02d}</tspan>  {esc(title)}</text>'
        + (f'<text x="{w - 24}" y="36" class="k" text-anchor="end">{esc(meta)}</text>' if meta else "")
    )
    edge = f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="{RX}" fill="none" stroke="url(#{uid}-edge)"/>'
    return piece(w, h, back + f'<g clip-path="url(#{uid}-clip)">{body}</g>' + head + edge, css, fdefs + defs)


def document(h, body, css="", defs="", label="", w=POSTER):
    text = html.unescape("".join(re.findall(r">([^<>]*)<", body))) + label
    style = font_face(text) + BASE_CSS + css
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">'
        f"<title>{esc(label)}</title><defs><style>{style}</style>{defs}</defs>{body}</svg>"
    )


def compose(rows, label):
    y = PAD
    body, css, defs = [], [], [GRAIN]
    for row in rows:
        h = max(p["h"] for p in row)
        x = PAD
        for p in row:
            body.append(f'<svg x="{x}" y="{y}" width="{p["w"]}" height="{p["h"]}" overflow="hidden">{p["body"]}</svg>')
            css.append(p["css"])
            defs.append(p["defs"])
            x += p["w"] + GAP
        y += h + GAP
    total = y - GAP + PAD
    frame = (
        f'<rect width="{POSTER}" height="{total}" rx="26" fill="{INK}"/>'
        f'<rect width="{POSTER}" height="{total}" rx="26" fill="url(#poster-dots)"/>'
    )
    defs.append(
        '<pattern id="poster-dots" width="14" height="14" patternUnits="userSpaceOnUse">'
        '<circle cx="1" cy="1" r=".7" fill="#ffffff" opacity=".05"/></pattern>'
    )
    return document(total, frame + "".join(body), "".join(css), "".join(defs), label)
