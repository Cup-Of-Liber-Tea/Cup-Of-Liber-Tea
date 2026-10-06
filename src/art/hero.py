import datetime as dt
import math

from ..svg import CYAN, INK, MINT, MUTED, PINK, RX, VIOLET, W, esc, f, mix, piece, ramp, rng, smooth

H = 430

SKIES = {
    "night": ("#020309", "#0a0c26", "#2a1356"),
    "dawn": ("#070a22", "#3b1d5e", "#ff8a5c"),
    "day": ("#03102a", "#0b3a74", "#36a2ec"),
    "dusk": ("#06041a", "#3a0f55", "#ff4f8b"),
}

WEATHER = {
    0: "CLEAR SKY", 1: "MAINLY CLEAR", 2: "PARTLY CLOUDY", 3: "OVERCAST", 45: "FOG", 48: "RIME FOG",
    51: "LIGHT DRIZZLE", 53: "DRIZZLE", 55: "DENSE DRIZZLE", 56: "FREEZING DRIZZLE", 57: "FREEZING DRIZZLE",
    61: "LIGHT RAIN", 63: "RAIN", 65: "HEAVY RAIN", 66: "FREEZING RAIN", 67: "FREEZING RAIN",
    71: "LIGHT SNOW", 73: "SNOW", 75: "HEAVY SNOW", 77: "SNOW GRAINS", 80: "RAIN SHOWERS",
    81: "RAIN SHOWERS", 82: "VIOLENT SHOWERS", 85: "SNOW SHOWERS", 86: "SNOW SHOWERS",
    95: "THUNDERSTORM", 96: "STORM + HAIL", 99: "STORM + HAIL",
}

ROLES = [
    "automating the boring parts of the internet",
    "self-hosting everything that can be self-hosted",
    "building infra that pages nobody at 3am",
    "turning coffee and kimchi into commits",
]


def kind_of(code):
    if code is None or code in (0, 1):
        return "clear"
    if code in (2, 3):
        return "cloudy"
    if code in (45, 48):
        return "fog"
    if 71 <= code <= 77 or code in (85, 86):
        return "snow"
    if code >= 95:
        return "storm"
    return "rain"


def phase_of(h):
    if 5 <= h < 7.5:
        return "dawn"
    if 7.5 <= h < 17:
        return "day"
    if 17 <= h < 20:
        return "dusk"
    return "night"


def ribbon(r, k, phase_shift):
    top, bot = [], []
    a1, a2 = r.uniform(14, 30), r.uniform(6, 14)
    w1, w2 = r.uniform(1.2, 2.2), r.uniform(3, 5)
    base = 70 + k * 26
    for i in range(15):
        x = -40 + i * 66
        t = x / W * math.tau
        y = base + a1 * math.sin(w1 * t + phase_shift + k) + a2 * math.sin(w2 * t - phase_shift * 1.7)
        th = 26 + 22 * math.sin(t * 1.3 + phase_shift + k * 0.7) ** 2
        top.append((x, y))
        bot.append((x, y + th))
    path = smooth(top)
    back = smooth(bot[::-1])
    return path + " L" + back[1:] + "Z"


def aurora(r, phase):
    strength = {"night": 0.62, "dusk": 0.5, "dawn": 0.42, "day": 0.24}[phase]
    out = []
    for k in range(4):
        rr = rng("aurora", r.random(), k)
        ds = [ribbon(rr, k, s) for s in (0, 1.1, 2.3)]
        dur = 16 + k * 5
        out.append(
            f'<path d="{ds[0]}" fill="url(#rib{k % 2})" opacity="{f(strength * (1 - k * 0.12))}" filter="url(#soft)">'
            f'<animate attributeName="d" dur="{dur}s" repeatCount="indefinite" values="{ds[0]};{ds[1]};{ds[2]};{ds[0]}" '
            f'calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1;.45 0 .55 1"/></path>'
        )
    return "".join(out)


