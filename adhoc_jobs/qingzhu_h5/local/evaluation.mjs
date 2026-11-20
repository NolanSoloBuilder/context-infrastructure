import {readFileSync} from 'node:fs';
import {analyzeBirth,parseBirth,InputError} from '../bazi/calendar.mjs';
import {number,pinyin} from './languages.mjs';

const library=JSON.parse(readFileSync(new URL('../data/original-public-library.json',import.meta.url)));
const catalog=JSON.parse(readFileSync(new URL('../public-catalog.json',import.meta.url)));
const poetry=JSON.parse(readFileSync(new URL('../data/naming-poetry.json',import.meta.url))).names;
const zodiacData=JSON.parse(readFileSync(new URL('../data/tool-public-snapshots.json',import.meta.url)));
const characters=new Map(library.characters.map(row=>[row.character,row]));
const surnames=(catalog['/api/v1/tools/surnames?page=1&size=100'].data.list||[]);
const surnameByText=new Map(surnames.map(row=>[row.surname,row]));
const compound=new Set('欧阳 司马 上官 诸葛 东方 皇甫 尉迟 公孙 慕容 独孤 司徒 司空 夏侯 令狐 长孙 端木 百里 南宫 万俟 闻人 乐正 赫连 钟离 宇文 申屠 东郭 第五 单于'.split(' '));
const levels=['未评估','待参考','较弱','中等','良好','优秀'];
const level=score=>levels[score>=90?5:score>=80?4:score>=70?3:2];
const positive=new Set([1,3,5,6,7,8,11,13,15,16,17,18,21,23,24,25,29,31,32,33,35,37,39,41,45,47,48,52,57,61,63,65,67,68,81]);
const mixed=new Set([26,27,30,36,38,42,51,55,58,71,72,73,75,77,78]);
const toneNames=['轻声','阴平','阳平','上声','去声'];
const badSounds={shibai:'失败',shiwang:'失望',wuneng:'无能',wuzhi:'无知',shangxin:'伤心',beiju:'悲剧'};
const toolsName=Object.freeze({phonetic:[15,'音韵美感'],glyph:[10,'字形结构'],meaning:[20,'字义内涵'],
  combination:[15,'姓名整体'],wuxing:[15,'五行匹配'],wuge:[15,'五格三才'],zodiac:[5,'生肖宜忌'],culture:[5,'文化关联']});

export function initEvaluation(db) {
  db.exec(`CREATE TABLE IF NOT EXISTS local_test_reports (
    id INTEGER PRIMARY KEY, session TEXT NOT NULL, created TEXT NOT NULL,
    fingerprint TEXT NOT NULL, report TEXT NOT NULL, UNIQUE(session,fingerprint));`);
}

function detect(raw,ctx) {
  const value=String(raw??'').trim();
  if(!/^[\p{Script=Han}]{2,4}$/u.test(value)) return ctx.fail(1001,'请输入 2 至 4 个汉字的完整姓名');
  const chars=[...value];
  const prefix=chars.slice(0,2).join('');
  const length=chars.length>2&&compound.has(prefix)?2:1;
  return {surname:chars.slice(0,length).join(''),name:chars.slice(length).join('')};
}

function wugeAnalysis(chars,surnameLength) {
  if(chars.some(x=>!x.strokes)) return null;
  const left=chars.slice(0,surnameLength).map(x=>x.strokes);
  const right=chars.slice(surnameLength).map(x=>x.strokes);
  const sum=nums=>nums.reduce((a,b)=>a+b,0);
  const total=sum(left)+sum(right);
  const tens=value=>[...'水木木火火土土金金水'][value%10];
  const numberEntry=value=>{
    const luck=positive.has(value)?'吉':mixed.has(value)?'半吉':'凶';
    return {value,wuxing:tens(value),luck,meaning:'按传统笔画数理参考'};
  };
  const tiange=numberEntry(sum(left)+(left.length===1?1:0));
  const renge=numberEntry(left.at(-1)+right[0]);
  const dige=numberEntry(sum(right)+(right.length===1?1:0));
  const waige=numberEntry((left.length===1?1:left[0])+(right.length===1?1:sum(right.slice(1))));
  const zonge=numberEntry(total);
  const tally=[tiange,renge,dige,waige,zonge];
  const scores={吉:95,半吉:75,凶:55};
  const score=Math.round(tally.reduce((a,b)=>a+scores[b.luck],0)/5);
  return {tiange,renge,dige,waige,zonge,zongge:zonge,score,
    sanCai:tally.slice(0,3).every(x=>x.luck==='吉')?'吉':'半吉',
    sanCaiWuxing:[tiange.wuxing,renge.wuxing,dige.wuxing],
    evaluation:'按本地字库笔画计算，五格数理仅作传统参考。'};
}

