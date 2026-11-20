import {createHash, randomUUID} from 'node:crypto';
import {existsSync, readFileSync} from 'node:fs';
import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';
import {join} from 'node:path';
import {analysisFor} from '../bazi/names.mjs';
import {InputError, parseBirth} from '../bazi/calendar.mjs';
import {lookupNamingCandidate, listNamingFavorites, clearNamingHistory} from './naming.mjs';

const library = JSON.parse(readFileSync(new URL('../data/original-public-library.json', import.meta.url), 'utf8'));
const characters = new Map(library.characters.map(row => [row.character, row]));
export function initAccounts(db) {
  db.exec(`
    CREATE TABLE IF NOT EXISTS local_site_accounts (
      session TEXT PRIMARY KEY, token TEXT NOT NULL, created TEXT NOT NULL, vip_expires TEXT
    );
    CREATE TABLE IF NOT EXISTS local_site_favorites (
      session TEXT NOT NULL, kind TEXT NOT NULL, target TEXT NOT NULL, data TEXT NOT NULL, created TEXT NOT NULL,
      PRIMARY KEY(session,kind,target)
    );
    CREATE TABLE IF NOT EXISTS local_site_orders (
      order_no TEXT PRIMARY KEY, session TEXT NOT NULL, type TEXT NOT NULL, name TEXT NOT NULL,
      price REAL NOT NULL, status INTEGER NOT NULL, history_id TEXT, created TEXT NOT NULL, paid_at TEXT
    );
    CREATE INDEX IF NOT EXISTS local_site_orders_session ON local_site_orders(session,created DESC);
    CREATE TABLE IF NOT EXISTS local_site_coupons (
      session TEXT NOT NULL, coupon_id INTEGER NOT NULL, claimed TEXT NOT NULL, status INTEGER NOT NULL,
      PRIMARY KEY(session,coupon_id)
    );
    CREATE TABLE IF NOT EXISTS local_site_redeems (
      session TEXT NOT NULL, code TEXT NOT NULL, redeemed TEXT NOT NULL,
      PRIMARY KEY(session,code)
    );
    CREATE TABLE IF NOT EXISTS local_site_reports (
      id TEXT PRIMARY KEY, session TEXT NOT NULL, fingerprint TEXT NOT NULL, full_name TEXT NOT NULL,
      report_type TEXT NOT NULL, data TEXT NOT NULL, created TEXT NOT NULL, UNIQUE(session,fingerprint)
    );
  `);
}

