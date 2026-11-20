import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {once} from 'node:events';
import {AI_MODEL,GenerationError,gatewayCredential,prepareGatewayPayload,streamRecommendations,validateRecommendation} from './ai-gateway.mjs';
import {analyzeBirth, ELEMENTS, parseBirth} from '../bazi/calendar.mjs';
import {namedCharacter} from './tools.mjs';

const dictionary = JSON.parse(readFileSync(new URL('../data/original-public-library.json', import.meta.url)));
const corpus = JSON.parse(readFileSync(new URL('../data/naming-poetry.json', import.meta.url)));
const byCharacter = new Map(dictionary.characters.map(row=>[row.character,row]));
const popular = new Set(dictionary.popularNames.map(row=>row.name));
const pool = [...new Set(corpus.characters)].map(char=>byCharacter.get(char)).filter(Boolean);
const poems = Object.entries(corpus.names);
const rankedDictionary = [...dictionary.characters].sort((a,b)=>
  b.recommendationScore-a.recommendationScore || b.culturalScore-a.culturalScore);
const maxResults = 800;
const idOffset = 1_000_000;
const idStride = 10_000;
const defaultAiCount = 20;
const partyTerms = {
  温润儒雅:'温润雅谦文仁柔清正礼', 聪慧灵动:'聪智敏灵慧明机伶颖达',
  大气稳重:'安宁宏弘宇博衡稳山远', 清雅独立:'清雅静高兰风洁素松独',
  豪迈英朗:'爽明朗峻峰轩豪杰朗英', 坚毅笃行:'坚定毅卓韧实行持恒勤',
  文艺浪漫:'诗文乐舞画梦云花雅歌', 沉静谦逊:'沉静谦宁和淡素安朴礼',
  学者教师:'博学文敏思知启贤研理', 艺术设计:'艺术巧雅美文乐韵绘华',
  医生护理:'仁善康健安济惠慈恒宁', 工程科技:'科工明新达创远智通能',
  商业管理:'达远志信正德诚统领策', 文化创意:'新创文才思墨颖俊奇灵',
  法律政务:'正义诚公真清理直法明', 文学传媒:'文语书言诗翰知雅思名',
};

function readInput(body) {
  const surname = typeof body.surname === 'string' ? body.surname.trim() : '';
  if (!/^\p{Script=Han}{1,2}$/u.test(surname)) throw new Error('请输入一到两个汉字的姓氏');
  const gender = [1,'1','male','男'].includes(body.gender) ? 'male'
    : [2,'2','female','女'].includes(body.gender) ? 'female' : null;
  if (!gender) throw new Error('请选择性别');
  const birthDate = body.birthDate || 'unknown';
  const birthTime = body.birthTime === 'unkno' || !body.birthTime ? 'unknown' : body.birthTime;
  const birth = birthDate==='unknown' ? null : parseBirth({surname,gender,birthDate,birthTime});
  const advanced = body.advancedOptions || {};
  const fixed = [advanced.preferredChar1||'',advanced.preferredChar2||''];
  let floating = '';
  if (body.fixed_char?.char) {
    const char = String(body.fixed_char.char).trim();
    const position = body.fixed_char.position;
    if (['首字','第一个字','前','首','first','1'].includes(position)) fixed[0]=char;
    else if (['末字','第二个字','后','尾','末','last','second','2'].includes(position)) fixed[1]=char;
    else floating=char;
  }
  for (const char of [...fixed,floating].filter(Boolean)) {
    if (!/^\p{Script=Han}$/u.test(char)) throw new Error('指定用字只能填写一个汉字');
    if (!byCharacter.has(char)) throw new Error(`本地字库暂未收录「${char}」，请更换指定用字`);
    if (surname.includes(char)) throw new Error('指定用字不能与姓氏相同');
  }
  if (fixed[0] && fixed[0]===fixed[1]) throw new Error('请使用两个不同的指定字');
  const explicitElements = Array.isArray(advanced.preferredWuxing)
    ? [...new Set(advanced.preferredWuxing)] : [];
  if (explicitElements.some(el=>!ELEMENTS.includes(el))) throw new Error('请选择有效的喜用五行');
  if (explicitElements.length && [...fixed,floating].filter(Boolean).some(char=>!explicitElements.includes(byCharacter.get(char).wuxing))) {
    throw new Error('指定用字与所选五行冲突，请调整用字或五行');
  }
  return {
    surname,gender,birthDate,birthTime:birth?.time||'unknown',birth,
    fixed,floating,explicitElements,
    personality:String(body.personality||'').slice(0,100),career:String(body.career||'').slice(0,100),
    birth_status:body.birth_status==='unborn'?'unborn':'born',
  };
}

