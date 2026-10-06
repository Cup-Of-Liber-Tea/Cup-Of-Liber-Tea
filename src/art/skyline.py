import datetime as dt

from ..svg import CYAN, PINK, VIOLET, W, card, esc, f, ramp, scoped, shade

H = 440
STAGE_Y = 52
STAGE_H = H - STAGE_Y - 8
CELL = 12
FOOT = 9.2
TALL = 118
STOPS = ["#2b1d6b", VIOLET, "#4f8cff", CYAN, "#d8fbff"]


def stats(weeks):
    days = [d for w in weeks for d in w]
    if not days:
        return {"total": 0, "current": 0, "longest": 0, "best": None, "active": 0}
    total = sum(d["count"] for d in days)
    longest = run = 0
    for d in days:
        run = run + 1 if d["count"] else 0
        longest = max(longest, run)
    current = 0
    tail = days[::-1]
    if tail and tail[0]["count"] == 0:
        tail = tail[1:]
    for d in tail:
        if not d["count"]:
            break
        current += 1
    best = max(days, key=lambda d: d["count"])
    return {"total": total, "current": current, "longest": longest, "best": best,
            "active": sum(1 for d in days if d["count"])}


def scene(weeks):
    cols = len(weeks)
    peak = max([d["count"] for w in weeks for d in w] + [1])
    pw, ph = cols * CELL, 7 * CELL
    out = []
    for wi, w in enumerate(weeks):
        for d in w:
            c = d["count"]
            if not c:
                continue
            q = (c / peak) ** 0.62
            h = 3 + TALL * q
            col = ramp(STOPS, q)
            dark = shade(col, 0.55)
            mid = shade(col, 0.3)
            x = wi * CELL + (CELL - FOOT) / 2
            y = d["weekday"] * CELL + (CELL - FOOT) / 2
            delay = wi * 0.028 + d["weekday"] * 0.04
            win = " w" if h > 34 else ""
            glow = f";box-shadow:0 0 {f(4 + 14 * q)}px {col}" if q > 0.55 else ""
            out.append(
                f'<div class="b" style="--x:{f(x)}px;--y:{f(y)}px;--h:{f(h)}px;--d:{f(delay)}s">'
                f'<i class="s n{win}" style="background:linear-gradient(0deg,{dark},{mid})"></i>'
                f'<i class="s s2{win}" style="background:linear-gradient(0deg,{dark},{mid})"></i>'
                f'<i class="s e{win}" style="background:linear-gradient(90deg,{shade(col, .7)},{dark})"></i>'
                f'<i class="s e2{win}" style="background:linear-gradient(90deg,{shade(col, .7)},{dark})"></i>'
                f'<i class="t" style="background:{col}{glow}"></i></div>'
            )
    css = (
        f".stage{{width:{W}px;height:{STAGE_H}px;position:relative;overflow:hidden;perspective:1250px;perspective-origin:50% -10%}}"
        f".world{{position:absolute;left:{f((W - pw) / 2)}px;top:{f(STAGE_H / 2 - ph / 2 + 36)}px;width:{pw}px;height:{ph}px;"
        "transform-style:preserve-3d;animation:cam 16s ease-in-out infinite alternate}"
        "@keyframes cam{from{transform:rotateX(58deg) rotateZ(-25deg)}to{transform:rotateX(65deg) rotateZ(-5deg)}}"
        f".plate{{position:absolute;inset:-16px;border-radius:6px;background:"
        f"radial-gradient(closest-side,{VIOLET}33,transparent),"
        f"repeating-linear-gradient(90deg,#ffffff10 0 1px,transparent 1px {CELL}px),"
        f"repeating-linear-gradient(0deg,#ffffff10 0 1px,transparent 1px {CELL}px),#0a0c1acc;"
        f"box-shadow:0 0 0 1px #ffffff14,0 0 60px {VIOLET}55}}"
        ".halo{position:absolute;inset:-120px;border-radius:50%;background:"
        f"conic-gradient(from 0deg,{CYAN}00,{CYAN}55,{PINK}44,{VIOLET}00 40%,{CYAN}00);filter:blur(30px);transform:translateZ(-2px);"
        "animation:halo 9s linear infinite}"
        "@keyframes halo{to{rotate:360deg}}"
        ".b{position:absolute;left:0;top:0;width:" + f(FOOT) + "px;height:" + f(FOOT) + "px;transform-style:preserve-3d;"
        "transform:translate3d(var(--x),var(--y),0);animation:rise 1.6s cubic-bezier(.2,.9,.25,1.08) var(--d) both}"
        "@keyframes rise{from{transform:translate3d(var(--x),var(--y),0) scale3d(1,1,.001)}to{transform:translate3d(var(--x),var(--y),0) scale3d(1,1,1)}}"
        ".b i{position:absolute;display:block}"
        ".t{left:0;top:0;width:100%;height:100%;transform:translateZ(var(--h))}"
        ".s{left:0;width:100%;height:var(--h);transform-origin:0 0}"
        ".n{top:0;transform:rotateX(90deg)}"
        ".s2{top:100%;transform:rotateX(90deg)}"
        ".e,.e2{top:0;width:var(--h);height:100%;transform-origin:0 0;transform:rotateY(-90deg)}"
        ".e2{left:100%}"
        ".w::after{content:'';position:absolute;inset:3px 2px;background:repeating-linear-gradient(0deg,#ffffff00 0 3px,#fff8 3px 4px);"
        "mix-blend-mode:screen;animation:flick 3s steps(2) infinite}"
        "@keyframes flick{50%{opacity:.55}}"
    )
    html = (
        f'<foreignObject x="0" y="{STAGE_Y}" width="{W}" height="{STAGE_H}">'
        f'<div xmlns="http://www.w3.org/1999/xhtml" class="sk"><div class="stage"><div class="world">'
        f'<div class="halo"></div><div class="plate"></div>{"".join(out)}</div></div></div></foreignObject>'
    )
    return html, scoped("sk", css)


