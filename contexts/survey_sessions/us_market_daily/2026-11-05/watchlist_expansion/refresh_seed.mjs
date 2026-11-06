import fs from 'node:fs';
import {refreshState} from '../../../../../adhoc_jobs/us_market_site/worker/engine.mjs';
const base=new URL('./',import.meta.url), path='adhoc_jobs/us_market_site/worker/seed.json';
const seed=JSON.parse(fs.readFileSync(path,'utf8')),collection=JSON.parse(fs.readFileSync(new URL('market_collection.json',base),'utf8'));
const rows=new Map(collection.map(r=>[r.symbol,r]));
const state=await refreshState(seed,async url=>{
 const s=decodeURIComponent(new URL(url).pathname.split('/').at(-1));
 return Response.json(JSON.parse(fs.readFileSync(new URL('market_raw/'+s+'.json',base),'utf8')));
},()=>{},{now:collection[0].captured_at,budgetMs:60000});
for(const a of state.catalog.groups.flatMap(g=>g.assets))if(rows.get(a.symbol)?.status==='ok'&&!a.last_refresh_error){
 const r=rows.get(a.symbol);a.quote.captured_at_utc=r.captured_at;a.quote.crosscheck_status='本次Yahoo完整日线新采集；自动行情为单一提供方，未声称逐项跨源核验。';a.extended.captured_at_utc=r.captured_at;
}
fs.writeFileSync(path,JSON.stringify(state,null,2)+'\n');
fs.writeFileSync(new URL('metrics_summary.json',base),JSON.stringify({session:state.catalog.regular_session,status:state.refresh_status,assets:state.catalog.groups.flatMap(g=>g.assets).map(a=>({symbol:a.symbol,close:a.quote?.close,session:a.quote?.session,period:state.risk_metrics.symbols[a.symbol]?.chart_ranges?.['1y']?.label,ma200:state.risk_metrics.symbols[a.symbol]?.ma200,error:a.last_refresh_error}))},null,2)+'\n');
console.log(state.catalog.regular_session,state.refresh_status.message);