const trimScore = n=>Math.max(0,Math.min(100,Math.round(n)));
const withoutTone = pinyin=>pinyin?.toLowerCase().normalize('NFD').replace(/\p{M}/gu,'')||'';
const toneMark = ['\u0304','\u0301','\u030c','\u0300'];
const toneNumber = pinyin=>toneMark.findIndex(mark=>pinyin?.normalize('NFD').includes(mark))+1;
const cleanMeaning = s=>(s||'').replace(/^用作人名意指|^用于人名意指/,'').replace(/(?:之)?义[。！]?$/,'');
const genderAdjustment = (row,gender)=>(gender==='female'?row.genderTendency-5:5-row.genderTendency)*1.5;
const genderNumber = input=>input.gender==='female'?2:1;
const formStamp = input=>input.birthDate==='unknown'?'':input.birthDate+' '+(input.birthTime==='unknown'?'unknown':input.birthTime+':00');
const genreTitle = '本地组合';
const clauses = new Set('宁可 宁有 如是 如有 可以 如如 何如 此如 有如 亦如 亦有 少有 可如 有可 如可 如此 如斯 维有 允有'.split(' '));
function nameChar(char) {
  const row = byCharacter.get(char);
  if (!row) return {char,character:char,pinyin:'',naming_pinyin:'',pinyin_regular:'',wuxing:'',strokes:null,meaning:''};
  return {
    char,character:char,pinyin:row.pinyin,naming_pinyin:row.pinyin,pinyin_regular:row.pinyin,
    tone:toneNumber(row.pinyin),tone_name:['轻声','阴平','阳平','上声','去声'][toneNumber(row.pinyin)],
    wuxing:row.wuxing,strokes:row.strokes,meaning:cleanMeaning(row.nameConnotation),
    name_meaning:row.nameConnotation,recommendation_score:row.recommendationScore,
  };
}

