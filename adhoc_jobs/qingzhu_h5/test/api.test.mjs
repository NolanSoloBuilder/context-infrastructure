import {test,before,after} from 'node:test';
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {once} from 'node:events';
import {mkdtempSync, rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';

let server, base, dbPath, dir;
async function start() {
  const child = spawn(process.execPath,['server.mjs'],{
    cwd:new URL('..',import.meta.url),
    env:{...process.env,PORT:'0',QINGZHU_API_ORIGIN:'',QINGZHU_BAZI_DB:dbPath},
    stdio:['ignore','pipe','pipe'],
  });
  let out='', stderr='';
  child.stderr.on('data',data=>{stderr+=data;});
  base = await new Promise((resolve,reject)=>{
    child.stdout.on('data',data=>{
      out+=data;
      const match=/http:\/\/127.0.0.1:\d+/.exec(out);
      if(match) resolve(match[0]);
    });
    child.on('exit',code=>reject(new Error('Server exited '+code+': '+stderr)));
    child.on('error',reject);
  });
  return child;
}
async function stop() {
  if (server?.exitCode===null) {
    const exited=once(server,'exit');
    server.kill();
    await exited;
  }
}
before(async()=>{
  dir=mkdtempSync(join(tmpdir(),'qingzhu-api-'));
  dbPath=join(dir,'test.sqlite');
  server=await start();
});
after(async()=>{await stop();rmSync(dir,{recursive:true,force:true});});

const path='/api/v1/bazi-naming';
const fixture={surname:'林',gender:'male',birthDate:'2026-11-17',birthTime:'23:00',selectedXiyongShen:['金','木']};

function client() {
  let cookie;
  return async (route,value,headers={})=>{
    const response=await fetch(base+route,{
      method:value===undefined?'GET':'POST',
      headers:{...headers,...(cookie?{cookie}:{}),...(value===undefined?{}:{'content-type':'application/json'})},
      body:value===undefined?undefined:JSON.stringify(value),
    });
    const setCookie=response.headers.get('set-cookie');
    if(setCookie) cookie=setCookie.split(';')[0];
    return {status:response.status,...await response.json()};
  };
}

test('独立接口从排盘到姓名、字典、分页、详情、收藏和重启恢复',async()=>{
  const fetchJson=client();
  const {data:quota}=await fetchJson(path+'/free-quota');
  const {data:analysis}=await fetchJson(path+'/analysis',fixture);
  assert.equal(analysis.bazi_str,'丙午 己亥 丙申 戊子');
  assert.deepEqual(analysis.xiyong_shen,['木','火']);
  const {data:preview}=await fetchJson(path+'/character-library/preview',fixture);
  assert.deepEqual(preview.xiyong_shen,['金','木']);
  assert.deepEqual(preview.groups.map(g=>g.chars.length),[3,3]);
  const [{data:created},{data:retry}]=await Promise.all([
    fetchJson(path+'/generate',fixture),fetchJson(path+'/generate',fixture),
  ]);
  const id=created.history_id;
  assert.equal(id,retry.history_id);
  const historyRoute=path+'/history/'+id;
  const {data:record}=await fetchJson(historyRoute);
  assert.equal(record.name_count,quota.name_count_per_use);
  assert.equal(record.names.length,record.name_count);
  assert.equal(record.xiyong_source,'parent');
  const {data:page1}=await fetchJson(historyRoute+'/names?page=1&page_size=30');
  const {data:page2}=await fetchJson(historyRoute+'/names?page=2&page_size=30');
  const {data:page3}=await fetchJson(historyRoute+'/names?page=3&page_size=30');
  assert.equal(page1.has_more,true);
  assert.equal(page2.has_more,false);
  assert.deepEqual(page3.names,[]);
  assert.equal(new Set([...page1.names,...page2.names].map(row=>row.id)).size,60);
  const chosen=page1.names[0];
  assert.match(chosen.full_name,/^林.{2}$/u);
  const detailRoute='/api/v1/naming/detail?name_id='+encodeURIComponent(chosen.id);
  const {data:detail}=await fetchJson(detailRoute);
  assert.equal(detail.name_card.full_name,chosen.full_name);
  assert.equal(detail.is_collected,false);
  const {data:favorite}=await fetchJson('/api/v1/naming/collect',{name_id:chosen.id,action:'collect'});
  assert.equal(favorite.is_collected,true);
  const dictionaryRoute=path+'/character-library?historyId='+id;
  const {data:library}=await fetchJson(dictionaryRoute);
  assert.equal(library.locked,false);
  const char=library.groups[0].chars[0].character;
  await fetchJson(path+'/character-library/favorite',{character:char});
  assert.equal((await fetchJson(dictionaryRoute)).data.groups[0].chars[0].favorited,true);
  const otherClient=client();
  assert.equal((await otherClient(historyRoute)).status,404);
  assert.equal((await otherClient(detailRoute)).status,404);
  assert.deepEqual((await otherClient(path+'/history')).data,{total:0,items:[]});
  await stop();
  server=await start();
  const {data:history}=await fetchJson(path+'/history?pageSize=5');
  assert.equal(history.total,1);
  assert.equal(history.items[0].id,id);
  assert.equal((await fetchJson(detailRoute)).data.is_collected,true);
  assert.equal((await fetchJson(historyRoute)).data.names[0].full_name,chosen.full_name);
});

test('非法出生日期和跨站写入不生成记录',async()=>{
  const fetchJson=client();
  const bad=await fetchJson(path+'/generate',{...fixture,birthDate:'2026-02-29'});
  assert.equal(bad.code,1001);
  const crossSite=await fetchJson(path+'/generate',fixture,{'sec-fetch-site':'cross-site'});
  assert.equal(crossSite.code,1001);
  assert.equal((await fetchJson(path+'/history')).data.total,0);
});
