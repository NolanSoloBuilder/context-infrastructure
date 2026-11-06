"""Render the complete audited author list into one Markdown overview, without duplicating cheap rows."""
import argparse,json,re,math
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--report-dir',required=True);a=p.parse_args();out=Path(a.report_dir)
v=json.loads((out/'valuation_all.json').read_text());m=json.loads((out/'market.json').read_text());assert v['asof']==m['asof'];items=v['items'];assert len(items)==v['count']==len({x['name'] for x in items})
assert {zone:sum(x['zone']==zone for x in items) for zone in ['低估','正常','高估']}==v['counts']
priority=['上证指数','上证50','沪深300','中证A500','科创50'];ordered=sorted(items,key=lambda x:(priority.index(x['name']) if x['name'] in priority else 5,x['source_order']))
indices={'上证指数':'sh000001','上证50':'sh000016','沪深300':'sh000300','科创50':'sh000688'};etfs={'上证50':'sh510050','沪深300':'sh510300','科创50':'sh588000'}
notes={'上证指数':'市场基准，估值按原图对应行读取','上证50':'单项估值独立判断，不套用整体星级','沪深300':'整体到观察线后评估宽基候选','中证A500':'研究与沪深300的成分重叠','科创50':'低于MA60约25.39%，暂不作为默认首笔'}
trend_file=out/'trends.json'
if trend_file.exists():
 trend=json.loads(trend_file.read_text());points=trend.get('assets',{}).get('sh000688',{}).get('points',[])
 if points and points[-1]['date']==m['asof'] and points[-1].get('ma60'):
  gap=(points[-1]['close']/points[-1]['ma60']-1)*100;notes['科创50']=('低于' if gap<0 else '高于')+f'MA60约{abs(gap):.2f}%，先核验风险与资金条件'
def pct(value):return f'{value:+.2f}%' if isinstance(value,(int,float)) and math.isfinite(value) else '—'
rows=[]
for x in ordered:
 name=x['name'];symbol=indices.get(name);q=m['metrics'].get(symbol) if symbol else None
 label=f"[{name} {symbol[2:]}↗]({q['source']})" if q else name
 quotes=f"{q['close']:.2f} | {pct(q['daily_pct'])} | {pct(q['twenty_session_pct'])}" if q else '— | — | —'
 parts=[]
 if x['earnings_yield']:parts.append('盈利收益率'+x['earnings_yield']+'%')
 if x['pe']:parts.append('PE'+x['pe']+'倍')
 if x['pb']:parts.append('PB'+x['pb']+'倍')
 funds='场内 '+(x['on_exchange_fund'] or '原图未列')+'；场外 '+(x['off_exchange_fund'] or '原图未列')
 if name in etfs:
  e=etfs[name];eq=m['metrics'][e];funds+=f"；观察ETF[{e[2:]}↗]({eq['source']})：{eq['close']:.3f}元 / {pct(eq['daily_pct'])} / {pct(eq['twenty_session_pct'])}"
 note=notes.get(name,'—')
 rows.append(f"| {label} | {quotes} | {'；'.join(parts)} · {x['zone']} | {funds} | {note} |")
quote_count=sum(1 for symbol in indices.values() if symbol in m['metrics'])
correction_file=out/'sources/valuation_corrections.json'
correction=('本次原图核对纠正：'+'；'.join(x['name']+'：'+x['corrected'] for x in json.loads(correction_file.read_text())['corrections'])+'。[纠正记录↓](./sources/valuation_corrections.json)') if correction_file.exists() else ''
cheap=[]
for x in items:
 if x['zone']=='低估':
  metric='盈利收益率' if x['earnings_yield'] else '市盈率' if x['pe'] else '市净率'
  value=x['earnings_yield'] or x['pe'] or x['pb'];cheap.append(dict(name=x['name'],code=x['index_code'],metric=metric,display=value+('%' if metric=='盈利收益率' else '倍'),zone=x['zone']))
(out/'valuation_cheap.json').write_text(json.dumps(dict(asof=v['asof'],count=len(cheap),source_image=v['source_image'],items=cheap),ensure_ascii=False,indent=2)+'\n')
body=f'''## 主观察表：行情、估值与星级

纳入螺丝钉**第{v['issue']}期常规原图全部{v['count']}项指数**：低估{v['counts']['低估']}项、正常{v['counts']['正常']}项、高估{v['counts']['高估']}项。估值日期为**{v['asof']}**，整体星级在开头统一说明，不给单指数套星数。表格可按名称、基金代码或估值分类筛选。[作者原文↗]({v['source_url']})

| 指数方向 | 收盘（点） | 当日 | 20交易日 | 作者估值与分类 | 原图基金代码／补充ETF行情 | 对你的观察 |
|---|---:|---:|---:|---|---|---|
'''+ '\n'.join(rows)+f'''

本期估值已全量核对{v["count"]}项；其中{quote_count}项指数行情及3只观察ETF行情已采集，其余行情留空。表内场内／场外基金代码按原图列示，可能包含不同基金类型，不统一称为ETF，也不是建议全部配置。补充ETF报价依次为收盘／当日／20交易日变化，日期均为{m["asof"]}。[行情数据↓](./market.json)

PE/PB单位为倍，盈利收益率为%，不直接横向按数值排序。ETF前复权价格不等于完整总回报；区间变化不等于最大回撤。{correction}

### 原始估值与核验资料

低估{v["counts"]["低估"]}项已整合在主表，用“低估”筛选可查看完整名单，不再重复铺第二张表。十年期国债{v["bond_reference"]["yield_display"]}仅作为原图参考项，不计入指数数目。不同日期的附表不混入本期常规估值。指数代码辅助标识不替代作者原图数值与分类。[全部{v["count"]}项数据↓](./valuation_all.json) · [原图↓]({v["source_image"]}) · [当期低估子集↓](./valuation_cheap.json) · [行情对比图↓](./market.svg)

'''
report=out/'report.md';text=report.read_text();text=re.sub(r'## 主观察表：行情、估值与星级\n[\s\S]*?(?=\n## |\Z)',lambda _:body.rstrip()+'\n',text,count=1);report.write_text(text)
print(f'Wrote one overview: {len(items)} unique indices, priority five first, no duplicate cheap table.')
