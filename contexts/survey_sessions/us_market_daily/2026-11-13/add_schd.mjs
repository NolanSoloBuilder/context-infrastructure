import fs from 'node:fs';
import {computeMetrics} from '../../../../adhoc_jobs/us_market_site/worker/engine.mjs';
const read = path => JSON.parse(fs.readFileSync(path,'utf8'));
const write = (path,value) => fs.writeFileSync(path,JSON.stringify(value,null,2)+'\n');
const seedPath = 'adhoc_jobs/us_market_site/worker/seed.json';
const registryPath = 'adhoc_jobs/us_market_daily/watchlist_groups.json';
const out = 'contexts/survey_sessions/us_market_daily/2026-11-13';
const seed = read(seedPath);
const registry = read(registryPath);
const marketSession = '2026-11-12';
const now = new Date();
const entry = {symbol:'SCHD',name:'美国红利股票ETF',kind:'fund',etf_category_id:'style',etf_category:'风格与集中'};
const sourceUrl = 'https://query2.finance.yahoo.com/v8/finance/chart/SCHD?range=5y&interval=1d&events=div%2Csplits&includeAdjustedClose=true';
const issuer = 'https://www.schwabassetmanagement.com/products/schd';
const secondary = 'https://stockanalysis.com/etf/schd/history/';
const index = 'https://www.spglobal.com/spdji/en/education/article/talkingpoints-why-dividend-and-capital-return-strategies-have-stood-out-in-2026/';
const {metrics,rows} = computeMetrics(read(out+'/SCHD_yahoo.json'),entry,marketSession,now);
const close = Number(rows.at(-1).close.toFixed(2));
if (metrics.asof_session!==marketSession || close!==35.93) throw Error('SCHD close must match dated second source');
const sources = [{title:'嘉信基金资料',url:issuer},{title:'标普道琼斯指数选股方法',url:index},{title:'11/12常规收盘交叉核验',url:secondary},{title:'VOO同窗复权行情',url:'https://finance.yahoo.com/quote/VOO/history/'}];
const base = (35.78/18.51)*1.05**3*18*(1-.0006)**3/1.09**3;
const stress = (35.78/18.51)*.98**3*14*(1-.0006)**3/1.11**3;
const round = n=>Number(n.toFixed(2));
const facts = {
 name:'Schwab U.S. Dividend Equity ETF',type:'美国红利股票ETF',
 strategy:'跟踪 Dow Jones U.S. Dividend 100 Index，按股息率、五年股息增长、ROE及现金流对债务等指标筛选。',
 expense_pct:.06,expense_verified_date:'2026-11-13',reviewed_date:'2026-11-13',holdings_date:'2026-11-11',
 holdings:[['TXN','德州仪器',4.70],['PG','宝洁',4.39],['KO','可口可乐',4.28],['HD','家得宝',4.27],['AMGN','安进',4.09]].map(([symbol,name,weight_pct])=>({symbol,name,weight_pct})),
 fact_lines:['30日SEC收益率3.06%（11/11）；过去12个月分配收益率2.95%（10/31）。两者口径不同。','10/31发行人组合市盈率18.51倍。9/30必需消费19.97%、医疗19.20%、能源15.38%，三类合计54.55%。','11/11前十大成分约41.38%，基金约99.92%为股票。'],
 notes:['相较VOO，SCHD把权重更多放在符合股息与质量筛选的公司，可用来研究红利和价值敞口。与VOO仍有重叠。','2025/11/12–2026/11/12，同窗税前复权总回报 SCHD +36.78%／VOO +12.07%，最大回撤 −6.87%／−8.90%，年化波动 11.76%／13.67%（Yahoo）。这一年结果不可外推。'],
 risks:['能源周期、成分公司削减股息及红利风格跑输都会影响总回报。高分配率不代表本金波动较小。'],sources
};
const valuation = {
 reviewed_at:now.toISOString(),market_session:marketSession,valuation_type:'conditional_fund_sensitivity',
 judgment:'红利与价值风格观察；现价高于本轮基准价格情景。',
 basis:`10/31官方P/E为18.51，使用同月最后一个交易日10/30价格35.78美元构造分母代理。三年情景现值=(35.78÷18.51)×(1+盈利增长)^3×终值倍数×(1−0.06%)^3÷(1+要求回报)^3。基准采用5%增长、18倍与9%要求回报，得${round(base)}美元；压力用−2%、14倍、11%，得${round(stress)}美元。未计现金分红，价格情景不能当作公允NAV或含息回报；发行人P/E的负盈利处理本次未核定。`,
 next:'下次跟踪组合盈利、分配覆盖率及行业权重。与VOO用同窗复权总回报、波动和最大回撤比较。',sources,
 base_value:round(base),stress_value:round(stress),discount_price:round(base*.8)
};
const quote={symbol:'SCHD',session:marketSession,close,day_pct:(close/rows.at(-2).close-1)*100,source_url:sourceUrl,captured_at_utc:now.toISOString(),crosscheck_url:secondary,crosscheck_status:'Yahoo与StockAnalysis同日收盘一致'};
const asset={...entry,kind_label:'ETF',role:'红利与质量',facts,valuation,research_status:valuation.judgment,quote,next:valuation.next};
for (const [doc,row] of [[registry,entry],[seed.catalog,asset]]) {
 const assets = doc.groups.find(g=>g.id==='funds').assets;
 const existing=assets.findIndex(a=>a.symbol==='SCHD');
 if(existing>=0) assets[existing]=row;
 else assets.splice(assets.findIndex(a=>a.symbol==='SPMO'),0,row);
}
if(registry.updated_at!=='2026-11-13') registry.version++;
registry.updated_at='2026-11-13';
seed.risk_metrics.symbols.SCHD={...metrics,source_url:sourceUrl};
write(seedPath,seed);
write(registryPath,registry);
write(out+'/SCHD_research.json',{facts,valuation,quote,metrics});
console.log(JSON.stringify({close,base:round(base),stress:round(stress),return:metrics.return_pct,mdd:metrics.max_drawdown_pct,high:metrics.high_52w,drawdown:metrics.price_drawdown_52w_pct,counts:registry.groups.map(g=>g.assets.length)}));
