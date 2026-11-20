import { createRequire } from 'node:module';
import { execFileSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { createHash } from 'node:crypto';
import { gunzipSync } from 'node:zlib';
import { analyzeBirth, ELEMENTS } from '../bazi/calendar.mjs';
import { analysisFor, generateNames } from '../bazi/names.mjs';

const ANIMALS = [..."鼠牛虎兔龙蛇马羊猴鸡狗猪"];
const BRANCHES = [..."子丑寅卯辰巳午未申酉戌亥"];
const require = createRequire(import.meta.url);
function lunarModule() {
  try {
    return require('lunar-javascript');
  } catch (error) {
    if (error.code !== 'MODULE_NOT_FOUND') throw error;
    return require(join(execFileSync('npm', ['root', '-g'], { encoding: 'utf8' }).trim(), 'lunar-javascript'));
  }
}
const { Solar, LunarUtil } = lunarModule();
const readData = (file) => JSON.parse(readFileSync(new URL('../' + file, import.meta.url)));
const original = readData('public-catalog.json');
const snapshot = readData('data/tool-public-snapshots.json');
const namedata = readData('data/original-public-library.json');
const characters = new Map(namedata.characters.map((item) => [item.character, item]));
const surnames = new Map(snapshot.surnames.list.map((item) => [item.surname, item]));
const constellations = original['/api/v1/tools/constellation/list'].data.list;
const zodiacList = original['/api/v1/tools/zodiac/list'].data;
const wuxingList = original['/api/v1/tools/naming-characters/wuxing'].data;
const poemBooks = original['/api/v1/tools/poem-naming/books'].data.books;
const stamp = () => new Intl.DateTimeFormat('sv-SE', { timeZone: 'Asia/Shanghai', dateStyle: 'short' }).format(new Date());
const reference = '按传统民俗文化整理，仅供娱乐和了解文化。';
const stripTone = (s) => String(s ?? '').normalize('NFD').replace(/\p{Mark}/gu, '').toLowerCase().replaceAll('ɡ','g');
const sex = (value) => /^(?:2|female|f|女)$/i.test(value ?? '') ? 'female' : 'male';
const hanName = /^[\p{Script=Han}]{1,2}$/u;
const bound = (value, fallback, min, max) => {
  const n = value == null || value === '' ? fallback : Number(value);
  return Number.isInteger(n) ? Math.min(max, Math.max(min, n)) : fallback;
};
const compareRank = (a, b) => (b.recommendationScore ?? 0) - (a.recommendationScore ?? 0) ||
  (b.culturalScore ?? 0) - (a.culturalScore ?? 0) || a.character.localeCompare(b.character, 'zh');
const sortedCharacters = [...characters.values()].sort(compareRank);

function paginate(rows, query, defaults = 20) {
  const page = bound(query.get('page'), 1, 1, 1000000);
  const size = bound(query.get('size') ?? query.get('page_size'), defaults, 1, 100);
  return { list: rows.slice((page - 1) * size, page * size), total: rows.length, page, size };
}
function genderMatch(row, target) {
  const trend = Number(row.genderTendency);
  if (!target || target === 'all' || target === '0') return true;
  if (target === '3' || target === 'neutral') return trend === 4 || trend === 5;
  return sex(target) === 'female' ? trend >= 4 : trend <= 5;
}
function hash(value) {
  return createHash('sha256').update(value).digest().readUInt32BE(0);
}
function dateFields(value, ctx) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) ctx.fail(1001, '请输入正确的公历日期');
  const [year, month, day] = value.split('-').map(Number);
  const check = new Date(Date.UTC(year, month - 1, day));
  if (year < 1900 || year > 2199 || check.getUTCMonth() + 1 !== month || check.getUTCDate() !== day)
    ctx.fail(1001, '日期无效，支持 1900–2199 年');
  return { year, month, day };
}
const pad = (i) => String(i).padStart(2, '0');
const stemElement = (stem) => LunarUtil.WU_XING_GAN[stem];
const branchElement = (branch) => LunarUtil.WU_XING_ZHI[branch];
const combinedElement = (ganzhi) => (stemElement(ganzhi[0]) ?? '') + (branchElement(ganzhi[1]) ?? '');

