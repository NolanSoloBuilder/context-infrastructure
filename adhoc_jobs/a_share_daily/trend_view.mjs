/** Pure price-series calculations and responsive chart markup; no quote fetching. */
const trendEscape=v=>String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#39;');
const trendPct=v=>Number.isFinite(v)?`${v>=0?'+':''}${v.toFixed(2)}%`:'—';
export function trendRange(asset,period='3y'){
 const all=asset.points||[];if(all.length<2)return null;
 const end=all.at(-1).date;
 let start=0,complete=true;
 if(period==='20d'){start=Math.max(0,all.length-21);complete=all.length>=21;}
 else {
  const years={'1y':1,'2y':2,'3y':3}[period]||1;
  const d=new Date(end+'T00:00:00Z'),month=d.getUTCMonth();d.setUTCFullYear(d.getUTCFullYear()-years);if(d.getUTCMonth()!==month)d.setUTCDate(0);
  const cutoff=d.toISOString().slice(0,10);start=all.findLastIndex(p=>p.date<=cutoff);complete=start>=0;start=Math.max(0,start);
 }
 const points=all.slice(start),returns=points.slice(1).map((p,i)=>p.close/points[i].close-1);
 let peak=points[0].close,mdd=0;
 for(const p of points){peak=Math.max(peak,p.close);mdd=Math.min(mdd,p.close/peak-1);}
 const mean=returns.reduce((a,b)=>a+b,0)/returns.length;
 const volatility=returns.length>1?Math.sqrt(returns.reduce((s,r)=>s+(r-mean)**2,0)/(returns.length-1))*Math.sqrt(252)*100:null;
 const high=points.reduce((a,b)=>a.close>b.close?a:b),low=points.reduce((a,b)=>a.close<b.close?a:b);
 return {points,complete,start:points[0].date,end,return_pct:(points.at(-1).close/points[0].close-1)*100,volatility_pct:volatility,mdd_pct:mdd*100,high,low};
}
export function trendDetail(symbol,asset,period='3y',options={ma20:false,ma60:true,extrema:true}){
 const r=trendRange(asset,period);if(!r)return '';
 const esc=trendEscape,label={'20d':'近20交易日','1y':'近一年','2y':'近两年','3y':'近三年'}[period];
 const values=r.points.flatMap(p=>[p.close,...(options.ma20&&Number.isFinite(p.ma20)?[p.ma20]:[]),...(options.ma60&&Number.isFinite(p.ma60)?[p.ma60]:[])]);
 const min=Math.min(...values),max=Math.max(...values),pad=(max-min||max*.02)*.12,lo=Math.max(0,min-pad),hi=max+pad;
 const begin=Date.parse(r.start),duration=Date.parse(r.end)-begin||1;
 const x=d=>60+(Date.parse(d)-begin)/duration*560,y=v=>200-(v-lo)/(hi-lo)*175;
 const line=field=>{let pen=false;return r.points.map(p=>{if(!Number.isFinite(p[field])){pen=false;return '';}const cmd=pen?'L':'M';pen=true;return `${cmd}${x(p.date).toFixed(2)},${y(p[field]).toFixed(2)}`;}).join(' ');};
 const color=r.return_pct>=0?'#176f65':'#b33e3e';
 const path=(field,c,dash='')=>`<path data-series="${field}" fill="none" stroke="${c}" stroke-width="${field==='close'?2.3:1.5}" ${dash?'stroke-dasharray="5 3"':''} d="${line(field)}"/>`;
 const ticks=[lo,(lo+hi)/2,hi].map(v=>`<line x1="60" x2="620" y1="${y(v)}" y2="${y(v)}" stroke="#e5ebe8"/><text x="54" y="${y(v)+4}" text-anchor="end">${v.toFixed(asset.unit==='元'?3:0)}</text>`).join('');
 const latest=asset.points.at(-1);
 const latestMAs=[20,60].map(n=>`<div><dt>MA${n}</dt><dd>${Number.isFinite(latest['ma'+n])?latest['ma'+n].toFixed(asset.unit==='元'?3:2)+' '+trendEscape(asset.unit):'数据不足'}</dd></div><div><dt>距MA${n}</dt><dd>${Number.isFinite(latest['ma'+n])?trendPct((latest.close/latest['ma'+n]-1)*100):'数据不足'}</dd></div>`).join('');
 const valuation=asset.valuation;
 const valuationHtml=valuation?`<details class="trend-research-section" open><summary>本期指数估值观察</summary><div><p>${esc(valuation.index_name)} · ${esc(valuation.asof)} · <span class="valuation-badge valuation-${{'低估':'low','正常':'normal','高估':'high'}[valuation.zone]}">${esc(valuation.zone)}</span></p><p>${[valuation.earnings_yield?'盈利收益率 '+valuation.earnings_yield+'%':'',valuation.pe?'PE '+valuation.pe+'倍':'',valuation.pb?'PB '+valuation.pb+'倍':''].filter(Boolean).join(' · ')} · <a href="${esc(valuation.source_url)}" target="_blank" rel="noopener noreferrer">作者原文↗</a></p><p>这是对应指数的估值分类，不是基金质量评分或自动买入信号。</p></div></details>`:'';
 const source=asset.source.startsWith('https://')?asset.source:'#';
 return `<article class="trend-detail-card" data-trend-symbol="${esc(symbol)}"><header><div><h3>${esc(asset.name)}</h3><small>${esc(asset.code||symbol.slice(2))} · ${esc(asset.market||'A股')} · ${esc(asset.unit)} · ${esc(asset.asof)}收盘</small></div><strong>${r.points.at(-1).close.toFixed(asset.unit==='元'?3:2)}</strong></header><dl class="trend-stats"><div><dt>${r.complete?label:'可用区间'}价格变化</dt><dd class="${r.return_pct>=0?'positive':'negative'}">${trendPct(r.return_pct)}</dd></div><div><dt>年化波动</dt><dd>${Number.isFinite(r.volatility_pct)?r.volatility_pct.toFixed(2)+'%':'—'}</dd></div><div><dt>区间最大回撤</dt><dd class="negative">${trendPct(r.mdd_pct)}</dd></div></dl><p class="trend-period">${r.start} → ${r.end} · ${r.points.length}个收盘${r.complete?'':' · 数据不足所选年限，展示可用历史'}</p><svg class="trend-svg" viewBox="0 0 640 238" tabindex="0" role="img" aria-label="${esc(asset.name)}价格曲线，点按查看日期和价格" data-start="${begin}" data-duration="${duration}" data-y-min="${lo}" data-y-max="${hi}"><title>${esc(asset.name)} · ${r.start}至${r.end} · ${esc(asset.basis)}</title>${ticks}${options.ma60?path('ma60','#7772a4','dash'):''}${options.ma20?path('ma20','#b4862c','dash'):''}${path('close',color)}${options.extrema?[r.high,r.low].map(p=>`<circle cx="${x(p.date)}" cy="${y(p.close)}" r="3.5" fill="${color}"/>`).join(''):''}<g data-trend-cursor hidden><line y1="25" y2="200" stroke="#70847b" stroke-dasharray="3 3"/><circle r="4" fill="${color}"/></g><text x="60" y="226">${r.start}</text><text x="620" y="226" text-anchor="end">${r.end}</text></svg><p class="trend-readout" aria-live="polite">点按／悬停查看日期、价格和均线；键盘 ← →</p>${options.extrema?`<p class="trend-extrema">最高收盘 ${r.high.close.toFixed(asset.unit==='元'?3:2)}（${r.high.date}）<br>最低收盘 ${r.low.close.toFixed(asset.unit==='元'?3:2)}（${r.low.date}）</p>`:''}<dl class="trend-ma-grid">${latestMAs}</dl>${valuationHtml}<details class="trend-source-section"><summary>来源、指标口径与数据缺口</summary><div><p class="trend-source">${esc(asset.basis)}${asset.quality?' · '+esc(asset.quality):''} · <a href="${esc(source)}" target="_blank" rel="noopener noreferrer">行情来源↗</a>${asset.product_source?` · <a href="${esc(asset.product_source)}" target="_blank" rel="noopener noreferrer">基金资料↗</a>`:''}</p><p>区间变化、波动和最大回撤基于价格序列；ETF前复权不等于完整含分红总回报。MA20/MA60固定交易日长度，并用区间前历史预热。历史价格不保证未来表现。</p></div></details></article>`;
}
export function trendCard(symbol,asset,period='3y',options={ma20:false,ma60:true,extrema:true}){
 const r=trendRange(asset,period);if(!r)return '';
 const esc=trendEscape,label={'20d':'20日','1y':'一年','2y':'两年','3y':'三年'}[period],last=asset.points.at(-1);
 const detail=trendDetail(symbol,asset,period,options),svg=/<svg class="trend-svg"[\s\S]*?<\/svg>/.exec(detail)?.[0]||'';
 const metrics=[[(r.complete?label:'可用区间')+'价格变化',trendPct(r.return_pct),r.return_pct>=0?'positive':'negative'],['年化波动',Number.isFinite(r.volatility_pct)?r.volatility_pct.toFixed(2)+'%':'—',''],['最大回撤',trendPct(r.mdd_pct),'negative']];
 const ma=n=>Number.isFinite(last['ma'+n])?trendPct((last.close/last['ma'+n]-1)*100):'数据不足';
 return `<article class="trend-card trend-summary-card" data-trend-symbol="${esc(symbol)}" role="button" tabindex="0" aria-haspopup="dialog" aria-label="查看${esc(asset.name)}详情"><div class="summary-head"><div><h3>${esc(asset.name.replace(/\s*·\s*(?:\d{6}|[A-Z][A-Z0-9.-]*)\s*$/,''))}</h3><p>${esc(asset.code||symbol.slice(2))} · ${esc(asset.market||'A股')} · ${esc(asset.unit)}</p></div><strong class="summary-price">${last.close.toFixed(asset.unit==='元'?3:2)}</strong></div><dl class="summary-metrics">${metrics.map(([l,v,c])=>`<div><dt>${l}</dt><dd class="${c}">${v}</dd></div>`).join('')}</dl><p class="summary-period">${r.start} → ${r.end}${r.complete?'':' · 不足所选年限'}</p><div class="summary-trend trend-plot">${svg}<p class="trend-readout" role="tooltip" hidden></p></div><div class="summary-ma"><span>距MA20 ${ma(20)}</span><span>距MA60 ${ma(60)}</span></div><div class="summary-foot"><span>${esc(asset.asof)} · 收盘</span><span>悬停 / 点击详情</span></div></article>`;
}
export function trendGrid(data,period='3y',options={ma20:false,ma60:true,extrema:true}){
 const entries=Object.entries(data.assets),base=entries.filter(([,a])=>a.group!=='china'),china=entries.filter(([,a])=>a.group==='china');
 const draw=items=>items.map(([s,a])=>trendCard(s,a,period,options)).join('');
 return draw(base)+(china.length?`<details class="reference china-fold" id="china-stocks"><summary>中概股与中概互联网 · ${china.length}项</summary><div class="section-content"><p class="trend-group-note">513050为人民币交易的境外互联网QDII-ETF，KWEB为美元ETF；其余为美股中概存托凭证。基金和个股成分可能重叠，不代表已经批准配置。每张卡片单独标明市场、币种、有效交易日；跨市场收盘并非同一时刻，不直接比较价格绝对值。A股整体5星不是个股买入信号。</p><div class="china-trend-grid">${draw(china)}</div></div></details>`:'')+(data.china_watchlist?.failures?.length?`<p class="trend-group-note">中概数据覆盖缺口：${data.china_watchlist.failures.map(a=>trendEscape(a.symbol)).join('、')}；未补造缺失曲线。</p>`:'');
}
export function trendSection(data){
 return `<section id="trends" class="report-section"><h2>指数、ETF 与中概股趋势</h2><p class="trend-intro">默认三年简版，桌面悬停预览，点击标的固定查看详情；中概股单独折叠。A股基线截至${trendEscape(data.asof)}；中概区按各卡片独立交易日展示已完成日线；${trendEscape(data.provider)}。</p><div class="trend-controls"><div role="group" aria-label="趋势图区间">${[['20d','20交易日'],['1y','一年'],['2y','两年'],['3y','三年']].map(([v,l])=>`<button type="button" data-trend-period="${v}" aria-pressed="${v==='3y'}">${l}</button>`).join('')}</div><div class="trend-overlays"><label><input type="checkbox" data-trend-overlay="ma20">MA20</label><label><input type="checkbox" data-trend-overlay="ma60" checked>MA60</label><label><input type="checkbox" data-trend-overlay="extrema" checked>最高／最低收盘</label></div></div><div class="trend-grid">${trendGrid(data)}</div><details class="reference"><summary>趋势图口径与边界</summary><div class="section-content"><p>价格变化为所选区间首末收盘变化，不年化；年化波动是区间日收益率样本标准差×√252；最大回撤为该区间相对此前区间峰值的最大跌幅，仅使用收盘序列，不包括盘中路径。ETF使用提供方前复权价格，不标记为完整含分红总回报；指数为价格指数。二者均不预测未来回报。</p><p>MA20／MA60采用每个历史日之前及当日20／60个交易日收盘算术均值，使用区间前的历史预热，不足留空。均线只是观察工具，不是自动买卖指令。所选年限若缺历史，明确标注可用区间，不补造数据。本页为每日审核快照，自动刷新检查新发布版本，不采集盘中行情。</p></div></details></section>`;
}