function constructResult(input,analysis,{mode='poetry',count=60,book,sourceOnly=false,mixedCoverage=false}={}) {
  const {surname,gender,fixed,floating,explicitElements}=input;
  const elements = explicitElements.length?explicitElements:analysis?.xiyong_shen || [];
  const themes = (input.personality+'、'+input.career).split('、').flatMap(option=>[...(partyTerms[option]||'')]);
  const surnameLast = byCharacter.get([...surname].at(-1));
  const letters = new Map();
  const fixedSet = new Set([...fixed,floating].filter(Boolean));
  let bodyPool = pool.filter(row=>!elements.length||elements.includes(row.wuxing));
  const expanded = mode === 'ai' && !sourceOnly;
  const curated = new Set(bodyPool.map(row=>row.character));
  if (expanded) {
    const availableElements = elements.length ? elements : ELEMENTS;
    const extra = availableElements.flatMap(element=>rankedDictionary.filter(row=>
      row.wuxing===element && row.recommendationScore>=85 && !curated.has(row.character)
      && (gender==='female'?row.genderTendency>=4:row.genderTendency<=5)).slice(0,35));
    bodyPool = bodyPool.concat(extra);
  }
  if (!sourceOnly && bodyPool.length<12) bodyPool = [...byCharacter.values()].filter(row=>elements.includes(row.wuxing)).slice(0,60);
  for (const char of fixedSet) {
    if (!bodyPool.some(row=>row.character===char)) bodyPool.push(byCharacter.get(char));
  }
  function permit(row) {
    return !surname.includes(row.character) && (fixedSet.has(row.character) ||
      (!elements.length||elements.includes(row.wuxing)) && (gender==='female'?row.genderTendency>=1:row.genderTendency<=8));
  }
  function add(a,b,source=null) {
    if (!a||!b||!permit(a)||!permit(b)||a.character===b.character) return;
    if (fixed[0]&&a.character!==fixed[0] || fixed[1]&&b.character!==fixed[1]) return;
    const given=a.character+b.character;
    if (floating&&!given.includes(floating)) return;
    if (clauses.has(given)) return;
    if(withoutTone(a.pinyin)===withoutTone(b.pinyin)) return;
    if(letters.has(given)) return;
    const naturalSound = trimScore(93 + (toneNumber(a.pinyin)!==toneNumber(b.pinyin)?5:0)
      - (surnameLast&&withoutTone(surnameLast.pinyin)===withoutTone(a.pinyin)?14:0));
    const strokes = trimScore(100-Math.max(0,Math.abs(a.strokes-b.strokes)-3)*2);
    const culture = trimScore((a.culturalScore+b.culturalScore)/2 + (source?5:-10));
    const distinct = popular.has(given)?71:94;
    const themeHits = themes.filter(c=>given.includes(c)||a.nameConnotation?.includes(c)||b.nameConnotation?.includes(c)).length;
    const adjusted = (a.recommendationScore+b.recommendationScore+genderAdjustment(a,gender)+genderAdjustment(b,gender))/2;
    const quality = adjusted*.31+naturalSound*.18+strokes*.11+culture*.20+distinct*.20+Math.min(themeHits,8)*.5;
    const rank = quality + (source?(mode==='poetry'?14:5):0);
    const tie = createHash('sha256').update(surname+given).digest().readUInt32BE();
    letters.set(given,{given,a,b,source,rank,tie,quality,naturalSound,strokes,culture,distinct,
      expanded:!source && [a,b].some(row=>!curated.has(row.character) && !fixedSet.has(row.character))});
  }

  for (const [name,row] of poems) {
    const [title,poem,author,dynasty,sourceBook]=row;
    if (!book||sourceBook===book) {
      const [a,b]=[...name];
      add(byCharacter.get(a),byCharacter.get(b),{title,poem,author,dynasty,book:sourceBook});
    }
  }
  if (!sourceOnly) for (const a of bodyPool) for (const b of bodyPool) add(a,b);
  const ranked = [...letters.values()].sort((a,b)=>b.rank-a.rank||a.tie-b.tie);
  const chosen=[];
  const used = new Map();
  const deferred=[];
  // Reserve part of the model shortlist for strong candidates outside the poetry list.
  // The earlier ranking still supplies most names and can fill unused slots.
  const rankedExpanded=expanded?ranked.filter(row=>row.expanded):[];
  const shortlist=rankedExpanded.slice(0,Math.floor(count/3));
  const shortlistNames=new Set(shortlist.map(row=>row.given));
  for (const row of shortlist.concat(ranked.filter(row=>!shortlistNames.has(row.given)))) {
    const flexible=[...row.given].filter(char=>!fixedSet.has(char));
    if(flexible.some(char=>(used.get(char)||0)>=7)) {deferred.push(row);continue;}
    chosen.push(row);
    for(const char of flexible) used.set(char,(used.get(char)||0)+1);
    if(chosen.length===count) break;
  }
  if(chosen.length<count) chosen.push(...deferred.slice(0,count-chosen.length));
  if (expanded) chosen.sort((a,b)=>b.rank-a.rank||a.tie-b.tie);
  if (expanded && mixedCoverage && !fixedSet.size && elements.length>1) {
    // Include a bounded, complete cross-element search among highly rated
    // naming characters. A global pair score can bury both character orders.
    const eligible = new Set(bodyPool.map(row=>row.character));
    const groupSize = Math.max(6,Math.floor(18 / Math.sqrt(elements.length*(elements.length-1)/2)));
    const anchors = new Set(elements.flatMap(element=>rankedDictionary.filter(row=>
      row.wuxing===element && eligible.has(row.character) &&
      (gender==='female'?row.genderTendency>=4:row.genderTendency<=5)).slice(0,groupSize)
      .map(row=>row.character)));
    const existing = new Set(chosen.map(row=>row.given));
    const supplemental = ranked.filter(row=>row.a.wuxing!==row.b.wuxing &&
      anchors.has(row.a.character) && anchors.has(row.b.character) && !existing.has(row.given));
    const stride = Math.ceil(supplemental.length/chosen.length);
    const combined = chosen.flatMap((row,index)=>[row,...supplemental.slice(index*stride,(index+1)*stride)]);
    chosen.splice(0,chosen.length,...combined);
  }
  return chosen.map((row,index)=>{
    const chars=[nameChar(row.a.character),nameChar(row.b.character)];
    const surnameParts=[...surname].map(nameChar);
    const meaning=chars.map(ch=>`「${ch.char}」取${ch.meaning||'本义'}`).join('，')+'。';
    const pinyin=[...surnameParts,...chars].map(ch=>ch.pinyin).filter(Boolean).join(' ');
    return {
      index,name:row.given,given_name:row.given,full_name:surname+row.given,surname,
      pinyin,wuxing:[...surnameParts,...chars].map(ch=>ch.wuxing).join(''),
      char_wuxing_combo:chars.map(ch=>ch.wuxing).join(''),chars,meaning,overall_meaning:meaning,
      score:trimScore(row.quality),reference:row.source,dimensions:{
        phonetic:{label:'音韵之美',score:row.naturalSound},
        shape:{label:'字形结构',score:row.strokes},
        guoxue:{label:'国学底蕴',score:row.culture},
        uniqueness:{label:'名字辨识度',score:row.distinct},
      },
    };
  });
}