export function namedCharacter(character) {
  const row = characters.get(character);
  const {lookup,modern} = shuowenIndex();
  const current = modern.get(character);
  const entry = lookup.get(character) ?? lookup.get(current?.traditional);
  if (!entry && !current && !row) return;
  const pinyin = row?.pinyin ?? current?.pinyin ?? entry?.pinyin ?? '';
  const unaccented = stripTone(pinyin);
  const initial = unaccented.match(/^(?:zh|ch|sh|[bpmfdtnlgkhjqxrzcsyw])/)?.[0] ?? '';
  const tone = ['\u0304','\u0301','\u030c','\u0300'].findIndex((value) => pinyin.normalize('NFD').includes(value)) + 1;
  return {
    ...row, character, pinyin, namingPinyin: pinyin, tone: tone ? `${tone}声` : '',
    initialConsonant: initial, finalVowels: unaccented.slice(initial.length),
    wuxing: row?.wuxing ?? '', wuxingDesc: wuxingList.find((x) => x.wuxing === row?.wuxing)?.desc ?? '',
    radical: current?.radical ?? entry?.radical ?? '', strokes: current?.strokes ?? row?.strokes ?? null,
    traditionalForm: [current?.traditional, entry?.character].find((name)=>name && name!==character) ?? null,
    traditionalStrokes: row?.strokes ?? modern.get(current?.traditional)?.strokes ?? null,
    characterStructure: '', isCommonNamingCharacter: Boolean(row),
    isPolyphonic: /[、, /]/.test(pinyin), characterMeaning: current?.explanation || entry?.explanation || row?.nameConnotation || '',
    nameConnotation: row?.nameConnotation ?? '', laiYuan: null, aspirationTags: [],
    overallRating: row?.rating ?? '', ratingDesc: '', usageFrequency: '',
  };
}
let shuowen;
function shuowenIndex() {
  if (shuowen) return shuowen;
  const data = JSON.parse(gunzipSync(readFileSync(new URL('../data/tool-shuowen.json.gz', import.meta.url))));
  const modernData = JSON.parse(gunzipSync(readFileSync(new URL('../data/tool-modern-dictionary.json.gz', import.meta.url))));
  const modern = new Map(Object.entries(modernData.entries));
  const lookup = new Map();
  const entries = Object.entries(data.entries).map(([character, properties]) => ({
    ...properties, character, pinyinHead: stripTone(properties.pinyin)[0] ?? '',
    wuxing: characters.get(character)?.wuxing ?? '', strokes: modern.get(character)?.strokes ?? characters.get(character)?.strokes ?? null,
    brief: properties.explanation.length <= 55 ? properties.explanation : properties.explanation.slice(0, 55) + '…',
  }));
  for (const row of entries) lookup.set(row.character, row);
  for (const row of entries) for (const alias of row.indexes) if (!lookup.has(alias)) lookup.set(alias, row);
  const merged = [...entries];
  for (const [character, row] of modern) if (!lookup.has(character)) {
    const naming = characters.get(character);
    merged.push({character,pinyin:row.pinyin,pinyinHead:stripTone(row.pinyin)[0]??'',
      brief:row.explanation.slice(0,55),radical:row.radical,wuxing:naming?.wuxing??'',strokes:row.strokes});
  }
  const counts = new Map();
  for (const row of merged) if (row.radical) counts.set(row.radical, (counts.get(row.radical) ?? 0) + 1);
  const radicals = [...counts.entries()].sort((a,b) => b[1]-a[1]).map(([radical, count]) => ({radical, count}));
  shuowen = {lookup, entries, merged, radicals, modern};
  return shuowen;
}
function dictionaryDetail(character, ctx) {
  const {lookup,modern} = shuowenIndex();
  const standard = modern.get(character);
  const entry = lookup.get(character) ?? lookup.get(standard?.traditional);
  const current = characters.get(character);
  if (!entry && !standard && !current) ctx.fail(1001, '本地字库尚未收录该字');
  return {
    character, explanation:entry?.explanation??'', radical:standard?.radical??entry?.radical??'', shuowen_radical:entry?.radical??'',
    pinyin:current?.pinyin??standard?.pinyin??entry?.pinyin??'', seal_character:entry?.seal_character??'',
    duan_notes:Array.isArray(entry?.duan_notes)?entry.duan_notes:[],
    explanation_modern:standard?.explanation??'', cultural_meaning:'', naming_suggestion:current?.nameConnotation??'',
    has_shuowen:Boolean(entry), traditional_form:[standard?.traditional,entry?.character].find((item)=>item&&item!==character)??null,
    strokes:standard?.strokes??current?.strokes??null, traditional_strokes:current?.strokes??modern.get(standard?.traditional)?.strokes??null,
    wuxing:current?.wuxing??'', structure:'', meaning:standard?.explanation??current?.nameConnotation??'', name_meaning:current?.nameConnotation??'',
  };
}

function charList(query) {
  const wuxing = query.get('wuxing') ?? '';
  const keyword = stripTone(query.get('keyword')).trim();
  const [low, high] = (query.get('strokes') ?? '').split('-').map(Number);
  const minimum = Number(query.get('min_score')) || 0;
  const rows = sortedCharacters.filter((row) =>
    (!wuxing || row.wuxing === wuxing) &&
    (!keyword || stripTone([row.character, row.pinyin, row.nameConnotation].join(' ')).includes(keyword)) &&
    (!low || row.strokes >= low) && (!high || row.strokes <= high) &&
    genderMatch(row, query.get('gender')) && row.recommendationScore >= minimum);
  return { ...paginate(rows, query), filters: { wuxing, strokes:query.get('strokes'), gender:query.get('gender'), minScore:minimum },
    guide:{ text:`找到 ${rows.length} 个符合条件的用字`, subText:'按五行、笔画和读音筛选', buttonText:'八字起名', link:'/bazi-naming/form' } };
}
function byElement(wuxing, ctx) {
  const meta = wuxingList.find((row) => row.wuxing === wuxing);
  if (!meta) ctx.fail(1001, '请选择金、木、水、火或土');
  const rows = sortedCharacters.filter((row) => row.wuxing === wuxing);
  const cards = (min, max) => rows.filter((row) => row.genderTendency >= min && row.genderTendency <= max)
    .slice(0, 20).map((row) => ({ character:row.character, pinyin:row.pinyin, score:row.recommendationScore, connotation:row.nameConnotation }));
  const strokeSets = [['3-5画', 3, 5], ['6-8画', 6, 8], ['9-11画', 9, 11], ['12画以上', 12, Infinity]];
  return {
    wuxing, wuxingDesc:meta.desc, wuxingTraits:meta.traits, totalCount:rows.length,
    recommended:{ male:cards(0, 4), female:cards(6, 10), neutral:cards(4, 6) },
    byStrokes:Object.fromEntries(strokeSets.map(([key, low, high]) => [key, rows.filter((r)=>r.strokes>=low&&r.strokes<=high).map((r)=>r.character)])),
    guide:{ text:meta.suitable, subText:'结合生辰查看更多建议', buttonText:'八字五行测算', link:'/tools/bazi', price:'免费' },
  };
}
function collectState(character, method, query, ctx, details) {
  if (!ctx.db || !ctx.session) return false;
  const scope = [ctx.session, 'character', character];
  ctx.db.exec(`CREATE TABLE IF NOT EXISTS local_site_favorites (session TEXT, kind TEXT, target TEXT, data TEXT, created TEXT, PRIMARY KEY(session,kind,target))`);
  if (method === 'DELETE' || query.get('action') === 'uncollect') {
    ctx.db.prepare('DELETE FROM local_site_favorites WHERE session=? AND kind=? AND target=?').run(...scope);
    return false;
  }
  if (method === 'POST') {
    const data = { id:'char:'+character, type:'character', char_info:{
      character, pinyin:details.pinyin, wuxing:details.wuxing, strokes:details.strokes,
    } };
    ctx.db.prepare('INSERT INTO local_site_favorites (session,kind,target,data,created) VALUES (?,?,?,?,?) ON CONFLICT DO NOTHING')
      .run(...scope, JSON.stringify(data), new Date().toISOString());
    return true;
  }
  return Boolean(ctx.db.prepare('SELECT 1 FROM local_site_favorites WHERE session=? AND kind=? AND target=?').get(...scope));
}
function charDetail(character, method, action, query, ctx) {
  const data = namedCharacter(character);
  if (!data) ctx.fail(1001, '本地用字宝典尚未收录该字');
  const is_collected = collectState(character, action ? method : 'GET', query, ctx, data);
  if (action) return { success:true, is_collected };
  const related = sortedCharacters.filter((row) => row.character !== character);
  return {
    data, is_collected,
    related:{ sameWuxing:related.filter((row) => row.wuxing === data.wuxing).slice(0, 8).map((row) => row.character),
      sameRadical:data.radical ? shuowenIndex().entries.filter((row) => row.radical === data.radical && row.character !== character).slice(0, 8).map((row)=>row.character) : [],
      similarMeaning:[] },
    guide:{ text:'结合字义与读音选择名字', buttonText:'八字起名', link:'/bazi-naming/form' },
  };
}

