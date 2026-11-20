import {createServer} from 'node:http';
import {isIP} from 'node:net';
import {createReadStream, statSync, readFileSync} from 'node:fs';
import {Readable} from 'node:stream';
import {pipeline} from 'node:stream/promises';
import {resolve, extname, sep, join} from 'node:path';
import {fileURLToPath} from 'node:url';

const root = fileURLToPath(new URL('./public', import.meta.url));
const catalog = JSON.parse(readFileSync(new URL('./public-catalog.json', import.meta.url)));
const port = Number(process.env.PORT || 4175);
const publicService = process.env.QINGYAN_PUBLIC === '1';
const aiPath = '/api/v1/naming_ai/generate-stream';
const aiDailyLimit = Number(process.env.QINGYAN_AI_DAILY_LIMIT || 60);
const aiClientLimit = Number(process.env.QINGYAN_AI_CLIENT_DAILY_LIMIT || 5);
if (publicService && [aiDailyLimit, aiClientLimit].some(value => !Number.isSafeInteger(value) || value < 1)) {
  throw new Error('AI 公网额度必须为正整数。');
}
let aiDay = -1;
let aiAccepted = 0;
let aiInFlight = 0;
const aiClients = new Map();

function admitPublicAi(req, res) {
  if (!publicService) return true;
  const day = Math.floor(Date.now() / 86_400_000);
  if (aiDay !== day) {
    aiDay = day;
    aiAccepted = 0;
    aiClients.clear();
  }
  // This listener is loopback-only. The public ingress is the dedicated Cloudflare Tunnel.
  const forwarded = req.headers['cf-connecting-ip'];
  const client = typeof forwarded === 'string' && isIP(forwarded) ? forwarded : req.socket.remoteAddress;
  const used = aiClients.get(client) || 0;
  if (aiAccepted >= aiDailyLimit || used >= aiClientLimit) {
    res.setHeader('Retry-After', Math.ceil(((day + 1) * 86_400_000 - Date.now()) / 1000));
    issue(res,429,'今日 AI 起名额度已用完，请明天再试。');
    return false;
  }
  if (aiInFlight >= 2) {
    res.setHeader('Retry-After', 30);
    issue(res,429,'已有起名任务正在生成，请稍后再试。');
    return false;
  }
  aiAccepted++;
  aiClients.set(client, used + 1);
  aiInFlight++;
  res.once('close', () => { aiInFlight--; });
  return true;
}

const upstream = process.env.QINGZHU_API_ORIGIN ? new URL(process.env.QINGZHU_API_ORIGIN) : null;
if (upstream && (upstream.pathname !== '/' || upstream.search || upstream.hash ||
    upstream.username || upstream.password || (upstream.protocol !== 'https:' &&
    !(upstream.protocol === 'http:' && ['localhost', '127.0.0.1', '[::1]'].includes(upstream.hostname))))) {
  throw new Error('QINGZHU_API_ORIGIN 必须是 HTTPS 源地址（本机联调可用 HTTP）。');
}
const localBazi = upstream ? null : (await import('./bazi/api.mjs')).createBaziApi();
const {createLocalApi,localSession} = upstream ? {} : await import('./local/api.mjs');
const localApi = await createLocalApi?.();
const index = readFileSync(join(root, 'index.html'), 'utf8');
const appPage = Buffer.from(localBazi ? index.replace('</head>',
  '    <meta name="qingzhu-local-bazi" content="enabled">\n  </head>') : index);
