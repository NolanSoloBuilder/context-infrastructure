"""Offline navigation prototype. Caller supplies already-verified immutable materials."""
import base64,copy,hashlib,json
COLS={'line':('lines','line_id'),'span':('spans','span_id'),'cell':('table_cells','cell_id')}
def wire(value): return json.dumps(value,ensure_ascii=False,separators=(',',':')).encode()
def overview(normalized,*,version_id,page,kind='line',cursor=None,max_bytes=32768,max_fields=300):
 if kind not in COLS or type(page)is not int or page<1 or type(max_bytes)is not int or max_bytes<256 or type(max_fields)is not int or not 1<=max_fields<=300:raise ValueError('invalid bounds')
 col,key=COLS[kind]
 rows=[r for r in normalized.get(col,[]) if r.get('page_number')==page and isinstance(r.get('text'),str) and r['text'].strip()]
 ids=[r[key] for r in rows]
 if len(ids)!=len(set(ids)):raise ValueError('ambiguous field ids')
 # Bound cursor to exact selection, not only textual page name. No authorization claim.
 binding=hashlib.sha256(wire([version_id,page,kind,rows])).hexdigest()
 offset=0
 if cursor is not None:
  try:
   c=json.loads(base64.urlsafe_b64decode(cursor.encode()));offset=c['offset']
   if set(c)!={'binding','offset'} or c['binding']!=binding or type(offset)is not int or not 0<=offset<len(rows):raise ValueError()
  except Exception as exc:raise ValueError('invalid or cross-scope cursor') from exc
 def token(i):return base64.urlsafe_b64encode(wire({'binding':binding,'offset':i})).decode()
 out={'viewVersion':'offline-page-overview/v1','documentVersionId':version_id,'pageNumber':page,'displayKind':'spatial_text','citable':False,'layer':kind,'availableLayers':{k:sum(r.get('page_number')==page and bool(r.get('text','').strip()) for r in normalized.get(c,[])) for k,(c,_) in COLS.items()},'coverage':{'start':offset,'end':offset,'total':len(rows),'complete':False},'fields':[],'truncated':False,'nextCursor':None}
 end=offset
 while end<len(rows) and end-offset<max_fields:
  r=rows[end];f={'kind':kind,'id':r[key],'text':r['text'],'bbox':copy.deepcopy(r.get('bbox'))}
  out['fields'].append(f);end+=1
  out.update(truncated=end<len(rows),nextCursor=token(end) if end<len(rows) else None)
  out['coverage'].update(end=end,complete=offset==0 and end==len(rows))
  if len(wire(out))>max_bytes:
   out['fields'].pop();end-=1;break
 out.update(truncated=end<len(rows),nextCursor=token(end) if end<len(rows) else None)
 out['coverage'].update(end=end,complete=offset==0 and end==len(rows))
 if end==offset and rows:raise ValueError('single full field exceeds response budget; no text truncated')
 if len(wire(out))>max_bytes:raise ValueError('metadata exceeds budget')
 return out