export function generateLocalNaming(body,options={}) {
  const input = readInput(body);
  const analysis = input.birth ? analyzeBirth(input.birth) : null;
  const count = Math.min(maxResults,Math.max(1,Math.trunc(Number(options.count)||60)));
  return {input,analysis,names:constructResult(input,analysis,{...options,count})};
}

export function generateAiCandidates(body,count=defaultAiCount) {
  return generateLocalNaming(body,{mode:'ai',count:Math.max(100,count*6),mixedCoverage:true});
}

export function initNaming(db) {
  db.exec(`
    CREATE TABLE IF NOT EXISTS local_naming_sessions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      owner TEXT NOT NULL,
      mode TEXT NOT NULL,
      input_json TEXT NOT NULL,
      analysis_json TEXT NOT NULL,
      names_json TEXT NOT NULL,
      created_at TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS local_naming_sessions_owner ON local_naming_sessions(owner, mode, id DESC);
    CREATE TABLE IF NOT EXISTS local_naming_favorites (
      owner TEXT NOT NULL,
      name_id TEXT NOT NULL,
      collected_at TEXT NOT NULL,
      PRIMARY KEY(owner,name_id)
    );
  `);
}
const initDone=new WeakSet();
function ensure(db){
  if(!initDone.has(db)){initNaming(db);initDone.add(db);}
}
function decode(row) {
  return row && {
    id:row.id,mode:row.mode,input:JSON.parse(row.input_json),analysis:JSON.parse(row.analysis_json),
    names:JSON.parse(row.names_json),created:row.created_at,
  };
}
function sessionById(db,owner,id,mode='') {
  if(!/^\d+$/.test(String(id))) return undefined;
  ensure(db);
  return decode(db.prepare('SELECT * FROM local_naming_sessions WHERE id=? AND owner=? AND (? = \'\' OR mode=?)').get(Number(id),owner,mode,mode));
}
const nameId=(id,index)=>idOffset+id*idStride+index+1;
function identify(raw) {
  if(!/^\d+$/.test(String(raw))) return null;
  const value=Number(raw)-idOffset;
  if(!Number.isSafeInteger(value)||value<idStride) return null;
  return {id:Math.floor(value/idStride),index:(value%idStride)-1};
}
function favorite(db,owner,id) {
  return !!db.prepare('SELECT 1 FROM local_naming_favorites WHERE owner=? AND name_id=?').get(owner,String(id));
}
function calculateGrids(surname, given) {
  if([...surname,...given].some(ch=>!ch.strokes)) return null;
  const sum = letters=>letters.reduce((value,ch)=>value+ch.strokes,0);
  const firstSurname=sum(surname);
  const next=given[0].strokes;
  const second=given[1].strokes;
  const counts = {
    tiange:firstSurname+(surname.length===1?1:0),
    renge:surname.at(-1).strokes+next,
    dige:next+second,
    waige:second+(surname.length===1?1:surname[0].strokes),
    zongge:firstSurname+next+second,
  };
  const elements=[...'水木木火火土土金金水'];
  const result=Object.fromEntries(Object.entries(counts).map(([key,value])=>[
    key,{value,wuxing:elements[value%10],raw_level:'简体笔画参考',desc:'按字库记录的常用简体笔画计算。'},
  ]));
  result.sancai={value:['tiange','renge','dige'].map(key=>result[key].wuxing).join(''),raw_level:'简体笔画参考'};
  return result;
}
function aiSource(name) {
  const reference=name.reference;
  if(reference) return {
    source:`《${reference.title}》${reference.poem}`,
    source_kind:'literary',source_type:reference.book,source_dynasty:reference.dynasty||'',
  };
  const basis=name.chars.map(char=>`「${char.char}」${char.wuxing?'属'+char.wuxing+'，':''}${char.meaning||'取其本义'}`);
  return {source:basis.join('；')+'。',source_kind:'combination',source_type:'选字依据',source_dynasty:''};
}

function aiDetailCharacter(char) {
  const meta=namedCharacter(char.char);
  return {
    ...char,
    radical:meta?.radical||'',
    strokes:meta?.strokes??char.strokes,
    character_structure:meta?.characterStructure||'',
    meaning:meta?.characterMeaning||char.meaning,
    name_meaning:meta?.nameConnotation||char.name_meaning,
  };
}

