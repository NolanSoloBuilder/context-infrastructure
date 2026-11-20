#!/usr/bin/env python3
"""Extract consecutive two-character naming candidates from pinned classical texts."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import re
from subprocess import check_output
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
REVISION = "b8594f81a89752241442f2ce267d6f66f96704ee"
SOURCE = f"https://raw.githubusercontent.com/chinese-poetry/chinese-poetry/{REVISION}/"
INPUTS = [
    ("诗经", "先秦", "诗经/shijing.json"),
    ("楚辞", "先秦", "楚辞/chuci.json"),
    *[("唐诗", "唐", f"全唐诗/poet.tang.{offset}.json")
      for offset in (0, 3000, 6000, 10000, 14000, 18000, 22000, 27000, 36000, 48000)],
    *[("宋词", "宋", f"宋词/ci.song.{offset}.json")
      for offset in (0, 3000, 6000, 9000)],
]
CHARACTERS = (
    "安宁允宇宸辰轩逸远屿岑岩峻岳坤垣羽岚恩亦彧砚衡予昀昕晗晟煦昭晞景明朗曜晴"
    "星灿熹暖冉彤晔晖焕旭烁炜知瑾珏瑜瑞珂琛玥瑶珩琰珍琳璟琬钧钦锐铭铎锡锦铮铠"
    "书言信承修初思成少仁善诗如静舒素真心川千清澄沐沅洛洵澜洋汀源津泓涵润淳泽"
    "洺洲澍霖雨雪霁云露雯希文翰行闻白北牧眠湄微汐沁恬伊南和音歌雅乔楷梓柯柠栩"
    "桐梧松柏楠榆栖若芷芮芊芸苒茵芙茉菡蕙萱蓁萍芃荷蔚竹筠筱笙简策楚苏槿棠柳"
    "禾穗茗兰宜嘉元季语颂奕弈彦杰英可欣君仪月忆友有乐忻怡念柔美树扬圆齐姝攸维"
    "桢令灵均芳佩秋阳荣华徽熙听嘉祥香盈纯颐惠淑婉颂鸢墨博俊智扬义诚礼恩鱼孜朋"
)

def fetch(path):
    return check_output(["curl", "-fsS", "--max-time", "20", SOURCE + quote(path)])

def load(entry):
    book, dynasty, path = entry
    return book, dynasty, json.loads(fetch(path))

def main():
    lexicon = json.loads((ROOT / "data/original-public-library.json").read_text())
    available = set(CHARACTERS) & {row["character"] for row in lexicon["characters"]}
    out = {}
    with ThreadPoolExecutor(max_workers=5) as workers:
        for book, dynasty, poems in workers.map(load, INPUTS):
            for poem in poems:
                if not isinstance(poem, dict):
                    continue
                title = poem.get("title") or poem.get("rhythmic")
                title = title.strip() if isinstance(title, str) else ""
                if not title or len(title) > 120:
                    continue
                author = poem.get("author") or ""
                for line in poem.get("paragraphs", poem.get("content", [])):
                    if not isinstance(line, str):
                        continue
                    for sentence in re.findall(r"[\u3400-\u9fff]{4,32}", line):
                        for left, right in zip(sentence, sentence[1:]):
                            if left != right and left in available and right in available:
                                out.setdefault(left + right, [title, sentence, author, dynasty, book])
    artifact = {"revision": REVISION, "characters": CHARACTERS, "names": out}
    (ROOT / "data/naming-poetry.json").write_text(
        json.dumps(artifact, ensure_ascii=False, separators=(",", ":")) + "\n"
    )
    (ROOT / "data/naming-poetry-LICENSE").write_bytes(fetch("LICENSE"))
    print(f"Indexed {len(out)} names with verifiable excerpts")

if __name__ == "__main__":
    main()
