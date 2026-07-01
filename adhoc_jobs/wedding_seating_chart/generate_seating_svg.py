from __future__ import annotations

import html
import math
from pathlib import Path


OUT_DIR = Path(__file__).resolve().parent


TABLES_FILLED = [
    (
        "主桌",
        [
            "新娘爸爸",
            "新娘妈妈",
            "新郎爸爸",
            "新郎妈妈",
            "新郎",
            "新娘",
            "新娘舅舅",
            "新娘姐姐",
            "新娘小外甥",
            "杨敏画",
        ],
    ),
    (
        "领导桌",
        [
            "薛主任",
            "薛主任家人",
            "姚林叔叔",
            "姚林家人1",
            "姚林家人2",
            "杜萍叔叔",
            "杜萍家人",
            "罗勇叔叔",
        ],
    ),
    (
        "女方好友1",
        [
            "杨乐依",
            "杨乐依家属",
            "林逢缘",
            "王丽兵",
            "王丽兵家属",
            "何碧瑶",
            "何碧瑶家属",
            "杨传雪",
            "薛文隽",
            "薛文隽家属",
        ],
    ),
    (
        "女方好友2",
        [
            "陈敏",
            "王欣荣",
            "张心怡",
            "陆剑瑜",
            "李昂",
            "张笑婷",
            "张笑婷家属",
            "吴昊",
            "吴昊家属",
            "",
            "",
        ],
    ),
    (
        "男方好友1",
        [
            "刘洋",
            "刘洋老婆",
            "刘旭",
            "丁昊斌",
            "方银宇",
            "方银宇家属",
            "江洋",
            "江洋老婆",
            "孟祥汉",
            "孟老婆",
            "晓倩",
        ],
    ),
    (
        "男方好友2",
        [
            "郭文涛",
            "景天",
            "光玮",
            "林兄",
            "麦督",
            "麦督老婆",
            "巫荣",
            "巫荣老婆",
            "巫荣家属",
            "乔克",
            "",
        ],
    ),
    (
        "男方好友3",
        [
            "蒋欢",
            "蒋欢老婆",
            "曹健",
            "曹健老婆",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ],
    ),
]


def seat_count_for(table_name: str) -> int:
    if table_name == "领导桌":
        return 8
    if table_name == "主桌":
        return 10
    return 11


def render_svg(filled: bool) -> str:
    width, height = 2620, 1500
    positions = [
        (380, 390),
        (1000, 390),
        (1620, 390),
        (2240, 390),
        (700, 1060),
        (1400, 1060),
        (2100, 1060),
    ]
    parts: list[str] = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>",
        "text { font-family: 'PingFang SC', 'Microsoft YaHei', Arial, sans-serif; fill: #2a2521; }",
        ".title { font-size: 42px; font-weight: 700; }",
        ".table-title { font-size: 30px; font-weight: 700; text-anchor: middle; }",
        ".seat-no { font-size: 15px; font-weight: 700; text-anchor: middle; dominant-baseline: central; fill: #7a4b2b; }",
        ".name { font-size: 18px; text-anchor: middle; dominant-baseline: central; }",
        ".hint { font-size: 20px; fill: #6c625a; }",
        ".table { fill: #fff7ed; stroke: #b98252; stroke-width: 4; }",
        ".seat { fill: #ffffff; stroke: #caa076; stroke-width: 2; }",
        ".line { stroke: #d7b99c; stroke-width: 2; }",
        ".page-bg { fill: #fffdf9; }",
        "</style>",
        f'<rect class="page-bg" x="0" y="0" width="{width}" height="{height}"/>',
        '<text class="title" x="80" y="82">婚礼席位图</text>',
        '<text class="hint" x="80" y="122">圆桌模板：按 PPT 顺序排列，座位号顺时针。空白处可直接填姓名。</text>',
    ]

    for (table_name, names), (cx, cy) in zip(TABLES_FILLED, positions):
        count = seat_count_for(table_name)
        names = (names + [""] * count)[:count] if filled else [""] * count
        parts.append(f'<circle class="table" cx="{cx}" cy="{cy}" r="112"/>')
        parts.append(f'<text class="table-title" x="{cx}" y="{cy - 8}">{html.escape(table_name)}</text>')
        parts.append(f'<text class="seat-no" x="{cx}" y="{cy + 36}">{count}人桌</text>')

        for i in range(count):
            angle = -math.pi / 2 + 2 * math.pi * i / count
            sx = cx + math.cos(angle) * 180
            sy = cy + math.sin(angle) * 180
            tx = cx + math.cos(angle) * 244
            ty = cy + math.sin(angle) * 244
            line_x1 = cx + math.cos(angle) * 126
            line_y1 = cy + math.sin(angle) * 126
            line_x2 = cx + math.cos(angle) * 156
            line_y2 = cy + math.sin(angle) * 156
            parts.append(f'<line class="line" x1="{line_x1:.1f}" y1="{line_y1:.1f}" x2="{line_x2:.1f}" y2="{line_y2:.1f}"/>')
            parts.append(f'<circle class="seat" cx="{sx:.1f}" cy="{sy:.1f}" r="29"/>')
            parts.append(f'<text class="seat-no" x="{sx:.1f}" y="{sy:.1f}">{i + 1}</text>')
            label = html.escape(names[i]) if names[i] else "________"
            parts.append(f'<text class="name" x="{tx:.1f}" y="{ty:.1f}">{label}</text>')

    parts.append("</svg>")
    return "\n".join(parts)


def main() -> None:
    (OUT_DIR / "wedding_seating_blank.svg").write_text(render_svg(False), encoding="utf-8")
    (OUT_DIR / "wedding_seating_filled.svg").write_text(render_svg(True), encoding="utf-8")


if __name__ == "__main__":
    main()