function detailsFor(db,owner,record,name) {
  const input=record.input;
  const analysis=record.analysis;
  const id=nameId(record.id,name.index);
  const reference=name.reference;
  const isAi=record.mode==='ai';
  const surnameParts=[...input.surname].map(nameChar);
  const detailSurname=isAi?surnameParts.map(aiDetailCharacter):surnameParts;
  const characters=isAi?name.chars.map(aiDetailCharacter):name.chars;
  const surnameChar=detailSurname.at(-1);
  const allChars=[...detailSurname,...characters];
  const grids=calculateGrids(detailSurname,characters);
  const signs=allChars.map(ch=>ch.tone||0);
  const tonePattern=signs.map(t=>t===0?'轻':t<=2?'平':'仄').join('—');
  const totalStrokes=allChars.every(ch=>ch.strokes)?allChars.reduce((n,c)=>n+c.strokes,0):null;
  const title=reference?.title;
  return {
    ...name,id,history_id:record.id,type:'name',mode:record.mode,is_collected:favorite(db,owner,id),
    created_at:record.created,gender:input.gender==='female'?'女':'男',
    bazi:analysis?.bazi_str||'',day_master:analysis?.riGan?.name||'',birth_time:formStamp(input),
    yongshen:input.explicitElements.length?input.explicitElements:analysis?.xiyong_shen||[],
    xiyong_shen:input.explicitElements.length?input.explicitElements:analysis?.xiyong_shen||[],
    ji_shen:analysis?.ji_shen||'',ri_gan:analysis?.riGan,ri_zhu_strength:analysis?.riZhuStrength,
    pattern:analysis?.pattern,yong_shen_detail:analysis?.yong_shen_detail,
    zodiac:analysis?.zodiac?.name||'',xingzuo:isAi?analysis?.xingzuo||null:analysis?.xingzuo?.name||'',
    zodiac_rules:analysis?.zodiac_rules,input_personality:input.personality,input_career:input.career,
    surname_char:surnameChar,stroke_total:totalStrokes,tone_pattern:tonePattern,wuge:grids,wuge_detail:grids,
    ...(isAi ? aiSource(name) : {
      source:reference?`《${title}》${reference.poem}`:'',
      source_type:reference?.book||genreTitle,source_dynasty:reference?.dynasty||'',
    }),
    ...(isAi ? {
      chars:characters,
      phonetic:{score:name.dimensions?.phonetic?.score??null,summary:`全名读音为 ${name.pinyin}，声调依次为 ${tonePattern}。`,items:[]},
      glyph:{score:name.dimensions?.shape?.score??null,summary:totalStrokes===null?'部分字的笔画暂无记录。':
        `全名共 ${totalStrokes} 画，按常用字形笔画计算。`,items:[]},
    } : {}),
    name_card:{name:name.given_name,full_name:name.full_name,pinyin:name.pinyin,surname:input.surname,
      gender:input.gender==='female'?'女':'男',birth_date:input.birthDate==='unknown'?'':input.birthDate,
      strokes:totalStrokes,zodiac:analysis?.zodiac?.name||''},
    poem:reference?{has_poem:true,source:title,verse:reference.poem,author:reference.author,dynasty:reference.dynasty}:{has_poem:false},
    characters,phonetics:{pinyins:allChars.map(ch=>ch.pinyin),tones:signs,tone_names:allChars.map(ch=>ch.tone_name),tone_pattern:tonePattern},
    shape_analysis:{chars:allChars,total_strokes:totalStrokes,balance:'参照简体常用字笔画'},
  };
}
export function lookupNamingCandidate(db, owner, raw) {
  const key=identify(raw);
  if(!key) return null;
  const record=sessionById(db,owner,key.id);
  const name=record?.names[key.index];
  return name ? detailsFor(db,owner,record,name) : null;
}
export function listNamingFavorites(db,owner) {
  ensure(db);
  return db.prepare('SELECT name_id,collected_at FROM local_naming_favorites WHERE owner=? ORDER BY collected_at DESC').all(owner)
    .map(row=>{
      const item=lookupNamingCandidate(db,owner,row.name_id);
      return item && {...item,name_id:item.id,created_at:row.collected_at,meaning:item.overall_meaning};
    }).filter(Boolean);
}
export function clearNamingHistory(db,owner) {
  ensure(db);
  db.exec('BEGIN IMMEDIATE');
  try {
    db.prepare('DELETE FROM local_naming_favorites WHERE owner=?').run(owner);
    const {changes}=db.prepare('DELETE FROM local_naming_sessions WHERE owner=?').run(owner);
    db.exec('COMMIT');
    return changes;
  } catch(error){db.exec('ROLLBACK');throw error;}
}

