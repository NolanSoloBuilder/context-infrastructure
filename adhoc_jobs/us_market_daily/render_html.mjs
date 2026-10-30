/** Build a portable HTML edition from the reviewed Markdown and saved evidence. */
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import crypto from 'node:crypto';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';

const require = createRequire(import.meta.url);
const args = process.argv.slice(2);
const option = name => args[args.indexOf(name) + 1];
if (!args.includes('--out') || !args.includes('--report-date')) {
  throw new Error('Usage: node render_html.mjs --out <daily-directory> --report-date YYYY-MM-DD');
}
const out = path.resolve(option('--out'));
const reportDate = option('--report-date');
const reportTitle = args.includes('--title') ? option('--title') : '美股观察';
if (!/^\d{4}-\d{2}-\d{2}$/.test(reportDate)) throw new Error('Expected an explicit Beijing report date');
const sourceFile = path.join(out, 'report.md');
const source = fs.readFileSync(sourceFile, 'utf8');
if (!source.includes(reportDate)) throw new Error('Report date and reviewed Markdown do not match');
const allowedRoot = path.dirname(out);
let markedModule;
try { markedModule = require.resolve('marked'); } catch {
  markedModule = path.join(os.homedir(), '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/marked/lib/marked.esm.js');
}
const { Marked } = await import(pathToFileURL(markedModule).href);
const escape = value => String(value).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&#39;');
const sha = value => crypto.createHash('sha256').update(value).digest('hex');
const assets = new Map();
const appendices = new Map();
const exports = new Map();
const sections = [
  ['今天对你最重要的事', 'priorities', '今天对你最重要的事', false],
  ['盘前与盘后观察', 'extended', '盘前与盘后观察', false],
  ['Google估值结果', 'valuation', 'Google研究详情', true],
  ['SOFI研究观察', 'sofi', 'SOFI研究详情', true],
  ['机器人供应链筛选', 'opportunities', '机器人研究详情', true],
  ['主观察表', 'watchlist', '主观察表', false],
  ['分类观察总表', 'watchlist', '分类观察总表', false],
  ['行业观察', 'sectors', '行业观察', true],
  ['🔎 Reddit 投资与信息差观察', 'reddit', 'Reddit 信息观察', true],
  ['对你当前状态的建议', 'entry', '入场研究', false],
  ['距观察档还有多远', 'levels', '距观察档还有多远', true],
  ['利率与未来一周事件', 'calendar', '利率与事件日历', true],
  ['完整表现与趋势数据', 'data', '完整表现与趋势数据', true],
  ['口径、核验和缺口', 'method', '数据口径与核验缺口', true],
];
const sectionMap = new Map(sections.map(s => [s[0], s]));

function localFile(href, base) {
  const resolved = fs.realpathSync(path.resolve(base, decodeURIComponent(href)));
  if (!resolved.startsWith(allowedRoot + path.sep)) throw new Error(`Reference outside report archive: ${href}`);
  if (fs.statSync(resolved).size > 3_000_000) throw new Error(`Reference too large: ${href}`);
  return resolved;
}

function dataUrl(filename, type) {
  if (!assets.has(filename)) assets.set(filename, `data:${type};base64,${fs.readFileSync(filename).toString('base64')}`);
  return assets.get(filename);
}

