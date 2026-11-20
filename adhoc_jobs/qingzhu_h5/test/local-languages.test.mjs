import {DatabaseSync} from 'node:sqlite';
import {test} from 'node:test';
import assert from 'node:assert/strict';
import {handleLanguages} from '../local/languages.mjs';
import {handleEvaluation,initEvaluation} from '../local/evaluation.mjs';
const db=new DatabaseSync(':memory:');
initEvaluation(db);
const ctx=(body,session='profile1')=>({db,session,body:async()=>body,
  fail:(code,msg,status)=>{throw Object.assign(new Error(msg),{code,status});}});
const run=(handler,method,route,body,session)=>handler({method},{},new URL('http://localhost/api/v1'+route),ctx(body,session));

test('小名按风格推荐，换一批去重并能查看详情',async()=>{
  const roots=await run(handleLanguages,'GET','/nickname/categories');
  assert.equal(roots.length,29);
  const first=await run(handleLanguages,'GET','/nickname/recommend?categories=fruit,flower&count=5');
  assert.equal(first.items.length,5);
  assert.ok(first.items.every(row=>['fruit','flower'].includes(row.category)));
  const second=await run(handleLanguages,'GET','/nickname/recommend?categories=fruit,flower&count=5&exclude_ids='+first.items.map(row=>row.id).join(','));
  assert.ok(second.items.every(row=>!first.items.some(x=>x.id===row.id)));
  const detail=await run(handleLanguages,'GET','/nickname/'+first.items[0].id);
  assert.equal(detail.nickname,first.items[0].nickname);
  assert.ok(detail.pinyin&&detail.meaning);
});

test('英文名搜索与推荐共享 ID，返回可用详情',async()=>{
  const recommended=await run(handleLanguages,'POST','/english-name/recommend',{gender:'F',style_tags:['优雅'],formality:'正式',page_size:3});
  assert.equal(recommended.names.length,3);
  assert.ok(recommended.names.every(row=>row.gender!=='M'&&row.formality==='正式'));
  const search=await run(handleLanguages,'GET','/english-name/search?keyword=Emma&gender=F');
  const detail=await run(handleLanguages,'GET','/english-name/'+search.names[0].id);
  assert.equal(detail.name,'Emma');
  assert.equal(detail.pop_rank_us,2);
  const popularity=await run(handleLanguages,'GET','/english-name/'+detail.id+'/popularity?country=US');
  assert.deepEqual(popularity.data,[{gender:'F',rank:2,count:85652,from_year:2020,to_year:2025}]);
  assert.ok(detail.meaning_cn&&detail.origin);
});

test('中文名按语义和性别生成，姓氏目录和详情可读',async()=>{
  const {names}=await run(handleLanguages,'GET','/foreigner-name/random?gender=F&meaning_tags=nature&count=3');
  assert.ok(names.length>0&&names.every(row=>row.gender!=='M'&&row.meaning_tags.includes('nature')));
  const detail=await run(handleLanguages,'GET','/foreigner-name/'+names[0].id);
  assert.equal(detail.given_name,names[0].given_name);
  assert.equal(detail.char_breakdown_en.length,2);
  const surnames=await run(handleLanguages,'GET','/foreigner-name/surnames/list?recommended_only=true');
  assert.ok(surnames.surnames.length>10);
});

test('测评包含真实读音、排盘、喜用匹配和持久化历史',async()=>{
  const detected=await run(handleEvaluation,'GET','/test-name/detect-surname?fullName=欧阳安明');
  assert.deepEqual(detected,{surname:'欧阳',name:'安明'});
  const args={surname:'林',name:'明安',gender:'男',birth_date:'2025-01-01',birth_hour:'午时',selected_xiyong_shen:['土']};
  const report=await run(handleEvaluation,'POST','/test-name/analyze',args);
  assert.equal(report.fullName,'林明安');
  assert.match(report.phoneticAnalysis.pinyinFull,/lín míng ān/);
  assert.equal(report.baziPaipan.bazi_str,'甲辰 丙子 庚午 壬午');
  assert.equal(report.wugeAnalysis.tiange.value,9);
  assert.equal(report.xiyongSource,'parent');
  assert.deepEqual(report.wuxingAnalysis.xiyongShen,['土']);
  const history=await run(handleEvaluation,'GET','/test-name/history');
  assert.ok(history.items.find(x=>x.id===report.id));
  await assert.rejects(()=>run(handleEvaluation,'GET','/test-name/report?id='+report.id,undefined,'other'),{status:404});
});

test('日期无效时不会保存测评记录',async()=>{
  const before=await run(handleEvaluation,'GET','/test-name/history');
  await assert.rejects(()=>run(handleEvaluation,'POST','/test-name/analyze',{
    surname:'林',name:'明安',gender:'女',birth_date:'2025-02-29',birth_hour:'unknown',
  }),{code:1001});
  assert.equal((await run(handleEvaluation,'GET','/test-name/history')).total,before.total);
});