function generated(db,owner,mode,input,analysis,names) {
  const created = new Date().toISOString();
  const {lastInsertRowid}=db.prepare(
    'INSERT INTO local_naming_sessions(owner,mode,input_json,analysis_json,names_json,created_at) VALUES(?,?,?,?,?,?)',
  ).run(owner,mode,JSON.stringify(input),JSON.stringify(analysis),JSON.stringify(names),created);
  return {id:Number(lastInsertRowid),mode,input,analysis,names,created};
}
function sessionSummary(record) {
  const {input,analysis,names,id,created}=record;
  return {
    id,session_id:id,surname:input.surname,gender:genderNumber(input),
    birth_time:formStamp(input),bazi:analysis?.bazi_str||'',
    name_count:names.length,actual_count:names.length,
    requested_count:input.generation?.requested_count||names.length,created_at:created,
    generation:input.generation||null,
    wuxing_analysis:{
      ...(analysis?.wuxing_analysis||{}),
      day_master:analysis?.riGan?.name||'',
      yongshen:input.explicitElements.length?input.explicitElements:analysis?.xiyong_shen||[],
      xiyong_shen:input.explicitElements.length?input.explicitElements:analysis?.xiyong_shen||[],
      wuxing_count:analysis?.wuxingWithCangGan||{},
    },
  };
}
function pagination(url) {
  const number=(key,def,max)=>Math.min(max,Math.max(1,Math.trunc(Number(url.searchParams.get(key))||def)));
  return {page:number('page',1,1e5),size:number('page_size',30,100)};
}
function poetryPage(db,owner,record,page=1,size=30) {
  const start=(page-1)*size;
  const favoriteIds=new Set(db.prepare('SELECT name_id FROM local_naming_favorites WHERE owner=?').all(owner).map(row=>row.name_id));
  return {
    ...sessionSummary(record),history_id:record.id,
    names:record.names.slice(start,start+size).map(name=>{
      const id=nameId(record.id,name.index);
      return {...name,id,source:name.reference,can_view:true,is_viewed:true,is_collected:favoriteIds.has(String(id)),rating:'A'};
    }),
    page,page_size:size,total:record.names.length,max_name_count:record.names.length,
    is_unlocked:true,is_unlimited:false,has_more:page*size<record.names.length,
    free_view_count:record.names.length,viewed_count:0,package_code:'LOCAL',
  };
}
function aiNames(record) {
  return record.names.map(name=>({...name,id:nameId(record.id,name.index),...aiSource(name)}));
}
function preview(body) {
  const input=readInput(body);
  const analysis=input.birth?analyzeBirth(input.birth):null;
  const first=nameChar([...input.surname].at(-1));
  return {
    date_unknown:!input.birth,bazi_analysis:analysis,xingzuo:analysis?.xingzuo||null,
    surname_info:{...first,surname:input.surname},
    surname_advice:{lines:['按声调、读音和字形筛选与姓氏协调的组合。']},
    yongshen_dict:analysis ? Object.fromEntries(analysis.xiyong_shen.map(el=>{
      const matches=pool.filter(row=>row.wuxing===el).sort((a,b)=>b.recommendationScore-a.recommendationScore);
      return [el,matches.map(row=>nameChar(row.character))];
    })) : null,
    zodiac_relations:analysis?{liu_he:analysis.zodiac.he,xiang_chong:analysis.zodiac.chong}:null,
  };
}
function rankedInput(body,mode,count,ctx) {
  try {
    const generatedNames=generateLocalNaming(body,{mode,count});
    if(!generatedNames.names.length) return ctx.fail(1001,'未找到符合条件的候选，请调整指定用字或喜用五行');
    return generatedNames;
  } catch(error) {return ctx.fail(1001,error.message);}
}

const activeGenerations = new Set();

