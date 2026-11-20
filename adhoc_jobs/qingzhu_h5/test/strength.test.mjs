import {readFileSync} from 'node:fs';
import assert from 'node:assert/strict';
import {test} from 'node:test';
import {analyzeBirth,parseBirth} from '../bazi/calendar.mjs';

const fixtures = JSON.parse(readFileSync(new URL('./original-strength-samples.json',import.meta.url)));
const pad = value=>String(value).padStart(2,'0');

function evaluate({input,expected}) {
  const birth = parseBirth({
    surname:'林',gender:input.gender===1?'male':'female',
    birthDate:[input.year,pad(input.month),pad(input.day)].join('-'),
    birthTime:[pad(input.hour),pad(input.minute)].join(':'),
  });
  const actual = analyzeBirth(birth);
  return {
    pillars:actual.bazi_str===expected.baziString,
    difference:Math.abs(actual.riZhuStrength.score-expected.riZhuStrength.score),
    level:actual.riZhuStrength.level===expected.riZhuStrength.level,
    favorable:actual.xiyong_shen.join('')===expected.yongShen.yong+expected.yongShen.xi,
  };
}

test('108 个公开样本的四柱与原站一致',()=>{
  assert.equal(fixtures.length,108);
  for (const fixture of fixtures) assert.equal(evaluate(fixture).pillars,true,JSON.stringify(fixture.input));
});

test('36 个未参与校准的样本保持评分和等级精度',()=>{
  const results = fixtures.filter(row=>row.group==='holdout').map(evaluate);
  assert.equal(results.length,36);
  assert.ok(results.filter(result=>result.difference===0).length>=20);
  assert.ok(results.every(result=>result.difference<=2));
  assert.ok(results.reduce((sum,result)=>sum+result.difference,0)/results.length<=0.5);
  assert.ok(results.every(result=>result.level));
  assert.ok(results.filter(result=>result.favorable).length>=33);
});