function chart(body, ctx) {
  const {year, month, day} = dateFields(`${body.year}-${pad(body.month)}-${pad(body.day)}`, ctx);
  const inputHour = body.hour === '' || body.hour == null ? null : Number(body.hour);
  const hour = inputHour ?? 12;
  const minute = Number(body.minute ?? 0);
  if (!Number.isInteger(hour) || hour < 0 || hour > 23 || !Number.isInteger(minute) || minute < 0 || minute > 59)
    ctx.fail(1001, '时分无效');
  const birth = { year,month,day,hour,minute,unknown:inputHour === null,birthDate:`${year}-${pad(month)}-${pad(day)}` };
  const result = analyzeBirth(birth);
  const lunar = Solar.fromYmdHms(year,month,day,hour,minute,0).getLunar();
  const eight = lunar.getEightChar();
  eight.setSect(1);
  const yun = eight.getYun(sex(body.gender) === 'female' ? 0 : 1);
  const shishen = (gan) => (LunarUtil.SHI_SHEN[eight.getDayGan() + gan] ?? '').replace('七杀','偏官');
  const cycle = (ganzhi) => ({ ganzhi, gan:ganzhi[0], zhi:ganzhi[1], ganWuxing:stemElement(ganzhi[0]),
    zhiWuxing:branchElement(ganzhi[1]), nayin:LunarUtil.NAYIN[ganzhi], shishen:shishen(ganzhi[0]) });
  const dayun = {
    direction: yun.isForward() ? '顺行' : '逆行', startAge: yun.getStartYear(),
    startMonth:yun.getStartMonth(), startDay:yun.getStartDay(),
    startInfo:`${yun.getStartYear()}岁${yun.getStartMonth()}月${yun.getStartDay()}天起运`,
    list:yun.getDaYun().filter((item)=>item.getGanZhi()).map((item,index)=>({ ...cycle(item.getGanZhi()),
      index:index+1,startAge:item.getStartAge(),endAge:item.getEndAge(),startYear:item.getStartYear(),endYear:item.getEndYear() })),
  };
  const currentYear = Number(stamp().split('-')[0]);
  const list = Array.from({length:10}, (_,i) => ({year:currentYear+i, ...cycle(Solar.fromYmd(currentYear+i,6,1).getLunar().getYearInGanZhi())}));
  const branches = Object.values(result.bazi).filter(Boolean).map((p)=>p.zhi);
  const relations = [];
  const harmony = ['子丑','寅亥','卯戌','辰酉','巳申','午未'];
  const trines = [['申子辰','水'],['巳酉丑','金'],['寅午戌','火'],['亥卯未','木']];
  for (let i=0; i<branches.length; i++) for (let j=i+1; j<branches.length; j++) {
    const a = branches[i], b = branches[j];
    if (a === b) continue;
    const join = (type, description) => relations.push({ type, zhi:[a,b], result:`${a}${b}${type}`, description });
    if (harmony.some((p)=>p.includes(a)&&p.includes(b))) join('六合','传统地支六合');
    if (Math.abs(BRANCHES.indexOf(a)-BRANCHES.indexOf(b)) === 6) join('相冲','传统地支六冲');
    if (trines.some(([p])=>p.includes(a)&&p.includes(b))) join('半合','同一组三合地支');
  }
  const lucky = {
    木:[['青色','绿色'],[3,8],['东'],['教育','园林']], 火:[['红色','紫色'],[2,7],['南'],['传媒','能源']],
    土:[['黄色','棕色'],[5,0],['中'],['建筑','农业']], 金:[['白色','银色'],[4,9],['西'],['制造','工艺']],
    水:[['黑色','蓝色'],[1,6],['北'],['交通','流通']],
  };
  const selected = result.xiyong_shen.map((x)=>lucky[x]).filter(Boolean);
  const shichen = Math.floor(((hour + 1) % 24) / 2);
  const range = shichen===0 ? '23:00–01:00' : `${pad(shichen*2-1)}:00–${pad(shichen*2+1)}:00`;
  return {
    ...result, solar:{...result.solar,week:'星期'+result.solar.week}, hourUnknown:birth.unknown,
    baziString:result.bazi_str, yongShen:result.yong_shen_detail, dayun,
    liunian:{ current:list[0],list }, shichen:{name:birth.unknown?'时辰未知':BRANCHES[shichen]+'时',range,index:shichen,unknown:birth.unknown},
    dizhi:{ relations,hasHe:relations.some((x)=>x.type.includes('合')),hasChong:relations.some((x)=>x.type==='相冲'),hasXing:false },
    luckyElements:Object.fromEntries(['color','number','direction','industry'].map((key,i) => [key,[...new Set(selected.flatMap((r)=>r[i]))]])),
  };
}

