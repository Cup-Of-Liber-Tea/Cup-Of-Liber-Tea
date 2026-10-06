import datetime as dt
import math

from ..fonts import STACK
from ..svg import CYAN, HALF, MUTED, PINK, VIOLET, card, esc, f, scoped

SLOTS = 56
R = 86
GW = 210


def sphere():
    pts = []
    golden = math.pi * (3 - math.sqrt(5))
    for i in range(SLOTS):
        y = 1 - 2 * (i + 0.5) / SLOTS
        pts.append((math.degrees(golden * i) % 360, math.degrees(math.asin(y))))
    return sorted(pts, key=lambda p: abs(p[1]))


def globe(signers, avatars, gy, gh):
    items = []
    for i, (lon, lat) in enumerate(sphere()):
        tf = f"rotateY({f(lon)}deg) rotateX({f(lat)}deg) translateZ({R}px)"
        if i < len(signers):
            s = signers[i]
            src = avatars.get(s["login"])
            inner = f'<img src="{src}" alt=""/>' if src else f'<span>{esc(s["login"][:1].upper())}</span>'
            items.append(f'<div class="av{" new" if i == 0 else ""}" style="transform:{tf}">{inner}</div>')
        else:
            items.append(f'<div class="dot" style="transform:{tf}"></div>')
    rings = "".join(f'<div class="mer" style="transform:rotateY({a}deg)"></div>' for a in range(0, 180, 30))
    rings += "".join(
        f'<div class="par" style="transform:rotateX(90deg) translateZ({f(R * math.sin(math.radians(a)))}px) scale({f(math.cos(math.radians(a)))})"></div>'
        for a in (-60, -30, 0, 30, 60)
    )
    html = (
        f'<foreignObject x="0" y="{gy}" width="{GW}" height="{gh}">'
        f'<div xmlns="http://www.w3.org/1999/xhtml" class="wl"><div class="gs"><div class="aura"></div><div class="tilt"><div class="g">'
        f'{rings}{"".join(items)}</div></div></div></div></foreignObject>'
    )
    css = (
        f".gs{{width:{GW}px;height:{gh}px;position:relative;perspective:700px;overflow:hidden}}"
        f".aura{{position:absolute;left:50%;top:50%;width:{R * 2 + 60}px;height:{R * 2 + 60}px;margin:-{R + 30}px;border-radius:50%;"
        f"background:radial-gradient(circle,{VIOLET}44,{CYAN}11 55%,transparent 70%);filter:blur(10px)}}"
        ".tilt{position:absolute;left:50%;top:50%;width:0;height:0;transform-style:preserve-3d;transform:rotateX(-16deg) rotateZ(8deg)}"
        ".g{position:absolute;width:0;height:0;transform-style:preserve-3d;animation:globe 32s linear infinite}"
        "@keyframes globe{to{transform:rotateY(360deg)}}"
        f".mer,.par{{position:absolute;left:-{R}px;top:-{R}px;width:{R * 2}px;height:{R * 2}px;border-radius:50%;"
        f"border:1px solid {CYAN}30;box-sizing:border-box}}"
        f".par{{border-color:{VIOLET}40}}"
        ".av,.dot{position:absolute;backface-visibility:hidden}"
        f".av{{left:-12px;top:-12px;width:24px;height:24px;border-radius:50%;overflow:hidden;box-shadow:0 0 0 1.5px #fff,0 0 12px {CYAN};background:#0d1020}}"
        ".av img{width:100%;height:100%;display:block}"
        f".av span{{display:flex;width:100%;height:100%;align-items:center;justify-content:center;font:800 11px {STACK};color:#fff;"
        f"background:linear-gradient(135deg,{VIOLET},{PINK})}}"
        f".av.new{{box-shadow:0 0 0 2px {PINK},0 0 18px {PINK}}}"
        f".dot{{left:-1.5px;top:-1.5px;width:3px;height:3px;border-radius:50%;background:{CYAN};box-shadow:0 0 6px {CYAN};opacity:.75}}"
    )
    return html, scoped("wl", css)


def ago(ts, now):
    if not ts:
        return ""
    m = int((now - dt.datetime.fromisoformat(ts)).total_seconds() // 60)
    return f"{m}m" if m < 60 else f"{m // 60}h" if m < 1440 else f"{m // 1440}d"


def render(data, state, h=330):
    now = dt.datetime.fromisoformat(data["now"])
    signers = state.get("wall") or []
    html, css = globe(signers, data.get("wall_avatars") or {}, 44, h - 52)
    x, x1 = GW + 8, HALF - 24
    side = [
        f'<text x="{x}" y="96" font-size="40" font-weight="800" fill="url(#wl-num)">{len(signers)}</text>'
        f'<text x="{x + 2}" y="116" font-size="8.5" letter-spacing="1.8" font-weight="700" fill="{MUTED}">SIGNATURES</text>'
    ]
    for i, s in enumerate(signers[:4]):
        y = 146 + i * 20
        side.append(
            f'<text x="{x}" y="{y}" font-size="11" font-weight="700" fill="{PINK if i == 0 else "#e9ecff"}">@{esc(s["login"][:13])}</text>'
            f'<text x="{x1}" y="{y}" text-anchor="end" font-size="9.5" fill="{MUTED}">{esc(ago(s.get("t"), now))}</text>'
        )
    if not signers:
        side.append(f'<text x="{x}" y="146" font-size="11" fill="{MUTED}">empty sky.</text>'
                    f'<text x="{x}" y="162" font-size="11" fill="{MUTED}">be the first star.</text>')
    by = h - 84
    side.append(
        f'<rect x="{x}" y="{by}" width="{x1 - x}" height="58" rx="10" fill="#ffffff06" stroke="{PINK}" stroke-opacity=".5" stroke-dasharray="4 4">'
        f'<animate attributeName="stroke-dashoffset" from="0" to="16" dur="1.2s" repeatCount="indefinite"/></rect>'
        f'<text x="{x + 12}" y="{by + 22}" font-size="10.5" font-weight="800">open an issue</text>'
        f'<text x="{x + 12}" y="{by + 38}" font-size="10.5" font-weight="800">titled <tspan fill="{PINK}">sign</tspan> ✦</text>'
    )
    defs = f'<linearGradient id="wl-num" x1="0" x2="1"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="{PINK}"/></linearGradient>'
    return card(HALF, h, "wl", 6, "GUESTBOOK", html + "".join(side), "VIA ACTIONS", css, defs, glow=(PINK, CYAN))