def render(data, state):
    weeks = (data.get("profile") or {}).get("weeks") or []
    st = stats(weeks)
    html, css = scene(weeks)
    best = st["best"]
    best_s = f'{dt.date.fromisoformat(best["date"]):%b %d}'.upper() + f' · {best["count"]}' if best and best["count"] else "—"
    rows = [("CURRENT STREAK", f'{st["current"]}d'), ("LONGEST STREAK", f'{st["longest"]}d'),
            ("ACTIVE DAYS", f'{st["active"]}/{sum(len(w) for w in weeks)}'), ("PEAK DAY", best_s)]
    info = (
        f'<text x="24" y="92" font-size="44" font-weight="800" fill="url(#sk-num)">{st["total"]:,}</text>'
        f'<text x="26" y="114" class="k">CONTRIBUTIONS · LAST 365 DAYS</text>'
    )
    for i, (k, v) in enumerate(rows):
        y = 82 + i * 34
        info += (
            f'<text x="{W - 24}" y="{y}" text-anchor="end" font-size="17" font-weight="800">{esc(v)}</text>'
            f'<text x="{W - 24}" y="{y + 14}" text-anchor="end" class="k" style="font-size:9px">{esc(k)}</text>'
        )
    legend = "".join(
        f'<rect x="{24 + i * 15}" y="{H - 30}" width="11" height="11" rx="2" fill="{ramp(STOPS, i / 4)}"/>' for i in range(5)
    )
    legend += f'<text x="{24 + 5 * 15 + 6}" y="{H - 20.5}" class="k" style="font-size:9px">LESS → MORE</text>'
    legend += f'<text x="{W - 24}" y="{H - 20.5}" text-anchor="end" class="k" style="font-size:9px">REAL CSS 3D · REBUILT EVERY 30 MIN</text>'
    defs = (
        f'<linearGradient id="sk-num" x1="0" x2="1"><stop offset="0" stop-color="#fff"/>'
        f'<stop offset=".6" stop-color="{CYAN}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient>'
    )
    return card(W, H, "sk", 1, "CONTRIBUTION SKYLINE", html + info + legend, f"@{data.get('login', '')}".upper(), css, defs)