def stars(r, phase):
    n = {"night": 150, "dusk": 80, "dawn": 50, "day": 14}[phase]
    out = []
    for i in range(n):
        x, y = r.uniform(0, W), r.uniform(0, 240) ** 1.08
        rad = r.choice([0.35, 0.5, 0.6, 0.8, 1.1, 1.4])
        op = r.uniform(0.25, 0.95)
        if i % 4 == 0:
            out.append(
                f'<circle cx="{f(x)}" cy="{f(y)}" r="{rad}" fill="#fff" opacity="{f(op)}">'
                f'<animate attributeName="opacity" values="{f(op)};.05;{f(op)}" dur="{f(r.uniform(2, 6))}s" '
                f'begin="-{f(r.uniform(0, 6))}s" repeatCount="indefinite"/></circle>'
            )
        else:
            out.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{rad}" fill="#fff" opacity="{f(op * 0.7)}"/>')
    return "".join(out)


def celestial(h, kind):
    day = 6 <= h < 19
    t = (h - 6) / 13 if day else ((h - 19) % 24) / 11
    x = 70 + t * 700
    y = 250 - math.sin(math.pi * t) * 185
    dim = 0.35 if kind in ("rain", "storm", "fog", "snow") else (0.7 if kind == "cloudy" else 1)
    if day:
        return (
            f'<g opacity="{dim}"><circle cx="{f(x)}" cy="{f(y)}" r="90" fill="url(#sunglow)"/>'
            f'<circle cx="{f(x)}" cy="{f(y)}" r="20" fill="#ffe3a3"/></g>'
        )
    return (
        f'<g opacity="{dim}"><circle cx="{f(x)}" cy="{f(y)}" r="70" fill="url(#moonglow)"/>'
        f'<circle cx="{f(x)}" cy="{f(y)}" r="15" fill="#eef0ff"/>'
        f'<circle cx="{f(x + 7)}" cy="{f(y - 4)}" r="13" fill="#0a0c26" opacity=".92"/></g>'
    )


def weather_layer(r, kind, phase):
    out = []
    if kind in ("rain", "storm"):
        n = 110 if kind == "storm" else 80
        for _ in range(n):
            x, l = r.uniform(0, W + 120), r.uniform(9, 18)
            d = r.uniform(0.55, 1.0)
            out.append(
                f'<line x1="{f(x)}" y1="0" x2="{f(x - l * 0.35)}" y2="{f(l)}" stroke="#bcd7ff" stroke-width=".9" opacity="{f(r.uniform(.2, .55))}">'
                f'<animateTransform attributeName="transform" type="translate" from="0 -40" to="-120 {H + 20}" '
                f'dur="{f(d)}s" begin="-{f(r.uniform(0, d))}s" repeatCount="indefinite"/></line>'
            )
        if kind == "storm":
            out.append(
                '<rect width="100%" height="100%" fill="#dfe6ff" opacity="0">'
                '<animate attributeName="opacity" values="0;0;.55;0;.35;0;0" keyTimes="0;.62;.63;.65;.66;.69;1" dur="7s" repeatCount="indefinite"/></rect>'
            )
    elif kind == "snow":
        for _ in range(90):
            x, rad, d = r.uniform(-40, W + 40), r.uniform(0.8, 2.4), r.uniform(7, 15)
            out.append(
                f'<circle cx="{f(x)}" cy="-10" r="{f(rad)}" fill="#fff" opacity="{f(r.uniform(.35, .85))}">'
                f'<animateTransform attributeName="transform" type="translate" values="0 0;{f(r.uniform(-30, 30))} {H / 2};{f(r.uniform(-40, 40))} {H + 20}" '
                f'dur="{f(d)}s" begin="-{f(r.uniform(0, d))}s" repeatCount="indefinite"/></circle>'
            )
    elif kind in ("fog", "cloudy"):
        n, col, op = (5, "#cfd6ff", 0.09) if kind == "fog" else (6, "#0b0d1f", 0.55)
        for i in range(n):
            y, rx, d = r.uniform(30, 230), r.uniform(160, 300), r.uniform(50, 90)
            out.append(
                f'<ellipse cx="0" cy="{f(y)}" rx="{f(rx)}" ry="{f(rx * 0.18)}" fill="{col}" opacity="{op}" filter="url(#fogblur)">'
                f'<animateTransform attributeName="transform" type="translate" from="-320 0" to="{W + 320} 0" '
                f'dur="{f(d)}s" begin="-{f(r.uniform(0, d))}s" repeatCount="indefinite"/></ellipse>'
            )
    elif phase != "day":
        for i in range(3):
            x, y = r.uniform(200, W + 100), r.uniform(10, 120)
            out.append(
                f'<g opacity="0"><line x1="{f(x)}" y1="{f(y)}" x2="{f(x + 90)}" y2="{f(y - 30)}" stroke="url(#meteor)" stroke-width="1.4" stroke-linecap="round"/>'
                f'<animate attributeName="opacity" values="0;1;0" keyTimes="0;.04;.1" dur="11s" begin="{2 + i * 3.7}s" repeatCount="indefinite"/>'
                f'<animateTransform attributeName="transform" type="translate" values="0 0;-260 86;-260 86" keyTimes="0;.1;1" dur="11s" begin="{2 + i * 3.7}s" repeatCount="indefinite"/></g>'
            )
    return "".join(out)


