"""Refresh the comparison cases using the public, non-account tool endpoint."""
import json
from pathlib import Path
from subprocess import check_output

CASES = [
    ("ordinary", 2025, 1, 1, 12), ("early-zi", 2026, 11, 17, 0),
    ("late-zi", 2026, 11, 17, 23), ("before-lichun", 2025, 2, 3, 21),
    ("after-lichun", 2025, 2, 3, 23), ("leap-month", 2023, 3, 22, 11),
    ("unknown-hour", 2026, 11, 17, -1), ("before-jingzhe", 2025, 3, 5, 15),
    ("after-jingzhe", 2025, 3, 5, 18),
]
EXTRA = [
    ("winter", 1990, 1, 7, 14), ("spring", 1996, 4, 23, 6),
    ("summer", 2000, 7, 12, 18), ("autumn", 2009, 9, 17, 9),
    ("leap-day", 2004, 2, 29, 22), ("cold-dew", 2024, 10, 8, 5),
    ("at-midnight", 2018, 5, 6, 0), ("pre-lunar-new-year", 2024, 2, 8, 17),
    ("summer-solstice", 2022, 6, 21, 12), ("rain-water", 2015, 2, 19, 18),
    ("old-year", 1952, 8, 20, 1), ("winter-solstice", 2017, 12, 22, 23),
]
URL = "https://h5.qingzhuzishe.com/api/v1/tools/bazi"
KEYS = ("solar", "lunar", "hourUnknown", "bazi", "baziString", "kongwang",
        "wuxingWithCangGan", "riZhuStrength", "yongShen", "pattern")

rows = []
for index, (name, year, month, day, hour) in enumerate(CASES + EXTRA):
    args = dict(year=year, month=month, day=day, hour=hour, minute=0, gender=1 if index % 2 == 0 else 2)
    response = json.loads(check_output(["curl", "-fsS", "--max-time", "12", URL,
        "-H", "Content-Type: application/json", "-H", "X-Platform: h5", "--data", json.dumps(args)]))
    data = response["data"] if response["code"] == 0 else {}
    rows.append(dict(case=name, group="boundary" if index < len(CASES) else "variation", input=args, expected=dict(code=response["code"], message=response["message"],
        **{key: data[key] for key in KEYS if key in data})))
    print(name, response["code"], data.get("baziString"), data.get("yongShen", {}).get("yong"))
output = Path(__file__).resolve().parents[1] / "test" / "original-bazi-cases.json"
output.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n")
