"""Check complete author-list preservation and table filtering against the audited data file."""
import argparse,json,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--url',required=True);p.add_argument('--data',required=True);p.add_argument('--out',required=True);a=p.parse_args();data=json.loads(Path(a.data).read_text());out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True);session='a-share-valuation-check'
def cli(*args):
 r=subprocess.run(['playwright-cli',f'-s={session}',*args],capture_output=True,text=True,timeout=90)
 if r.returncode or '### Error' in r.stdout:raise RuntimeError(r.stdout+r.stderr)
 return r.stdout
script=r'''async page => {
 const previous=page.locator('#last-session');if(await previous.count()){if(await previous.evaluate(e=>e.open))throw new Error('Previous session should start collapsed');await previous.locator(':scope > summary').click();}
 const expected=DATA,table=page.locator('#watchlist>.table-scroll tbody tr'),shown=()=>table.evaluateAll(rows=>rows.filter(r=>!r.hidden).length),result={status:'passed'};
 if(await table.count()!==expected.count)throw new Error('Incomplete full list');
 const compared=await table.evaluateAll((rows,items)=>items.map(x=>{const matches=rows.filter(r=>{const name=r.cells[0].textContent.trim();return name===x.name||name.startsWith(x.name+' ')});if(matches.length!==1)return x.name+': nonunique';const r=matches[0],val=r.cells[4].textContent,fund=r.cells[5].textContent;if(!val.includes(x.zone))return x.name+': class';for(const [key,prefix,suffix] of [['pe','PE','倍'],['pb','PB','倍'],['earnings_yield','盈利收益率','%']])if(x[key]&&!val.includes(prefix+x[key]+suffix))return x.name+': '+key;for(const key of ['on_exchange_fund','off_exchange_fund'])if(x[key]&&!fund.includes(x[key]))return x.name+': '+key;return null}).filter(Boolean),expected.items);
 if(compared.length)throw new Error(JSON.stringify(compared));result.allRowsAndValuesMatched=true;
 for(const [key,n] of [['all',expected.count],['focus',5],['low',expected.counts['低估']],['normal',expected.counts['正常']],['high',expected.counts['高估']]]){await page.locator(`[data-valuation-filter="${key}"]`).click();result[key]=await shown();if(result[key]!==n)throw new Error('Filter '+key);}
 await page.locator('[data-valuation-filter=all]').click();await page.getByRole('searchbox',{name:'搜索指数或基金代码'}).fill('513100');result.search=await shown();const n=expected.items.filter(x=>[x.name,x.on_exchange_fund,x.off_exchange_fund].filter(Boolean).some(v=>v.includes('513100'))).length;if(result.search!==n)throw new Error('Fund search mismatch');await page.getByRole('searchbox').fill('');
 if(await page.locator('#valuation').count()||await page.locator('#undervalued table').count())throw new Error('Duplicate valuation table');
 await page.setViewportSize({width:1280,height:1000});await page.locator('#watchlist').scrollIntoViewIfNeeded();await page.screenshot({path:OUT+'/valuation-desktop.png'});await page.setViewportSize({width:390,height:844});await page.locator('#watchlist').scrollIntoViewIfNeeded();await page.screenshot({path:OUT+'/valuation-mobile.png'});return result;
}'''.replace('DATA',json.dumps(data,ensure_ascii=False)).replace('OUT',json.dumps(str(out)))
try:
 cli('open',a.url);text=cli('run-code',script);start=text.index('### Result\n')+len('### Result\n');end=text.index('\n### Ran',start);result=json.loads(text[start:end]);result['asof']=data['asof'];(out/'valuation_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False))
finally:cli('close')
