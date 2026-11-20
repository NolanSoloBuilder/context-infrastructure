import test from 'node:test';
import assert from 'node:assert/strict';
import {AI_MODEL,prepareGatewayPayload,streamRecommendations,validateRecommendation} from '../local/ai-gateway.mjs';
import {generateLocalNaming} from '../local/naming.mjs';

const input={surname:'徐',gender:'female',birthDate:'unknown',birth_status:'unborn',fixed_char:{char:'听',position:'任意'},
  advancedOptions:{preferredWuxing:['火','土']},personality:'清雅独立'};
const result=generateLocalNaming(input,{mode:'ai',count:120});

function responseFor(content,{finish='stop',ended=true}={}) {
  const bytes=new TextEncoder().encode(
    'data: '+JSON.stringify({choices:[{delta:{content}}]})+'\r\n\r\n'+
    'data: '+JSON.stringify({choices:[{finish_reason:finish}],usage:{total_tokens:123}})+'\n\n'+
    (ended?'data: [DONE]\n\n':''));
  let index=0;
  return new Response(new ReadableStream({
    pull(controller){if(index>=bytes.length) controller.close();else{controller.enqueue(bytes.slice(index,index+3));index+=3;}},
  }),{headers:{'content-type':'text/event-stream'}});
}

test('模型请求使用指定模型和已校验候选，并传递原页面偏好',()=>{
  const payload=prepareGatewayPayload(result.input,result.analysis,result.names,20);
  assert.equal(payload.model,'openai/gpt-6.2-sol');
  assert.equal(payload.stream,true);
  const user=JSON.parse(payload.messages[1].content);
  assert.deepEqual(user.favorableElements,['火','土']);
  assert.equal(user.preferences.personality,'清雅独立');
  assert.equal(user.floating,'听');
  assert.equal(user.birth,null);
  assert.equal(user.birthStatus,'unborn');
  assert.equal(user.candidates.length,120);
  assert.equal(user.candidates[0].id,1);
  assert.ok(Object.keys(user.characters).length<user.candidates.length);
  assert.ok(user.candidates.every(row=>[...row.name].every(char=>user.characters[char]?.wuxing)));
  assert.ok(!payload.messages.some(row=>row.content.includes('AI_GATEWAY_API_KEY')));
});

test('SSE 跨 UTF-8 与 JSON 分片仍能解析逐条推荐和 usage',async()=>{
  const candidate=result.names[0];
  const row={name:candidate.given_name,score:93,reason:'与姓氏连读协调，用字清雅而自然，体现独立的气质。',tradeoff:'仍需结合方言检查谐音。'};
  const payload=prepareGatewayPayload(result.input,null,result.names,20);
  let requested;
  const events=[];
  for await(const event of streamRecommendations(payload,{
    credential:'test-key',fetcher:async(url,options)=>{
      requested=JSON.parse(options.body);
      return responseFor(JSON.stringify(row));
    },
  })) events.push(event);
  assert.equal(requested.model,AI_MODEL);
  assert.deepEqual(events.find(e=>e.type==='recommendation').row,row);
  assert.equal(events.find(e=>e.type==='usage').usage.total_tokens,123);
});

test('输出不符合候选、去重、排序和理由合同会拒绝',()=>{
  const candidates=new Map(result.names.map(name=>[name.given_name,name]));
  const row={name:result.names[0].given_name,score:90,reason:'这个名字与姓氏连读自然，字义明朗，可以体现温和独立。',tradeoff:'日常称呼可再用方言确认。'};
  assert.equal(validateRecommendation(row,candidates,new Set()).candidate,result.names[0]);
  assert.throws(()=>validateRecommendation({...row,name:'不存在'},candidates,new Set()),/候选库/);
  assert.throws(()=>validateRecommendation(row,candidates,new Set([row.name])),/重复/);
  assert.throws(()=>validateRecommendation(row,candidates,new Set(),89),/顺序/);
  assert.throws(()=>validateRecommendation({...row,reason:''},candidates,new Set()),/理由/);
});

test('网络、余额不足、截断和不完整结束均显式失败',async()=>{
  const collect=async(options)=>{
    for await(const event of streamRecommendations({model:AI_MODEL},{credential:'test-key',...options})) void event;
  };
  await assert.rejects(collect({fetcher:async()=>{throw new Error('connection error secret-value');}}),/无法连接/);
  await assert.rejects(collect({fetcher:async()=>new Response('secret-error',{status:402})}),/余额/);
  await assert.rejects(collect({fetcher:async()=>responseFor('{}',{finish:'length'})}),/未完整/);
  await assert.rejects(collect({fetcher:async()=>responseFor('{}',{ended:false})}),/提前结束/);
});
