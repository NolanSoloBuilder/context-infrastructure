import json
from pathlib import Path
mapping={
 'core':('宽基与成长',['VOO','QQQM']),
 'style':('风格与集中',['SPMO','MAGS']),
 'technology':('科技与半导体',['VGT','SOXX','SMH','DRAM','AIQ']),
 'software':('软件与AI应用',['IGV','XSW']),
 'healthcare':('医疗设备',['IHI']),
 'automation':('机器人与自动化',['BOTZ']),
 'cash':('现金管理',['SGOV']),
 'leveraged':('每日杠杆与反向工具',['KORU','SOXL','SOXS'])}
for file in ['adhoc_jobs/us_market_site/worker/seed.json','adhoc_jobs/us_market_daily/watchlist_groups.json']:
 p=Path(file);d=json.loads(p.read_text());cat=d.get('catalog',d)
 for g in cat['groups']:
  for a in g['assets']:
   if a.get('kind')=='fund':
    hit=[(k,label) for k,(label,ss) in mapping.items() if a['symbol'] in ss]
    assert len(hit)==1,(a['symbol'],hit)
    a['etf_category_id'],a['etf_category']=hit[0]
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
print('ETF categories synced')
