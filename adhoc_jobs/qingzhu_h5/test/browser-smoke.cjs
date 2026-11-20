// Start server.mjs first, then set BASE_URL or use the default local port.
const assert=require('node:assert/strict');
const {execFileSync}=require('node:child_process');
const {join}=require('node:path');
const root=execFileSync('npm',['root','-g'],{encoding:'utf8'}).trim();
const {chromium}=require(process.env.PLAYWRIGHT_MODULE || join(root,'playwright'));
const origin=process.env.BASE_URL || 'http://127.0.0.1:4175';

(async()=>{
  const browser=await chromium.launch({headless:true,...(process.env.CHROME_CHANNEL?{channel:process.env.CHROME_CHANNEL}:{})});
  const context=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,locale:'zh-CN'});
  await context.route(/^https:\/\//,route=>route.abort());
  const page=await context.newPage();
  page.setDefaultTimeout(8000);
  const errors=[];
  const apiErrors=[];
  page.on('pageerror',error=>errors.push(error.message));
  page.on('response',response=>{
    if(response.url().includes('/api/v1/bazi-naming/') && !response.ok()) apiErrors.push(response.url());
  });
  try {
    await page.goto(origin+'/bazi-naming/form');
    await page.getByRole('textbox',{name:'姓氏'}).fill('欧阳');
    await page.getByRole('radio',{name:'女宝'}).check();
    await page.locator('input[type=date]').fill('2026-11-18');
    await page.getByRole('button',{name:'金',exact:true}).click();
    await page.getByRole('button',{name:'木',exact:true}).click();
    const analysisResponse=page.waitForResponse(r=>r.url().endsWith('/bazi-naming/analysis'));
    await page.getByRole('button',{name:'开始八字分析'}).click();
    assert.equal((await (await analysisResponse).json()).code,0);
    await page.getByRole('heading',{name:'核对排盘与用字'}).waitFor({timeout:20000});
    assert.ok(await page.getByText('系统喜用神',{exact:true}).isVisible());
    assert.ok(await page.getByText(/实际取名依据/).isVisible());
    assert.equal(await page.getByText('需要更多名字？查看付费套餐').count(),0);
    const generation=page.waitForResponse(r=>r.url().endsWith('/bazi-naming/generate'));
    await page.getByRole('button',{name:/免费生成.*60.*个名字/}).click();
    assert.equal((await (await generation).json()).code,0);
    await page.waitForURL('**/bazi-naming/result?historyId=*');
    const resultURL=page.url();
    await page.locator('.name-card').first().waitFor();
    assert.equal(await page.locator('.name-card').count(),30);
    assert.ok((await page.locator('.name-card').first().innerText()).includes('欧'));
    await page.getByRole('button',{name:/加入对比/}).nth(0).click();
    await page.getByRole('button',{name:/加入对比/}).nth(0).click();
    await page.getByRole('button',{name:'对比 2 个',exact:true}).click();
    await page.getByRole('heading',{name:'原句或选字依据',exact:true}).waitFor();
    await page.getByRole('dialog').getByRole('button',{name:'关闭',exact:true}).click();
    await page.getByText('下一页',{exact:true}).click();
    await page.waitForURL('**/bazi-naming/result?historyId=*&page=2');
    await page.locator('.name-card').first().waitFor();
    assert.equal(await page.locator('.name-card').count(),30);
    assert.ok(await page.getByRole('button',{name:'对比 2 个',exact:true}).isVisible());
    await page.getByRole('link',{name:'查看详情',exact:true}).first().click();
    await page.waitForURL('**/naming/detail?*');
    await page.getByRole('heading',{name:'单字解读',exact:true}).waitFor();
    assert.match(await page.locator('body').innerText(),/欧阳/);
    await page.goto(resultURL);
    await page.getByText('查看完整字典',{exact:true}).click();
    await page.waitForURL('**/bazi-naming/character-library?historyId=*');
    await page.getByText('喜用字典',{exact:true}).waitFor();
    await page.getByText('高分常用字',{exact:true}).waitFor();
    assert.deepEqual(errors,[]);
    assert.deepEqual(apiErrors,[]);
    console.log('移动端通过：填表 → 分析 → 筛选金木 → 生成 60 个姓名 → 并排比较、翻页、详情和完整喜用字典');
  } finally {await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
