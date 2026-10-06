from ..svg import CYAN, HALF, MINT, MUTED, RED, card, esc, f, mix, rng

ROW = 88
TOP = 52
X0, X1 = 24, HALF - 24
SLOTS = 48
BEAT = 64
MIN_H = 330


def height(state):
    n = len(state.get("pulse") or {})
    return max(MIN_H, TOP + n * ROW + 10) if n else MIN_H


def beat_path(width, up, seed):
    r = rng("ecg", seed)
    d = []
    x = 0.0
    while x < width + BEAT:
        if up:
            seg = [(0, 0), (11, 0), (15, -3), (19, 0), (25, 0), (27, 4), (30, -20), (33, 9), (36, 0),
                   (44, 0), (49, -5), (54, 0), (BEAT, 0)]
        else:
            seg = [(0, 0), (BEAT * .3, r.uniform(-1, 1)), (BEAT * .6, r.uniform(-1, 1)), (BEAT, 0)]
        for sx, sy in seg:
            d.append(f"{'M' if not d else 'L'}{f(x + sx)} {f(sy)}")
        x += BEAT
    return " ".join(d)


def row(i, name, hist):
    y = TOP + i * ROW
    last = hist[-1] if hist else {"up": False, "ms": None}
    up = last["up"]
    col = MINT if up else RED
    pct = 100 * sum(1 for h in hist if h["up"]) / len(hist) if hist else 0
    ms = f'{last["ms"]}ms' if last.get("ms") is not None else "timeout"
    out = [
        f'<circle cx="{X0 + 4}" cy="{y + 12}" r="4" fill="{col}"/>'
        f'<circle cx="{X0 + 4}" cy="{y + 12}" r="4" fill="none" stroke="{col}"><animate attributeName="r" values="4;11" dur="{1.4 if up else .7}s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values=".9;0" dur="{1.4 if up else .7}s" repeatCount="indefinite"/></circle>'
        f'<text x="{X0 + 16}" y="{y + 16}" font-size="13" font-weight="800">{esc(name)}</text>'
        f'<text x="{X1}" y="{y + 16}" text-anchor="end" font-size="9.5" letter-spacing="1.4" font-weight="700" fill="{col}">'
        f'{"UP" if up else "DOWN"}<tspan fill="{MUTED}" font-weight="400"> · {esc(ms)}</tspan></text>'
    ]
    cy = y + 44
    span = X1 - X0
    out.append(
        f'<clipPath id="pl-c{i}"><rect x="{X0}" y="{cy - 26}" width="{span}" height="40"/></clipPath>'
        f'<g clip-path="url(#pl-c{i})"><g transform="translate({X0} {cy})" mask="url(#pl-fade)"><g>'
        f'<animateTransform attributeName="transform" type="translate" from="0 0" to="-{BEAT} 0" dur="{1.1 if up else 3.5}s" repeatCount="indefinite"/>'
        f'<path d="{beat_path(span, up, f"{name}{i}")}" fill="none" stroke="{col}" stroke-width="1.5" stroke-linejoin="round" filter="url(#pl-glow)"/>'
        f"</g></g></g>"
    )
    bar_x1 = X1 - 74
    cw = (bar_x1 - X0) / SLOTS
    recent = hist[-SLOTS:]
    lat = [h["ms"] for h in recent if h.get("ms")]
    worst = max(lat) if lat else 1
    by = y + 70
    for j in range(SLOTS):
        bx = X0 + j * cw
        k = j - (SLOTS - len(recent))
        if k < 0:
            out.append(f'<rect x="{f(bx)}" y="{by}" width="{f(cw - 1.2)}" height="10" rx="1" fill="#ffffff08"/>')
            continue
        h = recent[k]
        c = mix(MINT, CYAN, (h.get("ms") or 0) / worst) if h["up"] else RED
        out.append(f'<rect x="{f(bx)}" y="{by}" width="{f(cw - 1.2)}" height="10" rx="1" fill="{c}" opacity="{.4 + .6 * (j + 1) / SLOTS:.2f}"/>')
    out.append(
        f'<text x="{X1}" y="{by + 9}" text-anchor="end" font-size="10" fill="{MUTED}"><tspan fill="#fff" font-weight="800">{pct:.1f}%</tspan> up</text>'
    )
    if i:
        out.insert(0, f'<line x1="{X0}" x2="{X1}" y1="{y - 6}" y2="{y - 6}" stroke="#ffffff0d"/>')
    return "".join(out)


def render(data, state, h=None):
    nodes = state.get("pulse") or {}
    names = list(nodes)
    h = h or height(state)
    defs = (
        '<filter id="pl-glow" x="-10%" y="-80%" width="120%" height="260%"><feGaussianBlur stdDeviation="2.2" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
        '<linearGradient id="pl-fg" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        '<stop offset=".2" stop-color="#fff"/><stop offset=".85" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity=".1"/></linearGradient>'
        f'<mask id="pl-fade" maskUnits="userSpaceOnUse" x="-20" y="-60" width="{X1 - X0 + 200}" height="120">'
        f'<rect x="0" y="-60" width="{X1 - X0}" height="120" fill="url(#pl-fg)"/></mask>'
    )
    if not names:
        body = (f'<text x="24" y="90" font-size="14" font-weight="800">NO TARGETS</text>'
                f'<text x="24" y="110" font-size="10.5" fill="{MUTED}">add a STATUS_TARGETS secret</text>'
                f'<text x="24" y="126" font-size="10.5" fill="{MUTED}">one "name|url" per line</text>')
        return card(HALF, h, "pl", 5, "SERVICE PULSE", body, "STANDBY", "", defs, glow=(MINT, CYAN))
    down = sum(1 for n in names if not (nodes[n] and nodes[n][-1]["up"]))
    meta = "ALL NOMINAL" if not down else f"{down}/{len(names)} DOWN"
    body = "".join(row(i, n, nodes[n]) for i, n in enumerate(names))
    return card(HALF, h, "pl", 5, "SERVICE PULSE", body, meta, "", defs, glow=(MINT, CYAN) if not down else (RED, MINT))
