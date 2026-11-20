import assert from 'node:assert/strict';
import test from 'node:test';
import {DatabaseSync} from 'node:sqlite';
import {generateAiCandidates,generateLocalNaming,handleNaming,listNamingFavorites,clearNamingHistory} from '../local/naming.mjs';

const birth={surname:'徐',gender:'female',birthDate:'2025-01-01',birthTime:'unknown'};
const sent=Symbol();
function browser(owner,db) {
  const ctx={db,session:owner,body:async()=>({}),sent,fail:(code,message,status)=>{throw Object.assign(new Error(message),{code,status});}};
  return async (path,payload,method=payload===undefined?'GET':'POST')=>{
    let type;
    let stream='';
    const res={
      writeHead:(code,headers)=>{type=headers['Content-Type'];},
      write:part=>{stream+=part;},
      end:part=>{if(part) stream+=part;},
    };
    const result=await handleNaming({method},res,new URL('http://127.0.0.1'+path),{...ctx,body:async()=>payload??{}});
    if(result===sent){
      assert.match(type,/text\/event-stream/);
      return stream.trim().split('\n\n').map(line=>JSON.parse(line.replace(/^data: /,'').trim()));
    }
    return result;
  };
}

test('诗词候选的出处包含完整名字，不放宽五行或指定用字',()=>{
  const response=generateLocalNaming({...birth,advancedOptions:{preferredWuxing:['木','水']}},{mode:'poetry',count:40});
  assert.equal(response.names.length,40);
  assert.equal(new Set(response.names.map(row=>row.full_name)).size,40);
  assert.ok(response.names.every(row=>row.full_name.startsWith('徐') && /^[木水]{2}$/.test(row.char_wuxing_combo)));
  assert.ok(response.names.slice(0,10).every(row=>row.reference?.poem.includes(row.given_name)));
  const fixed=generateLocalNaming({...birth,fixed_char:{char:'宁',position:'末'}},{mode:'ai',count:20});
  assert.ok(fixed.names.every(row=>row.given_name.endsWith('宁')));
  assert.throws(()=>generateLocalNaming({...birth,advancedOptions:{preferredChar1:'宁　静'}}),/一个汉字/);
});

test('AI 扩展字库仍保持固定字、五行和出处约束',()=>{
  const payload={...birth,fixed_char:{char:'宁',position:'末'},advancedOptions:{preferredWuxing:['火','土']}};
  const candidates=generateLocalNaming(payload,{mode:'ai',count:120}).names;
  assert.equal(candidates.length,120);
  assert.ok(candidates.every(row=>row.given_name.endsWith('宁') && /^[火土]{2}$/.test(row.char_wuxing_combo)));
  assert.ok(candidates.every(row=>!row.reference || row.reference.poem.includes(row.given_name)));
  assert.ok(candidates.some(row=>!row.reference));
});

test('AI 喜用组合覆盖两种字序，保留原初排并遵守五行',()=>{
  const payload={...birth,advancedOptions:{preferredWuxing:['木','水']}};
  const baseline=generateLocalNaming(payload,{mode:'ai',count:120}).names.map(row=>row.given_name);
  const names=generateAiCandidates(payload).names;
  const values=new Set(names.map(row=>row.given_name));
  assert.equal(names.length,values.size);
  assert.ok(names.length>baseline.length);
  assert.ok(baseline.every(name=>values.has(name)));
  const supplemental=names.filter(row=>!baseline.includes(row.given_name));
  assert.ok(supplemental.some(row=>row.char_wuxing_combo==='木水'));
  assert.ok(supplemental.some(row=>row.char_wuxing_combo==='水木'));
  assert.ok(supplemental.every(row=>['木水','水木'].includes(row.char_wuxing_combo)));
});

test('诗词起名保存历史并支持分页、补充名单、跨会话隔离和收藏',async()=>{
  const db=new DatabaseSync(':memory:');
  const own=browser('own',db), stranger=browser('stranger',db);
  const result=await own('/api/v2/naming/generate',{...birth,nameCount:60});
  assert.equal(result.names.length,30);
  assert.equal(result.total,60);
  assert.equal(result.has_more,true);
  assert.ok(result.names.every(row=>row.can_view));
  assert.equal((await own('/api/v1/naming/history?page=1&page_size=3')).total,1);
  assert.equal((await stranger('/api/v1/naming/history')).total,0);
  const path='/api/v2/naming/history/'+result.history_id;
  await assert.rejects(stranger(path+'/names'),{status:404});
  const expanded=await own(path+'/extend',{nameCount:100});
  assert.equal(expanded.addedCount,100);
  const second=await own(path+'/names?page=1&page_size=30');
  assert.deepEqual(second.names.map(row=>row.id),result.names.map(row=>row.id));
  const candidate=result.names[0];
  const details=await own('/api/v1/naming/detail?name_id='+candidate.id);
  assert.equal(details.name_card.full_name,candidate.full_name);
  assert.equal(details.characters.length,2);
  assert.equal(details.poem.verse,candidate.reference.poem);
  assert.deepEqual(await own('/api/v1/naming/collect',{name_id:candidate.id,action:'collect'}),{is_collected:true});
  assert.equal(listNamingFavorites(db,'own')[0].name_id,candidate.id);
  assert.equal((await own(path+'/names')).names[0].is_collected,true);
  assert.equal(clearNamingHistory(db,'own'),1);
  assert.deepEqual(listNamingFavorites(db,'own'),[]);
  db.close();
});

