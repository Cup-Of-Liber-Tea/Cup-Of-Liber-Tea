import datetime as dt
import math

from ..svg import AMBER, CYAN, HALF, MUTED, PINK, VIOLET, arc, card, esc, f, ramp

H = 500
CX, CY = HALF / 2, 214
R0, RW = 36, 16
HEAT = ["#16112e", "#3b1f78", VIOLET, PINK, AMBER, "#fff4cc"]

VERDICTS = [
    ("VAMPIRE", "the repo wakes when the city sleeps", lambda s: s["vampire"] >= 0.28),
    ("NIGHT OWL", "most code ships after dark", lambda s: s["night"] >= 0.38),
    ("EARLY BIRD", "commits before the coffee cools", lambda s: s["early"] >= 0.22),
    ("WEEKEND WARRIOR", "saturdays are for shipping", lambda s: s["weekend"] >= 0.38),
    ("9-TO-5 MACHINE", "clean hours, clean diffs", lambda s: s["office"] >= 0.6),
    ("ALWAYS ON", "there is no off switch", lambda s: True),
]


def analyse(times):
    grid = [[0] * 24 for _ in range(7)]
    for t in times:
        d = dt.datetime.fromisoformat(t)
        grid[d.weekday()][d.hour] += 1
    n = sum(map(sum, grid))
    total = n or 1
    hours = [sum(grid[d][h] for d in range(7)) for h in range(24)]

    def share(hs, ds=range(7)):
        return sum(grid[d][h] for d in ds for h in hs) / total

    s = {
        "vampire": share(range(0, 5)),
        "night": share(list(range(21, 24)) + list(range(0, 4))),
        "early": share(range(5, 9)),
        "weekend": share(range(24), (5, 6)),
        "office": share(range(9, 18), range(5)),
    }
    name, line = next((v, l) for v, l, test in VERDICTS if test(s))
    if not n:
        name, line = "UNKNOWN", "no commit signal yet"
    return grid, hours, s, name, line, n


def dial(grid, now):
    peak = max(max(r) for r in grid) or 1
    out = []
    gap = math.radians(1)
    for d in range(7):
        r0 = R0 + d * RW + 1
        r1 = r0 + RW - 2
        for h in range(24):
            a0 = math.radians(-90 + h * 15) + gap
            a1 = math.radians(-90 + (h + 1) * 15) - gap
            v = grid[d][h]
            col = ramp(HEAT, math.log1p(v) / math.log1p(peak)) if v else "#ffffff0a"
            out.append(
                f'<path d="{arc(CX, CY, r0, r1, a0, a1)}" fill="{col}" opacity="0">'
                f'<animate attributeName="opacity" to="1" dur=".5s" begin="{f((h * 7 + d) * 0.012)}s" fill="freeze"/></path>'
            )
    outer = R0 + 7 * RW
    for h in range(0, 24, 3):
        a = math.radians(-90 + h * 15)
        x, y = CX + (outer + 13) * math.cos(a), CY + (outer + 13) * math.sin(a) + 3.5
        out.append(f'<text x="{f(x)}" y="{f(y)}" text-anchor="middle" font-size="9" font-weight="700" fill="{MUTED}">{h:02d}</text>')
    sweep = (
        f'<path d="M{f(CX)} {CY} L{f(CX)} {CY - outer} A{outer} {outer} 0 0 1 {f(CX + outer * math.sin(math.radians(38)))} '
        f'{f(CY - outer * math.cos(math.radians(38)))} Z" fill="url(#ch-sweep)">'
        f'<animateTransform attributeName="transform" type="rotate" from="0 {f(CX)} {CY}" to="360 {f(CX)} {CY}" dur="7s" repeatCount="indefinite"/></path>'
    )
    na = math.radians(-90 + (now.hour + now.minute / 60) * 15)
    nx, ny = CX + (outer + 4) * math.cos(na), CY + (outer + 4) * math.sin(na)
    needle = (
        f'<line x1="{f(CX + (R0 - 6) * math.cos(na))}" y1="{f(CY + (R0 - 6) * math.sin(na))}" x2="{f(nx)}" y2="{f(ny)}" '
        f'stroke="{CYAN}" stroke-width="1.6" filter="url(#ch-glow)"/>'
        f'<circle cx="{f(nx)}" cy="{f(ny)}" r="3.5" fill="{CYAN}"/>'
        f'<circle cx="{f(nx)}" cy="{f(ny)}" r="3.5" fill="none" stroke="{CYAN}">'
        f'<animate attributeName="r" values="3.5;13" dur="1.8s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="1;0" dur="1.8s" repeatCount="indefinite"/></circle>'
    )
    hub = (
        f'<circle cx="{f(CX)}" cy="{CY}" r="{R0 - 4}" fill="#0b0d1a" stroke="#ffffff14"/>'
        f'<text x="{f(CX)}" y="{CY + 1}" text-anchor="middle" font-size="12.5" font-weight="800">{now:%H:%M}</text>'
        f'<text x="{f(CX)}" y="{CY + 13}" text-anchor="middle" font-size="7" letter-spacing="1.5" font-weight="700" fill="{MUTED}">KST</text>'
    )
    return f'<g>{"".join(out)}</g>{sweep}{needle}{hub}'


def verdict(hours, s, name, line, n):
    peak_h = max(range(24), key=lambda h: hours[h])
    size = 30 if len(name) < 11 else 22
    out = [
        '<text x="24" y="404" class="k" style="font-size:9.5px">YOU ARE A</text>',
        f'<text x="23" y="438" font-size="{size}" font-weight="800" fill="url(#ch-name)">{esc(name)}</text>',
        f'<text x="24" y="470" font-size="11" fill="#c9cdf0">— {esc(line)}</text>',
    ]
    cells = [("PEAK", f"{peak_h:02d}h"), ("DARK", f"{s['night'] * 100:.0f}%"),
             ("WKND", f"{s['weekend'] * 100:.0f}%"), ("N", f"{n}")]
    for i, (k, v) in enumerate(cells):
        x = HALF - 24 - (1 - i % 2) * 62
        y = 404 + (i // 2) * 36
        out.append(
            f'<text x="{x}" y="{y}" text-anchor="end" font-size="15" font-weight="800">{esc(v)}</text>'
            f'<text x="{x}" y="{y + 12}" text-anchor="end" font-size="8" letter-spacing="1.6" font-weight="700" fill="{MUTED}">{k}</text>'
        )
    return "".join(out)


def render(data, state):
    now = dt.datetime.fromisoformat(data["now"])
    grid, hours, s, name, line, n = analyse(data.get("commits") or [])
    defs = (
        f'<linearGradient id="ch-sweep" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{CYAN}" stop-opacity="0"/>'
        f'<stop offset="1" stop-color="{CYAN}" stop-opacity=".28"/></linearGradient>'
        f'<linearGradient id="ch-name" x1="0" x2="1"><stop offset="0" stop-color="{AMBER}"/><stop offset=".55" stop-color="{PINK}"/>'
        f'<stop offset="1" stop-color="{VIOLET}"/></linearGradient>'
        '<filter id="ch-glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
    )
    body = dial(grid, now) + verdict(hours, s, name, line, n)
    return card(HALF, H, "ch", 2, "CHRONOTYPE", body, "MON IN → SUN OUT", "", defs, glow=(PINK, AMBER))
