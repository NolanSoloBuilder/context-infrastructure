import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';
import {join} from 'node:path';
import {readFileSync} from 'node:fs';
import {NICKNAMES, ENGLISH, CHINESE_SEEDS} from './language-data.mjs';

const require = createRequire(import.meta.url);
let pinyinModule;
try {
  pinyinModule = require('pinyin-pro');
} catch (error) {
  if (error.code !== 'MODULE_NOT_FOUND') throw error;
  const globalModules = execFileSync('npm', ['root','-g'],{encoding:'utf8'}).trim();
  pinyinModule = require(join(globalModules,'pinyin-pro'));
}
export const {pinyin} = pinyinModule;
const catalog = JSON.parse(readFileSync(new URL('../public-catalog.json',import.meta.url)));
const catNames = new Map(catalog['/api/v1/nickname/categories'].data.map(row=>[row.category,row.name]));
const surnames = catalog['/api/v1/foreigner-name/surnames/list?recommended_only=true'].data.surnames;
const asList = value => (Array.isArray(value) ? value : String(value??'').split(',')).map(x=>String(x).trim()).filter(Boolean);
export const clean = value => String(value??'').trim();
export const number = (value,fallback,limit) => Number.isFinite(Number(value)) && Number(value)>0
  ? Math.min(Math.floor(Number(value)),limit) : fallback;
const languageGender = value => ({male:'M',female:'F',1:'M',2:'F'})[value] || value;
const genderOK = (requested,actual) => !['M','F'].includes(requested) || requested===actual || actual==='U';
function stableInt(text) {
  let h=2166136261;
  for(const char of text) h=Math.imul(h ^ char.codePointAt(0),16777619);
  return h>>>0;
}
const feminineNicknames=new Set('朵朵 茉茉 小兰 桃花 莺莺 黛黛 Bella Lulu'.split(' '));
const masculineNicknames=new Set('小虎 牛牛 小龙 小熊 小马 Teddy Leo'.split(' '));
const categories = Object.entries(NICKNAMES).map(([category,entries])=>{
  const names = entries.split(' ').map(entry=>{
    const [nickname,meaning] = entry.split(':');
    const gender=feminineNicknames.has(nickname)?'F':masculineNicknames.has(nickname)?'M':'U';
    return {
      id:stableInt(category+':'+nickname),nickname,meaning,category,category_name:catNames.get(category),
      pinyin:/^[A-Za-z]+$/.test(nickname)?nickname:pinyin(nickname),
      gender,gender_fit_text:gender==='F'?'偏女宝':gender==='M'?'偏男宝':'男女皆宜',cute_score:5,inspiration:catNames.get(category)+'意象',
      personality:meaning,
    };
  }).filter(x=>x.meaning);
  return {category,name:catNames.get(category),count:names.length,names};
});
const nicknameRows = categories.flatMap(category=>category.names);

function recommendNicknames(params,ctx) {
  const chosen=new Set(asList(params.categories));
  const excludes=new Set(asList(params.exclude_ids).map(Number));
  const traits=asList(params.traits);
  const name=clean(params.full_name);
  const month=Number(clean(params.birth_date).slice(5,7));
  const pref=['','冬','冬','春','春','春','夏','夏','夏','秋','秋','秋','冬'][month];
  function match(row) {
    const letterMatches = [...name].some(c=>row.nickname.includes(c));
    const trait = traits.find(t=>row.meaning.includes(t));
    const season = pref && row.category==='season' && row.nickname.includes(pref);
    const reason = letterMatches ? '与大名用字呼应' : trait ? '契合「'+trait+'」的期待' :
      season ? '呼应出生时令' : chosen.has(row.category) ? '符合所选主题' : row.meaning;
    const score=(letterMatches?4:0)+(trait?3:0)+(season?2:0);
    return {...row,match_tags:[reason],recommendation_reason:reason,score};
  }
  const seed=ctx.session+':'+excludes.size+':'+clean(params.gender);
  const ranked=nicknameRows.filter(row=>!excludes.has(row.id)&&(!chosen.size||chosen.has(row.category))
    && genderOK(languageGender(params.gender),row.gender))
    .map(match).sort((a,b)=>b.score-a.score||stableInt(seed+a.id)-stableInt(seed+b.id));
  const unique=new Map();
  for(const row of ranked) if(!unique.has(row.nickname)) unique.set(row.nickname,row);
  const items=[...unique.values()].slice(0,number(params.count,12,36));
  return {items,total:unique.size};
}

