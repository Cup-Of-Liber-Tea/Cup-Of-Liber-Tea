import datetime as dt
import math

from ..svg import CYAN, MUTED, PINK, VIOLET, W, piece, smooth

H = 54


def wave(k, phase):
    pts = []
    for i in range(29):
        x = -30 + i * 31
        y = 16 + 6 * math.sin(i * 0.45 + phase + k) + 4 * math.sin(i * 0.17 - phase * 1.3)
        pts.append((x, y))
    return smooth(pts)


def render(data, state):
    now = dt.datetime.fromisoformat(data["now"])
    lines = []
    for k, col in enumerate((VIOLET, CYAN, PINK)):
        ds = [wave(k, p) for p in (0, 1.6, 3.2)]
        lines.append(
            f'<path d="{ds[0]}" fill="none" stroke="{col}" stroke-width="1.2" opacity="{.7 - k * .15:.2f}" mask="url(#ft-m)">'
            f'<animate attributeName="d" dur="{9 + k * 3}s" repeatCount="indefinite" values="{ds[0]};{ds[1]};{ds[2]};{ds[0]}"/></path>'
        )
    text = (
        f'<text x="{W / 2}" y="46" text-anchor="middle" font-size="9" letter-spacing="2.6" font-weight="700" fill="{MUTED}">'
        f"PYTHON → SVG + CSS 3D · RENDERED BY GITHUB ACTIONS · EDITION #{state.get('edition', 1):04d} · {now:%Y-%m-%d %H:%M} KST</text>"
    )
    defs = (
        '<linearGradient id="ft-g" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        '<stop offset=".5" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
        f'<mask id="ft-m" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="url(#ft-g)"/></mask>'
    )
    return piece(W, H, "".join(lines) + text, "", defs)
