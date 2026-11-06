"""Exercise period, overlay and pointer/keyboard chart interactions via Playwright CLI."""
import argparse,json,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--url',required=True);p.add_argument('--out',required=True);a=p.parse_args();out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True)
session='a-share-trend-check'
def cli(*args):
 r=subprocess.run(['playwright-cli',f'-s={session}',*args],text=True,capture_output=True,timeout=90)
 if r.returncode or '### Error' in r.stdout:raise RuntimeError(r.stdout+r.stderr)
 return r.stdout
script=r'''async page => {
 const result={status:'passed'};
 if(await page.locator('[data-trend-period="3y"][aria-pressed=true]').count()!==1)throw new Error('Default is not three years');
 if(await page.locator('#trend-dialog').evaluate(e=>e.open)||await page.locator('#china-stocks').evaluate(e=>e.open))throw new Error('Default panels should be closed');
 const total=await page.locator('.trend-summary-card[data-trend-symbol]').count();if(total<7)throw new Error('Missing cards');result.cards=total;
 for(const key of ['20d','1y','2y','3y']){await page.locator(`[data-trend-period="${key}"]`).click();result[key]=await page.locator('.summary-period').allTextContents();if(result[key].length!==total)throw new Error('Range incomplete');}
 await page.locator('[data-trend-overlay=ma20]').check();if(await page.locator('.trend-grid [data-series=ma20]').count()!==total)throw new Error('MA20 missing');
 await page.locator('[data-trend-overlay=ma60]').uncheck();if(await page.locator('.trend-grid [data-series=ma60]').count())throw new Error('MA60 still shown');await page.locator('[data-trend-overlay=ma60]').check();
 await page.setViewportSize({width:1280,height:1000});const card=page.locator('.trend-summary-card[data-trend-symbol]').first();const before=(await card.boundingBox()).height;
 await card.locator('h3').hover();await page.locator('#trend-hover-panel:not([hidden])').waitFor();result.hoverPreview=true;await page.screenshot({path:OUT+'/hover-preview.png'});
 await page.locator('[data-pin-trend]').click();await page.locator('#trend-dialog[open]').waitFor();result.pinned=true;if(Math.abs((await card.boundingBox()).height-before)>1)throw new Error('Opening detail expanded the list');
 const svg=page.locator('#trend-dialog .trend-svg');await svg.focus();await page.keyboard.press('Home');const first=await page.locator('#trend-dialog .trend-readout').textContent();await page.keyboard.press('ArrowRight');const second=await page.locator('#trend-dialog .trend-readout').textContent();if(first===second)throw new Error('Keyboard cursor stuck');result.keyboard=[first,second];
 result.dialogWidth=(await page.locator('#trend-dialog').boundingBox()).width;if(result.dialogWidth!==720)throw new Error('Desktop panel does not match reference width');await page.screenshot({path:OUT+'/detail-desktop.png'});
 result.mobile=[];
 for(const width of [320,375,390,430]){await page.setViewportSize({width,height:844});for(const key of ['20d','1y','2y','3y']){await page.locator(`[data-detail-period="${key}"]`).click();const state=await page.evaluate(()=>({width:innerWidth,pageWidth:document.documentElement.scrollWidth,dialogWidth:document.getElementById('trend-dialog').getBoundingClientRect().width,bodyFits:document.getElementById('trend-dialog-body').scrollWidth<=document.getElementById('trend-dialog-body').clientWidth+1}));if(state.pageWidth>width+1||state.dialogWidth>width||!state.bodyFits)throw new Error('Detail overflow '+JSON.stringify(state));result.mobile.push({...state,key});}}
 await page.setViewportSize({width:390,height:844});await page.locator('[data-detail-period="1y"]').click();await svg.scrollIntoViewIfNeeded();const box=await svg.boundingBox();await svg.dispatchEvent('pointerdown',{pointerType:'touch',clientX:box.x+box.width*.6,clientY:box.y+box.height*.5});result.touchReadout=await page.locator('#trend-dialog .trend-readout').textContent();if(!result.touchReadout.includes('收盘'))throw new Error('Touch readout missing');await page.screenshot({path:OUT+'/detail-mobile.png'});
 await page.keyboard.press('Escape');if(await page.locator('#trend-dialog').evaluate(e=>e.open))throw new Error('Escape did not close');await page.waitForFunction(()=>document.querySelector('.trend-summary-card[data-trend-symbol]')===document.activeElement,{},{timeout:2000});result.focusReturned=await card.evaluate(e=>e===document.activeElement);if(!result.focusReturned)throw new Error('Focus not restored');
 await page.locator('#china-stocks>summary').click();await page.locator('[data-trend-symbol="usBABA.N"] h3').click();if(!(await page.locator('#trend-dialog-body').textContent()).includes('美元'))throw new Error('Currency lost');await page.locator('#close-trend-detail').click();
 await page.setViewportSize({width:1280,height:1000});await page.locator('#trends').scrollIntoViewIfNeeded();await page.screenshot({path:OUT+'/summary-desktop.png'});
 if(await page.locator('.valuation-image-button').count()){
  await page.setViewportSize({width:390,height:844});await page.locator('.valuation-image-button').click();await page.waitForFunction(()=>document.getElementById('zoom-image').naturalWidth>0);const image=page.locator('#zoom-image'),frame=page.locator('#chart-dialog .zoom-scroll');const initial=(await image.boundingBox()).width;await page.getByRole('button',{name:'放大估值图',exact:true}).click();if((await image.boundingBox()).width<=initial)throw new Error('Image zoom failed');await page.getByRole('button',{name:'适应宽度',exact:true}).click();const state=await page.evaluate(()=>({dialog:document.getElementById('chart-dialog').getBoundingClientRect().width,frame:document.querySelector('#chart-dialog .zoom-scroll').clientWidth,scroll:document.querySelector('#chart-dialog .zoom-scroll').scrollWidth,pageWidth:document.documentElement.scrollWidth}));if(state.dialog>390||state.pageWidth>390||state.scroll>state.frame+1)throw new Error('Image viewer overflow '+JSON.stringify(state));await frame.evaluate(e=>e.scrollTop=e.scrollHeight);if(await frame.evaluate(e=>e.scrollTop)<=0)throw new Error('Poster cannot scroll');await frame.evaluate(e=>e.scrollTop=0);await page.screenshot({path:OUT+'/valuation-image-mobile.png'});await page.keyboard.press('Escape');if(await page.locator('#chart-dialog').evaluate(e=>e.open))throw new Error('Image close failed');result.valuationImageModal=true;
 }
 return result;
}''' .replace('OUT',json.dumps(str(out)))
try:
 cli('open',a.url);text=cli('run-code',script);start=text.index('### Result\n')+len('### Result\n');end=text.index('\n### Ran',start);result=json.loads(text[start:end]);result['url']=a.url
 (out/'trend_interaction_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(status=result['status'],curves=result['cards'],ranges=4,mobile_checks=len(result['mobile']),touch=result['touchReadout']),ensure_ascii=False))
finally:cli('close')
