import assert from 'node:assert/strict';
import { test } from 'node:test';
import { DatabaseSync } from 'node:sqlite';
import { handleTools } from '../local/tools.mjs';

async function useTools(path, body, opts={}) {
  const prefix = path.startsWith('/') ? '' : '/api/v1/tools/';
  const url = new URL(prefix + path, 'http://localhost:8080');
  return await handleTools({method:opts.method ?? (body === undefined ? 'GET' : 'POST')},{},url,{
    db:opts.db, session:opts.session ?? 'anon', body:async()=>body,
    fail(code,message){ throw Object.assign(new Error(message),{code}); },
  });
}

test('calendar and chart compute from the supplied date rather than reusing fixtures', async ()=>{
  const date = await useTools('almanac?query_date=2024-02-10');
  assert.equal(date.date.lunar.day,1);
  assert.equal(date.date.lunar.month,1);
  assert.equal(date.date.lunar.zodiac,'龙');
  assert.equal(date.shichen.length,12);
  assert.ok(date.festivals.lunar.includes('春节'));
  await assert.rejects(useTools('almanac?query_date=2025-02-29'),{code:1001});
  const input = {year:2026,month:11,day:17,hour:12,minute:0,gender:1};
  const first = await useTools('bazi',input);
  const second = await useTools('bazi',{...input,hour:0});
  assert.equal(first.bazi.day.ganzhi,'乙未');
  assert.notEqual(first.bazi.hour.ganzhi,second.bazi.hour.ganzhi);
  assert.ok(first.dayun.list.length>5);
  assert.equal(first.liunian.current.year,first.liunian.list[0].year);
  assert.ok(first.luckyElements.color.length);
});
test('classic dictionaries support lookup, filtering, pagination and collecting', async ()=>{
  const index = await useTools('surnames?keyword=ōuyáng');
  assert.equal(index.total,1);
  assert.equal(index.list[0].surname,'欧阳');
  assert.equal((await useTools('/api/v1/surnames/欧阳/exists')).exists,true);
  assert.ok((await useTools('surnames/欧阳')).origin);
  const filter = await useTools('naming-characters?wuxing=木&strokes=6-8&min_score=90&page=2&size=5');
  assert.equal(filter.page,2);
  assert.equal(filter.list.length,5);
  assert.ok(filter.list.every((row)=>row.wuxing==='木'&&row.strokes>=6&&row.strokes<=8&&row.recommendationScore>=90));
  const db = new DatabaseSync(':memory:');
  const opts = {db};
  assert.equal((await useTools('naming-characters/林',undefined,opts)).is_collected,false);
  await useTools('naming-characters/林/collect?action=collect',{},opts);
  assert.equal((await useTools('naming-characters/林',undefined,opts)).is_collected,true);
  await useTools('naming-characters/林/collect?action=uncollect',{},opts);
  assert.equal((await useTools('naming-characters/林',undefined,opts)).is_collected,false);
  const classical = await useTools('shuowen/char/林');
  assert.equal(classical.has_shuowen,true);
  assert.equal(classical.radical,'木');
  assert.equal(classical.shuowen_radical,'林');
  assert.equal((await useTools('shuowen/char/龙')).traditional_form,'龍');
  assert.ok(classical.explanation.includes('木'));
  const page = await useTools('shuowen/radical/木?size=6&page=2');
  assert.equal(page.items.length,6);
  assert.ok(page.items.every((row)=>row.radical==='木'));
  assert.ok((await useTools('shuowen/pinyin/l')).total>20);
  db.close();
});
test('tool lists filter and paginate the local reference catalogs', async ()=>{
  const db = new DatabaseSync(':memory:');
  const opts = {db,session:'abc'};
  const first = await useTools('funny-names?page=1&size=5',undefined,opts);
  const second = await useTools('funny-names?page=2&size=5',undefined,opts);
  assert.ok(first.list[0].id!==second.list[0].id);
  assert.ok(first.total>100);
  const id=first.list[0].id;
  assert.equal((await useTools(`funny-names/${id}/like`,{},opts)).isLiked,true);
  assert.equal((await useTools('funny-names?page=1&size=5',undefined,opts)).list[0].isLiked,true);
  assert.equal((await useTools('funny-names?page=1&size=5',undefined,{...opts,session:'xyz'})).list[0].isLiked,false);
  assert.equal((await useTools(`funny-names/${id}/like`,{},opts)).isLiked,false);
  assert.ok((await useTools('homophone-names?page=2&size=5',undefined,opts)).list.every((r)=>r.homophone));
  const popular = await useTools('popular-names?decade=2020s&gender=2');
  assert.ok(popular.list.every((row)=>row.decade==='2020s'&&row.gender===2));
  assert.equal((await useTools('popular-names/check?name=子涵')).found,true);
  assert.equal((await useTools('popular-names/check?name=𠮷𠮷𠮷')).found,false);
  db.close();
});
test('zodiac and constellation lookups include their lists, pairings and details', async ()=>{
  assert.equal((await useTools('zodiac/by-year',{year:1993})).zodiac,'鸡');
  assert.ok((await useTools('zodiac/characters/鸡?limit=4')).radical_characters.every((row)=>row.characters.length<=4));
  assert.ok((await useTools('zodiac/compatibility',{zodiac1:'马',zodiac2:'羊'})).analysis.love);
  assert.equal((await useTools('constellation/by-birthday?month=2&day=29',{})).constellation,'双鱼座');
  assert.ok((await useTools('constellation/白羊座')).personality.positive.length);
  const today = await useTools('constellation/today');
  assert.equal(today.ranking.length,12);
  assert.ok(today.ranking[0].score>=today.ranking.at(-1).score);
});
test('actual name generation works with surnames, books, score combinations and pagination', async ()=>{
  const results = await useTools('poem-naming/generate?book_id=tangshi&surname=王&count=6',{});
  assert.equal(results.names.length,6);
  assert.ok(results.names.every((row)=>row.fullName.startsWith('王')&&row.poem.book==='唐诗'));
  const parents = await useTools('parents-naming/generate?count=200&father_surname=林&mother_surname=陈',{});
  assert.equal(parents.names.length,200);
  assert.ok(parents.names.every((row)=>row.fullName.startsWith('林')));
  assert.ok(parents.names.some((row)=>['同音','同偏旁','直接包含','五行相生'].includes(row.matchType)));
  const rank = await useTools('wuge',{surname:'欧阳',gender:'female',limit:3});
  assert.equal(rank.combinations.length,3);
  assert.equal(rank.combinations[0].wuge.tiange.value,rank.surname_strokes);
  assert.ok(rank.combinations[0].sample_names.every((row)=>row.name.startsWith('欧阳')));
  const premium = await useTools('premium-names/generate?count=6&offset=0&surname=林',{});
  const next = await useTools('premium-names/generate?count=6&offset=6&surname=林',{});
  assert.ok(premium.names.every((row)=>!row.isLocked&&row.fullName.startsWith('林')));
  assert.ok(next.names.every((row)=>!premium.names.find((item)=>item.name===row.name)));
});