function markdown(text, base = out) {
  const md = new Marked({
    gfm: true,
    renderer: {
      html(token) { return escape(token.text); },
      link(token) {
        const label = this.parser.parseInline(token.tokens);
        const href = token.href;
        if (/^https?:\/\//i.test(href)) return `<a href="${escape(href)}" target="_blank" rel="noopener noreferrer">${label}</a>`;
        if (href.startsWith('#')) return `<a href="${escape(href)}">${label}</a>`;
        if (/^[a-z][a-z\d+.-]*:/i.test(href)) return label;
        const file = localFile(href, base);
        if (file === sourceFile) return `<a href="#top">${label}</a>`;
        const extension = path.extname(file).toLowerCase();
        if (extension === '.md') {
          const id = `reference-${sha(file).slice(0, 10)}`;
          if (!appendices.has(file)) appendices.set(file, { id, label, file });
          return `<a href="#${id}">${label}</a>`;
        }
        const types = { '.json': 'application/json', '.csv': 'text/csv', '.png': 'image/png', '.svg': 'image/svg+xml' };
        if (!types[extension]) throw new Error(`Unsupported local reference: ${href}`);
        exports.set(file, true);
        return `<a href="${dataUrl(file, types[extension])}" download="${escape(path.basename(file))}">${label}</a>`;
      },
      image(token) {
        if (/^[a-z][a-z\d+.-]*:/i.test(token.href)) throw new Error('Charts must be saved local assets');
        const file = localFile(token.href, base);
        const types = { '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.svg': 'image/svg+xml' };
        const type = types[path.extname(file).toLowerCase()];
        if (!type) throw new Error('Unsupported chart image');
        return `<figure><button type="button" class="chart-button" aria-label="放大图表：${escape(token.text)}"><img src="${dataUrl(file, type)}" alt="${escape(token.text)}" loading="eager" decoding="async"></button><figcaption>${escape(token.text)}<span>点击图表放大</span></figcaption></figure>`;
      },
    },
  });
  return md.parse(text)
    .replace(/<p>(<figure>[\s\S]*?<\/figure>)<\/p>/g, '$1')
    .replace(/<table>/g, '<div class="table-scroll" role="region" aria-label="数据表，可横向滚动" tabindex="0"><table>')
    .replace(/<\/table>/g, '</table></div>');
}

const chunks = source.replace(/^# .*\n+/, '').split(/^\*\*([^\n]+)\*\*\s*$/m);
const introduction = markdown(chunks[0]);
const rendered = [];
for (let i = 1; i < chunks.length; i += 2) {
  const heading = chunks[i].trim();
  const [, id, label, folded] = sectionMap.get(heading) || [heading, `section-${i}`, heading, false];
  const content = markdown(chunks[i + 1] || '');
  rendered.push(folded
    ? `<details id="${id}" class="report-section folded"><summary><span>${escape(label)}</span><span class="expand-label">展开</span></summary><div class="section-content">${content}</div></details>`
    : `<section id="${id}" class="report-section"><h2>${escape(label)}</h2>${content}</section>`);
}
const appendixHtml = [];
for (const item of appendices.values()) {
  const content = markdown(fs.readFileSync(item.file, 'utf8'), path.dirname(item.file)).replace(/<h1>/g, '<h3>').replace(/<\/h1>/g, '</h3>');
  appendixHtml.push(`<details class="reference" id="${item.id}"><summary>${item.label}</summary><div class="section-content">${content}</div></details>`);
}
const metricsPath = path.join(out, 'metrics.json');
const metrics = fs.existsSync(metricsPath) ? JSON.parse(fs.readFileSync(metricsPath, 'utf8')) : [];
const bySymbol = new Map(metrics.map(item => [item.symbol, item]));
const sessions = new Set(metrics.map(item => item.session));
if (sessions.size > 1) throw new Error('Market summary contains mixed sessions');
const indexSources = {
  '^GSPC': 'https://finance.yahoo.com/quote/%5EGSPC/history/',
  '^NDX': 'https://ca.investing.com/indices/nq-100-historical-data',
  '^IXIC': 'https://finance.yahoo.com/quote/%5EIXIC/history/',
  '^VIX': 'https://www.cboe.com/tradable-products/vix/',
};
const tickerHtml = ['^GSPC', '^NDX', '^IXIC', '^VIX'].filter(s => bySymbol.has(s)).map(s => {
  const item = bySymbol.get(s);
  const delta = `${item.day_pct >= 0 ? '+' : ''}${item.day_pct.toFixed(2)}%`;
  return `<div class="ticker"><a class="ticker-label" href="${indexSources[s]}" target="_blank" rel="noopener noreferrer">${escape(item.label)}</a><div class="ticker-values"><span>${Number(item.close).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span><span class="change ${s === '^VIX' ? 'neutral' : item.day_pct >= 0 ? 'positive' : 'negative'}">${delta}</span></div></div>`;
}).join('');
const [year, month, day] = reportDate.split('-');
const navItems = [['priorities', '重点机会'], ['watchlist', '分类总表'], ['extended', '盘前盘后'], ['valuation', 'Google详情'], ['sofi', 'SOFI详情'], ['opportunities', '机器人详情'], ['entry', '入场研究'], ['sectors', '行业'], ['reddit', 'Reddit'], ['calendar', '事件日历'], ['data', '完整数据']];
const navigation = navItems.filter(([id]) => rendered.some(section => section.includes(`id="${id}"`))).map(([id, label]) => `<a href="#${id}">${label}</a>`).join('');
const css = fs.readFileSync(new URL('./report.css', import.meta.url), 'utf8');
const script = fs.readFileSync(new URL('./report_interactions.js', import.meta.url), 'utf8');
const html = `<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<meta name="referrer" content="no-referrer">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src data:; style-src 'unsafe-inline'; script-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>${escape(reportTitle)} · ${reportDate}</title>
<style>${css}</style>
</head>
<body id="top">
<a class="skip-link" href="#main">跳转到日报正文</a>
<div class="page">
<header class="masthead">
  <div><p class="eyebrow">投资研究 · 数据与情景</p><h1>${escape(reportTitle)}</h1></div>
  <div class="edition"><time datetime="${reportDate}">${year}.${month}.${day}</time><span>北京时间</span></div>
</header>
<nav class="navigation" aria-label="日报目录">${navigation}<button type="button" id="print-report">打印 / 保存 PDF</button></nav>
<main id="main">
  <section class="introduction" aria-label="今日判断">${introduction}</section>
  ${tickerHtml ? `<div class="market-strip" aria-label="指数与波动率，收盘点位及当日变化">${tickerHtml}</div><p class="strip-note">指数单位为点；VIX为其当日值。以下个股与ETF报价单位为美元。</p>` : ''}
  ${rendered.join('\n')}
  ${appendixHtml.length ? `<section id="references" class="report-section reference-section"><h2>延伸阅读与研究依据</h2>${appendixHtml.join('\n')}</section>` : ''}
</main>
<footer><span>${escape(reportTitle)} · ${reportDate} · 已保存的研究</span><a href="#top">回到顶部 ↑</a></footer>
</div>
<dialog id="chart-dialog" aria-label="放大图表"><div class="dialog-toolbar"><span id="chart-title">图表</span><button type="button" id="close-chart" aria-label="关闭图表">关闭 ✕</button></div><div class="zoom-scroll"><img id="zoom-image" alt=""></div></dialog>
<script>${script}</script>
</body>
</html>`;
const outputFile = path.join(out, 'report.html');
fs.writeFileSync(outputFile, html);
const receipt = {
  report_date_beijing: reportDate, market_session: [...sessions][0] || null,
  generated_at_utc: new Date().toISOString(), source_markdown_sha256: sha(source),
  html_sha256: sha(html), html_bytes: Buffer.byteLength(html),
  embedded_chart_files: [...assets.keys()].filter(f => /\.(png|jpe?g|svg)$/.test(f)).map(f => path.relative(out, f)),
  embedded_appendices: [...appendices.keys()].map(f => path.relative(out, f)),
  downloadable_evidence: [...exports.keys()].map(f => path.relative(out, f)),
  content_policy: 'Reviewed report is the content source; no fetching or price recomputation; images and linked local evidence embedded for offline use.',
};
fs.writeFileSync(path.join(out, 'html_manifest.json'), JSON.stringify(receipt, null, 2) + '\n');
console.log(JSON.stringify({ file: outputFile, bytes: receipt.html_bytes, charts: receipt.embedded_chart_files.length, appendices: receipt.embedded_appendices.length }));
