import datetime as dt
import sys

from .net import GitHub, fetch_json

KST = dt.timezone(dt.timedelta(hours=9))
DAEJEON = (36.3504, 127.3845)

QUERY = """
query($login:String!){
  user(login:$login){
    login name createdAt
    followers{totalCount} following{totalCount}
    contributionsCollection{
      contributionCalendar{totalContributions weeks{contributionDays{date contributionCount weekday}}}
    }
  }
}
"""

REPOS = """
query($login:String!, $after:String){
  user(login:$login){
    repositories(ownerAffiliations:OWNER, isFork:false, first:100, after:$after, orderBy:{field:PUSHED_AT,direction:DESC}){
      pageInfo{hasNextPage endCursor}
      nodes{
        stargazerCount forkCount
        languages(first:12, orderBy:{field:SIZE,direction:DESC}){edges{size node{name color}}}
      }
    }
  }
}
"""


def log(msg):
    print(f"[data] {msg}", file=sys.stderr)


def parse_time(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(KST)


def repositories(gh, login, limit=10):
    nodes, after = [], None
    for _ in range(limit):
        page = gh.graphql(REPOS, login=login, after=after)["user"]["repositories"]
        nodes += page["nodes"]
        if not page["pageInfo"]["hasNextPage"]:
            break
        after = page["pageInfo"]["endCursor"]
    return nodes


def profile(gh, login):
    u = gh.graphql(QUERY, login=login)["user"]
    repos = repositories(gh, login)
    langs = {}
    for r in repos:
        for e in r["languages"]["edges"]:
            n = e["node"]
            cur = langs.setdefault(n["name"], {"name": n["name"], "color": n["color"] or "#8b8fa8", "bytes": 0})
            cur["bytes"] += e["size"]
    weeks = [
        [{"date": d["date"], "count": d["contributionCount"], "weekday": d["weekday"]} for d in w["contributionDays"]]
        for w in u["contributionsCollection"]["contributionCalendar"]["weeks"]
    ]
    return {
        "login": u["login"],
        "name": u["name"] or u["login"],
        "created": u["createdAt"],
        "followers": u["followers"]["totalCount"],
        "following": u["following"]["totalCount"],
        "repos": {
            "own": len(repos),
            "stars": sum(r["stargazerCount"] for r in repos),
            "forks": sum(r["forkCount"] for r in repos),
        },
        "langs": sorted(langs.values(), key=lambda x: -x["bytes"]),
        "weeks": weeks,
    }


def commit_times(gh, login, pages=5):
    out = []
    for page in range(1, pages + 1):
        res = gh.rest(f"search/commits?q=author:{login}&sort=author-date&order=desc&per_page=100&page={page}")
        items = res.get("items", [])
        out += [parse_time(i["commit"]["author"]["date"]).isoformat() for i in items]
        if len(items) < 100:
            break
    return out


def _event(e):
    p = e.get("payload") or {}
    kind = e["type"]
    detail = ""
    if kind == "PushEvent":
        tag = "PUSH"
        commits = p.get("commits") or []
        branch = (p.get("ref") or "").replace("refs/heads/", "")
        if commits:
            detail = commits[-1].get("message", "").splitlines()[0]
        else:
            detail = f"→ {branch}" + (f" @ {p['head'][:7]}" if p.get("head") else "")
    elif kind == "PullRequestEvent":
        tag, pr = "PR", p.get("pull_request") or {}
        detail = f"{p.get('action', '')} #{p.get('number', pr.get('number', ''))} {pr.get('title', '')}"
    elif kind == "IssuesEvent":
        tag, it = "ISSUE", p.get("issue") or {}
        detail = f"{p.get('action', '')} #{it.get('number', '')} {it.get('title', '')}"
    elif kind == "IssueCommentEvent":
        tag, it = "COMMENT", p.get("issue") or {}
        detail = f"on #{it.get('number', '')} {it.get('title', '')}"
    elif kind == "WatchEvent":
        tag, detail = "STAR", "starred"
    elif kind == "ForkEvent":
        tag, detail = "FORK", "forked"
    elif kind == "CreateEvent":
        tag = "CREATE"
        detail = f"{p.get('ref_type', '')} {p.get('ref') or ''}".strip()
    elif kind == "DeleteEvent":
        tag = "DELETE"
        detail = f"{p.get('ref_type', '')} {p.get('ref') or ''}".strip()
    elif kind == "ReleaseEvent":
        tag, detail = "RELEASE", (p.get("release") or {}).get("tag_name", "")
    elif kind == "PublicEvent":
        tag, detail = "PUBLIC", "open-sourced"
    elif kind == "PullRequestReviewEvent":
        tag, detail = "REVIEW", f"#{(p.get('pull_request') or {}).get('number', '')}"
    else:
        tag = kind.replace("Event", "").upper()[:7]
    return {"t": parse_time(e["created_at"]).isoformat(), "tag": tag, "repo": e["repo"]["name"], "detail": detail}


def events(gh, login, limit=9):
    raw = gh.rest(f"users/{login}/events/public?per_page=60")
    return [_event(e) for e in raw[:limit]]


def weather():
    lat, lon = DAEJEON
    res = fetch_json(
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code,is_day,wind_speed_10m&timezone=Asia%2FSeoul"
    )
    c = res["current"]
    return {"temp": c["temperature_2m"], "code": c["weather_code"], "is_day": c["is_day"], "wind": c["wind_speed_10m"]}


def collect(login, token):
    gh = GitHub(token)
    data = {"login": login, "now": dt.datetime.now(KST).isoformat()}
    for key, fn in (
        ("profile", lambda: profile(gh, login)),
        ("commits", lambda: commit_times(gh, login)),
        ("events", lambda: events(gh, login)),
        ("weather", weather),
    ):
        try:
            data[key] = fn()
            log(f"{key}: ok")
        except Exception as e:
            data[key] = None
            log(f"{key}: failed ({type(e).__name__}: {e})")
    return data
