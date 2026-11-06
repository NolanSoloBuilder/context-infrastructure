import http from 'node:http';import fs from 'node:fs';
import {renderPage} from '../../../../../adhoc_jobs/us_market_site/worker/render.mjs';
const root='adhoc_jobs/us_market_site/worker/';
const server=http.createServer(async(req,res)=>{try{
 const state=JSON.parse(fs.readFileSync(root+'seed.json','utf8'));state.daily_brief=JSON.parse(fs.readFileSync(root+'daily-brief.json','utf8'));
 if(req.url==='/'){res.writeHead(200,{'Content-Type':'text/html; charset=utf-8'});res.end(renderPage(state));}
 else if(req.url.startsWith('/api/state')){res.writeHead(200,{'Content-Type':'application/json'});res.end(JSON.stringify(state));}
 else if(req.url.startsWith('/api/history')){res.writeHead(200,{'Content-Type':'application/json'});res.end(JSON.stringify({dates:[],snapshots:[]}));}
 else if(req.url==='/api/status'){res.writeHead(200,{'Content-Type':'application/json'});res.end(JSON.stringify(state.refresh_status));}
 else {res.writeHead(503,{'Content-Type':'application/json'});res.end(JSON.stringify({error:'本地仅作布局预览；刷新与历史在生产站点验收。'}));}
 }catch(e){res.writeHead(500);res.end(e.message);}});
server.listen(8874,'127.0.0.1',()=>console.log('Local: http://127.0.0.1:8874/'));