const removedPage = /^\/(?:manual|rename|contact)(?:\/|$)|^\/offline(?:\/|$)/i;
const manualPackage = /^manual(?:[-_]|$)/i;
const manualAPI = /\/(?:masters|offline|manual(?:[-_][^/]*)?)(?:\/|$)/i;
const mime = {
  '.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8',
  '.css':'text/css; charset=utf-8','.svg':'image/svg+xml','.png':'image/png',
  '.jpg':'image/jpeg','.jpeg':'image/jpeg','.webp':'image/webp',
  '.woff':'font/woff','.woff2':'font/woff2',
};
function json(res, status, value) {
  res.writeHead(status, {'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store'});
  res.end(JSON.stringify(value));
}
function issue(res,status,message) {
  json(res,status,{code:status,message,data:null});
}
async function api(req,res,url,pathname) {
  if (req.method==='POST' && pathname===aiPath && !admitPublicAi(req,res)) return;
  if (manualAPI.test(pathname) || url.searchParams.getAll('type').some(x=>manualPackage.test(x))) {
    issue(res,404,'此服务不可用');
    return;
  }
  if (localApi && await localApi(req,res,url,json)) return;
  if (localBazi && await localBazi(req,res,url,json)) return;
  if (upstream && /^\/api\/v\d+\/(?:payment(?:\/|$)|(?:materials|tools\/unlock)\/create-order$|users\/redeem$|coupons\/[^/]+\/claim$)/.test(pathname)) {
    issue(res,410,'清言字舍免费开放，无需付费或兑换');
    return;
  }
  if (!upstream) {
    const key = url.pathname + url.search;
    const snapshot = Object.hasOwn(catalog,key) && catalog[key];
    // Keep preview lists bounded by the data actually stored on disk.
    const previewList = /^\/api\/v1\/tools\/(?:funny|homophone|popular)-names$/.test(pathname);
    if (req.method === 'GET' && snapshot) {
      json(res,200,previewList ?
        {...snapshot, data:{...snapshot.data,total:snapshot.data.list.length}} : snapshot);
    }
    else issue(res,404,'本地服务没有这个接口');
    return;
  }
  if (!['GET','HEAD','POST','PUT','PATCH','DELETE'].includes(req.method)) {
    issue(res,405,'请求方法不可用');
    return;
  }
  const controller = new AbortController();
  res.once('close',()=>controller.abort());
  const headers = {};
  for (const key of ['accept','content-type','authorization','x-platform']) {
    if (typeof req.headers[key] === 'string') headers[key] = req.headers[key];
  }
  const response = await fetch(upstream.origin + url.pathname + url.search,{
    method:req.method,headers,redirect:'manual',
    ...(!['GET','HEAD'].includes(req.method) ? {body:Readable.toWeb(req),duplex:'half'} : {}),
    signal:AbortSignal.any([AbortSignal.timeout(120_000),controller.signal])
  });
  if (response.status >= 300 && response.status < 400) {
    await response.body?.cancel();
    issue(res,502,'上游请求发生跳转');
    return;
  }
  // Keep SSE/report responses streaming. Do not forward cookies or hop-by-hop headers.
  const outgoing = {'Cache-Control':'no-store'};
  for (const key of ['content-type','content-disposition']) {
    const value=response.headers.get(key);
    if(value) outgoing[key]=value;
  }
  res.writeHead(response.status,outgoing);
  if(response.body) await pipeline(Readable.fromWeb(response.body),res);
  else res.end();
}

createServer(async (req,res)=>{
  try {
    if (!req.url?.startsWith('/') || req.url.startsWith('//')) {
      issue(res,400,'无效请求'); return;
    }
    const url=new URL(req.url,'http://localhost');
    const pathname=decodeURIComponent(url.pathname);
    if(pathname==='/healthz' && req.method==='GET') {
      json(res,200,{ok:true});return;
    }
    if(pathname.startsWith('/api/')) {await api(req,res,url,pathname);return;}
    if(!['GET','HEAD'].includes(req.method)) {issue(res,405,'请求方法不可用');return;}
    if(removedPage.test(pathname)) {
      res.writeHead(302,{Location:'/', 'Cache-Control':'no-store'});res.end();return;
    }
    let file=resolve(root,'.'+pathname);
    if(file!==root && !file.startsWith(root+sep)) {issue(res,404,'未找到');return;}
    let stat=statSync(file,{throwIfNoEntry:false});
    if(!stat?.isFile()) {
      if(extname(pathname) || /^\/(?:assets|images)\//.test(pathname)) {issue(res,404,'未找到');return;}
      file=join(root,'index.html');
      stat=statSync(file);
    }
    if(file===join(root,'index.html')) {
      localSession?.(req,res);
      res.writeHead(200,{'Content-Type':mime['.html'],'Content-Length':appPage.length,
        'Cache-Control':'no-cache','Referrer-Policy':'same-origin','X-Content-Type-Options':'nosniff'});
      res.end(req.method==='HEAD' ? undefined : appPage);
      return;
    }
    res.writeHead(200, {'Content-Type':mime[extname(file)]??'application/octet-stream',
      'Content-Length':stat.size,'Cache-Control':'no-cache','X-Content-Type-Options':'nosniff'});
    if(req.method==='HEAD')res.end();
    else await pipeline(createReadStream(file),res);
  } catch {
    if(!res.headersSent && !res.destroyed) issue(res,502,'请求失败，请重试');
    else if(!res.destroyed) res.destroy();
  }
}).listen(port,'127.0.0.1',function () {
  console.log(`清言字舍 http://127.0.0.1:${this.address().port}/`);
  console.log(upstream ? `API 将发往 ${upstream.origin}` : '自助工具使用本地后端。');
});
