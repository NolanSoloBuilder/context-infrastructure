"""Check version polling without waiting five minutes or changing hosted data."""
import argparse,json,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--url',required=True);p.add_argument('--out',required=True);a=p.parse_args();out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True);session='a-share-refresh-check'
def cli(*args):
 r=subprocess.run(['playwright-cli',f'-s={session}',*args],capture_output=True,text=True,timeout=90)
 if r.returncode or '### Error' in r.stdout:raise RuntimeError(r.stdout+r.stderr)
 return r.stdout
script=r'''async page => {
 await page.clock.install();await page.reload();
 const revision=await page.locator('meta[name=report-revision]').getAttribute('content');let mode='same',requests=0;
 await page.getByRole('button',{name:'立即检查',exact:true}).click();await page.waitForFunction(()=>document.querySelector('#report-refresh [role=status]').textContent.includes('已是最新'));
 await page.route('**/report-meta.json?*',async route=>{requests++;await route.fulfill({status:mode==='error'?503:200,contentType:'application/json',body:JSON.stringify({content_revision:mode==='new'?'a'.repeat(64):revision})});});
 const check=page.getByRole('button',{name:'立即检查',exact:true}),toggle=page.locator('#report-refresh input'),status=page.locator('#report-refresh [role=status]');
 await check.click();await page.waitForFunction(()=>document.querySelector('#report-refresh [role=status]').textContent.includes('已是最新'));
 const result={status:'passed',sameVersionKept:true,realMetadataChecked:true};
 await toggle.uncheck();let before=requests;await page.clock.fastForward(315000);if(requests!==before)throw new Error('Disabled polling still requested');result.disabledPaused=true;
 await toggle.check();before=requests;await page.clock.fastForward(315000);await page.waitForFunction(()=>!document.querySelector('#report-refresh button').disabled);if(requests<=before)throw new Error('Timer did not poll');result.timerPolled=true;
 await page.evaluate(()=>Object.defineProperty(document,'visibilityState',{configurable:true,get:()=> 'hidden'}));before=requests;await page.clock.fastForward(315000);if(requests!==before)throw new Error('Background polling continued');result.hiddenPaused=true;
 await page.evaluate(()=>{Object.defineProperty(document,'visibilityState',{configurable:true,get:()=> 'visible'});document.dispatchEvent(new Event('visibilitychange'));});await page.waitForFunction(()=>!document.querySelector('#report-refresh button').disabled);
 mode='error';await check.click();await page.waitForFunction(()=>document.querySelector('#report-refresh [role=status]').textContent.includes('检查失败'));result.failureRetainedReport=await page.locator('.trend-card').count()===14;if(!result.failureRetainedReport)throw new Error('Failure removed report');
 await page.locator('[data-trend-period="2y"]').click();await page.locator('#china-stocks>summary').click();await page.locator('.trend-summary-card h3').first().click();
 mode='new';await page.clock.fastForward(315000);await page.waitForURL(url=>url.searchParams.get('v')==='aaaaaaaaaaaa');await page.waitForLoadState();
 result.updateReloaded=page.url().includes('v=aaaaaaaaaaaa');result.restoredPeriod=await page.locator('[data-trend-period="2y"][aria-pressed=true]').count()===1;result.restoredCard=await page.locator('#trend-dialog').evaluate(e=>e.open);result.restoredChina=await page.locator('#china-stocks').evaluate(e=>e.open);
 if(!result.updateReloaded||!result.restoredPeriod||!result.restoredCard||!result.restoredChina)throw new Error('Refresh lost state '+JSON.stringify(result));
 result.requests=requests;return result;
}'''
try:
 cli('open',a.url);text=cli('run-code',script);start=text.index('### Result\n')+len('### Result\n');end=text.index('\n### Ran',start);result=json.loads(text[start:end]);result['test_mode']='Browser-local mocked version responses and virtual clock; no hosted data was modified';(out/'refresh_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False))
finally:cli('close')
