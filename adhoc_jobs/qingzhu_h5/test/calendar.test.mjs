import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {parseBirth, analyzeBirth, InputError, ELEMENTS} from '../bazi/calendar.mjs';
import {analysisFor, libraryFor, generateNames} from '../bazi/names.mjs';

const fixtures = JSON.parse(readFileSync(new URL('./original-bazi-cases.json', import.meta.url)));
const base = {surname:'林',gender:'male',birthDate:'2026-11-17',birthTime:'晚子时'};
const pad = x=>String(x).padStart(2,'0');

for (const {case:name,input,expected} of fixtures) {
  if (expected.code!==0) continue;
  test('原站公开排盘对照：'+name,()=>{
    const birth=parseBirth({...base,
      gender:input.gender===1?'male':'female',
      birthDate:`${input.year}-${pad(input.month)}-${pad(input.day)}`,
      birthTime:`${pad(input.hour)}:${pad(input.minute)}`,
    });
    const actual=analyzeBirth(birth);
    assert.equal(actual.bazi_str,expected.baziString);
    assert.deepEqual(actual.kongwang,expected.kongwang);
    assert.deepEqual(actual.wuxingWithCangGan,expected.wuxingWithCangGan);
    for(const field of ['year','month','day','isLeap','dayGanZhi']) {
      assert.equal(actual.lunar[field],expected.lunar[field]);
    }
    assert.equal(actual.pattern.name,expected.pattern.name);
    assert.equal(actual.riZhuStrength.level,expected.riZhuStrength.level);
    assert.deepEqual(actual.xiyong_shen,[expected.yongShen.yong,expected.yongShen.xi]);
    assert.equal(actual.ji_shen,expected.yongShen.ji);
  });
}

test('未知时辰不填造时柱，保留推算使用的年月日',()=>{
  const actual=analyzeBirth(parseBirth({...base,birthTime:'unknown'}));
  assert.equal(actual.bazi.hour,null);
  assert.equal(actual.kongwang.hour,null);
  assert.equal(actual.solar.hour,null);
  assert.equal(actual.hour_unknown,true);
  assert.equal(actual.bazi_str,'丙午 己亥 乙未');
  assert.equal(Object.values(actual.wuxing.count).reduce((n,p)=>n+p.count,0),6);
});

test('拒绝无效日期、输入回退与重复五行',()=>{
  for(const input of [
    {birthDate:'2025-02-29'},{birthDate:'2025-04-31'},{birthTime:'24:00'},
    {birthTime:'午后'},{surname:'123'},{gender:'U'},
    {selectedXiyongShen:['金','金']},{selectedXiyongShen:['风']},
  ]) assert.throws(()=>parseBirth({...base,...input}),InputError);
  assert.doesNotThrow(()=>parseBirth({...base,surname:'欧阳',birthDate:'2024-02-29'}));
});

test('指定五行控制字典与姓名，保留独立系统喜用神',()=>{
  const birth=parseBirth({...base,surname:'欧阳',gender:'female',selectedXiyongShen:['金','木']});
  const analysis=analysisFor(birth);
  assert.deepEqual(analysis.xiyong_shen,['木','火']);
  const preview=libraryFor(birth,analysis);
  assert.deepEqual(preview.xiyong_shen,['金','木']);
  assert.ok(preview.groups.every(g=>g.chars.length===3 && g.total>g.chars.length));
  const library=libraryFor(birth,analysis,0);
  assert.ok(library.groups.every(g=>g.chars.length===g.total));
  const rows=generateNames(birth,analysis);
  assert.equal(rows.length,60);
  assert.equal(new Set(rows.map(name=>name.full_name)).size,60);
  assert.ok(new Set(rows.map(row=>row.score)).size>1,'展示分应该保留候选之间的差别');
  assert.ok(rows.every(row=>row.score>=0&&row.score<=100));
  assert.ok(rows.every(row=>row.full_name.startsWith('欧阳') && row.full_name.length===4 &&
    row.wuxing.every(element=>['金','木'].includes(element)) && row.meaning.length>0));
  assert.deepEqual(rows,generateNames(birth,analysis));
});

test('五类单元素筛选都能产生足量姓名，性别参与排序',()=>{
  for(const element of ELEMENTS) {
    for(const gender of ['male','female']) {
      const birth=parseBirth({...base,gender,selectedXiyongShen:[element]});
      const rows=generateNames(birth,analysisFor(birth));
      assert.equal(rows.length,60,element+gender);
      assert.ok(rows.every(r=>r.wuxing.length===2 && r.wuxing.every(x=>x===element)),element+gender);
    }
  }
});
