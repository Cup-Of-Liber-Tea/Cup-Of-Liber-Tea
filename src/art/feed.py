import datetime as dt

from ..fonts import STACK
from ..svg import AMBER, CYAN, MINT, MUTED, PINK, RED, VIOLET, W, card, esc, scoped

TAGS = {
    "PUSH": MINT, "PR": VIOLET, "REVIEW": VIOLET, "STAR": AMBER, "FORK": CYAN, "CREATE": PINK,
    "RELEASE": AMBER, "ISSUE": "#ff8fa3", "COMMENT": MUTED, "DELETE": RED, "PUBLIC": MINT,
}
LINE_H = 23
COLS = 94


def when(t, now):
    d = dt.datetime.fromisoformat(t)
    mins = int((now - d).total_seconds() // 60)
    ago = f"{mins}m" if mins < 60 else f"{mins // 60}h" if mins < 1440 else f"{mins // 1440}d"
    return d.strftime("%m·%d %H:%M"), ago


def short(repo, login):
    owner, _, name = repo.partition("/")
    return name if owner.lower() == login.lower() else repo


def render(data, state):
    now = dt.datetime.fromisoformat(data["now"])
    login = data.get("login", "")
    evs = data.get("events") or []
    rows = []
    delay = 0.9
    for e in evs:
        stamp, ago = when(e["t"], now)
        repo = short(e["repo"], login)
        tag = e["tag"]
        budget = COLS - 12 - 9 - len(repo) - 6
        msg = e["detail"] if len(e["detail"]) <= budget else e["detail"][: max(0, budget - 1)] + "…"
        n = 12 + 9 + len(repo) + len(msg) + 6
        rows.append(
            f'<div class="ln ev" style="--n:{n};--d:{delay:.2f}s">'
            f'<span class="tm">{esc(stamp)}</span>'
            f'<span class="tag" style="--c:{TAGS.get(tag, MUTED)}">{esc(tag)}</span>'
            f'<span class="repo">{esc(repo)}</span><span class="msg">{esc(msg)}</span>'
            f'<span class="ago">{esc(ago)}</span></div>'
        )
        delay += 0.42
    if not rows:
        rows.append(f'<div class="ln ev" style="--n:40;--d:{delay:.2f}s"><span class="msg">no public signal in the last 90 days</span></div>')
        delay += 0.42
    body_h = (len(rows) + 3) * LINE_H + 20
    term_h = body_h + 38
    h = 50 + term_h + 24
    html = (
        f'<foreignObject x="14" y="50" width="{W - 28}" height="{term_h + 12}">'
        f'<div xmlns="http://www.w3.org/1999/xhtml" class="fd"><div class="wrap"><div class="glow"></div><div class="term">'
        f'<div class="bar"><i style="background:#ff5f57"></i><i style="background:#febc2e"></i><i style="background:#28c840"></i>'
        f'<span>{esc(login.lower())}@github: ~ — tail -f activity.log</span><b>LIVE</b></div>'
        f'<div class="bd">'
        f'<div class="ln cmd" style="--n:44;--d:.15s"><span class="ps">➜</span> <span class="cw">~</span> '
        f'<span class="c1">tail</span> -f <span class="c2">~/.github/activity.log</span> | <span class="c1">colorize</span></div>'
        + "".join(rows)
        + f'<div class="ln note" style="--n:60;--d:{delay:.2f}s">── synced {now:%H:%M} KST · next pull in ~30m · public events only ──</div>'
        f'<div class="ln pr" style="--n:4;--d:{delay + .4:.2f}s"><span class="ps">➜</span> <span class="cw">~</span> <span class="cur"></span></div>'
        f"</div></div></div></div></foreignObject>"
    )
    css = (
        f".wrap{{position:relative;width:{W - 28}px;height:{term_h + 12}px;font:12.5px/1 {STACK};color:#dfe3ff}}"
        f".glow{{position:absolute;inset:4px;border-radius:14px;overflow:hidden;filter:blur(14px);opacity:.55}}"
        f".glow::before{{content:'';position:absolute;inset:-200%;background:conic-gradient({VIOLET},{CYAN},{MINT},{PINK},{VIOLET});"
        "animation:spin 6s linear infinite}"
        "@keyframes spin{to{transform:rotate(1turn)}}"
        f".term{{position:absolute;inset:6px;border-radius:12px;background:linear-gradient(180deg,#0d1020f2,#06070df5);"
        "box-shadow:inset 0 0 0 1px #ffffff1a,0 20px 60px #000c;overflow:hidden}"
        ".term::after{content:'';position:absolute;inset:0;pointer-events:none;"
        "background:repeating-linear-gradient(0deg,#ffffff05 0 1px,transparent 1px 3px);mix-blend-mode:screen}"
        ".bar{height:34px;display:flex;align-items:center;gap:7px;padding:0 14px;border-bottom:1px solid #ffffff12;"
        "background:linear-gradient(180deg,#ffffff0c,#ffffff03)}"
        ".bar i{width:11px;height:11px;border-radius:50%;display:block}"
        ".bar span{flex:1;text-align:center;color:#8a90b4;font-size:11.5px;letter-spacing:.04em;margin-right:40px}"
        f".bar b{{font-size:9.5px;letter-spacing:.2em;color:{RED};display:flex;align-items:center;gap:6px}}"
        f".bar b::before{{content:'';width:7px;height:7px;border-radius:50%;background:{RED};box-shadow:0 0 10px {RED};"
        "animation:blink 1.2s steps(2) infinite}"
        "@keyframes blink{50%{opacity:.2}}"
        ".bd{padding:12px 18px}"
        f".ln{{height:{LINE_H}px;display:flex;align-items:center;gap:12px;white-space:nowrap;"
        "clip-path:inset(0 100% 0 0);animation:type calc(var(--n) * 14ms) steps(var(--n)) var(--d) forwards}"
        "@keyframes type{to{clip-path:inset(0 0 0 0)}}"
        f".ln.cmd,.ln.pr{{display:block;line-height:{LINE_H}px}}"
        f".ps{{color:{MINT};font-weight:800}}.cw{{color:{CYAN};font-weight:700;margin-right:8px}}"
        f".c1{{color:{PINK}}}.c2{{color:{AMBER}}}"
        ".tm{color:#5f6690;flex:none}"
        ".tag{flex:none;width:64px;text-align:center;font-size:9.5px;font-weight:800;letter-spacing:.14em;padding:4px 0;"
        "border-radius:4px;color:var(--c);background:color-mix(in srgb,var(--c) 14%,transparent);"
        "box-shadow:inset 0 0 0 1px color-mix(in srgb,var(--c) 45%,transparent)}"
        ".repo{color:#fff;font-weight:700;flex:none}"
        ".msg{color:#aab0d6;overflow:hidden;text-overflow:ellipsis;flex:1}"
        ".ago{color:#5f6690;flex:none;font-size:11px}"
        ".note{color:#4b5178;font-size:11px;justify-content:center}"
        f".cur{{display:inline-block;width:8px;height:15px;background:{CYAN};box-shadow:0 0 12px {CYAN};"
        "animation:blink 1s steps(2) infinite}"
        ".ev:hover{background:#ffffff08}"
    )
    return card(W, h, "fd", 4, "ACTIVITY STREAM", html, "PUBLIC EVENTS · KST", scoped("fd", css), "", glow=(MINT, VIOLET))