async function generateAiStream(req,res,body,ctx) {
  const {db,session:owner}=ctx;
  const controller=new AbortController();
  let disconnected=false;
  const close=()=>{disconnected=true;controller.abort();};
  const timeout=setTimeout(()=>controller.abort(),180000);
  let heartbeat;
  let record;
  let acquired=false;
  const updateStatus=status=>{
    record.input.generation.status=status;
    db.prepare('UPDATE local_naming_sessions SET input_json=?, names_json=? WHERE id=? AND owner=?')
      .run(JSON.stringify(record.input),JSON.stringify(record.names),record.id,owner);
  };
  res.writeHead(200,{'Content-Type':'text/event-stream; charset=utf-8','Cache-Control':'no-store','X-Accel-Buffering':'no'});
  const send=async event=>{
    if(controller.signal.aborted) throw new GenerationError('生成已中止');
    if(res.write('data: '+JSON.stringify(event)+'\n\n')===false) {
      await once(res,'drain',{signal:controller.signal});
    }
  };
  res.once?.('close',close);
  try {
    if(activeGenerations.has(owner)) throw new GenerationError('已有一批 AI 起名正在生成，请等待完成');
    activeGenerations.add(owner);
    acquired=true;
    const credential=gatewayCredential();
    const count={AI1:10,AI2:20,AI3:30}[body.package_code]||defaultAiCount;
    const result=generateAiCandidates(body,count);
    if(result.names.length<count) throw new GenerationError('符合条件的候选较少，请调整指定用字或喜用五行');
    const payload=prepareGatewayPayload(result.input,result.analysis,result.names,count);
    const allowed=new Map(result.names.map(name=>[name.given_name,name]));
    const used=new Set();
    const generation={provider:'vercel-ai-gateway',model:AI_MODEL,status:'generating',requested_count:count};
    record=generated(db,owner,'ai',{...result.input,generation},result.analysis,[]);
    const summary=sessionSummary(record);
    await send({type:'init',session_id:record.id,bazi:summary.bazi,
      day_master:summary.wuxing_analysis.day_master,yongshen:summary.wuxing_analysis.yongshen,
      wuxing_count:summary.wuxing_analysis.wuxing_count,total_batches:Math.ceil(count/5),
      name_count_target:count,model:AI_MODEL});
    heartbeat=setInterval(()=>res.write?.(': heartbeat\n\n'),15000);
    let previousScore=101;
    let delivered=0;
    const flush=async()=>{
      updateStatus('generating');
      const names=aiNames(record).slice(delivered);
      if(names.length) {
        await send({type:'batch',names});
        delivered=record.names.length;
      }
    };
    for await(const event of streamRecommendations(payload,{credential,signal:controller.signal})) {
      if(event.type==='usage') {
        record.input.generation.usage=event.usage;
        continue;
      }
      if(record.names.length>=count) continue;
      const row=event.row;
      const modelName=Number.isSafeInteger(row?.id)
        ? result.names[row.id-1]?.given_name : row?.name;
      const {candidate,score,reason,tradeoff}=validateRecommendation({...row,name:modelName},allowed,used,previousScore);
      previousScore=score;
      used.add(candidate.given_name);
      record.names.push({...candidate,index:record.names.length,score,
        meaning:reason,overall_meaning:reason+'\n使用提醒：'+tradeoff,ai_reason:reason,ai_tradeoff:tradeoff,
        ai_model:AI_MODEL,generation_provider:'vercel-ai-gateway'});
      if(record.names.length%5===0) await flush();
    }
    if(record.names.length!==count) throw new GenerationError('模型未生成足量姓名，请重新生成');
    await flush();
    updateStatus('complete');
    await send({type:'done',session_id:record.id,remaining_quota:null,model:AI_MODEL});
  } catch(error) {
    if(record) updateStatus(record.names.length?'partial':'failed');
    if(!disconnected && !res.destroyed) {
      res.write('data: '+JSON.stringify({type:'error',message:controller.signal.aborted?'生成超时，请重试':
        error instanceof GenerationError?error.message:'AI 生成失败，请重新尝试'})+'\n\n');
    }
  } finally {
    clearTimeout(timeout);
    clearInterval(heartbeat);
    res.off?.('close',close);
    if(acquired) activeGenerations.delete(owner);
    if(!res.destroyed) res.end();
  }
  return ctx.sent;
}

