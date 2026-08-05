#!/usr/bin/env node

const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFileSync } = require('child_process');
const { historySnapshotDir: snapshotDir, outputDir } = require('./private_paths');

process.umask(0o077);

const chromeProfileDir = path.join(os.homedir(), 'Library/Application Support/Google/Chrome/Default');
const bookmarksPath = path.join(chromeProfileDir, 'Bookmarks');
const historyPath = path.join(chromeProfileDir, 'History');
const historyJournalPath = path.join(chromeProfileDir, 'History-journal');
const historySnapshotPath = path.join(snapshotDir, 'History.sqlite');

const NOW = new Date('2026-06-20T00:00:00+08:00');
const ONE_DAY = 24 * 60 * 60 * 1000;

const FORMER_COMPANY_DOMAIN_PATTERNS = [
  /(^|\.)alibaba-inc\.com$/i,
  /(^|\.)elenet\.me$/i,
  /(^|\.)rajax\.me$/i,
  /(^|\.)alibaba\.net$/i,
];

const XHS_DOMAIN_PATTERNS = [
  /(^|\.)xiaohongshu\.com$/i,
  /(^|\.)xhscdn\.com$/i,
];

const VOLATILE_PATTERNS = [
  /ticket=/i,
  /scode=/i,
  /token=/i,
  /apply_page/i,
  /redirect_url=/i,
  /beta\.xiaohongshu\.com/i,
  /\.sit\.xiaohongshu\.com/i,
  /\.daily\./i,
  /devops\.beta\./i,
  /sl\.sit\./i,
];

const RISKY_OR_VOLATILE_CONTENT_PATTERNS = [
  /破解版|破解|激活码|永久激活|crack/i,
  /macwk\.com/i,
  /xclient\.info/i,
  /waitsun\.com/i,
  /sdifen\.com/i,
  /idejihuo\.com/i,
  /zlib|z-library|b-ok\.cc|1lib\.|zlib\.pro|u1lib/i,
  /free-web-proxy|proxy/i,
];

function ensureDirs() {
  fs.mkdirSync(snapshotDir, { recursive: true });
  fs.mkdirSync(outputDir, { recursive: true });
}

function chromeTimeToDate(value) {
  if (!value || String(value) === '0') return null;
  const micros = BigInt(value);
  return new Date(Number(micros / 1000n - 11644473600000n));
}

function chromeTimeToDateFromSql(value) {
  if (!value || Number(value) === 0) return null;
  return chromeTimeToDate(String(value));
}

function formatDate(date) {
  if (!date) return '';
  return date.toISOString().slice(0, 10);
}

function daysSince(date) {
  if (!date) return null;
  return Math.floor((NOW.getTime() - date.getTime()) / ONE_DAY);
}

function normalizeUrl(url, mode = 'exact') {
  try {
    const parsed = new URL(url);
    if (mode === 'without_hash') parsed.hash = '';
    if (mode === 'path') {
      parsed.hash = '';
      parsed.search = '';
    }
    return parsed.toString();
  } catch (_error) {
    return url;
  }
}

function hostOf(url) {
  try {
    return new URL(url).hostname.replace(/^www\./, '').toLowerCase();
  } catch (_error) {
    return '';
  }
}