const ssa = JSON.parse(readFileSync(new URL('../data/english-ssa-2020-2025.json',import.meta.url)));
const englishCatalog = new Map();
for(const [gender,rows] of Object.entries(ENGLISH)) {
  for(const [name,meaning_cn,origin,formality,tags] of rows) englishCatalog.set(name,{
    id:stableInt('en:'+name),name,gender,meaning_cn,origin,formality,style_tags:tags.split(','),
    culture_safe:'安全',popularity:[],
  });
}
for(const [rank,male,maleCount,female,femaleCount] of ssa.rows) {
  for(const [name,gender,count] of [[male,'M',maleCount],[female,'F',femaleCount]]) {
    let record=englishCatalog.get(name);
    if(!record){
      record={id:stableInt('en:'+name),name,gender,style_tags:[],popularity:[]};
      englishCatalog.set(name,record);
    } else if(!record.meaning_cn && record.gender!==gender) record.gender='U';
    record.popularity.push({gender,rank,count,from_year:ssa.startYear,to_year:ssa.endYear});
  }
}
const englishRows = [...englishCatalog.values()].map(row=>{
  const rank=Math.min(...row.popularity.filter(p=>p.gender===row.gender||row.gender==='U').map(p=>p.rank));
  return {...row,pop_rank_us:Number.isFinite(rank)?rank:null,
    pop_us:rank<=50?'高':rank<=150?'中':rank<=200?'低':'未列入前200'};
});
const englishIndex = new Map(englishRows.map(row=>[row.id,row]));

function englishFilter(body, search=false) {
  const gender=languageGender(body.gender);
  const keyword=clean(body.keyword).toLowerCase();
  const styles=asList(body.style_tags);
  const levels=asList(body.popularity);
  const formality=clean(body.formality);
  const chinese=clean(body.chinese_name);
  const initials=chinese ? pinyin(chinese,{toneType:'none',type:'array'}).map(pronunciation=>pronunciation[0]?.toLowerCase()) : [];
  const results=englishRows.filter(row=>genderOK(gender,row.gender))
    .filter(row=>!search||row.name.toLowerCase().includes(keyword)||row.meaning_cn?.includes(keyword))
    .filter(row=>!levels.length||levels.includes(row.pop_us))
    .filter(row=>!formality||row.formality===formality);
  return results.map(row=>{
    const stylesMatched=styles.filter(style=>row.style_tags.includes(style));
    const initialsMatch=initials.includes(row.name[0].toLowerCase());
    return {...row,
      match_score:80+Math.min(10,4*stylesMatched.length)+(initialsMatch?7:0)+(row.gender===gender?3:0),
      match_reason:[stylesMatched.length?'风格匹配：'+stylesMatched.join('、'):'',
        initialsMatch?'首字母与中文名拼音呼应':'',formality?'适合'+formality+'场合':''].filter(Boolean).join(' · '),
    };
  }).sort((a,b)=>b.match_score-a.match_score||Number(!!b.meaning_cn)-Number(!!a.meaning_cn)
    || (a.pop_rank_us??Infinity)-(b.pop_rank_us??Infinity)||a.name.localeCompare(b.name));
}

const foreignRows = CHINESE_SEEDS.map(([given_name,gender,meaning_tags,meaning_en,chars])=>{
  const notation=pinyin(given_name,{type:'array'});
  const char_breakdown_en=[...chars.matchAll(/(\p{Script=Han}):([^\p{Script=Han}]+)/gu)].map((m,i)=>({
    char:m[1],pinyin:notation[i],meaning:m[2].trim(),meaning_en:m[2].trim(),
  }));
  const initials=pinyin(given_name,{toneType:'none',type:'array'});
  const hardSyllables=initials.filter(text=>/^(zh|ch|sh|[jqxzcsy]|r)/i.test(text)).length;
  const difficulty=hardSyllables>=2?'hard':hardSyllables?'medium':'easy';
  return {
    id:stableInt('cn:'+given_name),given_name,gender,meaning_tags,meaning_en,meaning_short_en:meaning_en,
    pinyin:notation.join(' '),pronounce_difficulty:difficulty,char_breakdown_en,
    pronunciation_guide:notation.join(' · '),origin_en:'Modern given name formed from Chinese characters',
  };
});