test('AI 起名按 init/batch/done 协议交付指定字与无生日结果',async(t)=>{
  const db=new DatabaseSync(':memory:');
  const request=browser('owner',db);
  const payload={...birth,birthDate:'unknown',fixed_char:{char:'清',position:'首'},personality:'清雅独立'};
  const eligible=generateLocalNaming(payload,{mode:'ai',count:120}).names;
  const choices=[eligible.find(row=>!row.reference),
    ...eligible.filter(row=>row.reference).slice(0,19)];
  const oldCredential=process.env.AI_GATEWAY_API_KEY;
  process.env.AI_GATEWAY_API_KEY='test-key';
  t.after(()=>{if(oldCredential===undefined) delete process.env.AI_GATEWAY_API_KEY; else process.env.AI_GATEWAY_API_KEY=oldCredential;});
  t.mock.method(globalThis,'fetch',async()=>{
    const content=choices.map((row,index)=>JSON.stringify({
      name:row.given_name,score:99-index,reason:'这个名字读音清楚，字义清雅，与姓氏连读自然，适合日常称呼。',
      tradeoff:'建议用家乡方言再连读确认。',
    })).join('\n');
    return new Response('data: '+JSON.stringify({choices:[{delta:{content}}]})+'\n\n'+
      'data: '+JSON.stringify({choices:[{finish_reason:'stop'}]})+'\n\n'+'data: [DONE]\n\n',
      {headers:{'content-type':'text/event-stream'}});
  });
  const preview=await request('/api/v1/naming_ai/preview',payload);
  assert.equal(preview.date_unknown,true);
  assert.equal(preview.bazi_analysis,null);
  const stream=await request('/api/v1/naming_ai/generate-stream',payload);
  assert.deepEqual(stream.map(event=>event.type),['init','batch','batch','batch','batch','done']);
  const id=stream[0].session_id;
  assert.equal(stream.at(-1).session_id,id);
  const candidates=stream.filter(event=>event.type==='batch').flatMap(event=>event.names);
  assert.equal(candidates.length,20);
  assert.ok(candidates.every(row=>Number.isSafeInteger(row.id)&&row.given_name.startsWith('清')));
  const loaded=await request('/api/v1/naming_ai/sessions/'+id);
  assert.equal(loaded.session.actual_count,20);
  assert.deepEqual(loaded.names,candidates);
  const detail=await request('/api/v1/naming_ai/names/'+candidates[0].id);
  assert.equal(detail.full_name,candidates[0].full_name);
  assert.equal(detail.birth_time,'');
  assert.equal(detail.input_personality,'清雅独立');
  const combination=candidates.find(row=>row.source_kind==='combination');
  assert.ok(combination);
  assert.equal(combination.source_type,'选字依据');
  assert.match(combination.source,/属/);
  assert.ok(candidates.every(row=>row.source_kind==='literary' ? row.reference.poem.includes(row.given_name) : !row.reference));
  assert.equal(detail.source,candidates[0].source);
  assert.equal(detail.source_kind,candidates[0].source_kind);
  assert.equal(detail.chars[0].radical,'氵');
  assert.equal(detail.phonetic.score,detail.dimensions.phonetic.score);
  assert.equal(detail.glyph.score,detail.dimensions.shape.score);
  assert.equal((await request('/api/v1/naming_ai/generate-stream',{...payload,surname:''}))[0].type,'error');
  db.close();
});

test('Gateway 未配置和半途失败时返回错误并保留可识别的部分记录',async(t)=>{
  const db=new DatabaseSync(':memory:');
  const request=browser('failure-owner',db);
  const payload={...birth,birthDate:'unknown',fixed_char:{char:'清',position:'首'}};
  const oldKey=process.env.AI_GATEWAY_API_KEY;
  const oldOidc=process.env.VERCEL_OIDC_TOKEN;
  t.after(()=>{
    if(oldKey===undefined) delete process.env.AI_GATEWAY_API_KEY; else process.env.AI_GATEWAY_API_KEY=oldKey;
    if(oldOidc===undefined) delete process.env.VERCEL_OIDC_TOKEN; else process.env.VERCEL_OIDC_TOKEN=oldOidc;
    db.close();
  });
  delete process.env.AI_GATEWAY_API_KEY;
  delete process.env.VERCEL_OIDC_TOKEN;
  assert.match((await request('/api/v1/naming_ai/generate-stream',payload))[0].message,/凭据/);
  assert.equal((await request('/api/v1/naming_ai/sessions')).total,0);
  process.env.AI_GATEWAY_API_KEY='test-key';
  const choices=generateLocalNaming(payload,{mode:'ai',count:120}).names.slice(0,5);
  const content=choices.map((row,index)=>JSON.stringify({
    name:row.given_name,score:95-index,reason:'这个名字用字自然，读音流畅，适合日常呼唤，与姓氏搭配协调。',
    tradeoff:'仍需结合日常方言再连读确认。',
  })).join('\n')+'\n';
  t.mock.method(globalThis,'fetch',async()=>new Response(
    'data: '+JSON.stringify({choices:[{delta:{content}}]})+'\n\n',
    {headers:{'content-type':'text/event-stream'}}));
  const events=await request('/api/v1/naming_ai/generate-stream',payload);
  assert.deepEqual(events.map(event=>event.type),['init','batch','error']);
  const history=await request('/api/v1/naming_ai/sessions/'+events[0].session_id);
  assert.equal(history.session.generation.status,'partial');
  assert.equal(history.names.length,5);
  assert.equal(history.session.requested_count,20);
  assert.equal(history.session.generation.model,'openai/gpt-6.2-sol');
  assert.equal(history.names[0].ai_model,'openai/gpt-6.2-sol');
});
