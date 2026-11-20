"""Build a compact local metadata and definitions index from Chinese-Xinhua."""
from pathlib import Path
from subprocess import check_output
import gzip
import json
import sys

ROOT = Path(__file__).resolve().parent.parent
REV = "fe6d6c2e8baa82187f4c96bbe042e43f96c05666"
BASE = f"https://raw.githubusercontent.com/pwxcoo/chinese-xinhua/{REV}"
source = Path(sys.argv[1]).read_bytes() if len(sys.argv)>1 else check_output(
    ["curl", "-fsSL", "--max-time", "60", BASE+"/data/word.json"])
license = Path(sys.argv[2]).read_bytes() if len(sys.argv)>2 else check_output(
    ["curl", "-fsSL", "--max-time", "10", BASE+"/LICENSE"])
items = {}
for row in json.loads(source):
    word = row["word"]
    if len(word)!=1 or word in items:
        continue
    explanation = row["explanation"].strip()
    # The classic database supplies full ancient definitions; retain a readable modern gloss here.
    if len(explanation)>350:
        explanation = explanation[:350].rstrip()+"…"
    items[word] = {
        "traditional": row["oldword"] if len(row["oldword"])==1 else "",
        "strokes": int(row["strokes"]) if row["strokes"].isdigit() else None,
        "pinyin": row["pinyin"], "radical": row["radicals"],
        "explanation": explanation
    }
out = {"source": "https://github.com/pwxcoo/chinese-xinhua", "revision": REV, "entries":items}
(ROOT/"data"/"tool-modern-dictionary.json.gz").write_bytes(gzip.compress(
    json.dumps(out, ensure_ascii=False, separators=(",",":")).encode(), mtime=0))
(ROOT/"data"/"tool-modern-dictionary.LICENSE").write_bytes(license)
print(f"{len(items)} modern entries")
