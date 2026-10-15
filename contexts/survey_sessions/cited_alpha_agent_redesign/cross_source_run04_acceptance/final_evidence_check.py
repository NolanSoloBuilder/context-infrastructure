import json,hashlib
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
from bs4 import BeautifulSoup
from pypdf import PdfReader
root=Path('/Users/xuhao/Documents/Other/context-infrastructure/contexts/source_materials/cited_alpha_cross_source_tesla_2024')
d=json.loads(Path('/tmp/cited-alpha-cross-source-business-04/independent-checkpoints/190.json').read_text());p=d['progress'];cat=p['rawCatalog']
canonical=lambda x:json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
print('checkpoint canonical',len(canonical(d)),hashlib.sha256(canonical(d)).hexdigest())
sha='2a5dc10024afd96cf71f154c949759123c1da05715fb574866eaba6e1ec3bb18';raw=(root/(sha+'.html')).read_bytes();assert hashlib.sha256(raw).hexdigest()==sha
soup=BeautifulSoup(raw,'html.parser');tables=soup.find_all('table')
pdf=root/'05dfde334f800ec5f0ee140c0dd78409f24ad775e11a0c68f8a6b534b04cafdc.pdf';assert hashlib.sha256(pdf.read_bytes()).hexdigest()==pdf.stem
pages=PdfReader(pdf).pages
providers=json.loads(Path('/tmp/cited-alpha-cross-source-business-02/recovered-provider-readonly/providerDocuments.json').read_text());ph=hashlib.sha256(canonical(providers)).hexdigest()
out=[]
for key,e in cat.items():
 l=e['locator']
 if 'filing'in e:
  t=tables[l['table_index']];tr=[r for r in t.find_all('tr')if r.find_parent('table')is t][l['row_index']];cells=tr.find_all(['td','th'],recursive=False);cell=cells[l['cell_index']];assert ' '.join(cell.stripped_strings)==e['quote']
  if not l['xbrl_facts']:
   out.append({'id':key,'kind':'sec','label':' '.join(cells[0].stripped_strings),'period':l.get('column_headers'), 'quote':e['quote'],'coordinate':[l['table_index'],l['row_index'],l['cell_index']],'rawExact':True,'unit':'percent' if 'margin' in ' '.join(cells[0].stripped_strings).lower() else 'million USD','typedXbrl':False})
   continue
  f=l['xbrl_facts'][0];ix=cell.find('ix:nonfraction');assert ix['name']==f['concept'] and ix['contextref']==f['context_ref'] and ix['unitref']==f['unit_ref']
  val=Decimal(''.join(ix.stripped_strings).replace(',',''))*Decimal(10)**int(ix.get('scale',0));val=-val if ix.get('sign')=='-'else val;assert val==Decimal(f['value'])
  ctx=soup.find('xbrli:context',id=f['context_ref']);start=ctx.find('xbrli:startdate').text;end=ctx.find('xbrli:enddate').text
  assert start==f['period']['startdate']and end==f['period']['enddate']
  dims=[{'dimension':x['dimension'],'member':x.text}for x in ctx.find_all('xbrldi:explicitmember')];assert dims==f['dimensions'];assert int(ix.get('scale',0))==f['scale']
  assert soup.find('xbrli:unit',id=f['unit_ref']).find('xbrli:measure').text==f['unit']
  out.append({'id':key,'kind':'sec','label':' '.join(cells[0].stripped_strings),'period':start[:4],'quote':e['quote'],'coordinate':[l['table_index'],l['row_index'],l['cell_index']],'concept':f['concept'],'dimensions':dims,'unit':f['unit'],'scale':f['scale'],'rawExact':True})
 else:
  v=e['provenance']['document_version'];assert v['providerReceipt']['sha256']==ph;assert v['rawReceipt']['sha256']==pdf.stem;assert v['documentVersionId']==l['document_version_id']
  r=l['record'];n=r['page_number'];vs=r['bbox']['normalized_vertices'];y=sum(x['y']for x in vs)/4;xmid=sum(x['x']for x in vs)/4
  doc=next(x for x in providers if any(z['pageNumber']==n for z in x['pages']));page=next(x for x in doc['pages']if x['pageNumber']==n)
  matches=[]
  for line in page['lines']:
   layout=line['layout'];text=''.join(doc['text'][int(z.get('startIndex',0)):int(z['endIndex'])]for z in layout['textAnchor']['textSegments']).strip()
   if layout['boundingPoly']['normalizedVertices']==vs and text==e['quote']:matches.append(line)
  assert len(matches)==1,(key,len(matches));assert r['line_id']==l['field_id']and r['text']==e['quote']
  # Independent original PDF text layer: locate same number and its row.
  txt=pages[n-1].extract_text(extraction_mode='layout');line=next((line.strip()for line in txt.splitlines()if e['quote']in line),None);assert line
  same=[z['text']for z in e['context']['lines']if abs(sum(a['y']for a in z['bbox']['normalized_vertices'])/4-y)<.008]
  period='Q4 2024' if n==4 else ('2024'if xmid>.80 else '2023')
  out.append({'id':key,'kind':'pdf','page':n,'fieldId':l['field_id'],'quote':e['quote'],'label':same[0],'period':period,'providerPolygonExact':True,'originalPdfTextRow':line,'bbox':vs,'unit':'GWh'if 'Storage deployed'in same[0]else 'vehicles'if 'deliveries'in same[0]else 'million USD','unaudited':True})
cs=[]
for k,c in p['calculations'].items():
 f=[cat[i]['locator']['xbrl_facts'][0]for i in c['inputEvidenceIds']];assert f[0]['concept']==f[1]['concept']and f[0]['dimensions']==f[1]['dimensions']and f[0]['unit']==f[1]['unit'];assert f[0]['period']['startdate']=='2024-01-01'and f[1]['period']['startdate']=='2023-01-01'
 for a,b in zip(c['inputs'],f):assert Decimal(a['valueDecimal'])==Decimal(b['value'])and a['unit']==b['unit']
 assert c['operation']=='growth_rate';value=((Decimal(f[0]['value'])/Decimal(f[1]['value'])-1)*100).quantize(Decimal('.01'),rounding=ROUND_HALF_UP);assert value==Decimal(c['valueDecimal'])
 cs.append({'id':k,'inputEvidenceIds':c['inputEvidenceIds'],'label':next(x['label']for x in out if x['id']==c['inputEvidenceIds'][0]),'valuePercent':str(value),'decimalRecomputed':True})
result={'checkpoint':190,'evidence':out,'calculations':cs,'boundary':'local raw material checks only; no report acceptance'}
Path('/tmp/cited-alpha-run04-final-evidence-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print('verified',len(out),len(cs))