def ridges(weeks, r):
    recent = [[d["count"] for d in w] + [0] * (7 - len(w)) for w in (weeks or [])[-22:]]
    while len(recent) < 22:
        recent.insert(0, [0] * 7)
    peak = max(1, max(max(w) for w in recent))
    out = []
    x0, x1, n = -10, W + 10, 140
    out.append('<g mask="url(#fade)">')
    for k, week in enumerate(recent):
        base = 244 + k * 6
        jit = rng("ridge", k, r.random())
        phases = [jit.uniform(0, math.tau) for _ in range(3)]
        line = []
        for i in range(n + 1):
            t = i / n
            env = math.exp(-((t - 0.5) / 0.27) ** 4)
            u = (t - 0.18) / 0.64 * 8
            seq = [0] + week + [0]
            if 0 <= u <= 8:
                a = int(min(7, u))
                s = (1 - math.cos(math.pi * (u - a))) / 2
                v = (seq[a] * (1 - s) + seq[a + 1] * s) / peak
            else:
                v = 0
            noise = sum(math.sin(t * (9 + j * 7) + phases[j]) for j in range(3)) / 3
            y = base - env * (62 * v ** 0.7 + 4 * noise + 3) - 0.5
            line.append((x0 + t * (x1 - x0), y))
        tone = ramp(["#3a2d7a", "#6b5cff", CYAN, "#e6fdff"], (k / 21) ** 1.6)
        d = smooth(line)
        out.append(
            f'<path d="{d} L{x1} {f(base + 60)} L{x0} {f(base + 60)}Z" fill="url(#ground)"/>'
            f'<path d="{d}" fill="none" stroke="{tone}" stroke-width="{1.1 + k * 0.025:.2f}" opacity="{f(.45 + k / 21 * .55)}"/>'
        )
        if k == 21:
            out.append(
                f'<path d="{d}" fill="none" stroke="#fff" stroke-width="1.6" filter="url(#glow)" pathLength="1" '
                f'stroke-dasharray=".14 .86"><animate attributeName="stroke-dashoffset" from="1" to="0" dur="6s" repeatCount="indefinite"/></path>'
            )
    out.append("</g>")
    return "".join(out)