function pageOf(rows, params, field) {
  const page=number(params.page,1,100000);
  const pageSize=number(params.page_size ?? params.size,20,100);
  return {[field]:rows.slice((page-1)*pageSize,page*pageSize),total:rows.length,page,page_size:pageSize,size:pageSize};
}

export async function handleLanguages(req,res,url,ctx) {
  const leaf=decodeURIComponent(url.pathname).replace(/^\/api\/v1/,'');
  const query=Object.fromEntries(url.searchParams);
  const method=req.method;
  if(method==='GET' && leaf==='/tools/unlock/status'){
    return Object.fromEntries(['nickname','english_name','chinese_name','poem_tool','parents_naming'].map(key=>[
      key,{unlocked:true,price:0,original_price:0,package_id:null},
    ]));
  }
  if(method==='GET' && leaf==='/nickname/categories') return categories.map(({names,...category})=>category);
  if(method==='GET' && leaf==='/nickname/recommend') return recommendNicknames(query,ctx);
  if(method==='GET' && /^\/nickname\/\d+$/.test(leaf)) {
    return nicknameRows.find(row=>row.id===Number(leaf.split('/').at(-1))) ?? ctx.fail(404,'未找到这个小名',404);
  }
  if(method==='GET'&&leaf==='/english-name/stats/overview'){
    return {total:englishRows.length,by_gender:Object.fromEntries(['M','F','U'].map(k=>[k,englishRows.filter(row=>row.gender===k).length])),
      by_popularity:Object.fromEntries(['高','中','低','未列入前200'].map(k=>[k,englishRows.filter(row=>row.pop_us===k).length]))};
  }
  if(method==='POST'&&leaf==='/english-name/recommend'){
    const body=await ctx.body();
    return pageOf(englishFilter(body),body,'names');
  }
  if(method==='GET'&&leaf==='/english-name/search') return pageOf(englishFilter(query,true),query,'names');
  if(method==='GET'&&/^\/english-name\/\d+(\/popularity)?$/.test(leaf)){
    const row=englishIndex.get(Number(leaf.split('/')[2]));
    if(!row) return ctx.fail(404,'未找到这个英文名',404);
    if(leaf.endsWith('/popularity')){
      const country=query.country||'US';
      const records=country==='US'?row.popularity:[];
      return {country,data:records,history:records,source:country==='US'?ssa.source:null};
    }
    return row;
  }
  if(method==='GET'&&leaf==='/foreigner-name/surnames/list') {
    const list=surnames.filter(row=>!query.difficulty||row.pronounce_difficulty===query.difficulty);
    return {total:list.length,surnames:list};
  }
  if(method==='GET'&&leaf==='/foreigner-name/stats') return {total:foreignRows.length};
  if(method==='GET'&&['/foreigner-name/list','/foreigner-name/random'].includes(leaf)){
    const tags=asList(query.meaning_tags);
    const matched=foreignRows.filter(row=>genderOK(languageGender(query.gender),row.gender))
      .filter(row=>!query.difficulty||row.pronounce_difficulty===query.difficulty)
      .filter(row=>!tags.length||tags.some(tag=>row.meaning_tags.split(',').includes(tag)));
    if(leaf.endsWith('/list')) return pageOf(matched,query,'names');
    const randomized=[...matched];
    for(let i=randomized.length-1;i>0;i--){
      const j=Math.floor(Math.random()*(i+1));
      [randomized[i],randomized[j]]=[randomized[j],randomized[i]];
    }
    return {names:randomized.slice(0,number(query.count,1,5)),total:matched.length};
  }
  if(method==='GET'&&/^\/foreigner-name\/\d+$/.test(leaf)) {
    return foreignRows.find(row=>row.id===Number(leaf.split('/').at(-1))) ?? ctx.fail(404,'未找到这个中文名',404);
  }
}
