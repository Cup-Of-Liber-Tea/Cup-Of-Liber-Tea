import datetime as dt
import json
import os

from .net import GitHub

KEEP = 72


def pending_issue():
    if os.environ.get("GITHUB_EVENT_NAME") != "issues":
        return None
    path = os.environ.get("GITHUB_EVENT_PATH")
    if not path or not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as fh:
        ev = json.load(fh)
    issue = ev.get("issue") or {}
    if ev.get("action") != "opened" or not issue.get("title", "").strip().lower().startswith("sign"):
        return None
    user = issue.get("user") or {}
    if user.get("type") != "User":
        return None
    return {"number": issue["number"], "login": user["login"], "id": user["id"]}


def sign(state, issue, now):
    wall = [s for s in state.get("wall", []) if s["login"].lower() != issue["login"].lower()]
    wall.insert(0, {"login": issue["login"], "id": issue["id"], "t": now.isoformat()})
    state["wall"] = wall[:KEEP]


def reply(issue, token):
    repo = os.environ.get("GITHUB_REPOSITORY")
    if not repo or not token:
        return
    gh = GitHub(token)
    body = (
        f"✦ **signed, @{issue['login']}.**\n\n"
        "your avatar is now orbiting the guestbook globe on the profile. "
        "the render takes a minute or two to land — thanks for stopping by.\n\n"
        f"<sub>handled by github actions · {dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M} UTC</sub>"
    )
    gh.rest(f"repos/{repo}/issues/{issue['number']}/comments", {"body": body})
    gh.rest(f"repos/{repo}/issues/{issue['number']}", {"state": "closed", "state_reason": "completed"}, "PATCH")
