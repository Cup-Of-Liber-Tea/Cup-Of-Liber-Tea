import json
import time
import urllib.error
import urllib.request

UA = "cup-of-liber-tea-renderer/2.0"


def fetch(url, headers=None, data=None, method=None, timeout=20, retries=2):
    hdrs = {"User-Agent": UA, **(headers or {})}
    last = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
            with urllib.request.urlopen(req, timeout=timeout) as res:
                return res.read(), res.headers.get("Content-Type", "")
        except urllib.error.HTTPError as e:
            if e.code < 500 and e.code != 429:
                raise
            last = e
        except Exception as e:
            last = e
        time.sleep(1.5 * (attempt + 1))
    raise last


def fetch_json(url, headers=None, payload=None, method=None, timeout=20):
    data = json.dumps(payload).encode() if payload is not None else None
    hdrs = dict(headers or {})
    if data is not None:
        hdrs["Content-Type"] = "application/json"
    body, _ = fetch(url, hdrs, data, method, timeout)
    return json.loads(body or b"null")


class GitHub:
    def __init__(self, token):
        self.headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    def rest(self, path, payload=None, method=None):
        return fetch_json(f"https://api.github.com/{path.lstrip('/')}", self.headers, payload, method)

    def graphql(self, query, **variables):
        out = fetch_json("https://api.github.com/graphql", self.headers, {"query": query, "variables": variables})
        if out.get("errors") and not out.get("data"):
            raise RuntimeError(out["errors"][0].get("message", "graphql error"))
        return out["data"]


def probe(url, timeout=12):
    start = time.perf_counter()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (pulse monitor)"})
        with urllib.request.urlopen(req, timeout=timeout) as res:
            res.read(2048)
            code = res.status
    except urllib.error.HTTPError as e:
        code = e.code
    except Exception:
        return {"up": False, "ms": None, "code": 0}
    ms = round((time.perf_counter() - start) * 1000)
    return {"up": code < 500, "ms": ms, "code": code}
