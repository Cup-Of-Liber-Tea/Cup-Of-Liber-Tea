import base64
import io
import pathlib

from .net import fetch

BASE = "https://raw.githubusercontent.com/JetBrains/JetBrainsMono/master/fonts/ttf/JetBrainsMono-{}.ttf"
WEIGHTS = {400: "Regular", 700: "Bold", 800: "ExtraBold"}
CACHE = pathlib.Path(__file__).resolve().parent.parent / ".cache" / "fonts"
FAMILY = "JBM"
STACK = f"'{FAMILY}','JetBrains Mono','SFMono-Regular',Menlo,Consolas,'Liberation Mono',monospace"

_raw = {}


def _load(weight):
    if weight in _raw:
        return _raw[weight]
    path = CACHE / f"{WEIGHTS[weight]}.ttf"
    if not path.exists():
        try:
            body, _ = fetch(BASE.format(WEIGHTS[weight]), timeout=30)
            CACHE.mkdir(parents=True, exist_ok=True)
            path.write_bytes(body)
        except Exception:
            _raw[weight] = None
            return None
    _raw[weight] = path.read_bytes()
    return _raw[weight]


def _subset(raw, text):
    from fontTools import subset
    from fontTools.ttLib import TTFont

    font = TTFont(io.BytesIO(raw))
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["kern", "liga", "calt"]
    opts.name_IDs = []
    opts.hinting = False
    sub = subset.Subsetter(opts)
    sub.populate(text=text)
    sub.subset(font)
    out = io.BytesIO()
    font.flavor = "woff2"
    font.save(out)
    return out.getvalue()


def font_face(text, weights=(400, 700, 800)):
    chars = "".join(sorted(set(text) | set(" 0123456789")))
    rules = []
    for w in weights:
        raw = _load(w)
        if not raw:
            continue
        try:
            data = base64.b64encode(_subset(raw, chars)).decode()
        except Exception:
            continue
        rules.append(
            f"@font-face{{font-family:'{FAMILY}';font-weight:{w};"
            f"src:url(data:font/woff2;base64,{data}) format('woff2');}}"
        )
    return "".join(rules)
