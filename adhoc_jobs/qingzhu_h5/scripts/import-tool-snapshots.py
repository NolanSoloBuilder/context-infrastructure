"""Refresh independently usable public catalogs, never called by the server."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
from subprocess import check_output, CalledProcessError
from urllib.parse import quote, urlencode

ROOT = Path(__file__).resolve().parent.parent
PREFIX = "https://h5.qingzhuzishe.com/api/v1/tools/"
SNAPSHOT = ROOT / "data" / "tool-public-snapshots.json"
base = json.loads((ROOT / "public-catalog.json").read_text())

def request(route, params=None, *, post=False):
    path = PREFIX + quote(route, safe="/")
    if params:
        path += "?" + urlencode(params)
    command = ["curl", "-fsS", "--max-time", "10", path]
    if post:
        command += ["-X", "POST"]
    data = json.loads(check_output(command))
    if data.get("code") != 0:
        raise RuntimeError(f"{route}: {data.get('message')}")
    return data["data"]

def pages(route, params=None, size=100):
    first = request(route, {"page": 1, "size": size, **(params or {})})
    rows = first["list"][:]
    per_page = first.get("size", len(rows))
    if not per_page:
        return first
    for page in range(2, min(100, 1 + (first["total"] - 1)//per_page) + 1):
        part = request(route, {"page": page, "size": per_page, **(params or {})})["list"]
        if not part:
            break
        rows += part
    def row_key(row):
        return row.get("id", row.get("surname"))
    rows = list({row_key(row): row for row in reversed(rows)}.values())[::-1]
    return {**first, "list": rows, "total": len(rows)}

def safe_request(route, params=None, post=False):
    try:
        return request(route, params, post=post)
    except (RuntimeError, CalledProcessError) as error:
        print(error)
        return None

constellations = base["/api/v1/tools/constellation/list"]["data"]["list"]
zodiacs = base["/api/v1/tools/zodiac/list"]["data"]
top_names = ["王","李","张","刘","陈","杨","赵","黄","周","吴","徐","孙","马","朱","胡","郭","林","何","高","罗","郑","梁","谢","宋","唐","许","邓","韩","曹","欧阳","司马","上官","诸葛","慕容","司徒","东方", "费"]
books = base["/api/v1/tools/poem-naming/books"]["data"]["books"]
tasks = [("constellation", x["name"], "constellation/" + x["name"], None, False) for x in constellations]
for x in zodiacs:
    name = x["name"]
    tasks.extend([("zodiac", name, "zodiac/" + name, None, False),
                  ("zodiacCharacters", name, "zodiac/characters/" + name, {"limit": 30}, False)])
tasks += [("surname", x, "surnames/" + x, None, False) for x in top_names]
tasks += [("poems", x["id"], "poem-naming/generate", {"book_id": x["id"], "count": 20}, True) for x in books]
def fetch(item):
    group, key, route, params, post = item
    return group, key, safe_request(route, params, post)
out = {"source": PREFIX}
with ThreadPoolExecutor(max_workers=4) as pool:
    for group, key, data in pool.map(fetch, tasks):
        if data is not None:
            out.setdefault(group, {})[key] = data
    categories = {"surnames": {}, "funny-names": {"sort": "hot"}, "homophone-names": {"sort": "hot"}}
    def fetch_pages(item):
        route, params = item
        return route, pages(route, params, 100 if route == "surnames" else 50)
    for route, data in pool.map(fetch_pages, categories.items()):
        out[route] = data
out["surnames"]["size"] = 100
SNAPSHOT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")) + "\n")
print({k:(len(v["list"]) if isinstance(v, dict) and "list" in v else len(v)) for k,v in out.items()})
