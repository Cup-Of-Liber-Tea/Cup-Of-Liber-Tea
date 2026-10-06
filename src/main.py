import argparse
import base64
import datetime as dt
import hashlib
import json
import os
import pathlib
import sys
import traceback

from . import data as source
from . import fixtures, guestbook
from .art import chrono, feed, footer, hero, orbit, pulse, skyline, wall
from .svg import HALF, MUTED, W, card, compose
from .net import fetch, probe

LOGIN = os.environ.get("PROFILE_LOGIN") or os.environ.get("GITHUB_REPOSITORY_OWNER") or "Cup-Of-Liber-Tea"
OUTPUT = "profile.svg"
HISTORY = 96


def log(msg):
    print(f"[render] {msg}", file=sys.stderr)


def targets():
    out = []
    for line in os.environ.get("STATUS_TARGETS", "").splitlines():
        line = line.strip()
        if not line:
            continue
        name, sep, url = line.partition("|")
        out.append((name.strip(), url.strip()) if sep else ("", name.strip()))
    for i in range(1, 6):
        url = os.environ.get(f"WEBSITE_URL{i}", "").strip()
        if url:
            out.append(("", url))
    return [((n or f"NODE-{i + 1:02d}").upper()[:16], u) for i, (n, u) in enumerate(out)]


def data_uri(url):
    try:
        body, ctype = fetch(url, timeout=15)
        return f"data:{(ctype or 'image/png').split(';')[0]};base64,{base64.b64encode(body).decode()}"
    except Exception:
        return None


def monitor(state, now):
    nodes = targets()
    if not nodes:
        return
    pulse_state = state.get("pulse", {})
    fresh = {}
    for name, url in nodes:
        res = probe(url)
        fresh[name] = (pulse_state.get(name, []) + [{**res, "t": now.isoformat()}])[-HISTORY:]
        log(f"pulse {name}: {'up' if res['up'] else 'down'}")
    state["pulse"] = fresh


def run(out, offline):
    out.mkdir(parents=True, exist_ok=True)
    state_file = out / "state.json"
    try:
        state = json.loads(state_file.read_text(encoding="utf-8"))
    except Exception:
        state = {}
    if offline:
        data = fixtures.sample()
        for k, v in fixtures.sample_state().items():
            state.setdefault(k, v)
    else:
        data = source.collect(LOGIN, os.environ.get("GH_TOKEN"))
    cache = state.setdefault("cache", {})
    for key in ("profile", "commits", "events", "weather"):
        if data.get(key) is None and cache.get(key) is not None:
            data[key] = cache[key]
            log(f"{key}: using last good snapshot")
        elif data.get(key) is not None and not offline:
            cache[key] = data[key]
    now = dt.datetime.fromisoformat(data["now"])
    state["edition"] = int(state.get("edition", 0)) + 1
    state["seed"] = hashlib.sha256(f"{LOGIN}{state['edition']}{data['now']}".encode()).hexdigest()[:12]

    blocked = {b.strip().lower() for b in os.environ.get("GUESTBOOK_BLOCK", "").split(",") if b.strip()}
    issue = guestbook.pending_issue()
    if issue and issue["login"].lower() in blocked:
        issue = None
    state["wall"] = [s for s in state.get("wall", []) if s["login"].lower() not in blocked]
    if issue:
        guestbook.sign(state, issue, now)
        log(f"guestbook: signed by @{issue['login']}")
    if not offline:
        monitor(state, now)

    data["avatar"] = data_uri(f"https://github.com/{LOGIN}.png?size=160")
    data["wall_avatars"] = {
        s["login"]: data_uri(f"https://avatars.githubusercontent.com/u/{s['id']}?s=64") for s in state.get("wall", [])
    }

    failed = []

    def build(name, fn, w, h):
        try:
            return fn()
        except Exception:
            failed.append(name)
            log(f"{name}: render failed\n{traceback.format_exc()}")
            body = f'<text x="24" y="80" font-size="13" fill="{MUTED}">signal lost — retrying next cycle</text>'
            return card(w, h, f"fb-{name}", 0, name.upper(), body)

    paired = max(pulse.height(state), pulse.MIN_H)
    rows = [
        [build("hero", lambda: hero.render(data, state), W, hero.H)],
        [build("skyline", lambda: skyline.render(data, state), W, skyline.H)],
        [build("chronotype", lambda: chrono.render(data, state), HALF, chrono.H),
         build("orbit", lambda: orbit.render(data, state), HALF, orbit.H)],
        [build("stream", lambda: feed.render(data, state), W, 300)],
        [build("pulse", lambda: pulse.render(data, state, paired), HALF, paired),
         build("guestbook", lambda: wall.render(data, state, paired), HALF, paired)],
        [build("footer", lambda: footer.render(data, state), W, footer.H)],
    ]
    try:
        svg = compose(rows, f"{LOGIN} — generative profile")
        (out / OUTPUT).write_text(svg, encoding="utf-8")
        log(f"{OUTPUT} {len(svg) // 1024} KB, failed: {failed or 'none'}")
    except Exception:
        failed.append("compose")
        log(f"compose failed, keeping previous file\n{traceback.format_exc()}")
    state_file.write_text(json.dumps(state, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    keep = {OUTPUT, state_file.name}
    for stale in out.iterdir():
        if stale.is_file() and stale.name not in keep:
            stale.unlink()

    if issue:
        try:
            guestbook.reply(issue, os.environ.get("ISSUE_TOKEN"))
        except Exception as e:
            log(f"guestbook reply failed: {e}")
    return 1 if "compose" in failed else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="dist")
    ap.add_argument("--offline", action="store_true")
    args = ap.parse_args()
    sys.exit(run(pathlib.Path(args.out), args.offline))


if __name__ == "__main__":
    main()
