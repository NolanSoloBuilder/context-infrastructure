"""Record public-only scoring samples. No account or realistic child profile is used."""
from datetime import datetime, timedelta
import json
from pathlib import Path
from random import Random
from subprocess import check_output
from time import sleep

URL = "https://h5.qingzhuzishe.com/api/v1/tools/bazi"
OUT = Path(__file__).resolve().parents[1] / "test/original-strength-samples.json"
KEYS = ("baziString", "riZhuStrength", "yongShen")
rng = Random(98231)
rows = []
for index in range(108):
    stamp = datetime(1950, 1, 1) + timedelta(days=rng.randrange(28000))
    fields = dict(year=stamp.year, month=stamp.month, day=stamp.day, hour=rng.randrange(24),
                  minute=rng.choice([0, 17, 30, 49]), gender=index % 2 + 1)
    data = json.loads(check_output(["curl", "-fsS", "--max-time", "10", URL, "-H",
        "Content-Type: application/json", "--data", json.dumps(fields)]))
    if data["code"] != 0:
        raise RuntimeError(f"Sample {index}: {data['message']}")
    rows.append({"group": "holdout" if index % 3 == 2 else "calibration", "input": fields,
        "expected": {key: data["data"][key] for key in KEYS}})
    sleep(0.18)
OUT.write_text(json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + "\n")
print(f"Recorded {len(rows)} public samples.")
