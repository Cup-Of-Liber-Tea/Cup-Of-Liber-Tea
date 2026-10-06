import math

from ..fonts import STACK
from ..svg import AMBER, CYAN, HALF, MUTED, PINK, VIOLET, card, esc, f, rng, scoped

H = 500
TILT = 68
SY, SH = 44, 336


def planets(langs):
    total = sum(l["bytes"] for l in langs) or 1
    rows = [{**l, "share": l["bytes"] / total} for l in langs[:7]]
    rest = sum(l["bytes"] for l in langs[7:])
    if rest:
        rows.append({"name": "Other", "color": "#5b6078", "bytes": rest, "share": rest / total})
    return rows


def system(rows, avatar):
    n = len(rows)
    out = []
    r = rng("orbit", n)
    for i, row in enumerate(rows):
        rad = 72 + i * (98 / (n - 1)) if n > 1 else 120
        size = 8 + 24 * math.sqrt(row["share"])
        period = 8 * (rad / 80) ** 1.5
        delay = -period * r.random()
        col = row["color"]
        out.append(
            f'<div class="ring" style="--r:{f(rad)}px;border-color:{col}40"></div>'
            f'<div class="orb" style="--t:{f(period)}s;animation-delay:{f(delay)}s">'
            f'<div class="p" style="left:{f(rad - size / 2)}px;top:{f(-size / 2)}px;width:{f(size)}px;height:{f(size)}px;'
            f'--t:{f(period)}s;animation-delay:{f(delay)}s">'
            f'<div class="dot" style="background:radial-gradient(circle at 32% 30%,#fff,{col} 38%,{col}88 70%,#000a);'
            f'box-shadow:0 0 {f(size * .8)}px {col}aa"></div>'
            f'<div class="lab">{esc(row["name"])}</div></div></div>'
        )
    core = f'<img src="{avatar}" alt=""/>' if avatar else '<div class="core"></div>'
    belt = "".join(
        f'<i style="left:{f(math.cos(a) * rr)}px;top:{f(math.sin(a) * rr)}px;opacity:{f(r.uniform(.2, .8))}"></i>'
        for a, rr in ((r.uniform(0, math.tau), r.uniform(182, 196)) for _ in range(80))
    )
    html = (
        f'<foreignObject x="0" y="{SY}" width="{HALF}" height="{SH}">'
        f'<div xmlns="http://www.w3.org/1999/xhtml" class="ob"><div class="stg"><div class="sys">'
        f'<div class="belt">{belt}</div>{"".join(out)}'
        f'<div class="sun"><div class="corona"></div><div class="disc">{core}</div></div>'
        f"</div></div></div></foreignObject>"
    )
    css = (
        f".stg{{width:{HALF}px;height:{SH}px;position:relative;overflow:hidden;perspective:900px;perspective-origin:50% 30%}}"
        f".sys{{position:absolute;left:{HALF / 2}px;top:{SH / 2}px;width:0;height:0;transform-style:preserve-3d;"
        f"transform:rotateX({TILT}deg) rotateZ(-18deg)}}"
        ".ring{position:absolute;left:calc(var(--r)*-1);top:calc(var(--r)*-1);width:calc(var(--r)*2);height:calc(var(--r)*2);"
        "border:1px solid;border-radius:50%;box-sizing:border-box}"
        ".orb{position:absolute;left:0;top:0;width:0;height:0;transform-style:preserve-3d;animation:orb var(--t) linear infinite}"
        "@keyframes orb{to{transform:rotateZ(360deg)}}"
        ".p{position:absolute;transform-style:preserve-3d;animation:bill var(--t) linear infinite}"
        f"@keyframes bill{{from{{transform:rotateZ(0deg) rotateX(-{TILT}deg)}}to{{transform:rotateZ(-360deg) rotateX(-{TILT}deg)}}}}"
        ".dot{position:absolute;inset:0;border-radius:50%}"
        ".lab{position:absolute;top:100%;left:50%;transform:translateX(-50%);margin-top:4px;white-space:nowrap;"
        f"font:700 8.5px/1 {STACK};letter-spacing:.12em;color:#c9cdf0;text-transform:uppercase;text-shadow:0 1px 6px #000}}"
        f".sun{{position:absolute;left:-34px;top:-34px;width:68px;height:68px;transform:rotateX(-{TILT}deg);transform-style:preserve-3d}}"
        f".corona{{position:absolute;inset:-26px;border-radius:50%;background:conic-gradient({AMBER},{PINK},{VIOLET},{CYAN},{AMBER});"
        "filter:blur(14px);opacity:.75;animation:cor 7s linear infinite}"
        "@keyframes cor{to{rotate:360deg}}"
        ".disc{position:absolute;inset:0;border-radius:50%;overflow:hidden;box-shadow:0 0 0 2px #ffffffcc,0 0 30px #ffd59a}"
        ".disc img,.core{width:100%;height:100%;display:block;border-radius:50%}"
        f".core{{background:radial-gradient(circle at 35% 30%,#fff,{AMBER} 40%,{PINK})}}"
        ".belt{position:absolute;left:0;top:0;width:0;height:0;animation:orb 140s linear infinite}"
        ".belt i{position:absolute;width:2px;height:2px;border-radius:50%;background:#cfd4ff}"
    )
    return html, scoped("ob", css)


def legend(rows):
    out = []
    colw = (HALF - 48 - 20) / 2
    for i, row in enumerate(rows):
        col, line = divmod(i, 4)
        x = 24 + col * (colw + 20)
        y = 404 + line * 22
        out.append(
            f'<circle cx="{f(x + 4)}" cy="{y - 4}" r="3.5" fill="{row["color"]}"/>'
            f'<text x="{f(x + 14)}" y="{y}" font-size="11" font-weight="700">{esc(row["name"][:14])}</text>'
            f'<text x="{f(x + colw)}" y="{y}" text-anchor="end" font-size="10" fill="{MUTED}">{row["share"] * 100:.1f}%</text>'
        )
    return "".join(out)


def dust():
    r = rng("dust")
    return "".join(
        f'<circle cx="{f(r.uniform(4, HALF - 4))}" cy="{f(r.uniform(48, 380))}" r="{r.choice([.4, .6, .8, 1])}" fill="#fff" opacity="{f(r.uniform(.1, .6))}"/>'
        for _ in range(80)
    )


def render(data, state):
    prof = data.get("profile") or {}
    repos = prof.get("repos") or {}
    rows = planets(prof.get("langs") or []) or [{"name": "Signal lost", "color": "#5b6078", "bytes": 1, "share": 1}]
    html, css = system(rows, data.get("avatar"))
    defs = (
        f'<radialGradient id="ob-neb" cx=".5" cy=".42" r=".5"><stop offset="0" stop-color="{VIOLET}" stop-opacity=".25"/>'
        f'<stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient>'
    )
    body = (
        f'<rect width="{HALF}" height="{H}" fill="url(#ob-neb)"/>' + dust() + html
        + f'<line x1="24" x2="{HALF - 24}" y1="384" y2="384" stroke="#ffffff10"/>' + legend(rows)
    )
    meta = f'{repos.get("own", 0)} REPOS · ★{repos.get("stars", 0)}'
    return card(HALF, H, "ob", 3, "LANGUAGE ORBIT", body, meta, css, defs, glow=(AMBER, VIOLET))
