"""Refresh a local snapshot of the original site's public dictionary endpoints."""
import json
from datetime import datetime, timezone
from pathlib import Path
from subprocess import check_output
from urllib.parse import urlencode

ORIGIN = "https://h5.qingzhuzishe.com"
DESTINATION = Path(__file__).resolve().parents[1] / "data" / "original-public-library.json"


def download(path, **filters):
    rows = []
    for page in range(1, 51):
        url = f"{ORIGIN}{path}?" + urlencode({"size": 100, "page": page, **filters})
        response = json.loads(check_output(["curl", "-fsS", "--max-time", "15", url]))
        if response["code"] != 0:
            raise ValueError(response["message"])
        data = response["data"]
        if data["page"] != page or not data["list"]:
            raise ValueError(f"Unexpected pagination for {url}")
        rows.extend(data["list"])
        if len(rows) >= data["total"]:
            if len(rows) != data["total"]:
                raise ValueError(f"Total changed while importing {path}")
            return rows
    raise ValueError(f"Page limit reached for {path}")


if __name__ == "__main__":
    dictionary = "/api/v1/tools/naming-characters"
    popular = "/api/v1/tools/popular-names"
    characters = download(dictionary)
    # The global endpoint repeats rows across page boundaries. Independent
    # element partitions recover characters skipped by global pagination.
    partitions = {element: download(dictionary, wuxing=element) for element in "木火土金水"}
    if any(row["wuxing"] != element for element, rows in partitions.items() for row in rows):
        raise ValueError("The server did not honor the element filter")
    names = download(popular)
    counts = {"characters": len(characters), "popularNames": len(names)}
    # The public rankings can repeat names across records. Keep the first row
    # for each key, preserving the server's page order.
    by_character = {}
    for row in characters + [row for rows in partitions.values() for row in rows]:
        by_character.setdefault(row["character"], row)
    characters = list(by_character.values())
    names = list({(row["name"], row["gender"], row["decade"]): row for row in reversed(names)}.values())[::-1]
    data = {
        "source": ORIGIN,
        "capturedAt": datetime.now(timezone.utc).isoformat(),
        "endpoints": [dictionary, popular],
        "sourceRows": counts,
        "characterPartitions": {element: len(rows) for element, rows in partitions.items()},
        "characters": characters,
        "popularNames": names,
    }
    temp = DESTINATION.with_suffix(".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n")
    temp.replace(DESTINATION)
    print(f"Imported {len(characters)} characters and {len(names)} public names.")