function almanac(date, ctx) {
  const { year, month, day } = dateFields(date, ctx);
  const solar = Solar.fromYmd(year,month,day);
  const l = solar.getLunar();
  const sYear = l.getYearInGanZhi(), sMonth = l.getMonthInGanZhi(), sDay = l.getDayInGanZhi();
  const luckyDirection = { xi:l.getDayPositionXiDesc(), fu:l.getDayPositionFuDesc(), cai:l.getDayPositionCaiDesc(),
    yangGui:l.getDayPositionYangGuiDesc(), yinGui:l.getDayPositionYinGuiDesc() };
  const shichen = BRANCHES.map((branch,i) => {
    const hour = i === 0 ? 0 : i*2;
    const t = Solar.fromYmdHms(year,month,day,hour,0,0).getLunar();
    const ganzhi = t.getTimeInGanZhi();
    return { name:branch+'时', time:i===0?'23:00–01:00':`${pad(hour-1)}:00–${pad(hour+1)}:00`,
      ganzhi, wuxing:combinedElement(ganzhi),chong:'冲'+t.getTimeChongShengXiao(),
      sha:'煞'+t.getTimeSha(),yi:t.getTimeYi(),ji:t.getTimeJi(),jiXiong:t.getTimeTianShenLuck() };
  });
  const nayin = l.getDayNaYin();
  const dayWuxing = combinedElement(sDay);
  const chong = '冲'+l.getDayChongShengXiao();
  const sha = '煞'+l.getDaySha();
  return {
    date:{solar:{year,month,day,week:'星期'+solar.getWeekInChinese(),weekIndex:solar.getWeek(),constellation:solar.getXingZuo()+'座'},
      lunar:{year:l.getYear(),month:Math.abs(l.getMonth()),day:l.getDay(),yearCn:l.getYearInChinese()+'年',
        monthCn:l.getMonthInChinese()+'月',dayCn:l.getDayInChinese(),isLeap:l.getMonth()<0,zodiac:l.getYearShengXiao(),
        yearGanZhi:sYear,monthGanZhi:sMonth,dayGanZhi:sDay},
      ganzhi:{year:sYear,month:sMonth,day:sDay,yearWuxing:combinedElement(sYear),monthWuxing:combinedElement(sMonth),dayWuxing,nayin}},
    yi:l.getDayYi(),ji:l.getDayJi(),jishen:{list:l.getDayJiShen(),direction:`喜神${luckyDirection.xi}，福神${luckyDirection.fu}，财神${luckyDirection.cai}`},
    xiongsha:{list:l.getDayXiongSha(),avoid:''},shichen,wuxing:{day:dayWuxing,nayin,description:`日柱 ${sDay}，纳音为 ${nayin}`},
    chongsha:{chong,chongDesc:`今日${sDay}，${chong}`,sha,shaDesc:sha},
    xingsu:{name:l.getXiu(),animal:l.getAnimal(),description:l.getXiuSong(),jiXiong:l.getXiuLuck()},
    jianchu:{name:l.getZhiXing(),description:`十二建除：${l.getZhiXing()}日`,yi:l.getDayYi().slice(0, 4),ji:l.getDayJi().slice(0, 4)},
    pengzu:{gan:l.getPengZuGan(),zhi:l.getPengZuZhi()},taishen:{position:l.getDayPositionTai(),description:'传统黄历胎神方位'},
    festivals:{solar:solar.getFestivals(),lunar:l.getFestivals(),jieqi:l.getJieQi(),special:[...solar.getOtherFestivals(),...l.getOtherFestivals()]},
    luckyDirection,disclaimer:reference,
  };
}