const now = () => new Date().toISOString();
function exists(db, table) {
  return db?.prepare("SELECT 1 FROM sqlite_schema WHERE type='table' AND name=?").get(table);
}
function page(query, rows) {
  const p = Math.max(1, Math.floor(Number(query.get('page')) || 1));
  const size = Math.min(100, Math.max(1, Math.floor(Number(query.get('page_size') ?? query.get('pageSize')) || 20)));
  return {total: rows.length, items: rows.slice((p - 1) * size, p * size), page: p, page_size: size};
}
function ensureAccount({db,session}) {
  db.prepare('INSERT OR IGNORE INTO local_site_accounts VALUES (?,?,?,NULL)').run(session, randomUUID(), now());
  return db.prepare('SELECT * FROM local_site_accounts WHERE session=?').get(session);
}
function makeUser(ctx) {
  const row = ensureAccount(ctx);
  const id = parseInt(createHash('sha256').update(ctx.session).digest('hex').slice(0, 9), 16);
  return {
    id, nickname: '本地设备', avatar: '', phone: '', has_bindPhone: false, has_openid: false,
    is_local_device: true, is_vip: false, is_unlimited: true,
    vip_expires_at: null, created_at: row.created, free_count: 60, name_quota: 60,
    paid_count: 0, remaining_count: 60
  };
}
function orderView(order) {
  return {
    order_no: order.order_no, package_type: order.type, package_name: order.name,
    title: order.name, remark: order.name + ' · 本地演示', amount: order.price, total_amount: order.price, pay_amount: order.price, price: order.price,
    status: order.status, paid: order.status === 1, pay_status: ({0:'unpaid',1:'paid',2:'cancelled'})[order.status],
    created_at: order.created, paid_at: order.paid_at, naming_history_id: order.history_id, is_demo: true
  };
}
function getOrder(ctx, orderNo) {
  const result = ctx.db.prepare('SELECT * FROM local_site_orders WHERE session=? AND order_no=?').get(ctx.session, String(orderNo ?? ''));
  if (!result) ctx.fail(404, '找不到该本地订单', 404);
  return result;
}
function getBaziRecord(ctx, id) {
  if (!exists(ctx.baziDb, 'bazi_history')) return null;
  const row = ctx.baziDb.prepare('SELECT data FROM bazi_history WHERE session=? AND id=?').get(ctx.session, id);
  return row ? JSON.parse(row.data) : null;
}
function getBaziName(ctx, id) {
  const match = /^([a-f0-9-]{36}):(\d+)$/.exec(String(id ?? ''));
  const record = match && getBaziRecord(ctx, match[1]);
  const result = record?.names?.[Number(match?.[2])];
  if (!result) return null;
  const {birthDate,time,gender} = record.birth;
  const birth_time = time === 'unknown' ? birthDate : birthDate + 'T' + time;
  return {...result,id,history_id:record.id,gender,birth_time,analysis:record.analysis};
}
function baziFavorites(ctx) {
  if (!exists(ctx.baziDb, 'favorites')) return [];
  return ctx.baziDb.prepare('SELECT kind,target FROM favorites WHERE session=?').all(ctx.session).flatMap(({kind,target}) => {
    if (kind === 'name') {
      const info = getBaziName(ctx, target);
      if (!info) return [];
      const {gender, surname, pinyin, full_name, wuxing, score, history_id} = info;
      return [{id: 'name:' + target, name_id: target, type: 'name', full_name, surname, pinyin, wuxing, score,
        gender: gender === 'male' ? '男' : '女', history_id, from: 'bazi-naming'}];
    }
    const row = characters.get(target);
    return row ? [{id: 'char:' + target, type: 'character', char_info: row, from: 'bazi-naming'}] : [];
  });
}
function listFavorites(ctx, query) {
  const merged = new Map();
  function add(row) {
    if (!row) return;
    const key = row.type === 'character' ? 'char:' + row.char_info?.character : 'name:' + row.name_id;
    if (!merged.has(key)) merged.set(key, row);
  }
  const saved = ctx.db.prepare('SELECT data,created FROM local_site_favorites WHERE session=? ORDER BY created DESC').all(ctx.session);
  saved.forEach(row => add({...JSON.parse(row.data), created_at: row.created}));
  baziFavorites(ctx).forEach(add);
  if (exists(ctx.db, 'local_naming_favorites')) listNamingFavorites(ctx.db, ctx.session).forEach(add);
  const selected = query.get('type');
  return page(query, [...merged.values()].filter(item => !selected || item.type === selected));
}

function csvCell(value) {
  const text = String(value ?? '').replace(/^(?=\s*[=+@\-])/,"'");
  return '"' + text.replaceAll('"','""') + '"';
}
const materials = [
  {code: 'characters', name: '起名用字字典.csv', desc: '含拼音、五行、笔画和用字寓意', type: 'text/csv; charset=utf-8',
    render: () => '\uFEFF字符,拼音,五行,笔画,寓意\r\n' + library.characters
      .map(r => [r.character,r.pinyin,r.wuxing,r.strokes,r.nameConnotation].map(csvCell).join(',')).join('\r\n')},
  {code: 'popular', name: '公开热门姓名.csv', desc: '供重名与名字风格参考', type: 'text/csv; charset=utf-8',
    render: () => '\uFEFF名字\r\n' + library.popularNames.map(r => csvCell(typeof r === 'string' ? r : r.name || r.full_name)).join('\r\n')},
  {code: 'guide', name: '起名核对清单.txt', desc: '用字、读音、谐音与出处核对方法', type: 'text/plain; charset=utf-8',
    render: () => [
      '起名核对清单', '1. 和姓氏连读，确认普通话及常用方言读音。', '2. 查字典并确认多音、异体和生僻字的登记风险。',
      '3. 有古籍出处时，逐句查原文，理解上下文。', '4. 区分本地匹配分与真实人口登记数据。',
      '5. 用带姓氏的完整姓名检查缩写、谐音和书写体验。', '含五行、笔画的内容可作民俗文化参考。'
    ].join('\r\n')}
];
function metadata(item) {
  const bytes = Buffer.byteLength(item.render());
  return {code: item.code, name: item.name, desc: item.desc, description: item.desc, file_name: item.name,
    size: bytes, size_text: Math.max(1, Math.ceil(bytes / 1024)) + ' KB'};
}
function download(ctx, res, fileName, type, data) {
  const body = Buffer.from(data);
  res.writeHead(200, {'Content-Type': type, 'Content-Length': body.length,
    'Content-Disposition': `attachment; filename*=UTF-8''${encodeURIComponent(fileName)}`,
    'X-Content-Type-Options': 'nosniff', 'Cache-Control': 'private, no-store'});
  res.end(body);
  return ctx.sent;
}

