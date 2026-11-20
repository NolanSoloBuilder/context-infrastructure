"""Build the offline Shuowen index from the pinned Apache-2.0 corpus."""
import gzip
from io import BytesIO
import json
from pathlib import Path
from subprocess import check_output
from tarfile import open as tar_open
import sys

ROOT = Path(__file__).resolve().parent.parent
REV = "6553a350763ce4feca2c5d1cc2cad7e594dc2975"
path = f"https://codeload.github.com/shuowenjiezi/shuowen/tar.gz/{REV}"
archive = Path(sys.argv[1]).read_bytes() if len(sys.argv) > 1 else check_output(
    ["curl", "-fsSL", "--max-time", "30", path])
with tar_open(fileobj=BytesIO(archive), mode="r:gz") as src:
    items = {}
    notice = None
    for item in src:
        if item.name.endswith("/LICENSE"):
            notice = src.extractfile(item).read()
        if not item.isfile() or "/data/" not in item.name or not item.name.endswith(".json"):
            continue
        row = json.load(src.extractfile(item))
        if not isinstance(row, dict) or not row.get("wordhead") or not row.get("explanation"):
            continue
        head = row["wordhead"]
        data = {key: row.get(key, "") for key in ("explanation", "radical", "seal_character", "duan_notes")}
        data["pinyin"] = row.get("pinyin_full") or row.get("pinyin", "")
        data["indexes"] = list(dict.fromkeys(row.get("indexes") or [head]))
        items.setdefault(head, data)
if notice is None:
    raise ValueError("Missing Apache notice in Shuowen archive")
(ROOT/"data"/"tool-shuowen.LICENSE").write_bytes(notice)
values = {"source": "https://github.com/shuowenjiezi/shuowen", "revision": REV, "entries": items}
payload = json.dumps(values, ensure_ascii=False, separators=(",", ":")).encode()
(ROOT/"data"/"tool-shuowen.json.gz").write_bytes(gzip.compress(payload, mtime=0))
print(f"{len(items)} Shuowen entries")
