import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {analyzeBirth, ELEMENTS} from './calendar.mjs';

const library = JSON.parse(readFileSync(new URL('../data/original-public-library.json', import.meta.url)));
const characters = new Map(library.characters.filter(row=>ELEMENTS.includes(row.wuxing))
  .map(row=>[row.character,row]));
const knownNames = new Set(library.popularNames.map(row=>row.name));
const safeCharacters = new Set([...
  '安宁允宇宸辰轩逸远屿岑岩峻岳坤垣羽岚恩亦彧砚衡予昀昕晗晟煦昭晞景明朗曜晴星灿熹暖冉彤晔晖焕旭烁炜知瑾珏瑜瑞珂琛玥瑶珩琰珍琳璟琬钧钦锐铭铎锡锦铮铠书言信承修初思成少仁善诗如静舒素真心川千清澄沐沅洛洵澜洋汀源津泓涵润淳泽洺洲澍霖雨雪霁云露雯希文翰行闻白北牧眠湄微汐沁恬伊南和音歌雅乔楷梓柯柠栩桐梧松柏楠榆栖若芷芮芊芸苒茵芙茉菡蕙萱蓁萍芃荷蔚竹筠筱笙简策楚苏槿棠柳禾穗茗兰宜嘉元季语颂奕弈彦杰英可欣君仪月忆羽友有乐忻怡念柔美清欣']);
const poems = new Map([
  ['嘉树',{title:'九章·橘颂',poem:'后皇嘉树，橘徕服兮。'}],
  ['清扬',{title:'郑风·野有蔓草',poem:'有美一人，清扬婉兮。'}],
  ['清和',{title:'游赤石进帆海',poem:'首夏犹清和，芳草亦未歇。'}],
  ['清圆',{title:'苏幕遮·燎沉香',poem:'叶上初阳干宿雨、水面清圆，一一风荷举。'}],
  ['嘉言',{title:'尚书·大禹谟',poem:'嘉言罔攸伏，野无遗贤，万邦咸宁。'}],
  ['景明',{title:'岳阳楼记',poem:'至若春和景明，波澜不惊。'}],
  ['思齐',{title:'论语·里仁',poem:'见贤思齐焉，见不贤而内自省也。'}],
  ['静姝',{title:'邶风·静女',poem:'静女其姝，俟我于城隅。'}],
  ['攸宁',{title:'小雅·斯干',poem:'君子攸宁。'}],
  ['维桢',{title:'大雅·文王',poem:'王国克生，维周之桢。'}],
  ['令仪',{title:'小雅·湛露',poem:'岂弟君子，莫不令仪。'}],
  ['令闻',{title:'大雅·卷阿',poem:'颙颙卬卬，如圭如璋，令闻令望。'}],
]);

export const NAME_LIMIT = 60;
const GENDER_WEIGHT = 1.7;
const MIXED_ELEMENTS_BONUS = 3;
const CLASSICAL_SOURCE_BONUS = 13;
const MAX_RANK_SCORE = 100 + 5*GENDER_WEIGHT + MIXED_ELEMENTS_BONUS + CLASSICAL_SOURCE_BONUS;
const rankFor = (row,gender) => row.recommendationScore
  + (gender === 'female' ? row.genderTendency-5 : 5-row.genderTendency)*GENDER_WEIGHT;
const compare = (gender) => (a,b)=>rankFor(b,gender)-rankFor(a,gender)
  || a.strokes-b.strokes || a.character.localeCompare(b.character,'zh-CN');

function candidateRows(element,gender) {
  return [...characters.values()].filter(row=>row.wuxing===element)
    .filter(row=>gender==='female' ? row.genderTendency>=3 : row.genderTendency<=7)
    .sort(compare(gender));
}

export const effectiveElements = (birth, analysis) =>
  birth.selected.length ? birth.selected : analysis.xiyong_shen;

export function analysisFor(birth) {
  const analysis = analyzeBirth(birth);
  const elements = effectiveElements(birth,analysis);
  const per_wuxing = elements.map(wuxing=>({wuxing,count:candidateRows(wuxing,birth.gender).length}));
  const picked_count = per_wuxing.reduce((sum,group)=>sum+group.count,0);
  return {...analysis,naming_char_stats:{
    gender:birth.gender==='male'?1:2,per_wuxing,picked_count,combo_max:picked_count*(picked_count-1),
  }};
}