function normalizedCharacter(row, literal) {
  return {
    char: row?.char || row?.character || literal,
    pinyin: row?.pinyin || '未收录',
    wuxing: row?.wuxing || '未收录',
    strokes: row?.strokes ?? null,
    meaning: row?.meaning || row?.nameConnotation || '字义请查权威字典。',
    name_meaning: row?.meaning || row?.nameConnotation || '字义请查权威字典。'
  };
}
function candidateFrom(ctx, input) {
  const id = input.name_id;
  return id != null ? getBaziName(ctx, id) || (exists(ctx.db, 'local_naming_sessions') ?
    lookupNamingCandidate(ctx.db, ctx.session, id) : null) : null;
}
function reportData(ctx, input) {
  const result = candidateFrom(ctx, input);
  if (input.name_id && !result) ctx.fail(404, '当前设备找不到这个姓名结果', 404);
  const surname = String(result?.surname || input.surname || '').trim();
  const given = String(result?.given_name || result?.name || input.name || '').trim();
  const name = result?.full_name || surname + given;
  if (!/^\p{Script=Han}{1,2}$/u.test(surname) || !/^\p{Script=Han}{1,3}$/u.test(given) ||
      !/^\p{Script=Han}{2,5}$/u.test(name)) {
    ctx.fail(1001, '请选择有效的姓名');
  }
  const stamp = /^(\d{4}-\d{2}-\d{2})(?:[T ](\d{2}:\d{2}))?/.exec(result?.birth_time ?? '');
  const birthDate = input.birth_date || stamp?.[1] || '';
  const birthHour = input.birth_hour || stamp?.[2] || 'unknown';
  const gender = ['female','女','2'].includes(String(input.gender || result?.gender)) ? 'female' : 'male';
  const context = result?.analysis || (() => {
    if (!birthDate) return null;
    try {
      return analysisFor(parseBirth({surname, gender, birthDate, birthTime: birthHour}));
    } catch (error) {
      if (!(error instanceof InputError)) throw error;
      return null;
    }
  })();
  const rows = Array.from(given).map((ch,index) => normalizedCharacter(
    result?.characters?.[index] || result?.givenChars?.[index] || characters.get(ch), ch
  ));
  const source = result?.source?.title ? result.source : result?.poem?.has_poem ?
    {title: result.poem.source, poem: result.poem.verse, author: result.poem.author, dynasty: result.poem.dynasty} : null;
  const plainMeaning = result?.overall_meaning || (typeof result?.meaning === 'string' ? result.meaning :
    (result?.meaning?.detail || result?.meaning?.brief || ''));
  const summary = rows.map(row => `${row.char}：${row.meaning}`).join('；');
  const strokes = rows.map(row => row.strokes);
  const hasStrokes = strokes.every(Number.isFinite);
  const paipan = context?.bazi ? {
    has_bazi: true, pillars: context.bazi, baziString: context.bazi_str, bazi_str: context.bazi_str,
    kongwang: context.kongwang, changsheng: context.changsheng
  } : null;
  return {
    fullName: name, historyId: String(result?.history_id ?? input.history_id ?? ''), score: Number(result?.score?.total ?? result?.score) || 0,
    surnameInfo: {surname, pinyin: Array.from(surname).map(ch => characters.get(ch)?.pinyin).filter(Boolean).join(' '), figures: []},
    personalInfo: context ? {
      birth_date: birthDate,
      lunar_date: context.lunar ? `${context.lunar.monthCn || ''}${context.lunar.dayCn || ''}` : '',
      birth_hour: birthHour === 'unknown' ? '不清楚' : birthHour, gender: gender === 'male' ? '男' : '女', zodiac: context.zodiac?.name || ''
    } : null,
    charAnalysis: rows,
    source,
    sourceAnalysis: plainMeaning,
    baziPaipan: paipan,
    wuxingAnalysis: {
      has_bazi: !!context?.bazi, lack: context?.wuxing?.lack || [],
      wuxing_count: context?.wuxingWithCangGan, yongshen: context?.yong_shen_detail,
      analysis: context?.yong_shen_detail?.description, name_wuxing: rows.map(row => row.wuxing).join('、')
    },
    yinyunAnalysis: {chars: rows, summary: '请结合姓氏、家庭语音习惯和方言连读实际核对。'},
    shapeAnalysis: hasStrokes ? {chars: rows, total_strokes_simplified: strokes.reduce((a,b) => a+b,0)} : null,
    suggestion: plainMeaning || summary,
    disclaimer: '本地报告基于公开字库及传统民俗用字规则。未收录的资料不作推断。'
  };
}
function reportUrl(type, id) {
  return `/api/v1/report/${type === 'culture' ? 'culture/' : ''}download/${id}`;
}
function reportMeta(row) {
  return {
    report_id: row.id, full_name: row.full_name, report_type: row.report_type,
    status: 'completed', progress: 100, created_at: row.created,
    download_url: reportUrl(row.report_type, row.id), is_generated_locally: true
  };
}
function getReport(ctx, id) {
  const row = ctx.db.prepare('SELECT * FROM local_site_reports WHERE session=? AND id=?').get(ctx.session, id);
  if (!row) ctx.fail(404, '找不到本地报告', 404);
  return row;
}
function findReport(ctx, query) {
  const fullName = String(query.surname || '') + String(query.name || '');
  const identity = String(query.history_id ?? '');
  return ctx.db.prepare(`SELECT * FROM local_site_reports WHERE session=? AND full_name=? AND report_type='culture'
    AND (?='' OR json_extract(data,'$.historyId')=?) ORDER BY created DESC LIMIT 1`)
    .get(ctx.session, fullName, identity, identity);
}
function createReport(ctx, input) {
  const data = reportData(ctx, input);
  const fingerprint = createHash('sha256').update(JSON.stringify([
    data.fullName, input.name_id ?? '', input.history_id ?? '', input.birth_date ?? '', input.birth_hour ?? '', input.gender ?? ''
  ])).digest('hex');
  const id = randomUUID();
  ctx.db.prepare('INSERT OR IGNORE INTO local_site_reports VALUES (?,?,?,?,?,?,?)').run(
    id, ctx.session, fingerprint, data.fullName, 'culture', JSON.stringify(data), now()
  );
  const row = ctx.db.prepare('SELECT * FROM local_site_reports WHERE session=? AND fingerprint=?').get(ctx.session, fingerprint);
  return {...reportMeta(row), exists: id !== row.id, use_quota: true, message: '本地报告已生成'};
}
const localRequire = createRequire(import.meta.url);
let PDFDocument;
function pdfConstructor() {
  if (PDFDocument) return PDFDocument;
  try {
    PDFDocument = localRequire('pdfkit');
  } catch (error) {
    if (error.code !== 'MODULE_NOT_FOUND') throw error;
    const root = execFileSync('npm', ['root','-g'], {encoding:'utf8', timeout:4000}).trim();
    PDFDocument = localRequire(join(root,'pdfkit'));
  }
  return PDFDocument;
}
function reportFont(ctx) {
  const configured = process.env.QINGZHU_PDF_FONT;
  const defaults = [
    ['/System/Library/Fonts/Supplemental/Songti.ttc','STSongti-SC-Regular'],
    ['/System/Library/Fonts/STHeiti Light.ttc','STHeitiSC-Light'],
    ['/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc','NotoSansCJKsc-Regular'],
    ['/usr/share/fonts/opentype/noto/NotoSansCJKsc-Regular.otf', null]
  ];
  const selected = [ ...(configured ? [[configured,process.env.QINGZHU_PDF_FONT_FAMILY]] : []), ...defaults ]
    .find(([filename]) => existsSync(filename));
  if (!selected) ctx.fail(503, '生成报告需要安装中文字体，或设置 QINGZHU_PDF_FONT', 503);
  return selected;
}
async function pdfContent(ctx, report) {
  let Document;
  try {
    Document = pdfConstructor();
  } catch {
    ctx.fail(503, '生成报告需要全局 PDFKit，可运行 npm install -g pdfkit', 503);
  }
  const font = reportFont(ctx);
  const document = new Document({size:'A4', margin:48, font:'Helvetica', pdfVersion:'1.4',
    info:{Title:'姓名文化解读报告', Author:'清言字舍'}});
  const [file,family] = font;
  document.font(file,family || undefined);
  const chunks = [];
  const finished = new Promise((resolve,reject) => {
    document.on('data', chunk => chunks.push(chunk));
    document.on('end', () => resolve(Buffer.concat(chunks)));
    document.on('error', reject);
  });
  document.fillColor('#334f41').fontSize(20).text('姓名文化解读报告');
  document.moveDown(.4).fillColor('#243026').fontSize(15).text(report.fullName);
  document.moveDown().fontSize(11);
  if (report.source) {
    document.text('古籍出处');
    document.text([report.source.title,report.source.author,report.source.dynasty].filter(Boolean).join(' · '));
    if (report.source.poem) document.text(report.source.poem, {lineGap:4});
    document.moveDown();
  }
  document.text('单字解读');
  for (const char of report.charAnalysis) {
    document.text(`${char.char}（${char.pinyin}）  五行：${char.wuxing}${char.strokes?'  笔画：'+char.strokes:''}`);
    document.text(char.meaning, {lineGap:4}).moveDown(.3);
  }
  if (report.baziPaipan) {
    document.moveDown(.4).text('传统排盘');
    document.text(report.baziPaipan.bazi_str);
    if (report.wuxingAnalysis?.analysis) document.text(report.wuxingAnalysis.analysis,{lineGap:4});
  }
  document.moveDown().text('选名参考').text(report.suggestion, {lineGap:4});
  document.moveDown().fontSize(9).fillColor('#59675c').text(report.disclaimer, {lineGap:4});
  document.end();
  return finished;
}

