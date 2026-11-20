const assert=require('node:assert/strict');
const {execFileSync}=require('node:child_process');
const {join}=require('node:path');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||join(execFileSync('npm',['root','-g'],{encoding:'utf8'}).trim(),'playwright'));
const base=process.env.BASE_URL||'http://127.0.0.1:4175';

(async()=>{
  const browser=await chromium.launch({headless:true,...(process.env.CHROME_CHANNEL?{channel:process.env.CHROME_CHANNEL}:{})});
  try {
    const context=await browser.newContext({viewport:{width:390,height:844},hasTouch:true,isMobile:true,locale:'zh-CN'});
    await context.route(/^https?:\/\//,route=>route.request().url().startsWith(base+'/')?route.continue():route.abort());
    const page=await context.newPage();
    page.setDefaultTimeout(8500);
    const errors=[], bad=[];
    page.on('pageerror',error=>errors.push(error.message));
    page.on('response',response=>{
      if(response.url().startsWith(base+'/api/') && response.status()>=500) bad.push(response.url().slice(base.length).split('?')[0]);
    });
    const visit=path=>page.goto(base+path,{waitUntil:'domcontentloaded'});
    const exact=text=>page.getByText(text,{exact:true});

    await visit('/nickname/form');
    await exact('水果类').click();
    await exact('开始起小名').click();
    await page.waitForURL('**/nickname/result');
    await page.locator('.nickname-card').first().waitFor();
    assert.ok(await page.locator('.nickname-card').count()>=5);
    await page.locator('.nickname-card').first().click();
    await page.waitForURL('**/nickname/detail/*');
    await exact('小名寓意').or(exact('名字寓意')).or(exact('详细寓意')).first().waitFor().catch(async()=>{
      assert.ok((await page.locator('body').innerText()).includes('水果类'));
    });
    console.log('小名：主题筛选、推荐、详情');

    await visit('/english-name/form');
    await exact('智能推荐').click();
    await page.waitForURL('**/english-name/result*');
    const search=page.getByPlaceholder('搜索英文名');
    await search.fill('Liam');
    const searchResponse=page.waitForResponse(r=>r.url().includes('/api/v1/english-name/search'));
    await search.press('Enter');
    assert.equal((await (await searchResponse).json()).data.names[0].name,'Liam');
    const en=page.locator('.name-card').first();
    await en.waitFor();
    const englishDetail=page.waitForResponse(r=>/\/api\/v1\/english-name\/\d+$/.test(r.url()));
    await en.click();
    await page.waitForURL('**/english-name/detail/*');
    const englishName=(await (await englishDetail).json()).data;
    assert.ok(englishName.meaning_cn);
    await page.getByText(englishName.name,{exact:true}).first().waitFor();
    console.log('英文名：推荐、详情');

    await visit('/chinese-name');
    await exact('Discover My Name').click();
    await page.waitForURL('**/chinese-name/*');
    await page.getByText(/Meaning|Pronunciation/).first().waitFor();
    console.log('外文用户中文名：生成、双语详情');

    await visit('/test/form');
    await page.getByPlaceholder('请输入完整姓名').fill('欧阳明安');
    await page.locator('.gender-btn').first().click();
    await page.locator('.select-field').nth(0).click();
    await page.getByRole('button',{name:'确认',exact:true}).click();
    await page.locator('.select-field').nth(1).click();
    await page.getByRole('button',{name:'确认',exact:true}).click();
    const analysis=page.waitForResponse(r=>r.url().endsWith('/api/v1/test-name/analyze'));
    await exact('开始测评').click();
    assert.equal((await (await analysis).json()).code,0);
    await page.waitForURL('**/test/score*');
    await page.getByRole('heading',{name:'欧阳明安',exact:true}).waitFor();
    console.log('姓名测评：复姓、实算评分、报告');

    await visit('/tools/articles');
    await page.getByRole('link',{name:'公历、农历和出生时辰怎么填'}).click();
    await exact('打开八字起名').waitFor();
    console.log('起名知识：列表、详情和工具入口');

    await visit('/');
    await exact('清言字舍').first().waitFor();
    assert.equal(await exact('清言字舍 · 免费开放').count(),0);
    await page.getByRole('link',{name:'开始起名',exact:true}).waitFor();
    assert.equal(await page.getByRole('link',{name:'数据来源与许可'}).count(),0);
    await visit('/mine/about');
    await page.getByRole('heading',{name:'数据来源与许可'}).waitFor();
    assert.equal(await page.getByText(/京ICP备|京公网安备|青竹字舍/).count(),0);
    await visit('/vip/buy');
    await page.waitForURL('**/mine/about');
    await exact('免费使用').waitFor();
    await visit('/mine');
    await exact('免费使用说明').waitFor();
    const retired=await page.request.post(base+'/api/v1/payment/trial-vip/create',{data:{}});
    assert.equal(retired.status(),410);
    console.log('清言字舍品牌、许可、会员入口迁移及结算停用');

    const routes=['/','/naming','/naming/form','/naming-ai/form','/nickname','/english-name',
      '/test','/test/history','/tools','/tools/character','/tools/surname','/tools/bazi',
      '/tools/zodiac','/tools/almanac','/tools/wuge','/tools/classic','/tools/parents','/tools/premium',
      '/tools/constellation','/tools/constellation/match','/tools/constellation/fortune',
      '/tools/naming-characters','/tools/naming-characters/wuxing','/tools/naming-characters/filter',
      '/tools/shuowen','/tools/funny-names','/tools/popular-names','/tools/homophone-names',
      '/coupons','/mine','/mine/coupons','/mine/favorites','/mine/quota','/mine/redeem',
      '/mine/materials','/mine/reports','/mine/naming-history'];
    for(const route of routes){
      await visit(route);
      await page.locator('#app > #app').waitFor();
      await page.waitForLoadState('networkidle');
      assert.ok(!(await page.locator('body').innerText()).includes('此功能需要连接起名服务后端'),route);
    }
    assert.deepEqual(bad,[]);
    assert.deepEqual(errors,[]);
    console.log('入口冒烟 '+routes.length+' 页，没有后端缺失或脚本错误');
  } finally {await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
