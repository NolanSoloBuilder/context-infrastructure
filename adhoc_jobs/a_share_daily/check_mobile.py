"""Verify report containment in real Chromium through the global Playwright CLI."""
import argparse,json,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--url',required=True);p.add_argument('--out',required=True);a=p.parse_args()
out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True)
session='a-share-mobile-check'
def cli(*args):
 r=subprocess.run(['playwright-cli',f'-s={session}',*args],capture_output=True,text=True,timeout=90)
 if r.returncode or '### Error' in r.stdout:raise RuntimeError(r.stdout+r.stderr)
 return r.stdout
script=r'''async page => {
 const result=[];
 const contain=()=>({width:innerWidth,pageWidth:document.documentElement.scrollWidth,cellsContained:[...document.querySelectorAll('.merged-overview>.table-scroll:first-of-type td')].every(e=>e.scrollWidth<=e.clientWidth+1),charts:[...document.querySelectorAll('.chart-button,.trend-card,.trend-svg,.trend-controls')].map(e=>({left:e.getBoundingClientRect().left,right:e.getBoundingClientRect().right})),tables:[...document.querySelectorAll('.table-scroll')].map(e=>({width:e.clientWidth,scrollWidth:e.scrollWidth,right:e.getBoundingClientRect().right}))});
 for(const width of [320,360,375,390,430,768,1280]){
  await page.setViewportSize({width,height:844});
  for(const expanded of [false,true]){
   await page.evaluate(open=>document.querySelectorAll('details').forEach(e=>e.open=open),expanded);
   const state=await page.evaluate(contain);
   if(!state.cellsContained || state.pageWidth>width+1 || state.charts.some(e=>e.right>width+1 || e.left<0) || state.tables.some(e=>e.right>width+1))throw new Error('Page overflow '+JSON.stringify(state));
   const scrollable=await page.evaluate(()=>[...document.querySelectorAll('.table-scroll')].filter(e=>e.clientWidth>0).every(e=>{e.scrollLeft=e.scrollWidth;const ok=e.scrollWidth<=e.clientWidth+1 || e.scrollLeft>0;e.scrollLeft=0;return ok}));
   if(!scrollable)throw new Error('Wide table cannot scroll');
   result.push({...state,expanded,tableScrolling:true});
  }
 }
 await page.setViewportSize({width:390,height:844});
 await page.locator('.chart-button,.trend-card').first().scrollIntoViewIfNeeded();
 await page.screenshot({path:OUT+'/mobile-chart.png'});
 await page.locator('#undervalued,#valuation-sources').first().scrollIntoViewIfNeeded();
 await page.screenshot({path:OUT+'/mobile-table.png'});
 let modal={present:false};
 if(await page.locator('.chart-button').count()){
 await page.locator('.chart-button').first().click();
 modal=await page.evaluate(()=>{const d=document.querySelector('dialog'),z=d.querySelector('.zoom-scroll');z.scrollLeft=z.scrollWidth;return {present:true,open:d.open,width:d.getBoundingClientRect().width,pageWidth:document.documentElement.scrollWidth,zoomScrollable:z.scrollLeft>0}});
 if(!modal.open || modal.width>390 || modal.pageWidth>390 || !modal.zoomScrollable)throw new Error('Modal overflow '+JSON.stringify(modal));
 await page.screenshot({path:OUT+'/mobile-zoom.png'});
 await page.locator('#close-chart').click();
 }
 return {status:'passed',viewports:result,modal};
}'''.replace('OUT',json.dumps(str(out)))
try:
 cli('open',a.url)
 text=cli('run-code',script)
 start=text.index('### Result\n')+len('### Result\n');end=text.index('\n### Ran',start)
 result=json.loads(text[start:end]);result['url']=a.url
 (out/'mobile_layout_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'status':result['status'],'viewports':len(result['viewports']),'modal':result['modal'],'evidence':str(out)},ensure_ascii=False))
finally:
 cli('close')