function matchConstellation(first, second, ctx) {
  const a = constellations.find((r)=>r.name===first);
  const b = constellations.find((r)=>r.name===second);
  if (!a || !b) ctx.fail(1001, '请选择两个星座');
  const matrix = snapshot.constellation[a.name].compatibility;
  const score = a.name===b.name ? 90 : matrix.best.includes(b.name) ? 96 : matrix.good.includes(b.name) ? 86 :
    matrix.challenging.includes(b.name) ? 61 : 75;
  const summary = score>=90 ? '特质有较多交集' : score>=80 ? '容易找到互补点' : '适合通过沟通磨合';
  const description = `${a.name}和${b.name}的传统星座配对解读。`;
  return { constellation1:a, constellation2:b, overall:{score,level:score>=90?'契合':score>=80?'良好':'有差异',summary},
    scores:{love:{score,desc:'关注彼此表达感受的方式'},friendship:{score:Math.min(100,score+3),desc:'从共同兴趣建立连接'},work:{score:Math.max(50,score-3),desc:'确认分工和共同目标'}},
    analysis:{attraction:description,strengths:summary,challenges:'遇到意见差异时容易按自己的经验判断。',tips:'讨论各自的偏好和界限。'},
    advice:['用实际相处经验判断关系','面对分歧先确认彼此的想法',reference] };
}
function todayFortune() {
  const date = stamp();
  const iso = new Date(date+'T00:00:00Z');
  const weekdays = [...'日一二三四五六'];
  const themes = ['适合整理近期的目标。','可以给专注的任务留出时间。','和朋友交流有助于开阔思路。','优先完成可控的小事。','给日程留一些缓冲。'];
  const list = constellations.map(({name,symbol})=>{
    const value = hash(date+name);
    const score = 65+value%31;
    return {name,symbol,score,level:score>=88?'旺盛':score>=76?'平稳':'调整',summary:themes[(value>>8>>>0)%themes.length]};
  });
  return {date,weekday:'星期'+weekdays[iso.getUTCDay()],list,ranking:[...list].sort((a,b)=>b.score-a.score)};
}
function zodiacByYear(year, ctx) {
  if (!Number.isInteger(year) || year < 1900 || year > 2199) ctx.fail(1001, '请选择 1900–2199 的年份');
  const ganzhi = Solar.fromYmd(year,6,1).getLunar().getYearInGanZhi();
  const [heavenly_stem, earthly_branch] = [...ganzhi];
  const zodiac = ANIMALS[BRANCHES.indexOf(earthly_branch)];
  const entry = snapshot.zodiac[zodiac];
  return {year,zodiac,earthly_branch,heavenly_stem,ganzhi,wuxing:branchElement(earthly_branch),nayin:LunarUtil.NAYIN[ganzhi],info:entry.basic};
}
function matchZodiac(first, second, ctx) {
  const a = Object.hasOwn(snapshot.zodiac,first) ? snapshot.zodiac[first] : null;
  const b = Object.hasOwn(snapshot.zodiac,second) ? snapshot.zodiac[second] : null;
  if (!a || !b) ctx.fail(1001, '请选择两个生肖');
  const groups = a.compatibility;
  const score = groups.best.includes(second) ? 96 : groups.good.includes(second) || first===second ? 85 :
    groups.bad.includes(second) ? 55 : groups.harm.includes(second) ? 63 : 75;
  const level = score>=90?'契合':score>=80?'良好':score>=70?'平稳':'相处需沟通';
  const description = groups.bad.includes(second) ? '传统说法列为相冲' : groups.best.includes(second) ? '传统说法列为相合' : '按传统生肖关系解读';
  return {zodiac1:a.basic,zodiac2:b.basic,relation:{type:description,score,level,color:score>=80?'#5a8564':'#a8793d',description},
    analysis:{overall:description,love:'关注相处中的实际感受',friendship:'从共同话题建立联系',business:'为合作设定清晰的分工'},
    advice:[reference],disclaimer:reference};
}

const auspicious = new Set([1,3,5,6,7,8,11,13,15,16,17,18,21,23,24,25,29,31,32,33,35,37,39,41,45,47,48,52,57,61,63,65,67,68,81]);
const halfLucky = new Set([26,27,30,38,49,50,51,55,58,71,73,75,77,78]);
function numerology(surname, gender, limit, ctx) {
  if (!hanName.test(surname)) ctx.fail(1001, '请输入一到两个汉字的姓氏');
  const parts = [...surname].map((c)=>characters.get(c)?.strokes ?? namedCharacter(c)?.traditionalStrokes ?? namedCharacter(c)?.strokes);
  if (parts.some((p)=>!Number.isInteger(p))) ctx.fail(1001, '本地字库没有该姓氏的笔画资料');
  const s = parts.reduce((a,b)=>a+b,0);
  const target = gender ? (sex(gender)==='female'?'2':'1') : '';
  const rankLetter = (nu) => {
    const base = (nu - 1) % 81 + 1;
    const wuxing = ['木','火','土','金','水'][Math.floor((((nu - 1) % 10))/2)];
    const key = auspicious.has(base) ? '吉' : halfLucky.has(base) ? '半吉' : '凶';
    return { value:nu,wuxing,level:key,name:`数理 ${base}`,desc:`${base} 数在传统五格中属${key}` };
  };
  const groups = new Map();
  for (const row of sortedCharacters) {
    if (!Number.isInteger(row.strokes) || row.strokes < 2 || row.strokes > 30 || !genderMatch(row,target)) continue;
    if (!groups.has(row.strokes)) groups.set(row.strokes,[]);
    groups.get(row.strokes).push(row);
  }
  const choices = [];
  for (const [a, left] of groups) for (const [b,right] of groups) {
    const raw = [s+(parts.length===1?1:0),parts.at(-1)+a,a+b,b+(parts.length===1?1:parts[0]),s+a+b];
    const letters = raw.map(rankLetter);
    const config = letters.slice(0,3).map((row)=>row.wuxing).join('');
    const supportive = (x,y)=>x===y||'木火土金水'[('木火土金水'.indexOf(x)+1)%5]===y;
    const relationScore = 55 + (supportive(config[0],config[1])?18:0) + (supportive(config[1],config[2])?18:0);
    const weights = [1,3,3,1,2];
    const score = Math.round((letters.reduce((sum, row, i)=>sum+weights[i]*({吉:96,半吉:70,凶:45}[row.level]),0)/10+relationScore)/2);
    const recommended = (rows) => rows.slice(0,10).map((row)=>({
      char:row.character,pinyin:row.pinyin,strokes:row.strokes,wuxing:row.wuxing,meaning:row.nameConnotation,
    }));
    const sample_names = [];
    for (const first of left.slice(0,3)) for (const last of right.slice(0,3)) {
      if (first.character!==last.character && sample_names.length<5)
        sample_names.push({ name:surname+first.character+last.character,meaning:[first.nameConnotation,last.nameConnotation].filter(Boolean).join('、') });
    }
    if (!sample_names.length) continue;
    choices.push({name1_strokes:a,name2_strokes:b,display:`${s} + ${a} + ${b}`,score,
      wuge:Object.fromEntries(['tiange','renge','dige','waige','zongge'].map((key,i)=>[key,letters[i]])),
      sancai:{config,level:relationScore>=90?'大吉':relationScore>=70?'吉':'平',score:relationScore,desc:'按三才五行的相生关系比较组合'},
      recommended_chars:{name1:recommended(left),name2:recommended(right)},sample_names});
  }
  return {surname,surname_strokes:s,surname_wuxing:characters.get([...surname].at(-1))?.wuxing ?? '',
    combinations:choices.sort((x,y)=>y.score-x.score||x.name1_strokes-y.name1_strokes||x.name2_strokes-y.name2_strokes)
      .slice(0,limit).map((row,index)=>({...row,rank:index+1})),disclaimer:reference};
}

