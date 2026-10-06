import datetime as dt
import math
import random

from .data import KST


def sample(seed=7, weather_code=61, hour=None):
    r = random.Random(seed)
    now = dt.datetime.now(KST)
    if hour is not None:
        now = now.replace(hour=hour, minute=r.randint(0, 59))
    end = now.date()
    start = end - dt.timedelta(days=364 + (end.weekday() + 1) % 7)
    weeks, week = [], []
    d = start
    while d <= end:
        wd = (d.weekday() + 1) % 7
        burst = 1 + 2.4 * max(0, math.sin((d - start).days / 23))
        base = r.random() < (0.55 if wd in (0, 6) else 0.82)
        count = int(r.expovariate(1 / (5 * burst))) if base else 0
        week.append({"date": d.isoformat(), "count": count, "weekday": wd})
        if wd == 6:
            weeks.append(week)
            week = []
        d += dt.timedelta(days=1)
    if week:
        weeks.append(week)
    commits = []
    for _ in range(500):
        h = r.choices(range(24), weights=[6, 5, 4, 2, 1, 1, 1, 1, 2, 3, 4, 4, 2, 4, 5, 5, 5, 4, 3, 4, 6, 8, 9, 8])[0]
        day = now - dt.timedelta(days=r.randint(0, 200))
        commits.append(day.replace(hour=h, minute=r.randint(0, 59)).isoformat())
    langs = [
        ("Python", "#3572A5", 4_200_000), ("TypeScript", "#3178c6", 1_900_000), ("JavaScript", "#f1e05a", 900_000),
        ("Rust", "#dea584", 420_000), ("Go", "#00ADD8", 310_000), ("Shell", "#89e051", 160_000),
        ("PowerShell", "#012456", 120_000), ("Dockerfile", "#384d54", 40_000), ("HTML", "#e34c26", 90_000),
    ]
    tags = [
        ("PUSH", "Cup-Of-Liber-Tea/sample-alpha", "feat: lease-based worker scheduler"),
        ("PUSH", "Cup-Of-Liber-Tea/sample-beta", "chore: tune log retention"),
        ("FORK", "octo-org/example", "forked"),
        ("PR", "Cup-Of-Liber-Tea/sample-gamma", "opened #12 add retry budget"),
        ("STAR", "octo-org/hello-world", "starred"),
        ("PUSH", "Cup-Of-Liber-Tea/sample-delta", "fix: http/3 alt-svc header"),
        ("CREATE", "Cup-Of-Liber-Tea/sample-epsilon", "branch exp/cache"),
        ("RELEASE", "Cup-Of-Liber-Tea/sample-zeta", "v2.4.0"),
        ("PUSH", "Cup-Of-Liber-Tea/sample-eta", "perf: zero-copy relay"),
    ]
    evs = [
        {"t": (now - dt.timedelta(minutes=17 + i * r.randint(25, 160))).isoformat(), "tag": t, "repo": rp, "detail": dt_}
        for i, (t, rp, dt_) in enumerate(tags)
    ]
    return {
        "login": "Cup-Of-Liber-Tea",
        "now": now.isoformat(),
        "profile": {
            "login": "Cup-Of-Liber-Tea", "name": "coffee kimchi", "created": "2024-07-05T10:59:30Z",
            "followers": 224, "following": 343,
            "repos": {"total": 63, "own": 41, "stars": 37, "forks": 9},
            "langs": [{"name": n, "color": c, "bytes": b} for n, c, b in langs],
            "weeks": weeks,
        },
        "commits": commits,
        "events": evs,
        "weather": {"temp": 17.4, "code": weather_code, "is_day": 0, "wind": 3.1},
    }


def sample_state(seed=7):
    r = random.Random(seed)
    nodes = {}
    for name in ("NODE-01", "NODE-02", "NODE-03"):
        hist = []
        for i in range(48):
            up = r.random() > (0.04 if name != "NODE-03" else 0.15)
            hist.append({"up": up, "ms": r.randint(60, 420) if up else None})
        nodes[name] = hist
    wall = [{"login": "octocat", "id": 583231}, {"login": "Cup-Of-Liber-Tea", "id": 174796444}]
    return {"edition": 411, "pulse": nodes, "wall": wall}