def typer(lines, x_center, y, size=15):
    cw = size * 0.6
    tl = [[] for _ in lines]
    cur = []
    t = 0.0
    type_s, hold, erase_s, pause = 0.045, 2.6, 0.016, 0.45
    for i, s in enumerate(lines):
        for j in range(len(s) + 1):
            for k in range(len(lines)):
                tl[k].append((t, j * cw if k == i else 0))
            cur.append((t, j * cw))
            t += type_s
        t += hold
        for j in range(len(s), -1, -1):
            for k in range(len(lines)):
                tl[k].append((t, j * cw if k == i else 0))
            cur.append((t, j * cw))
            t += erase_s
        t += pause
    period = t
    widest = max(len(s) for s in lines) * cw + 2 * cw
    x = x_center - widest / 2 + 2 * cw

    def anim(seq, attr, offset=0.0):
        keys, vals = [], []
        for tt, v in seq:
            kt = tt / period
            if keys and kt <= keys[-1]:
                continue
            keys.append(kt)
            vals.append(f(v + offset))
        keys[0] = 0
        return (f'<animate attributeName="{attr}" dur="{f(period)}s" repeatCount="indefinite" calcMode="discrete" '
                f'keyTimes="{";".join(f"{k:.4f}" for k in keys)}" values="{";".join(vals)}"/>')

    out = [f'<text x="{f(x - 2 * cw)}" y="{y}" font-size="{size}" fill="{MINT}" font-weight="700">$</text>']
    for i, s in enumerate(lines):
        out.append(
            f'<clipPath id="type{i}"><rect x="{f(x)}" y="{y - size}" width="0" height="{size + 6}">{anim(tl[i], "width")}</rect></clipPath>'
            f'<text x="{f(x)}" y="{y}" font-size="{size}" clip-path="url(#type{i})" fill="#dfe4ff">{esc(s)}</text>'
        )
    out.append(
        f'<rect x="{f(x)}" y="{y - size + 2}" width="{f(cw)}" height="{size + 1}" fill="{CYAN}" opacity=".9">'
        f'{anim(cur, "x", x)}<animate attributeName="opacity" values=".9;.15;.9" dur="1s" repeatCount="indefinite"/></rect>'
    )
    return "".join(out)


def title(text, y):
    common = f'x="{W / 2}" y="{y}" text-anchor="middle" font-size="50" font-weight="800" letter-spacing="3"'
    glitch = (
        '<animateTransform attributeName="transform" type="translate" dur="5.5s" repeatCount="indefinite" '
        'values="0 0;0 0;-3 1;2 -1;0 0;0 0" keyTimes="0;.86;.88;.9;.92;1"/>'
    )
    return (
        f'<text {common} fill="{VIOLET}" opacity=".75" filter="url(#bloom)">{esc(text)}</text>'
        f'<g opacity=".55"><text {common} fill="{CYAN}" transform="translate(-1.6 0)">{esc(text)}{glitch}</text>'
        f'<text {common} fill="{PINK}" transform="translate(1.6 0)">{esc(text)}</text></g>'
        f'<text {common} fill="url(#titlefill)">{esc(text)}</text>'
        f'<text {common} fill="none" stroke="#fff" stroke-width=".7" stroke-dasharray="190" stroke-dashoffset="190" opacity=".9">{esc(text)}'
        f'<animate attributeName="stroke-dashoffset" from="190" to="0" dur="3.2s" fill="freeze"/>'
        f'<animate attributeName="opacity" values=".9;.9;0" keyTimes="0;.7;1" dur="4.5s" fill="freeze"/></text>'
    )


