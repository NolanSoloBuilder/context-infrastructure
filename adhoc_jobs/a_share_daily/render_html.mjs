/** Build a portable HTML edition from the reviewed Markdown and saved evidence. */
import fs from 'node:fs';
import { trendSection } from './trend_view.mjs';
import { colorValuationCells, valuationLegend, valuationControls } from './valuation_labels.mjs';
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
if (source.includes('## 主观察表：行情、估值与星级') && /^## (市场与 ETF|当日估值表)$/m.test(source)) throw new Error('Merged overview must not coexist with duplicate market/valuation sections');
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
  ['主观察表：行情、估值与星级', 'watchlist', '主观察表 · 行情、估值与星级', false],
  ['当日估值表', 'valuation', '指数估值与星级', false],
  ['我的状态与下一步动作', 'entry', '下一步：补齐资金条件', false],
  ['5星触发后如何行动', 'levels', '5星观察线与分批评估', true],
  ['银行螺丝钉：最新核验观点', 'lsd', '银行螺丝钉：完整观点', true],
  ['群内作者更新：已通过南冬CLI读取', 'authors', '作者对照：依据、条件与仓位', true],
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
  return colorValuationCells(md.parse(text))
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
  const fullList = ['valuation','watchlist'].includes(id) ? /^### ((?:全部低估品种|原始估值与核验资料)[^\n]*)$/m.exec(body) : null;
  let content = fullList
    ? markdown(body.slice(0, fullList.index)) + `<details class="reference" id="${fullList[1].startsWith('全部低估') ? 'undervalued' : 'valuation-sources'}"><summary><span>${escape(fullList[1])}</span></summary><div class="section-content">${markdown(body.slice(fullList.index + fullList[0].length))}</div></details>`
    : markdown(body);
  if (heading === '主观察表：行情、估值与星级') content = content.replace('<div class="table-scroll"', valuationLegend() + '<div class="table-scroll"');
  if (heading === '主观察表：行情、估值与星级' && fs.existsSync(path.join(out, 'valuation_all.json'))) content = content.replace('<div class="table-scroll"', valuationControls() + '<div class="table-scroll"') + '<p class="valuation-empty" hidden>本期没有符合条件的指数。</p>';
  if (heading === '主观察表：行情、估值与星级' && fs.existsSync(path.join(out, 'valuation_all.json'))) {
    const valuation=JSON.parse(fs.readFileSync(path.join(out, 'valuation_all.json'), 'utf8'));
    const original=localFile(valuation.source_image,out);
    const title=`螺丝钉估值原图 · 第${valuation.issue}期 · ${valuation.asof}`;
    const quickView=`<button type="button" class="valuation-image-button" aria-haspopup="dialog" aria-controls="chart-dialog" data-image-title="${escape(title)}"><span>查看螺丝钉估值原图</span><small>第${escape(valuation.issue)}期 · ${escape(valuation.asof)}</small><img src="${dataUrl(original, 'image/jpeg')}" alt="" hidden></button>`;
    content=content.replace('<p class="valuation-legend"',quickView+'<p class="valuation-legend"');
  }
  rendered.push(folded
    ? `<details id="${id}" class="report-section folded"><summary><span>${escape(label)}</span><span class="expand-label">展开</span></summary><div class="section-content">${content}</div></details>`
    : `<section id="${id}" class="report-section${heading === '主观察表：行情、估值与星级' ? ' merged-overview' : ''}"><h2>${escape(label)}</h2>${content}</section>`);
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
const trendFile = path.join(out, 'trends.json');
const trendData = fs.existsSync(trendFile) ? JSON.parse(fs.readFileSync(trendFile, 'utf8')) : null;
if (trendData && (trendData.asof !== market.asof || Object.values(trendData.assets).some(a => a.group !== 'china' && a.asof !== market.asof))) throw new Error('Trend snapshot date mismatch');
if (trendData && Object.values(trendData.assets).some(a => a.group === 'china' && (a.asof >= reportDate || a.points.at(-1)?.date !== a.asof))) throw new Error('Overseas curve is not a completed pre-report session');
if (trendData && fs.existsSync(path.join(out, 'valuation_all.json'))) {
  const valuation=JSON.parse(fs.readFileSync(path.join(out, 'valuation_all.json'), 'utf8'));
  const related={sh000001:'上证指数',sh000016:'上证50',sh000300:'沪深300',sh000688:'科创50',sh510050:'上证50',sh510300:'沪深300',sh588000:'科创50'};
  for(const [symbol,name] of Object.entries(related)){const asset=trendData.assets[symbol],row=valuation.items.find(x=>x.name===name);if(asset && row)asset.valuation={...row,index_name:row.name,asof:valuation.asof,source_url:valuation.source_url};}
}
const trendsHtml = trendData ? trendSection(trendData) : '';
const reportSections = rendered.map(section => {
  if (!section.includes('id="watchlist"')) return section;
  if (!market.carried_forward) return section + trendsHtml;
  return `<details id="last-session" class="report-section folded"><summary><span>最近交易日行情与估值 · ${escape(market.asof)}</span><span class="expand-label">展开</span></summary><div class="section-content">${section}${trendsHtml}</div></details>`;
}).join('\n');
const trendScript = trendData ? fs.readFileSync(new URL('./trend_view.mjs', import.meta.url), 'utf8').replace(/^export /gm, '') + '\n' + fs.readFileSync(new URL('./trend_client.js', import.meta.url), 'utf8') : '';
const [year, month, day] = reportDate.split('-');
const navItems = [['priorities', '今日重点'], ['watchlist', '主观察表'], ['trends', '趋势图'], ['china-stocks', '中概股'], ['valuation', '估值星级'], ['entry', '资金条件'], ['authors', '作者对照'], ['calendar', '事件观察'], ['method', '数据口径']];
const navigation = navItems.filter(([id]) => (id === 'trends' ? !!trendData : id === 'china-stocks' ? Object.values(trendData?.assets || {}).some(a => a.group === 'china') : rendered.some(section => section.includes(`id="${id}"`)))).map(([id, label]) => `<a href="#${id}">${label}</a>`).join('');
const css = fs.readFileSync(new URL('../us_market_daily/report.css', import.meta.url), 'utf8');
const mobileCss = fs.readFileSync(new URL('./report_mobile.css', import.meta.url), 'utf8');
const script = fs.readFileSync(new URL('../us_market_daily/report_interactions.js', import.meta.url), 'utf8');
const valuationModalScript = fs.readFileSync(new URL('./valuation_modal.js', import.meta.url), 'utf8');
const valuationFilterScript = fs.readFileSync(new URL('./valuation_filter.js', import.meta.url), 'utf8');
const refreshScript = fs.readFileSync(new URL('./report_refresh.js', import.meta.url), 'utf8');
const contentRevision = sha(fs.readFileSync(new URL('./valuation_labels.mjs', import.meta.url), 'utf8') + valuationFilterScript + valuationModalScript + source + css + mobileCss + script + trendScript + refreshScript + JSON.stringify(trendData) + [...assets.values()].join('') + fs.readFileSync(new URL(import.meta.url), 'utf8'));
const html = `<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<meta name="referrer" content="no-referrer">
<meta name="report-revision" content="${contentRevision}">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src data:; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'; base-uri 'none'; form-action 'none'">
<title>A股观察 · ${reportDate}</title>
<style>${css}</style>
<style data-a-share-mobile>${mobileCss}</style>
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
<div class="report-refresh" id="report-refresh"><label><input type="checkbox" checked>自动检查新版</label><button type="button">立即检查</button><span role="status" aria-live="polite">默认每5分钟检查最新已发布晨报</span></div>
  <section class="introduction" aria-label="今日判断">${introduction}</section>
  ${tickerHtml && !source.includes('## 主观察表：行情、估值与星级') ? `<div class="market-strip" aria-label="指数与波动率，收盘点位及当日变化">${tickerHtml}</div><p class="strip-note">指数单位为点，ETF报价为人民币元；行情截至${market.asof}收盘。</p>` : ''}
  ${reportSections}${trendsHtml && !rendered.some(section => section.includes('id="watchlist"')) ? trendsHtml : ''}
  ${appendixHtml.length ? `<section id="references" class="report-section reference-section"><h2>延伸阅读与研究依据</h2>${appendixHtml.join('\n')}</section>` : ''}
</main>
<footer><span>A股观察 · ${reportDate} · 已保存的收盘研究</span><a href="#top">回到顶部 ↑</a></footer>
</div>
<aside id="trend-hover-panel" class="trend-hover-panel" role="dialog" aria-modal="false" aria-label="标的数据预览" hidden></aside>
<dialog id="trend-dialog" aria-label="标的完整数据"><div class="trend-detail-toolbar"><span id="trend-dialog-title">标的详情</span><div class="trend-dialog-periods" role="group" aria-label="详情曲线区间">${[['20d','20日'],['1y','一年'],['2y','两年'],['3y','三年']].map(([key,label])=>`<button type="button" data-detail-period="${key}" aria-pressed="${key==='3y'}">${label}</button>`).join('')}</div><button type="button" id="close-trend-detail">关闭</button></div><div id="trend-dialog-body" class="trend-panel-body"></div></dialog>
<dialog id="chart-dialog" aria-label="放大图表"><div class="dialog-toolbar"><span id="chart-title">图表</span><div id="valuation-zoom-controls" class="valuation-zoom-controls" role="group" aria-label="估值图缩放" hidden><button type="button" data-valuation-zoom="out" aria-label="缩小估值图">−</button><output aria-live="polite">100%</output><button type="button" data-valuation-zoom="in" aria-label="放大估值图">＋</button><button type="button" data-valuation-zoom="fit">适应宽度</button></div><button type="button" id="close-chart" aria-label="关闭图表">关闭 ✕</button></div><div class="zoom-scroll"><img id="zoom-image" alt=""></div></dialog>
<script>${script}</script>
<script>${refreshScript}</script>
<script>${valuationFilterScript}</script>
<script>${valuationModalScript}</script>
<script>document.querySelectorAll('#watchlist tbody tr').forEach(row=>{const cell=row.cells[2];if(cell && (row.closest('#undervalued') || cell.textContent.trim()==='—')){cell.classList.remove('positive','negative');cell.classList.add('neutral');}});</script>
${trendData ? `<script id="trend-data" type="application/json">${JSON.stringify(trendData).replaceAll('<', '\\u003c')}</script><script>${trendScript}</script>` : ''}
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
  content_revision: contentRevision,
  refresh_script_sha256: sha(refreshScript),
  trend_asof: trendData?.asof || null,
  trend_script_sha256: sha(trendScript),
  mobile_style: 'report_mobile.css',
  mobile_style_sha256: sha(mobileCss),
  shared_interactions_sha256: sha(script),
};
fs.writeFileSync(path.join(out, 'html_manifest.json'), JSON.stringify(receipt, null, 2) + '\n');
console.log(JSON.stringify({ file: outputFile, bytes: receipt.html_bytes, charts: receipt.embedded_chart_files.length, appendices: receipt.embedded_appendices.length }));
