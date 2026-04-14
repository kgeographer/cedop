"""Minimal WHG API call harness. Import or run inline."""
import json, ssl, urllib.parse, urllib.request
from pathlib import Path
import certifi
_ssl = ssl.create_default_context(cafile=certifi.where())

_env = Path(__file__).parent.parent.parent / ".env"
TOKEN = next(
    (l.split("=", 1)[1].strip().strip('"').strip("'")
     for l in _env.read_text().splitlines()
     if l.startswith("WHG_API_TOKEN=")),
    None
)
UA = "Mozilla/5.0 (compatible; CEDOP/1.0; +https://cedop.kgeographer.org)"
BASE = "https://whgazetteer.org"


def whg_get(path: str, **params) -> dict:
    params["token"] = TOKEN
    url = BASE + path + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, context=_ssl) as r:
        return json.loads(r.read())
