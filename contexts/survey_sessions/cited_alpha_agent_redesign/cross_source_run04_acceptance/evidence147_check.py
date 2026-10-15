import json,hashlib
from pathlib import Path
from decimal import Decimal
from bs4 import BeautifulSoup
from pypdf import PdfReader
root=Path('/Users/xuhao/Documents/Other/context-infrastructure/contexts/source_materials/cited_alpha_cross_source_tesla_2024')
sha='2a5dc10024afd96cf71f154c949759123c1da05715fb574866eaba6e1ec3bb18';raw=(root/(sha+'.html')).read_bytes();assert hashlib.sha256(raw).hexdigest()==sha
soup=BeautifulSoup(raw,'html.parser');tables=soup.find_all('table')
pdf=root/'05dfde334f800ec5f0ee140c0dd78409f24ad775e11a0c68f8a6b534b04cafdc.pdf';assert hashlib.sha256(pdf.read_bytes()).hexdigest()==pdf.stem
pdftext=PdfReader(pdf).pages[4].extract_text()
catalog=json.loads(Path('/tmp/cited-alpha-cross-source-business-04/independent-checkpoints/147.json').read_text())['progress']['rawCatalog']
rows=[];checks=[]
for key,e in catalog.items():
 l=e['locator'];t=tables[l['table_index']];trs=[r for r in t.find_all('tr')if r.find_parent('table')is t];tr=trs[l['row_index']];cells=tr.find_all(['td','th'],recursive=False);cell=cells[l['cell_index']];quote=' '.join(cell.stripped_strings);assert quote==e['quote'];f=l['xbrl_facts'][0];ix=cell.find('ix:nonfraction');assert ix is not None
 assert ix['name']==f['concept'] and ix['contextref']==f['context_ref'] and ix['unitref']==f['unit_ref'] and int(ix.get('scale',0))==f['scale']
 value=Decimal(''.join(ix.stripped_strings).replace(',',''))*(Decimal(10)**int(ix.get('scale',0)));value=-value if ix.get('sign')=='-'else value;assert value==Decimal(f['value'])
 ctx=soup.find('xbrli:context',id=f['context_ref']);period=ctx.find('xbrli:period');start=period.find('xbrli:startdate').text;end=period.find('xbrli:enddate').text;assert start==f['period']['startdate'] and end==f['period']['enddate']
 dims=[{'dimension':a['dimension'],'member':a.text}for a in ctx.find_all('xbrldi:explicitmember')];assert dims==f['dimensions']
 unit=soup.find('xbrli:unit',id=f['unit_ref']).find('xbrli:measure').text;assert unit==f['unit']=='iso4217:USD'
 assert e['provenance']['sha256']==sha and e['provenance']['capture_receipt']['contentHash']=='sha256:'+sha and e['provenance']['capture_receipt']['status']=='retained'
 label=' '.join(cells[0].stripped_strings);pdf_match=quote in pdftext
 rows.append(f"| `{key}` | {label} | {start[:4]} | {quote} | {l['table_index']}/{l['row_index']}/{l['cell_index']} | {f['concept'].split(':')[-1]} | {f['context_ref']} | "+('; '.join(x['member'] for x in dims)or '无维度')+f" | {'页5出现同值，见限制' if pdf_match else '未做PDF字段匹配'} |")
 checks.append({'id':key,'sourceRow':label,'quote':quote,'period':[start,end],'dimensions':dims,'rawValue':str(value),'htmlExact':True})
Path('/tmp/cited-alpha-run04-evidence147-review.md').write_text('''# Run04 checkpoint147：14条已登记证据独立审查

结论：14条全部来自同一SEC合并利润表 table23，7个指标各2024/2023两年。逐条按原始DOM table/row/cell定位重取文本，匹配原件的XBRL concept/context/period/dimensions/unit/scale/value，未发现错行、收入混成本或期间错位。它们尚不是完整报告，也未涵盖税项、GAAP净利、non-GAAP调整、现金流或风险解释；不能据此给报告通过结论。

## 方法与证据层级

仅访问指定checkpoint的progress.rawCatalog，未读messages/思考/签名；未轮询运行、调用模型/网络/数据库。SEC原件SHA重新算得2a5dc10024afd96cf71f154c949759123c1da05715fb574866eaba6e1ec3bb18，所有14条provenance sha/captureReceipt contentHash及retained状态一致。云端是否仍可读取沿用Root已完成的独立scope/hash检查，本次没有访问GCS。

PDF原件SHA重新匹配05dfde334f800ec5f0ee140c0dd78409f24ad775e11a0c68f8a6b534b04cafdc，读取物理页5。该页与已归档独立baseline支持汽车总收入、能源、服务、总收入、毛利两年对照；表中“页5出现同值”本身只是文本层辅助检查，不冒充PDF字段坐标核验。这14条没有任何PDF evidence locator，故没有声称其PDF bbox/字段身份通过。

## 逐条核对

所有期间均为本年01-01至12-31；unit=iso4217:USD、scale=6，因此展示值单位百万美元，typed value是原始美元。指标列来自原始行标题；坐标为零起始DOM索引（不是视觉列号）。

| evidence ID | 原始行 | 年 | quote（百万美元） | table/row/cell | concept | context | 维度 | PDF辅助 |
|---|---|---|---:|---|---|---|---|---|
'''+ '\n'.join(rows)+'''

## 口径限制

- Automotive sales（72,480/78,509）是不含监管积分及租赁的汽车销售收入；Total automotive revenues（77,070/82,419）包含上述项。后者不等于包含Services and other的汽车分部收入87,604/90,738，不能互换标签。
- Energy generation and storage（10,086/6,035）为收入行row8；不是成本行row15的7,446/4,894，也不能仅称储能收入。核对使用实际DOM行而非全文搜数字。
- Gross profit（17,450/17,660）是合并毛利润，不是营业利润/净利润/自由现金流。此14条不包含任何GAAP/non-GAAP净利证据或税项，无法核验2023税项收益驱动净利变化的解释。
- 两年总收入、毛利等数值与独立baseline重叠项一致。全部14条都有SEC原件级重取证据，不仅是rawCatalog内部字段自洽；PDF仅辅助对照，不是两个独立机构的背书。
- 原件quote与XBRL事实正确不等于后续正文解释正确；派生同比/利润率仍需后续实际计算记录和引用绑定。本快照无计算不等于无法继续，也不预判运行结局。

离线复核脚本：/tmp/run04-evidence147-check.py；逐条机器结果：/tmp/run04-evidence147-source-checks.json。
''')
Path('/tmp/run04-evidence147-source-checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2));print('14 exact HTML field checks passed; report written')