export async function handleAccount(req, res, url, ctx) {
  const path = decodeURIComponent(url.pathname).replace(/^\/api\/v1/, '');
  const route = req.method + ' ' + path;
  const query = url.searchParams;
  const retiredCheckout = /^\/payment(?:\/|$)/.test(path) && !/^GET \/payment\/order\//.test(route);
  const retiredRedemption = path==='/users/redeem' || /^\/coupons\/[^/]+\/claim$/.test(path);
  if (retiredCheckout || retiredRedemption || ['/materials/create-order','/tools/unlock/create-order'].includes(path)) {
    return ctx.fail(410,'清言字舍免费开放，无需付费或兑换',410);
  }
  switch (route) {
    case 'POST /users/login/device': return {token: ensureAccount(ctx).token, user: makeUser(ctx)};
    case 'GET /users/me': return makeUser(ctx);
    case 'POST /users/logout': return {logged_out: true};
    case 'GET /users/quota': return {
      name_quota: 60, name_used: 0, name_remaining: 60, free_count: 60, paid_count: 0,
      free_quota: 60, is_unlimited: true, is_local_device: true
    };
    case 'GET /users/bonus-rewards': return {has_pending: false, pending_total: 0, items: []};
    case 'GET /coupons': return [];
    case 'GET /coupons/mine': return page(query, []);
    case 'GET /naming/favorites': return listFavorites(ctx, query);
    case 'DELETE /naming/history': {
      const removed = exists(ctx.db, 'local_naming_sessions') ? clearNamingHistory(ctx.db, ctx.session) : 0;
      return typeof removed === 'object' ? removed : {deleted_count: Number(removed || 0)};
    }
    case 'GET /tools/unlock/status': {
      const access = {unlocked: true, price: 0, original_price: 0};
      return {
        ...access, is_unlocked: true, isUnlocked: true, has_access: true,
        nickname: access, english_name: access, chinese_name: access, parents_naming: access
      };
    }
    case 'GET /packages':
    case 'GET /packages/list': return [];
    case 'GET /orders': {
      const filter = query.get('status');
      const all = ctx.db.prepare('SELECT * FROM local_site_orders WHERE session=? ORDER BY created DESC,order_no DESC').all(ctx.session);
      return page(query, all.filter(order => filter === null || Number(filter) === order.status).map(orderView));
    }
    case 'POST /users/login/sms/code':
    case 'POST /users/login/sms':
    case 'GET /users/login/wechat/url':
    case 'POST /users/login/wechat':
    case 'POST /users/bindPhone':
    case 'POST /users/bindWechat':
    case 'POST /wechat/jssdk-signature':
    case 'GET /wechat/jssdk-signature':
      ctx.fail(1001, '本地版使用当前设备，无需手机或微信登录');
      break;
    case 'GET /materials/check': return {unlocked: true, is_unlocked: true, package_level_name: '本地资料包'};
    case 'GET /materials/list': {
      const files = materials.map(metadata);
      return {unlocked: true, package_level_name: '本地资料包', total_size_text: Math.ceil(files.reduce((n,f)=>n+f.size,0)/1024) + ' KB',
        price: 0, original_price: 0, files};
    }
    case 'GET /naming/report/quota': return {remaining_quota: -1, used_quota: 0, total_quota: -1, report_price: 0};
    case 'GET /naming/report': return reportData(ctx, Object.fromEntries(query));
    case 'GET /naming/report/download': {
      const report = reportData(ctx, Object.fromEntries(query));
      return download(ctx,res,report.fullName + '_简读报告.pdf','application/pdf',await pdfContent(ctx, report));
    }
    case 'GET /report/my-reports': return ctx.db.prepare('SELECT * FROM local_site_reports WHERE session=? ORDER BY created DESC').all(ctx.session).map(reportMeta);
    case 'GET /report/culture/check': {
      const found = findReport(ctx, Object.fromEntries(query));
      return found ? {...reportMeta(found), exists: true} : {exists: false};
    }
    case 'POST /report/culture/create': return createReport(ctx, await ctx.body());
  }

  let match = /^\/payment\/order\/(?:guest\/)?([^/]{1,120})$/.exec(path);
  if (req.method === 'GET' && match) return orderView(getOrder(ctx, match[1]));
  match = /^\/orders\/([^/]{1,120})\/cancel$/.exec(path);
  if (req.method === 'POST' && match) {
    const order = getOrder(ctx,match[1]);
    if (order.status === 1) ctx.fail(409, '已完成的演示订单不能取消');
    ctx.db.prepare('UPDATE local_site_orders SET status=2 WHERE session=? AND order_no=? AND status=0').run(ctx.session,order.order_no);
    return orderView(getOrder(ctx,order.order_no));
  }
  match = /^\/report\/(?:culture\/)?(status|download)\/([a-f0-9-]{36})$/.exec(path);
  if (req.method === 'GET' && match) {
    const row = getReport(ctx, match[2]);
    if (match[1] === 'status') return reportMeta(row);
    return download(ctx,res,row.full_name + '_姓名文化解读报告.pdf','application/pdf',await pdfContent(ctx, JSON.parse(row.data)));
  }
  match = /^\/materials\/(download|file)\/([a-z]+)$/.exec(path);
  if (req.method === 'GET' && match) {
    const item = materials.find(row => row.code === match[2]);
    if (!item) ctx.fail(404, '未找到资料', 404);
    return match[1] === 'download' ? {download_url: '/api/v1/materials/file/' + item.code, file_name: item.name} :
      download(ctx,res,item.name,item.type,item.render());
  }
  return undefined;
}
