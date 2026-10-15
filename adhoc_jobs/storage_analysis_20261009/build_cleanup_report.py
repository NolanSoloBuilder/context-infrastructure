"""Render the verified cleanup ledger as a local, read-only report."""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def esc(value):
    return html.escape(str(value))


def render(data):
    stats = data["disk"]
    cards = "".join(
        f'<div class="stat"><span>{esc(label)}</span><strong>{value:.2f}<small> GB</small></strong></div>'
        for label, value in [
            ("清理前可用", stats["free_before_bytes"] / 1e9),
            ("现在可用", stats["free_after_bytes"] / 1e9),
            ("本次清理累计增加", stats["free_increase_bytes"] / 1e9),
        ]
    )
    before = stats["free_before_bytes"] / stats["total_bytes"] * 100
    after = stats["free_after_bytes"] / stats["total_bytes"] * 100
    bars = "".join(
        f'<div class="barrow"><span>{label}</span><div class="bar"><i style="width:{value:.3f}%"></i></div><b>{value:.1f}% 可用</b></div>'
        for label, value in [("清理前", before), ("清理后", after)]
    )
    rows = "".join(
        '<tr data-group="{group}"><td><b>{name}</b><div class="path">{path}</div></td>'
        '<td><span class="badge {group}">{status}</span><div>{action}</div></td>'
        '<td class="amount">{amount}</td><td>{note}</td></tr>'.format(
            **{key: esc(row.get(key, "")) for key in ["group", "name", "path", "status", "action", "amount", "note"]}
        )
        for row in data["rows"]
    )
    notes = "".join(f"<li>{esc(note)}</li>" for note in data["notes"])
    sources = "".join(
        f'<a href="{esc(source)}">{esc(source)}</a>' for source in data["source_files"]
    )
    extra = data.get("additional_phase", {})
    extra_note = (
        '<p>追加清理：可用空间从 {:.2f} GB 增至 {:.2f} GB，本轮增加 {:.2f} GB。</p>'.format(
            extra["free_before_bytes"] / 1e9,
            stats["free_after_bytes"] / 1e9,
            extra["free_increase_bytes"] / 1e9,
        )
        if extra else ""
    )
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>磁盘清理结果 · 2026-10-09</title><style>
:root{{color-scheme:light;--ink:#172333;--sub:#677587;--line:#e1e8ed;--green:#0a815f;--blue:#1558c4}}
*{{box-sizing:border-box}}body{{margin:0;background:#f4f7fa;color:var(--ink);font:14px/1.65 -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif}}
main{{max-width:1200px;padding:38px 22px 70px;margin:auto}}h1{{font-size:30px;letter-spacing:-1px;margin:0 0 8px}}h2{{font-size:20px;margin:0 0 16px}}p{{margin:8px 0;color:var(--sub)}}.panel{{background:white;border:1px solid var(--line);border-radius:18px;padding:24px;margin:22px 0}}
.stats{{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}}.stat span{{display:block;color:var(--sub)}}.stat strong{{display:block;font-size:36px;font-variant-numeric:tabular-nums}}small{{font-size:16px;font-weight:500;color:var(--sub)}}
.barrow{{display:grid;grid-template-columns:70px 1fr 110px;gap:14px;align-items:center;margin:14px 0;font-variant-numeric:tabular-nums}}.bar{{height:14px;border-radius:12px;background:#e9eff5;overflow:hidden}}.bar i{{display:block;background:var(--green);height:100%;border-radius:12px}}
.filters{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px}}button{{border:1px solid var(--line);border-radius:20px;padding:7px 15px;background:white;font:inherit;cursor:pointer}}button[aria-pressed="true"]{{background:#172333;color:white;border-color:#172333}}
.scroll{{overflow:auto}}table{{border-collapse:collapse;width:100%;min-width:850px}}th,td{{text-align:left;padding:15px 12px;border-bottom:1px solid var(--line);vertical-align:top}}th{{font-size:12px;color:var(--sub)}}td:first-child{{width:25%}}td:nth-child(2){{width:31%}}td:last-child{{width:29%}}.path{{font:11px/1.6 ui-monospace,monospace;color:var(--sub);margin-top:5px;overflow-wrap:anywhere}}.amount{{white-space:nowrap;font-variant-numeric:tabular-nums}}
.badge{{display:inline-block;border-radius:5px;padding:2px 8px;margin-bottom:7px;font-size:12px;font-weight:600}}.done{{color:#076447;background:#e7f5ee}}.kept{{color:#435266;background:#eef2f6}}.pending{{color:#915500;background:#fff3d9}}a{{color:var(--blue);text-decoration:none}}a:hover{{text-decoration:underline}}.sources{{display:flex;gap:12px;flex-wrap:wrap;font-size:12px}}li{{margin:8px 0}}details{{margin-top:20px}}summary{{cursor:pointer;font-weight:600}}
@media(max-width:650px){{main{{padding:24px 14px}}.panel{{padding:18px}}.stats{{grid-template-columns:1fr;gap:14px}}.stat strong{{font-size:30px}}.barrow{{grid-template-columns:55px 1fr 85px;font-size:12px}}}}
</style></head><body><main>
<h1>磁盘清理结果</h1><p>{esc(data["generated_at"])} · {esc(data["status_label"])} · GB 为十进制</p>
<section class="panel"><div class="stats">{cards}</div>{bars}{extra_note}<p>总容量 {stats["total_bytes"]/1e9:.2f} GB。可用空间以同一 Data 卷的 df 前后回读为准，包含运行中的写入和系统自然回收。</p></section>
<section class="panel"><h2>每项处理结果</h2><div class="filters">
<button data-filter="all" aria-pressed="true">全部</button><button data-filter="done" aria-pressed="false">已执行清理</button><button data-filter="kept" aria-pressed="false">核实后保留</button><button data-filter="pending" aria-pressed="false">需要后续操作</button>
</div><div class="scroll"><table><thead><tr><th>项目</th><th>处理结果</th><th>目录体量 / 减少量</th><th>保留范围与下一步</th></tr></thead><tbody>{rows}</tbody></table></div></section>
<section class="panel"><h2>复核与边界</h2><ul>{notes}</ul>
<p><a href="analysis_before.html">查看清理前分析快照</a> · <a href="cleanup_results.json">结构化总结果</a></p>
<details><summary>逐目录证据与会话候选清单</summary><div class="sources">{sources}</div></details></section>
</main><script>
document.querySelectorAll('[data-filter]').forEach(button=>button.addEventListener('click',()=>{{
  const filter=button.dataset.filter;
  document.querySelectorAll('[data-filter]').forEach(other=>other.setAttribute('aria-pressed',String(other===button)));
  document.querySelectorAll('tr[data-group]').forEach(row=>{{row.hidden=filter!=='all'&&row.dataset.group!==filter;}});
}}));
</script></body></html>'''


if __name__ == "__main__":
    result = json.loads((ROOT / "cleanup_results.json").read_text())
    (ROOT / "report.html").write_text(render(result))