def render(data, state):
    now = dt.datetime.fromisoformat(data["now"])
    h = now.hour + now.minute / 60
    w = data.get("weather") or {}
    code = w.get("code")
    kind = kind_of(code)
    phase = phase_of(h)
    top, mid, hor = SKIES[phase]
    prof = data.get("profile") or {}
    edition = state.get("edition", 1)
    seed = state.get("seed") or f"{edition:07x}"
    r = rng("hero", seed, now.strftime("%Y%m%d%H"))

    defs = (
        f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{top}"/>'
        f'<stop offset=".45" stop-color="{mid}"/><stop offset=".72" stop-color="{hor}"/><stop offset="1" stop-color="{INK}"/></linearGradient>'
        f'<linearGradient id="ground" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{mix(INK, hor, .18)}"/><stop offset=".5" stop-color="{INK}"/></linearGradient>'
        f'<linearGradient id="rib0" x1="0" x2="1"><stop offset="0" stop-color="{MINT}" stop-opacity="0"/><stop offset=".3" stop-color="{MINT}"/>'
        f'<stop offset=".65" stop-color="{CYAN}"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></linearGradient>'
        f'<linearGradient id="rib1" x1="0" x2="1"><stop offset="0" stop-color="{VIOLET}" stop-opacity="0"/><stop offset=".4" stop-color="{VIOLET}"/>'
        f'<stop offset=".75" stop-color="{PINK}"/><stop offset="1" stop-color="{PINK}" stop-opacity="0"/></linearGradient>'
        '<linearGradient id="titlefill" x1="0" x2="1" gradientUnits="objectBoundingBox">'
        '<stop offset="0" stop-color="#ffffff"/><stop offset=".45" stop-color="#d9d2ff"/><stop offset=".5" stop-color="#ffffff"/>'
        '<stop offset=".55" stop-color="#bff6ff"/><stop offset="1" stop-color="#ffffff"/>'
        '<animateTransform attributeName="gradientTransform" type="translate" values="-1 0;1 0" dur="6s" repeatCount="indefinite"/></linearGradient>'
        '<linearGradient id="meteor" x1="0" x2="1"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
        '<radialGradient id="sunglow"><stop offset="0" stop-color="#ffcf7a" stop-opacity=".55"/><stop offset="1" stop-color="#ffcf7a" stop-opacity="0"/></radialGradient>'
        '<radialGradient id="moonglow"><stop offset="0" stop-color="#c9d2ff" stop-opacity=".35"/><stop offset="1" stop-color="#c9d2ff" stop-opacity="0"/></radialGradient>'
        '<radialGradient id="vignette" cx=".5" cy=".45" r=".75"><stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".65"/></radialGradient>'
        '<filter id="soft" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="9"/></filter>'
        '<filter id="fogblur" x="-50%" y="-200%" width="200%" height="500%"><feGaussianBlur stdDeviation="18"/></filter>'
        '<filter id="bloom" x="-20%" y="-60%" width="140%" height="220%"><feGaussianBlur stdDeviation="12"/></filter>'
        '<filter id="glow" x="-10%" y="-50%" width="120%" height="200%"><feGaussianBlur stdDeviation="2.2" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
        '<linearGradient id="fadeg" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".14" stop-color="#fff"/>'
        '<stop offset=".86" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
        f'<mask id="fade"><rect width="{W}" height="{H}" fill="url(#fadeg)"/></mask>'
        f'<clipPath id="hero"><rect width="{W}" height="{H}" rx="{RX}"/></clipPath>'
    )

    since = (prof.get("created") or "2024")[:4]
    temp = w.get("temp")
    wx = WEATHER.get(code, "—") if code is not None else "NO SIGNAL"
    caption_l = f"EDITION #{edition:04d}  ·  SEED {seed[:7]}"
    caption_r = f"DAEJEON {now:%H:%M} KST  ·  " + (f"{temp:.0f}°C  ·  " if temp is not None else "") + wx

    body = (
        f'<g clip-path="url(#hero)"><rect width="{W}" height="{H}" fill="url(#sky)"/>'
        + stars(r, phase)
        + celestial(h, kind)
        + aurora(r, phase)
        + weather_layer(r, kind, phase)
        + ridges(prof.get("weeks"), r)
        + f'<rect width="{W}" height="{H}" fill="url(#vignette)"/>'
        + f'<rect width="{W}" height="{H}" filter="url(#grain)" opacity=".07"/>'
        + "</g>"
        + title("CUP-OF-LIBER-TEA", 112)
        + f'<text x="{W / 2}" y="146" text-anchor="middle" font-size="12" letter-spacing="5" font-weight="700" fill="{MUTED}">'
        f'{esc((prof.get("name") or "coffee kimchi").upper())}  ·  DAEJEON, KR  ·  SINCE {since}</text>'
        + typer(ROLES, W / 2, 182)
        + f'<text x="{W - 64}" y="222" text-anchor="end" font-size="9.5" letter-spacing="2" fill="{MUTED}" opacity=".8">LAST 22 WEEKS OF COMMITS ↓</text>'
        + f'<text x="28" y="{H - 18}" font-size="10" letter-spacing="2.5" font-weight="700" fill="{MUTED}">{esc(caption_l)}</text>'
        + f'<text x="{W - 28}" y="{H - 18}" text-anchor="end" font-size="10" letter-spacing="2.5" font-weight="700" fill="{MUTED}">{esc(caption_r)}</text>'
        + f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="{RX}" fill="none" stroke="#ffffff" stroke-opacity=".1"/>'
    )
    return piece(W, H, body, "", defs)