function csvEscape(value) {
  const text = String(value ?? '');
  if (/[",\n]/.test(text)) return `"${text.replace(/"/g, '""')}"`;
  return text;
}

function collectBookmarks(bookmarks) {
  const rows = [];
  function walk(node, trail = []) {
    if (node.type === 'url') {
      rows.push({
        name: node.name || '',
        url: node.url || '',
        path: trail.join('/'),
        dateAdded: chromeTimeToDate(node.date_added),
        dateLastUsedBookmark: chromeTimeToDate(node.date_last_used),
      });
      return;
    }
    for (const child of node.children || []) {
      walk(child, [...trail, node.name]);
    }
  }

  for (const root of ['bookmark_bar', 'other', 'synced']) {
    walk(bookmarks.roots[root], [root]);
  }
  return rows;
}

function copyHistorySnapshot() {
  fs.copyFileSync(historyPath, historySnapshotPath);
  if (fs.existsSync(historyJournalPath)) {
    fs.copyFileSync(historyJournalPath, `${historySnapshotPath}-journal`);
  }
}

function loadHistoryRows() {
  const query = 'select url, title, visit_count, last_visit_time from urls where last_visit_time > 0';
  const raw = execFileSync('sqlite3', ['-json', historySnapshotPath, query], {
    encoding: 'utf8',
    maxBuffer: 64 * 1024 * 1024,
  });
  return JSON.parse(raw || '[]');
}

function buildHistoryIndex(historyRows) {
  const exact = new Map();
  const withoutHash = new Map();
  const pathOnly = new Map();

  function put(map, key, row) {
    if (!key) return;
    const existing = map.get(key);
    if (!existing || Number(row.last_visit_time) > Number(existing.last_visit_time)) map.set(key, row);
  }

  for (const row of historyRows) {
    put(exact, normalizeUrl(row.url, 'exact'), row);
    put(withoutHash, normalizeUrl(row.url, 'without_hash'), row);
    put(pathOnly, normalizeUrl(row.url, 'path'), row);
  }
  return { exact, withoutHash, pathOnly };
}

function historyMatchFor(url, index) {
  const exact = index.exact.get(normalizeUrl(url, 'exact'));
  if (exact) return { row: exact, precision: 'exact' };
  const withoutHash = index.withoutHash.get(normalizeUrl(url, 'without_hash'));
  if (withoutHash) return { row: withoutHash, precision: 'without_hash' };
  const pathOnly = index.pathOnly.get(normalizeUrl(url, 'path'));
  if (pathOnly) return { row: pathOnly, precision: 'path_only' };
  return { row: null, precision: 'none' };
}

function classify(row) {
  const host = hostOf(row.url);
  const haystack = `${row.name}\n${row.url}\n${row.path}`;
  const reasons = [];
  const categories = [];

  if (FORMER_COMPANY_DOMAIN_PATTERNS.some((pattern) => pattern.test(host))) {
    categories.push('former_company_candidate');
    reasons.push('前司/旧工作域名候选');
  }

  if (XHS_DOMAIN_PATTERNS.some((pattern) => pattern.test(host))) {
    categories.push('current_work');
  }

  if (VOLATILE_PATTERNS.some((pattern) => pattern.test(row.url))) {
    categories.push('volatile_link');
    reasons.push('带临时授权参数或测试环境');
  }

  if (/^http:\/\//i.test(row.url)) {
    categories.push('plain_http');
    reasons.push('HTTP 非 HTTPS');
  }

  if (RISKY_OR_VOLATILE_CONTENT_PATTERNS.some((pattern) => pattern.test(haystack))) {
    categories.push('risky_or_volatile_content');
    reasons.push('破解/镜像/代理/资源站候选，容易失效或有风险');
  }

  if (/\b20(19|20|21|22|23|24)\b|2023|2024|23H2|24\.|2401|2405|Q3|Q4/i.test(haystack)) {
    categories.push('dated_content_candidate');
    reasons.push('标题或路径含旧年份/季度/版本');
  }

  if (!row.name.trim()) {
    categories.push('empty_title');
    reasons.push('标题为空');
  }

  const staleDays = daysSince(row.lastUsed);
  if (staleDays === null) {
    categories.push('no_recent_visit_evidence');
    reasons.push('书签和 History 都没有访问证据');
  } else if (staleDays >= 730) {
    categories.push('not_used_2y');
    reasons.push('超过 2 年无访问记录');
  } else if (staleDays >= 365) {
    categories.push('not_used_1y');
    reasons.push('超过 1 年无访问记录');
  }

  return { categories, reasons };
}

async function checkLive(rows) {
  const concurrency = 14;
  const timeoutMs = 7000;
  const unique = [...new Map(rows.map((row) => [row.url, row])).values()];
  const results = [];
  let cursor = 0;

  async function check(row) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    const started = Date.now();
    try {
      const response = await fetch(row.url, {
        method: 'HEAD',
        redirect: 'manual',
        signal: controller.signal,
        headers: {
          'User-Agent': 'Mozilla/5.0 bookmark-audit',
        },
      });
      return {
        url: row.url,
        status: response.status,
        redirectedTo: response.headers.get('location') || '',
        ms: Date.now() - started,
        error: '',
      };
    } catch (error) {
      return {
        url: row.url,
        status: '',
        redirectedTo: '',
        ms: Date.now() - started,
        error: error.name === 'AbortError' ? 'timeout' : String(error.message || error),
      };
    } finally {
      clearTimeout(timer);
    }
  }

  async function worker() {
    while (cursor < unique.length) {
      const row = unique[cursor++];
      results.push(await check(row));
    }
  }

  await Promise.all(Array.from({ length: concurrency }, worker));
  return results;
}

function enrichBookmarks(bookmarkRows, historyIndex) {
  return bookmarkRows.map((row) => {
    const match = historyMatchFor(row.url, historyIndex);
    const historyDate = chromeTimeToDateFromSql(match.row?.last_visit_time);
    const lastUsedCandidates = [row.dateLastUsedBookmark, historyDate].filter(Boolean);
    const lastUsed = lastUsedCandidates.length
      ? new Date(Math.max(...lastUsedCandidates.map((item) => item.getTime())))
      : null;
    const enriched = {
      ...row,
      host: hostOf(row.url),
      historyVisitCount: match.row?.visit_count || 0,
      historyMatchPrecision: match.precision,
      lastUsed,
      lastUsedDays: daysSince(lastUsed),
      lastUsedSource: row.dateLastUsedBookmark && (!historyDate || row.dateLastUsedBookmark > historyDate)
        ? 'bookmark_date_last_used'
        : historyDate
          ? `history_${match.precision}`
          : 'none',
    };
    const classification = classify(enriched);
    return {
      ...enriched,
      categories: classification.categories,
      reasons: classification.reasons,
    };
  });
}

function writeCsv(filePath, rows) {
  const headers = [
    'name',
    'url',
    'host',
    'path',
    'date_added',
    'last_used',
    'last_used_days',
    'last_used_source',
    'history_visit_count',
    'history_match_precision',
    'categories',
    'reasons',
    'live_status',
    'live_error',
    'live_redirect',
  ];
  const lines = [headers.join(',')];
  for (const row of rows) {
    lines.push(headers.map((header) => {
      const value = {
        date_added: formatDate(row.dateAdded),
        last_used: formatDate(row.lastUsed),
        last_used_days: row.lastUsedDays ?? '',
        last_used_source: row.lastUsedSource,
        history_visit_count: row.historyVisitCount,
        history_match_precision: row.historyMatchPrecision,
        categories: row.categories.join('|'),
        reasons: row.reasons.join('|'),
        live_status: row.live?.status ?? '',
        live_error: row.live?.error ?? '',
        live_redirect: row.live?.redirectedTo ?? '',
      }[header] ?? row[header] ?? '';
      return csvEscape(value);
    }).join(','));
  }
  fs.writeFileSync(filePath, `${lines.join('\n')}\n`);
}

function writeLiveCsv(filePath, rows) {
  const headers = ['url', 'status', 'error', 'redirectedTo', 'ms'];
  const lines = [headers.join(',')];
  for (const row of rows) {
    lines.push(headers.map((header) => csvEscape(row[header] ?? '')).join(','));
  }
  fs.writeFileSync(filePath, `${lines.join('\n')}\n`);
}

function topRows(rows, predicate, limit = 30) {
  return rows
    .filter(predicate)
    .sort((a, b) => {
      if (!a.lastUsed && !b.lastUsed) return a.host.localeCompare(b.host);
      if (!a.lastUsed) return -1;
      if (!b.lastUsed) return 1;
      return a.lastUsed - b.lastUsed;
    })
    .slice(0, limit);
}

function bulletRows(rows) {
  if (!rows.length) return ['- 无'];
  return rows.map((row) => {
    const last = row.lastUsed ? `${formatDate(row.lastUsed)}，${row.lastUsedDays} 天前` : '无访问证据';
    return `- ${row.name || '(空标题)'} | ${row.host} | ${last} | ${row.reasons.join('；')} | ${row.url}`;
  });
}

function countBy(rows, category) {
  return rows.filter((row) => row.categories.includes(category)).length;
}

function writeReport(rows, liveRan) {
  const reportPath = path.join(outputDir, 'audit_report.md');
  const lines = [];
  const noEvidence = countBy(rows, 'no_recent_visit_evidence');
  const notUsed1y = countBy(rows, 'not_used_1y') + countBy(rows, 'not_used_2y');
  const former = countBy(rows, 'former_company_candidate');
  const volatile = countBy(rows, 'volatile_link');
  const risky = countBy(rows, 'risky_or_volatile_content');
  const plainHttp = countBy(rows, 'plain_http');
  const dated = countBy(rows, 'dated_content_candidate');

  lines.push('# Chrome Bookmark Audit Report');
  lines.push('');
  lines.push(`Generated: ${new Date().toISOString()}`);
  lines.push('');
  lines.push('## Summary');
  lines.push('');
  lines.push(`- Total bookmarks: ${rows.length}`);
  lines.push(`- No visit evidence in bookmark metadata or History: ${noEvidence}`);
  lines.push(`- Last used over 1 year ago: ${notUsed1y}`);
  lines.push(`- Former-company / old-work domain candidates: ${former}`);
  lines.push(`- Volatile auth/test-env links: ${volatile}`);
  lines.push(`- Dated title/path candidates: ${dated}`);
  lines.push(`- Risky or volatile resource/mirror candidates: ${risky}`);
  lines.push(`- Plain HTTP links: ${plainHttp}`);
  lines.push(`- Live accessibility check: ${liveRan ? 'ran with no-cookie HEAD requests' : 'not run'}`);
  lines.push('');

  if (liveRan) {
    const networkBad = rows.filter((row) => row.live && row.live.error);
    const hardHttp = rows.filter((row) => row.live && [404, 410, 451].includes(Number(row.live.status)));
    const authOrForbidden = rows.filter((row) => row.live && [401, 403].includes(Number(row.live.status)));
    lines.push('## Live Check Summary');
    lines.push('');
    lines.push(`- Network error or timeout: ${networkBad.length}`);
    lines.push(`- HTTP 404/410/451: ${hardHttp.length}`);
    lines.push(`- HTTP 401/403: ${authOrForbidden.length}`);
    lines.push('');
    lines.push('### Network Error / Timeout');
    lines.push('');
    lines.push(...bulletRows(networkBad.slice(0, 40)));
    lines.push('');
    lines.push('### HTTP 404/410/451');
    lines.push('');
    lines.push(...bulletRows(hardHttp.slice(0, 40)));
    lines.push('');
  }

  lines.push('## Old Or Unused Candidates');
  lines.push('');
  lines.push(...bulletRows(topRows(rows, (row) => row.categories.includes('not_used_2y') || row.categories.includes('not_used_1y'), 40)));
  lines.push('');
  lines.push('## No Visit Evidence');
  lines.push('');
  lines.push('这里表示当前 Chrome 书签字段和当前 History 快照都没有访问记录。它更像清理候选，不等同于从未打开过。');
  lines.push('');
  lines.push(...bulletRows(topRows(rows, (row) => row.categories.includes('no_recent_visit_evidence'), 40)));
  lines.push('');
  lines.push('## Former Company / Old Work Candidates');
  lines.push('');
  lines.push(...bulletRows(topRows(rows, (row) => row.categories.includes('former_company_candidate'), 80)));
  lines.push('');
  lines.push('## Volatile Auth Or Test Env Links');
  lines.push('');
  lines.push(...bulletRows(topRows(rows, (row) => row.categories.includes('volatile_link'), 60)));
  lines.push('');
  lines.push('## Risky Or Volatile Resource Links');
  lines.push('');
  lines.push(...bulletRows(topRows(rows, (row) => row.categories.includes('risky_or_volatile_content'), 60)));
  lines.push('');
  lines.push('## Plain HTTP Links');
  lines.push('');
  lines.push(...bulletRows(topRows(rows, (row) => row.categories.includes('plain_http'), 60)));
  fs.writeFileSync(reportPath, `${lines.join('\n')}\n`);
  return reportPath;
}

async function main() {
  ensureDirs();
  const checkLiveEnabled = process.argv.includes('--check-live');
  const bookmarks = JSON.parse(fs.readFileSync(bookmarksPath, 'utf8'));
  const bookmarkRows = collectBookmarks(bookmarks);
  copyHistorySnapshot();
  const historyRows = loadHistoryRows();
  const historyIndex = buildHistoryIndex(historyRows);
  let rows = enrichBookmarks(bookmarkRows, historyIndex);

  if (checkLiveEnabled) {
    const liveResults = await checkLive(rows);
    const liveByUrl = new Map(liveResults.map((item) => [item.url, item]));
    rows = rows.map((row) => ({ ...row, live: liveByUrl.get(row.url) }));
    writeLiveCsv(path.join(outputDir, 'live_check.csv'), liveResults);
  }

  rows.sort((a, b) => {
    if (!a.lastUsed && !b.lastUsed) return a.host.localeCompare(b.host);
    if (!a.lastUsed) return -1;
    if (!b.lastUsed) return 1;
    return a.lastUsed - b.lastUsed;
  });

  const csvPath = path.join(outputDir, 'audit_items.csv');
  writeCsv(csvPath, rows);
  const reportPath = writeReport(rows, checkLiveEnabled);

  console.log(JSON.stringify({
    bookmarks: bookmarkRows.length,
    historyRows: historyRows.length,
    report: reportPath,
    csv: csvPath,
    liveCheck: checkLiveEnabled ? path.join(outputDir, 'live_check.csv') : null,
    noVisitEvidence: countBy(rows, 'no_recent_visit_evidence'),
    notUsedOver1Year: countBy(rows, 'not_used_1y') + countBy(rows, 'not_used_2y'),
    formerCompanyCandidates: countBy(rows, 'former_company_candidate'),
    volatileLinks: countBy(rows, 'volatile_link'),
    riskyOrVolatileContent: countBy(rows, 'risky_or_volatile_content'),
    plainHttp: countBy(rows, 'plain_http'),
  }, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
