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
  ['市场与 ETF', 'watchlist', '主观察表', false],
  ['当日估值表', 'valuation', '指数估值与星级', false],
  ['我的状态与下一步动作', 'entry', '对你当前状态的建议', false],
  ['5星触发后如何行动', 'levels', '5星观察线与分批评估', true],
  ['银行螺丝钉：最新核验观点', 'lsd', '银行螺丝钉：完整观点', true],
  ['群内作者更新：已通过南冬CLI读取', 'authors', '重远投资观：要点与螺丝钉对照', true],
  ['FiNews补充：只保留影响你决策的信息', 'finews', 'FiNews线索与核验', true],
  ['ETF事件与下一项观察', 'calendar', '事件与下次观察', true],
  ['每日交付与来源状态', 'method', '数据口径与交付说明', true],
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
        const types = { '.json': 'application/json', '.csv': 'text/csv', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.svg': 'image/svg+xml' };
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

const chunks = source.replace(/^# .*\n+/, '').split(/^## ([^\n]+)\s*$/m);
const introduction = markdown(chunks[0]);
const rendered = [];
for (let i = 1; i < chunks.length; i += 2) {
  const heading = chunks[i].trim();
  const [, id, label, folded] = sectionMap.get(heading) || [heading, `section-${i}`, heading, false];
  const body = chunks[i + 1] || '';
  const fullList = id === 'valuation' ? /^### (全部低估品种[^\n]*)$/m.exec(body) : null;
  const content = fullList
    ? markdown(body.slice(0, fullList.index)) + `<details class="reference" id="undervalued"><summary><span>${escape(fullList[1])}</span></summary><div class="section-content">${markdown(body.slice(fullList.index + fullList[0].length))}</div></details>`
    : markdown(body);
  rendered.push(folded
    ? `<details id="${id}" class="report-section folded"><summary><span>${escape(label)}</span><span class="expand-label">展开</span></summary><div class="section-content">${content}</div></details>`
    : `<section id="${id}" class="report-section"><h2>${escape(label)}</h2>${content}</section>`);
}
const appendixHtml = [];
for (const item of appendices.values()) {
  const content = markdown(fs.readFileSync(item.file, 'utf8'), path.dirname(item.file)).replace(/<h1>/g, '<h3>').replace(/<\/h1>/g, '</h3>');
  appendixHtml.push(`<details class="reference" id="${item.id}"><summary>${item.label}</summary><div class="section-content">${content}</div></details>`);
}
const market = JSON.parse(fs.readFileSync(path.join(out, 'market.json'), 'utf8'));
const bySymbol = market.metrics;
const sessions = new Set(Object.values(bySymbol).map(item => item.session));
if (sessions.size !== 1 || !sessions.has(market.asof)) throw new Error('Market summary contains mixed sessions');
const tickerHtml = ['sh000001', 'sh000016', 'sh000300', 'sh000688'].map(symbol => {
  const item = bySymbol[symbol];
  if (!item || !Number.isFinite(item.close) || !Number.isFinite(item.daily_pct)) throw new Error('Missing index quote');
  const delta = `${item.daily_pct >= 0 ? '+' : ''}${item.daily_pct.toFixed(2)}%`;
  return `<div class="ticker"><a class="ticker-label" href="${escape(item.source)}" target="_blank" rel="noopener noreferrer">${escape(item.name)}</a><div class="ticker-values"><span>${Number(item.close).toLocaleString('en-US', {minimumFractionDigits:2, maximumFractionDigits:2})}</span><span class="change ${item.daily_pct >= 0 ? 'positive' : 'negative'}">${delta}</span></div></div>`;
}).join('');
const [year, month, day] = reportDate.split('-');
const navItems = [['priorities', '今日重点'], ['watchlist', '观察名单'], ['valuation', '估值星级'], ['entry', '入场研究'], ['authors', '作者对照'], ['calendar', '事件观察'], ['method', '数据口径']];
const navigation = navItems.filter(([id]) => rendered.some(section => section.includes(`id="${id}"`))).map(([id, label]) => `<a href="#${id}">${label}</a>`).join('');
const css = fs.readFileSync(new URL('../us_market_daily/report.css', import.meta.url), 'utf8');
const script = fs.readFileSync(new URL('../us_market_daily/report_interactions.js', import.meta.url), 'utf8');
const html = `<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<meta name="referrer" content="no-referrer">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src data:; style-src 'unsafe-inline'; script-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>A股观察 · ${reportDate}</title>
<style>${css}</style>
</head>
<body id="top">
<a class="skip-link" href="#main">跳转到日报正文</a>
<div class="page">
<header class="masthead">
  <div><p class="eyebrow">每日研究 · 收盘观察</p><h1>A股观察</h1></div>
  <div class="edition"><time datetime="${reportDate}">${year}.${month}.${day}</time><span>北京时间</span></div>
</header>
<nav class="navigation" aria-label="日报目录">${navigation}<button type="button" id="print-report">打印 / 保存 PDF</button></nav>
<main id="main">
  <section class="introduction" aria-label="今日判断">${introduction}</section>
  ${tickerHtml ? `<div class="market-strip" aria-label="指数与波动率，收盘点位及当日变化">${tickerHtml}</div><p class="strip-note">指数单位为点，ETF报价为人民币元；行情截至${market.asof}收盘。</p>` : ''}
  ${rendered.join('\n')}
  ${appendixHtml.length ? `<section id="references" class="report-section reference-section"><h2>延伸阅读与研究依据</h2>${appendixHtml.join('\n')}</section>` : ''}
</main>
<footer><span>A股观察 · ${reportDate} · 已保存的收盘研究</span><a href="#top">回到顶部 ↑</a></footer>
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
  shared_style: '../us_market_daily/report.css',
  shared_interactions: '../us_market_daily/report_interactions.js',
  shared_style_sha256: sha(css),
  shared_interactions_sha256: sha(script),
};
fs.writeFileSync(path.join(out, 'html_manifest.json'), JSON.stringify(receipt, null, 2) + '\n');
console.log(JSON.stringify({ file: outputFile, bytes: receipt.html_bytes, charts: receipt.embedded_chart_files.length, appendices: receipt.embedded_appendices.length }));