function createReport(body,ctx) {
  const surname=String(body.surname??'').trim(), name=String(body.name??'').trim();
  if(!/^[\p{Script=Han}]{1,2}$/u.test(surname)||!/^[\p{Script=Han}]{1,3}$/u.test(name)){
    return ctx.fail(1001,'请填写有效的姓氏和名字');
  }
  const gender=({男:'male',女:'female',male:'male',female:'female'})[body.gender];
  const fullName=surname+name;
  let birth;
  try{
    birth=parseBirth({surname,gender,birthDate:body.birth_date,birthTime:body.birth_hour||'unknown',
      selectedXiyongShen:body.selected_xiyong_shen||[]});
  } catch(error){
    if(error instanceof InputError) return ctx.fail(1001,error.message);
    throw error;
  }
  const analysis=analyzeBirth(birth);
  const notation=pinyin(fullName,{type:'array'});
  const numeric=pinyin(fullName,{type:'array',toneType:'num'});
  const sound=pinyin(fullName,{type:'array',toneType:'none'});
  const chars=[...fullName].map((char,i)=>{
    const row=characters.get(char);
    const tone=Number(numeric[i]?.match(/[1-5]$/)?.[0]||0)%5;
    return {char,pinyin:notation[i]||char,tone,toneName:toneNames[tone],wuxing:row?.wuxing||'',
      strokes:row?.strokes??null,meaning:row?.nameConnotation||'',nameUsage:row?.nameConnotation||'',
      isSurname:i<[...surname].length,genderTendency:row?.genderTendency,
      genderDescription:row?.genderTendencyDesc,recommendationScore:row?.recommendationScore,
      recommendation:row?.rating||'',isCommon:!!row};
  });
  const nameChars=chars.filter(char=>!char.isSurname);
  const tones=chars.map(char=>char.tone);
  const toneVariation=new Set(tones).size;
  const hasDieyin=sound.some((value,index)=>index>0&&value===sound[index-1]);
  const homophone=badSounds[sound.slice([...surname].length).join('')]||'';
  const strokes=chars.map(char=>char.strokes).filter(x=>x!==null);
  const fullStrokeCoverage=strokes.length===chars.length;
  const totalStrokes=strokes.reduce((a,b)=>a+b,0);
  const balance=fullStrokeCoverage&&Math.max(...strokes)-Math.min(...strokes)<=9;
  const favorable=birth.selected.length?birth.selected:analysis.xiyong_shen;
  const matching=nameChars.filter(char=>favorable.includes(char.wuxing)).length;
  const rated=nameChars.filter(char=>Number.isFinite(char.recommendationScore));
  const wuge=wugeAnalysis(chars,[...surname].length);
  const poem=Object.hasOwn(poetry,name)?poetry[name]:null;
  const poemSource=poem?{title:poem[0],source:poem[4],verse:poem[1],author:poem[2],dynasty:poem[3]}:null;
  const zodiacProfile=zodiacData.zodiac[analysis.zodiac.name];
  const zodiacCharacters=zodiacData.zodiacCharacters[analysis.zodiac.name];
  const favorableChars=new Set((zodiacCharacters?.radical_characters||[])
    .flatMap(group=>group.characters.map(row=>row.character)));
  const zodiacMatches=nameChars.filter(row=>favorableChars.has(row.char)).map(row=>row.char);
  const scores={
    phonetic:Math.max(50,76+toneVariation*5-(hasDieyin?7:0)-(homophone?15:0)),
    glyph:fullStrokeCoverage?(balance?90:76):null,
    meaning:rated.length?Math.round(rated.reduce((n,c)=>n+c.recommendationScore,0)/rated.length):null,
    combination:homophone?68:hasDieyin?79:86,
    wuxing:nameChars.some(x=>x.wuxing)?Math.round(61+38*matching/nameChars.length):null,
    wuge:wuge?.score??null,zodiac:zodiacMatches.length?Math.round(78+20*zodiacMatches.length/nameChars.length):null,culture:poemSource?95:null,
  };
  const scoreBreakdown=Object.fromEntries(Object.entries(toolsName).map(([key,[weight,title]])=>[
    key,{name:title,score:scores[key]??0,weight:scores[key]===null?0:weight,
      level:scores[key]===null?'未评估':level(scores[key])},
  ]));
  const dimensions=Object.values(scoreBreakdown);
  const totalScore=Math.round(dimensions.reduce((n,d)=>n+d.score*d.weight,0)/dimensions.reduce((n,d)=>n+d.weight,0));
  const origin=surnameByText.get(surname);
  const stamp=new Date().toISOString();
  const report={
    surname,name,fullName,gender:gender==='male'?'男':'女',birthDate:birth.birthDate,birthHour:birth.unknown?'不清楚':body.birth_hour||birth.time,
    totalScore,scoreBreakdown,charAnalysis:chars,unlockLevel:'TR3',llmUsed:false,
    safetyCheck:{isSafe:!homophone,hasBadHomophone:!!homophone,hasSensitiveWord:false,llmChecked:false,
      warnings:homophone?['读音接近「'+homophone+'」，建议结合方言再确认']:[]},
    surnameDetail:{surname,pinyin:pinyin(surname),origin:origin?.originBrief||'',rank:origin?.rank},
    phoneticAnalysis:{tonePattern:chars.map(x=>x.toneName).join(' → '),tones,hasRhythm:toneVariation>1,
      hasDieyin,hasShuangsheng:false,pinyinFull:notation.join(' '),chars,
      toneComment:toneVariation>1?'声调变化清楚':'声调较集中，可连读检查'},
    glyphAnalysis:{strokes,totalStrokes,avgStrokes:strokes.length?Math.round(10*totalStrokes/strokes.length)/10:0,
      chars,surnameChars:chars.filter(x=>x.isSurname),nameChars,isBalanced:balance,
      strokeComment:fullStrokeCoverage?'按本地用字库记录计算笔画':'部分用字没有本地笔画记录'},
    wugeAnalysis:wuge,
    wuxingAnalysis:{nameWuxing:nameChars.map(x=>x.wuxing),xiyongShen:favorable,yongshen:favorable,
      baziWuxing:analysis.wuxingWithCangGan,jishen:analysis.ji_shen,hasDeficiency:analysis.wuxing.lack.length>0,
      deficiency:analysis.wuxing.lack},
    baziPaipan:{bazi:analysis.bazi,bazi_str:analysis.bazi_str,riGan:analysis.riGan,kongwang:analysis.kongwang},
    wuxingEnergy:{wuxing:Object.fromEntries(Object.entries(analysis.wuxing.count).map(([k,v])=>[k,v.count])),
      wuxingWithCangGan:analysis.wuxingWithCangGan,lack:analysis.wuxing.lack,excess:analysis.wuxing.excess},
    yongShenDetail:{...analysis.yong_shen_detail,reasoning:analysis.yongshen_reasoning},
    riZhuStrength:analysis.riZhuStrength,pattern:analysis.pattern,
    selectedXiyongShen:birth.selected,systemXiyongShen:analysis.xiyong_shen,xiyongSource:birth.selected.length?'parent':'system',
    zodiacAnalysis:{zodiac:analysis.zodiac.name,year:birth.year,traits:zodiacProfile?.basic?.description||analysis.zodiac.description,
      favorable:zodiacMatches,unfavorable:[],likeRules:[],avoidRules:[],
      evaluation:zodiacMatches.length?'用字「'+zodiacMatches.join('、')+'」出现在公开生肖宜用字目录。':
        '本次用字未命中已收录的生肖宜用字。'},
    combinationAnalysis:{score:scores.combination,level:level(scores.combination),
      overallImpression:matching?'名字读音有可辨识度，部分用字符合所选喜用五行。':'可结合姓氏读音与使用场景复核。'},
    cultureAnalysis:{hasPoem:!!poemSource,poemSource},poemSource,
  };
  const key=JSON.stringify([surname,name,gender,birth.birthDate,birth.time,birth.selected]);
  ctx.db.prepare('INSERT OR IGNORE INTO local_test_reports(session,created,fingerprint,report) VALUES (?,?,?,?)')
    .run(ctx.session,stamp,key,JSON.stringify(report));
  const row=ctx.db.prepare('SELECT id,report,created FROM local_test_reports WHERE session=? AND fingerprint=?').get(ctx.session,key);
  return {...JSON.parse(row.report),id:row.id,reportId:row.id,createdAt:row.created};
}