const profile = (surname, gender, selected) => ({surname,gender,selected,birthDate:'2000-01-01',year:2000,month:1,day:1,hour:12,minute:0,unknown:true});
const pickName = (row, surname, gender, extra={}) => ({
  name:row.name, fullName:surname+row.name, gender:gender==='female'?'女':'男', rating:'优秀',
  meaning:row.meaning, score:row.score, pinyin:row.pinyin, wuxing:row.wuxing, isLocked:false,
  verse:row.source?.poem ?? '', source:row.source ? {title:row.source.title, author:row.source.author, dynasty:row.source.dynasty} : null,
  ...extra,
});
function parentsNames(query, ctx) {
  const fatherSurname = query.get('father_surname')?.trim() ?? '';
  const motherSurname = query.get('mother_surname')?.trim() ?? '';
  if (!hanName.test(fatherSurname)||!hanName.test(motherSurname)) ctx.fail(1001, '请填写有效的父母姓氏');
  const gender = sex(query.get('gender'));
  const limit = bound(query.get('count'), 100, 1, 200);
  const mother = namedCharacter([...motherSurname].at(-1));
  const matchStats = Object.fromEntries(['直接包含','同音','同偏旁','同声母','五行相生','精选推荐'].map((key)=>[key,0]));
  const motherInfo = {character:mother?.character??motherSurname,pinyin:mother?.pinyin??'',radical:mother?.radical??'',
    wuxing:mother?.wuxing??'',initial:mother?.initialConsonant??'',final:mother?.finalVowels??''};
  const extra = [];
  const seen = new Set();
  const pinyin = stripTone(mother?.pinyin);
  // Use the mother's given surname character or a homophone, then diversify with other documented matches.
  const matches = sortedCharacters.filter((row)=>genderMatch(row,gender)).slice(0, 500)
    .flatMap((row)=>{
      if (fatherSurname.includes(row.character)) return [];
      const text = stripTone(row.pinyin);
      const matchesMother = motherSurname.includes(row.character) ? '直接包含' :
        pinyin && text===pinyin ? '同音' :
        motherInfo.radical && shuowenIndex().lookup.get(row.character)?.radical===motherInfo.radical ? '同偏旁' :
        motherInfo.initial && text.startsWith(motherInfo.initial) ? '同声母' :
        motherInfo.wuxing && '木火土金水'[('木火土金水'.indexOf(motherInfo.wuxing)+1)%5]===row.wuxing ? '五行相生' : '';
      return matchesMother ? [[row,matchesMother]] : [];
    }).sort((a,b)=>Object.keys(matchStats).indexOf(a[1])-Object.keys(matchStats).indexOf(b[1])||compareRank(a[0],b[0]));
  const partners = sortedCharacters.filter((row)=>row.strokes<=15&&genderMatch(row,gender)&&!fatherSurname.includes(row.character)).slice(0,40);
  for (let repeat=0; repeat<4 && extra.length<limit; repeat++) {
    for (let i=0; i<matches.length; i++) {
      const [a, matchType] = matches[i];
      const b = partners[(i+repeat*11) % partners.length];
      if (a.character===b.character) continue;
      const arranged = (i+repeat)%2 ? [a,b] : [b,a];
      const name = arranged.map((c)=>c.character).join('');
      if (seen.has(name)) continue;
      seen.add(name);
      const meaning = arranged.map((c)=>`${c.character}：${c.nameConnotation}`).join('；');
      const matchReason = `${a.character}与母亲姓氏${motherSurname}采用「${matchType}」方式关联`;
      extra.push(pickName({name,meaning,pinyin:arranged.map((c)=>c.pinyin).join(' '),wuxing:arranged.map((c)=>c.wuxing).join(''),
        score:Math.round((a.recommendationScore+b.recommendationScore)/2)},fatherSurname,gender,{matchType,matchReason,tags:[matchType]}));
      matchStats[matchType]++;
      if (extra.length===limit) break;
    }
  }
  if (extra.length<limit) {
    const birth = profile(fatherSurname,gender, ['木','水']);
    for (const row of generateNames(birth,analysisFor(birth))) {
      if (seen.has(row.name)) continue;
      extra.push(pickName(row,fatherSurname,gender,{matchType:'精选推荐',matchReason:'补充备选名字',tags:['精选推荐']}));
      matchStats['精选推荐']++;
      if (extra.length===limit) break;
    }
  }
  return {names:extra,total:extra.length,fatherSurname,motherSurname,motherInfo,gender,matchStats};
}
function classicNames(query, ctx) {
  const id = query.get('book_id') ?? 'shijing';
  const captured = snapshot.poems?.[id];
  const book = poemBooks.find((row)=>row.id===id);
  const surname = query.get('surname')?.trim() ?? '';
  if (surname && !hanName.test(surname)) ctx.fail(1001, '请输入一到两个汉字的姓氏');
  if (!book || !captured?.names?.length) ctx.fail(1001, '本地古籍库尚未收录可用候选');
  const count = bound(query.get('count'),6,1,20);
  const start = hash(surname+id+'-'+Date.now())%captured.names.length;
  const candidates = [...captured.names.slice(start),...captured.names.slice(0,start)].slice(0,count);
  return { surname,book:{id, name:book.name},names:candidates.map((row)=>({...row,fullName:surname+row.name})) };
}
function premiumNames(query, ctx) {
  const surname = query.get('surname')?.trim() || '';
  if (!hanName.test(surname)) ctx.fail(1001, '请输入一到两个汉字的姓氏');
  const gender = sex(query.get('gender'));
  const offset = bound(query.get('offset'),0,0,10000);
  const count = bound(query.get('count'),30,1,100);
  const rows = new Map();
  for (let i=0; i<ELEMENTS.length; i++) {
    const birth = profile(surname,gender,[ELEMENTS[i],ELEMENTS[(i+1)%ELEMENTS.length]]);
    for (const row of generateNames(birth,analysisFor(birth))) if (!rows.has(row.name)) rows.set(row.name,row);
  }
  const sorted = [...rows.values()].sort((a,b)=>Number(Boolean(b.source))-Number(Boolean(a.source))||b.score-a.score||a.name.localeCompare(b.name,'zh'));
  const names = sorted.slice(offset,offset+count).map((row)=>pickName(row,surname,gender));
  return {names,total:sorted.length,freeCount:sorted.length,lockedCount:0,isUnlocked:true,maxNameCount:sorted.length,surname,
    gender,stats:{excellentCount:sorted.length,goodCount:0},isOperator:false,isVip:false};
}