export async function handleNaming(req,res,url,ctx) {
  const path=decodeURIComponent(url.pathname);
  const method=req.method||'GET';
  const {db,session:owner}=ctx;
  const localRoute=/^\/api\/v\d+\/(?:naming_ai|naming)\//.test(path);
  if(!localRoute) return;
  ensure(db);
  if(method==='GET' && path==='/api/v1/naming/free-quota') return {can_free_naming:true,paid_remaining:0,free_remaining:1};
  if(method==='GET' && path==='/api/v1/naming/recent-purchases') return [];
  if(method==='GET' && path==='/api/v1/naming_ai/trial_status') {
    return {has_trial:true,trial_name_count:defaultAiCount,is_vip:false,paid_remaining:0};
  }
  if(method==='POST' && path==='/api/v1/naming_ai/preview') {
    const body=await ctx.body();
    try{return preview(body);}catch(error){return ctx.fail(1001,error.message);}
  }
  if(method==='POST' && /^\/api\/v[12]\/naming\/generate$/.test(path)) {
    const body=await ctx.body();
    const {input,analysis,names}=rankedInput(body,'poetry',body.nameCount||60,ctx);
    const record=generated(db,owner,'poetry',input,analysis,names);
    return poetryPage(db,owner,record);
  }
  if(method==='POST' && path==='/api/v1/naming_ai/generate-stream') {
    return generateAiStream(req,res,await ctx.body(),ctx);
  }
  if(method==='GET' && ['/api/v1/naming/history','/api/v1/naming_ai/sessions'].includes(path)) {
    const mode=path.includes('naming_ai')?'ai':'poetry';
    const {page,size}=pagination(url);
    const rows=db.prepare('SELECT * FROM local_naming_sessions WHERE owner=? AND mode=? ORDER BY id DESC LIMIT ? OFFSET ?')
      .all(owner,mode,size,(page-1)*size);
    const total=db.prepare('SELECT COUNT(*) AS n FROM local_naming_sessions WHERE owner=? AND mode=?').get(owner,mode).n;
    return {items:rows.map(row=>sessionSummary(decode(row))),total,page,page_size:size};
  }
  const details=path.match(/^\/api\/v(\d+)\/(naming_ai\/sessions|naming\/history)\/(\d+)(?:\/(names|extend))?$/);
  if(details) {
    const mode=details[2].startsWith('naming_ai')?'ai':'poetry';
    const record=sessionById(db,owner,details[3],mode);
    if(!record) return ctx.fail(404,'找不到这次起名记录',404);
    if(mode==='ai'&&method==='GET'&&!details[4]) return {session:sessionSummary(record),names:aiNames(record)};
    if(mode==='poetry'&&method==='GET'&&details[4]==='names') {
      const {page,size}=pagination(url);
      return poetryPage(db,owner,record,page,size);
    }
    if(mode==='poetry'&&method==='POST'&&details[4]==='extend') {
      const body=await ctx.body();
      const extra=Math.max(1,Math.min(200,Math.trunc(Number(body.nameCount)||100)));
      const starting=record.names.length;
      const candidates=constructResult(record.input,record.analysis,{count:Math.min(maxResults,starting+extra)});
      const used=new Set(record.names.map(name=>name.given_name));
      const more=candidates.filter(name=>!used.has(name.given_name)).slice(0,extra);
      if(!more.length) return ctx.fail(1001,'已展示这个条件下的全部候选');
      record.names.push(...more.map((name,index)=>({...name,index:starting+index})));
      db.prepare('UPDATE local_naming_sessions SET names_json=? WHERE id=? AND owner=?')
        .run(JSON.stringify(record.names),record.id,owner);
      return {addedCount:more.length,newNameCount:record.names.length,remainingQuota:maxResults-record.names.length};
    }
  }
  if(method==='GET' && /^\/api\/v1\/naming_ai\/names\//.test(path)) {
    const item=lookupNamingCandidate(db,owner,path.split('/').at(-1));
    if(!item||item.mode!=='ai') return ctx.fail(404,'找不到这个候选姓名',404);
    return item;
  }
  if(method==='GET'&&path==='/api/v1/naming/detail') {
    const id=url.searchParams.get('name_id');
    if(!identify(id)) return;
    const item=lookupNamingCandidate(db,owner,id);
    if(!item) return ctx.fail(404,'找不到这个候选姓名',404);
    return {
      ...item,
      score:{total:item.score,level:'推荐',comment:'根据本地字形、音律、文化出处和辨识度估算。',dimensions:item.dimensions},
      meaning:{brief:item.overall_meaning,detail:item.overall_meaning},
    };
  }
  if(method==='POST'&&path==='/api/v1/naming/collect') {
    const body=await ctx.body();
    if(!identify(body.name_id)) return;
    const item=lookupNamingCandidate(db,owner,body.name_id);
    if(!item) return ctx.fail(404,'找不到这个候选姓名',404);
    if(!['collect','uncollect'].includes(body.action)) return ctx.fail(1001,'不支持此收藏操作');
    const id=String(item.id);
    if(body.action==='uncollect') db.prepare('DELETE FROM local_naming_favorites WHERE owner=? AND name_id=?').run(owner,id);
    else db.prepare('INSERT OR IGNORE INTO local_naming_favorites(owner,name_id,collected_at) VALUES(?,?,?)')
      .run(owner,id,new Date().toISOString());
    return {is_collected:favorite(db,owner,id)};
  }
}