export async function handleEvaluation(req,res,url,ctx) {
  const path=url.pathname;
  if(!path.startsWith('/api/v1/test-name/')) return;
  const route=req.method+' '+path.slice('/api/v1/test-name/'.length);
  if(route==='GET detect-surname') return detect(url.searchParams.get('fullName'),ctx);
  if(['POST analyze','POST unlock','POST unlock-vip','POST redeem-unlock'].includes(route)){
    return createReport(await ctx.body(),ctx);
  }
  if(route==='GET report'){
    const id=Number(url.searchParams.get('id'));
    const row=ctx.db.prepare('SELECT id,report,created FROM local_test_reports WHERE id=? AND session=?').get(id,ctx.session);
    if(!row) return ctx.fail(404,'未找到这份测评',404);
    return {...JSON.parse(row.report),id:row.id,reportId:row.id,createdAt:row.created};
  }
  if(route==='GET history'){
    const size=number(url.searchParams.get('pageSize'),20,50);
    const page=number(url.searchParams.get('page'),1,9999);
    const rows=ctx.db.prepare('SELECT id,report,created FROM local_test_reports WHERE session=? ORDER BY id DESC LIMIT ? OFFSET ?')
      .all(ctx.session,size,(page-1)*size);
    const total=ctx.db.prepare('SELECT count(*) AS n FROM local_test_reports WHERE session=?').get(ctx.session).n;
    return {items:rows.map(row=>{
      const {fullName,surname,name,gender,birthDate,birthHour,totalScore,unlockLevel}=JSON.parse(row.report);
      return {id:row.id,fullName,surname,name,gender,birthDate,birthHour,totalScore,unlockLevel,createdAt:row.created};
    }),total};
  }
}