function nameLists(path, query, method, id, ctx) {
  const section = snapshot[path];
  if (method==='POST') {
    const item = section.list.find((x)=>String(x.id)===id);
    if (!item) ctx.fail(1001, '找不到这条记录');
    const key = path+':'+id;
    const current = ctx.db.prepare('SELECT 1 FROM local_tool_likes WHERE session=? AND item=?').get(ctx.session,key);
    if (current) ctx.db.prepare('DELETE FROM local_tool_likes WHERE session=? AND item=?').run(ctx.session,key);
    else ctx.db.prepare('INSERT INTO local_tool_likes (session,item) VALUES (?,?)').run(ctx.session,key);
    return {success:true,isLiked:!current,likeCount:(item.likeCount??0)+Number(!current)};
  }
  const category = query.get('category');
  const keyword = stripTone(query.get('keyword')).trim();
  const rows = section.list.filter((row)=>(!category||category===row.category) &&
    (!keyword||stripTone([row.name,row.pinyin,row.homophone,row.story,row.reason].join(' ')).includes(keyword)));
  const sort = query.get('sort') ?? 'hot';
  const likes = new Set(ctx.db.prepare('SELECT item FROM local_tool_likes WHERE session=?').all(ctx.session).map((r)=>r.item));
  if (sort==='fun' || sort==='funny') rows.sort((a,b)=>(b.funLevel??0)-(a.funLevel??0));
  else if (sort==='latest' || sort==='new') rows.sort((a,b)=>b.id-a.id);
  else if (sort==='likes') rows.sort((a,b)=>(b.likeCount??0)+Number(likes.has(path+':'+b.id))-(a.likeCount??0)-Number(likes.has(path+':'+a.id)));
  else rows.sort((a,b)=>(b.hotScore??0)-(a.hotScore??0));
  const page = paginate(rows,query);
  return { ...page,categories:section.categories??[...new Set(section.list.map((r)=>r.category))].map((key)=>({key,
    name:section.list.find((r)=>r.category===key).categoryName,count:section.list.filter((r)=>r.category===key).length})),
    guide:section.guide,
    list:page.list.map((row)=>({...row,isLiked:likes.has(path+':'+row.id),likeCount:(row.likeCount??0)+Number(likes.has(path+':'+row.id))})) };
}
const birthFromQuery = (query, ctx) => {
  const month = Number(query.get('month'));
  const day = Number(query.get('day'));
  const {year} = dateFields(`2000-${pad(month)}-${pad(day)}`,ctx);
  return Solar.fromYmd(year,month,day).getXingZuo()+'座';
};