export function libraryFor(birth, analysis, limit = 3, favorites = new Set()) {
  const elements = effectiveElements(birth,analysis);
  return {
    xiyong_shen:elements,locked:false,
    groups:elements.map(wuxing=>{
      const rows = candidateRows(wuxing,birth.gender);
      return {wuxing,total:rows.length,chars:rows.slice(0,limit||undefined).map(row=>({
        character:row.character,pinyin:row.pinyin,wuxing,
        name_connotation:row.nameConnotation,recommendation_score:row.recommendationScore,
        gender_tendency:row.genderTendency,strokes:row.strokes,
        favorited:favorites.has(row.character),
      }))};
    }),
  };
}

const plainPinyin = pinyin=>pinyin.toLowerCase().normalize('NFD').replace(/\p{M}/gu,'');
const shortMeaning = value=>value?.replace(/(?:之)?义[。！]?$/,'') || '用字寓意';
const compareCandidate = (a,b)=>b.quality-a.quality || a.digits-b.digits || a.given.localeCompare(b.given,'zh-CN');

export function generateNames(birth,analysis) {
  const elements = effectiveElements(birth,analysis);
  const ranked = elements.flatMap(element=>candidateRows(element,birth.gender));
  const pool = ranked.filter(row=>safeCharacters.has(row.character));
  const candidateMap = new Map();
  const surname = [...birth.surname];
  const lastSyllable = characters.get(surname.at(-1))?.pinyin;
  function add(first,second,reference) {
    if (!first || !second || first.character===second.character ||
        surname.includes(first.character) || surname.includes(second.character) ||
        !elements.includes(first.wuxing) || !elements.includes(second.wuxing)) return;
    if (plainPinyin(first.pinyin)===plainPinyin(second.pinyin) ||
        (lastSyllable && plainPinyin(first.pinyin)===plainPinyin(lastSyllable))) return;
    const given = first.character+second.character;
    const quality = (rankFor(first,birth.gender)+rankFor(second,birth.gender))/2
      + (first.wuxing!==second.wuxing?MIXED_ELEMENTS_BONUS:0) + (reference?CLASSICAL_SOURCE_BONUS:0)
      - (knownNames.has(given)?6:0) - Math.abs(first.strokes-second.strokes)*0.32;
    const digest = createHash('sha256').update(birth.surname+given).digest('hex');
    candidateMap.set(given,{given,quality,digits:parseInt(digest.slice(0,8),16),first,second,reference});
  }
  for (const first of pool) for (const second of pool) add(first,second);
  for (const [given,source] of poems) {
    const [first,second] = [...given].map(char=>characters.get(char));
    add(first,second,source);
  }
  const ordered = [...candidateMap.values()].sort(compareCandidate);
  const usage = new Map();
  const chosen = [];
  for (const candidate of ordered) {
    const chars = [...candidate.given];
    if (chars.some(ch=>(usage.get(ch)||0)>=8)) continue;
    chosen.push(candidate);
    for (const ch of chars) usage.set(ch,(usage.get(ch)||0)+1);
    if (chosen.length===NAME_LIMIT) break;
  }
  if (chosen.length<NAME_LIMIT) {
    const used = new Set(chosen.map(candidate=>candidate.given));
    chosen.push(...ordered.filter(candidate=>!used.has(candidate.given)).slice(0,NAME_LIMIT-chosen.length));
  }
  return chosen.map((row,index)=>{
    const givenChars = [row.first,row.second];
    return {
      index, name:row.given,surname:birth.surname,full_name:birth.surname+row.given,
      pinyin:givenChars.map(ch=>ch.pinyin).join(' '),wuxing:givenChars.map(ch=>ch.wuxing),
      meaning:givenChars.map(ch=>`${ch.character}取“${shortMeaning(ch.nameConnotation)}”之意`).join('，')+'。',
      source:row.reference || null,score:Math.round(100*Math.max(0,Math.min(1,row.quality/MAX_RANK_SCORE))),
      givenChars,
    };
  });
}