export async function handleTools(req, res, url, ctx) {
  const pathname = decodeURIComponent(url.pathname);
  const method = req.method;
  const query = url.searchParams;
  const surnameExists = pathname.match(/^\/api\/v1\/surnames\/([^/]+)\/exists$/);
  if (method==='GET' && surnameExists) return {exists:surnames.has(surnameExists[1])};
  const prefix = '/api/v1/tools/';
  if (!pathname.startsWith(prefix)) return;
  const path = pathname.slice(prefix.length);
  const [resource, tail, leaf] = path.split('/');
  if (resource==='unlock') return;
  if (method==='GET') {
    switch (path) {
      case 'almanac': return almanac(query.get('query_date')||stamp(),ctx);
      case 'constellation/list': return { list:constellations };
      case 'constellation/today': return todayFortune();
      case 'zodiac/list': return zodiacList;
      case 'poem-naming/books': return {books:poemBooks.map((book)=>({...book,count:snapshot.poems?.[book.id]?.names?.length??0}))};
      case 'surnames': {
        const needle = stripTone(query.get('keyword')).trim();
        const rows = [...surnames.values()].filter((row)=>!needle||(stripTone([row.surname,row.pinyin].join(' ')).includes(needle)||stripTone(row.pinyin).replace(/\s+/g,'').includes(needle)));
        const page = paginate(rows,query,100);
        return {...page,totalPages:Math.ceil(page.total/page.size)};
      }
      case 'naming-characters': return charList(query);
      case 'naming-characters/wuxing': return wuxingList.map((row)=>({...row,count:sortedCharacters.filter((char)=>char.wuxing===row.wuxing).length}));
      case 'shuowen/stats': {
        const {entries,merged,radicals,modern}=shuowenIndex();
        return { total:merged.length, with_shuowen:entries.length, with_modern:modern.size, radical_count:radicals.length };
      }
      case 'shuowen/radicals': return {items:shuowenIndex().radicals};
      case 'shuowen/hot': return {items:original['/api/v1/tools/shuowen/hot'].data.items.slice(0,bound(query.get('limit'),12,1,100))};
      case 'popular-names': {
        const decade = query.get('decade');
        const gender = query.get('gender');
        const rows = namedata.popularNames.filter((r)=>(!decade||decade==='all'||r.decade===decade) &&
          (!gender||gender==='all'||String(r.gender)===gender));
        const meta = original['/api/v1/tools/popular-names'].data;
        return {...meta,...paginate(rows,query)};
      }
      case 'popular-names/check': {
        const name = query.get('name')?.trim() ?? '';
        const top = namedata.popularNames.filter((r)=>r.name===name).sort((a,b)=>b.estimatedCount-a.estimatedCount)[0];
        return top ? {...top,found:true,funFact:`在本地公开榜单排行第 ${top.rank}`,percentile:''} :
          {name,found:false,funFact:'本地热门名榜单中未找到这个名字'};
      }
    }
    if (resource==='constellation' && tail && !leaf) {
      const entry = (Object.hasOwn(snapshot.constellation,tail) ? snapshot.constellation[tail] : null) ?? Object.values(snapshot.constellation).find((r)=>r.basic.name_en.toLowerCase()===tail.toLowerCase());
      if (!entry) ctx.fail(1001,'未找到该星座');
      return entry;
    }
    if (resource==='zodiac' && tail==='characters' && leaf) {
      const source = Object.hasOwn(snapshot.zodiacCharacters,leaf) ? snapshot.zodiacCharacters[leaf] : null;
      if (!source) ctx.fail(1001,'未找到该生肖的用字');
      const limit = bound(query.get('limit'),8,1,30);
      return {...source,radical_characters:source.radical_characters.map((row)=>({...row,characters:row.characters.slice(0,limit)}))};
    }
    if (resource==='zodiac' && tail && !leaf) {
      if (!Object.hasOwn(snapshot.zodiac,tail)) ctx.fail(1001,'未找到该生肖');
      return snapshot.zodiac[tail];
    }
    if (resource==='surnames' && tail && !leaf) {
      const item = surnames.get(tail);
      if (!item) ctx.fail(1001,'本地姓氏库未收录该姓氏');
      return snapshot.surname[tail] ?? {...item,origin:item.originBrief,figures:[],figureCount:0};
    }
    if (resource==='naming-characters' && tail==='wuxing' && leaf) return byElement(leaf,ctx);
    if (resource==='naming-characters' && tail && !leaf) return charDetail(tail,method,false,query,ctx);
    if (resource==='shuowen' && tail==='char' && leaf) return dictionaryDetail(leaf,ctx);
    if (resource==='shuowen' && ['radical','pinyin'].includes(tail) && leaf) {
      const {merged} = shuowenIndex();
      const rows = merged.filter((r)=>tail==='radical'?r.radical===leaf:r.pinyinHead===leaf.toLowerCase());
      const {list,...page} = paginate(rows,query);
      return {...page,items:list.map(({character,pinyin,radical,brief,wuxing,strokes})=>({character,pinyin,radical,brief,wuxing,strokes}))};
    }
  }
  if (resource==='naming-characters' && tail && leaf==='collect' && ['POST','DELETE'].includes(method))
    return charDetail(tail,method,true,query,ctx);
  if (['funny-names','homophone-names'].includes(resource) && ((method==='GET'&&!tail)||(method==='POST'&&leaf==='like'))) {
    ctx.db.exec('CREATE TABLE IF NOT EXISTS local_tool_likes (session TEXT, item TEXT, PRIMARY KEY(session,item))');
    return nameLists(resource,query,method,tail,ctx);
  }
  if (method!=='POST') return;
  switch (path) {
    case 'bazi': return chart(await ctx.body(),ctx);
    case 'wuge': {
      const body = await ctx.body();
      return numerology(body.surname?.trim()??'',body.gender,bound(body.limit,10,1,40),ctx);
    }
    case 'constellation/by-birthday': return {constellation:birthFromQuery(query,ctx)};
    case 'constellation/compatibility': return matchConstellation(query.get('constellation1'),query.get('constellation2'),ctx);
    case 'zodiac/by-year': return zodiacByYear(Number((await ctx.body()).year),ctx);
    case 'zodiac/compatibility': {
      const body = await ctx.body();
      return matchZodiac(body.zodiac1,body.zodiac2,ctx);
    }
    case 'poem-naming/generate': return classicNames(query,ctx);
    case 'parents-naming/generate': return parentsNames(query,ctx);
    case 'premium-names/generate': return premiumNames(query,ctx);
  }
}
