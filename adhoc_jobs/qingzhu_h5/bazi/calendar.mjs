import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';
import {join} from 'node:path';

const require = createRequire(import.meta.url);
let lunarPackage;
try {
  lunarPackage = require('lunar-javascript');
} catch (error) {
  if (error.code !== 'MODULE_NOT_FOUND') throw error;
  const globalModules = execFileSync('npm', ['root', '-g'], {encoding: 'utf8'}).trim();
  lunarPackage = require(join(globalModules, 'lunar-javascript'));
}
const {Solar, LunarUtil} = lunarPackage;

export const ELEMENTS = [...'金木水火土'];
const CYCLE = [...'木火土金水'];
const ANIMALS = [...'鼠牛虎兔龙蛇马羊猴鸡狗猪'];
const BRANCHES = [...'子丑寅卯辰巳午未申酉戌亥'];
const HOURS = new Map([
  ['晚子时',23],['早子时',0],['子时',23],
  ...[...'丑寅卯辰巳午未申酉戌亥'].map((branch,index)=>[branch+'时',index*2+1]),
]);
const GENERATES = Object.fromEntries(CYCLE.map((el,i)=>[el,CYCLE[(i+1)%5]]));
const CONTROLS = Object.fromEntries(CYCLE.map((el,i)=>[el,CYCLE[(i+2)%5]]));
const incoming = (relation, element) => CYCLE.find(el=>relation[el]===element);
const GAN = LunarUtil.WU_XING_GAN;
const ZHI = LunarUtil.WU_XING_ZHI;

export class InputError extends Error {}

export function parseBirth(body) {
  const surname = typeof body.surname === 'string' ? body.surname.trim() : '';
  if (!/^[\p{Script=Han}]{1,2}$/u.test(surname) || surname.length > 2) {
    throw new InputError('请输入一到两个汉字的姓氏');
  }
  const gender = body.gender;
  if (!['male','female'].includes(gender)) throw new InputError('请选择性别');
  const match = typeof body.birthDate === 'string' && /^(\d{4})-(\d{2})-(\d{2})$/.exec(body.birthDate);
  if (!match) throw new InputError('请输入有效的出生日期');
  const [year, month, day] = match.slice(1).map(Number);
  const check = new Date(Date.UTC(year,month-1,day));
  if (year < 1950 || year > 2199 || check.getUTCFullYear() !== year ||
      check.getUTCMonth() + 1 !== month || check.getUTCDate() !== day) {
    throw new InputError('出生日期不在支持范围内或日期无效');
  }
  const clock = body.birthTime;
  const unknown = clock === 'unknown';
  const timeMatch = typeof clock === 'string' && /^([01]\d|2[0-3]):([0-5]\d)$/.exec(clock);
  if (!unknown && !timeMatch && !HOURS.has(clock)) throw new InputError('请选择有效的出生时辰');
  const hour = unknown ? 12 : timeMatch ? Number(timeMatch[1]) : HOURS.get(clock);
  const minute = timeMatch ? Number(timeMatch[2]) : 0;
  const time = unknown ? 'unknown' : [hour, minute].map(n=>String(n).padStart(2,'0')).join(':');
  const selected = body.selectedXiyongShen === undefined ? [] : body.selectedXiyongShen;
  if (!Array.isArray(selected) || selected.length > 2 || new Set(selected).size !== selected.length ||
      selected.some(element=>!ELEMENTS.includes(element))) {
    throw new InputError('请选择一到两个不同的喜用五行');
  }
  return {surname,gender,birthDate:body.birthDate,time,year,month,day,hour,minute,unknown,selected};
}

const GODS = ['比肩','劫财','食神','伤官','偏财','正财','偏官','正官','偏印','正印'];
const SIGNS = {
  白羊:'火', 金牛:'土', 双子:'风', 巨蟹:'水', 狮子:'火', 处女:'土',
  天秤:'风', 天蝎:'水', 射手:'火', 摩羯:'土', 水瓶:'风', 双鱼:'水',
};

const normalizeGod = value=>value==='七杀'?'偏官':value;

function pillar(chart, name, stars) {
  const ganzhi = chart['get'+name]();
  const [gan,zhi] = ganzhi;
  const cangGan = chart['get'+name+'HideGan']();
  const nayin = chart['get'+name+'NaYin']();
  const shishen = name === 'Day' ? '日主' : normalizeGod(chart['get'+name+'ShiShenGan']());
  const partner = BRANCHES.find(branch=>LunarUtil.HE_ZHI_6[BRANCHES.indexOf(zhi)+1]===branch);
  return {
    gan,zhi,ganzhi,ganWuxing:GAN[gan],zhiWuxing:ZHI[zhi],nayin,nayinWuxing:nayin.at(-1),
    shishen,zizuo:chart['get'+name+'DiShi'](),zhiShishen:chart['get'+name+'ShiShenZhi']().map(normalizeGod),
    cangGan,cangGanWuxing:cangGan.map(stem=>GAN[stem]),shensha:stars(zhi),partner,
  };
}

function starLookup(dayGan, dayZhi, yearZhi) {
  const heaven = {甲:'丑未',戊:'丑未',庚:'丑未',乙:'子申',己:'子申',丙:'亥酉',丁:'亥酉',壬:'卯巳',癸:'卯巳',辛:'寅午'};
  const arts = {甲:'巳',乙:'午',丙:'申',丁:'酉',戊:'申',己:'酉',庚:'亥',辛:'子',壬:'寅',癸:'卯'};
  const travel = [['申子辰','寅','酉'],['寅午戌','申','卯'],['巳酉丑','亥','午'],['亥卯未','巳','子']];
  const reference = travel.filter(([group])=>group.includes(dayZhi)||group.includes(yearZhi));
  return branch=>[
    heaven[dayGan]?.includes(branch) && '天乙贵人',
    arts[dayGan]===branch && '文昌',
    reference.some(([,horse])=>horse===branch) && '驿马',
    reference.some(([, ,flower])=>flower===branch) && '桃花',
  ].filter(Boolean);
}

function elementCounts(pillars) {
  const count = list=>Object.fromEntries(ELEMENTS.map(el=>[el,list.filter(value=>value===el).length]));
  return {
    standard:count(pillars.flatMap(p=>[p.ganWuxing,p.zhiWuxing])),
    withHidden:count(pillars.flatMap(p=>[p.ganWuxing,...p.cangGanWuxing])),
  };
}

// Calibrated against publicly observable four-pillar results. These weights
// approximate the service; the service's own implementation is not available.
const MONTH_STRENGTH = {same:64, resource:58.5, output:31, wealth:27, controls:20.5};
const STEM_STRENGTH = {same:10, resource:9, output:0, wealth:-1, controls:-4};

function relationToDay(element, own) {
  if (element === own) return 'same';
  if (GENERATES[element] === own) return 'resource';
  if (GENERATES[own] === element) return 'output';
  if (CONTROLS[own] === element) return 'wealth';
  return 'controls';
}

function strengthOf(pillars, day, month) {
  const own = day.ganWuxing;
  const supporting = [own,incoming(GENERATES,own)];
  const controlling = incoming(CONTROLS,own);
  let strength = MONTH_STRENGTH[relationToDay(month.zhiWuxing, own)];
  for (const pillar of pillars) {
    if (pillar!==day) strength += STEM_STRENGTH[relationToDay(pillar.ganWuxing, own)];
    if (pillar===month) {
      if (pillar.cangGanWuxing.slice(1).includes(controlling)) strength -= 3;
      continue;
    }
    if (pillar.zhiWuxing===own) strength += 7.5;
    else if (pillar.zhiWuxing===controlling) strength -= 1;
    if (pillar.cangGanWuxing.slice(1).includes(own)) strength += 3.5;
  }
  const roots = pillars.filter(p=>p.cangGanWuxing.includes(own)).map(p=>p.zhi);
  const score = Math.max(20,Math.min(80,Math.round(strength)));
  const level = score < 42 ? '偏弱' : score >= 58 ? '偏强' : '中和';
  const helpful = level === '偏强'
    ? [incoming(CONTROLS,own),CONTROLS[own],GENERATES[own]]
    : level === '中和' ? [supporting[1],incoming(CONTROLS,own)] : [supporting[1],own];
  const harmful = CYCLE.filter(el=>!helpful.includes(el));
  const lines = [
    `日主【${day.gan}】属${own}，月支${month.zhi}属${month.zhiWuxing}。`,
    roots.length ? `在${roots.join('、')}见同类藏干。` : '地支藏干中未见同类根气。',
    `按月令、透干和根气综合判断，日主${level}（${score} 分）。`,
  ];
  return {score,level,helpful,harmful,lines,roots,analysis:lines.join('')};
}

export function analyzeBirth(birth) {
  const {year,month,day,hour,minute,unknown} = birth;
  const solar = Solar.fromYmdHms(year,month,day,hour,minute,0);
  const lunar = solar.getLunar();
  const chart = lunar.getEightChar();
  chart.setSect(1);
  const stars = starLookup(chart.getDayGan(),chart.getDayZhi(),chart.getYearZhi());
  const bazi = {
    year:pillar(chart,'Year',stars), month:pillar(chart,'Month',stars),
    day:pillar(chart,'Day',stars), hour:unknown ? null : pillar(chart,'Time',stars),
  };
  const pillars = Object.values(bazi).filter(Boolean);
  const {standard,withHidden} = elementCounts(pillars);
  const lack = ELEMENTS.filter(el=>standard[el]===0);
  const excess = ELEMENTS.filter(el=>standard[el]>=3);
  const balance = lack.length ? `五行缺${lack.join('、')}` : '五行齐全';
  const riZhuStrength = strengthOf(pillars,bazi.day,bazi.month);
  const [yong,xi] = riZhuStrength.helpful;
  const dayElement = bazi.day.ganWuxing;
  const ji = riZhuStrength.level === '偏强' ? incoming(GENERATES,dayElement) :
    riZhuStrength.level === '偏弱' ? GENERATES[dayElement] : '';
  const principle = '以月令、透干和根气判断强弱，再取扶抑喜用。';
  const yong_shen_detail = {
    yong,xi,ji,xian:riZhuStrength.harmful.filter(el=>el!==ji).join('、'),
    description:`建议优先选${yong}、${xi}属性的字。`,method:'扶抑',
    tiaohou:{primary_gan:[],secondary_gan:[],primary_wuxing:[],secondary_wuxing:[],xiyong_wuxing:[yong,xi],note:''},
  };
  const patternGod = bazi.month.shishen;
  const pattern = {
    name:patternGod+'格',
    category:'正格',
    description:`以月干十神${patternGod}标示格局。`,
  };
  const godCounts = Object.fromEntries(GODS.map(god=>[god,0]));
  for (const p of pillars) for (const god of [p.shishen,...p.zhiShishen]) {
    if (god in godCounts) godCounts[god]++;
  }
  const zodiacIndex = BRANCHES.indexOf(bazi.year.zhi);
  const zodiac = {
    name:ANIMALS[zodiacIndex],wuxing:bazi.year.zhiWuxing,
    chong:ANIMALS[(zodiacIndex+6)%12],he:ANIMALS[BRANCHES.indexOf(bazi.year.partner)] ?? '',
    description:`以年柱${bazi.year.ganzhi}查生肖。`,
  };
  const zodiac_rules = {traits:`生肖${zodiac.name}。本地选字以喜用五行为准。`,like:[],avoid:[]};
  const xingzuo = solar.getXingZuo();
  const keys = [['year','Year'],['month','Month'],['day','Day'],['hour','Time']];
  const perPillar = f=>Object.fromEntries(keys.map(([k,method])=>[k,bazi[k] ? f(method,bazi[k]) : null]));
  return {
    bazi,bazi_str:pillars.map(p=>p.ganzhi).join(' '),hour_unknown:unknown,
    solar:{year,month,day,hour:unknown ? null : hour,minute:unknown ? null : minute,week:solar.getWeekInChinese(),weekIndex:solar.getWeek()},
    lunar:{year:lunar.getYear(),month:Math.abs(lunar.getMonth()),day:lunar.getDay(),
      yearCn:lunar.getYearInChinese(),monthCn:lunar.getMonthInChinese()+'月',dayCn:lunar.getDayInChinese(),
      isLeap:lunar.getMonth()<0,yearGanZhi:lunar.getYearInGanZhi(),monthGanZhi:lunar.getMonthInGanZhi(),dayGanZhi:lunar.getDayInGanZhi()},
    wuxing:{count:Object.fromEntries(ELEMENTS.map(el=>[el,{
      count:standard[el],percentage:Math.round(100*standard[el]/(2*pillars.length)),
    }])),lack,excess,balance},
    wuxing_analysis:{metal:standard.金,wood:standard.木,water:standard.水,fire:standard.火,earth:standard.土,lack:lack.join('、'),strong:excess.join('、'),advice:balance},
    wuxingWithCangGan:withHidden,
    wuxing_detail:{lines:riZhuStrength.lines,lack,excess,month_relation:bazi.month.zhiWuxing,month_role:bazi.month.zhiShishen[0],roots:riZhuStrength.roots,help_gans:pillars.filter(p=>riZhuStrength.helpful.includes(p.ganWuxing)).map(p=>p.gan)},
    xiyong_shen:[yong,xi],ji_shen:ji,yong_shen_detail,
    yongshen_reasoning:{principle,lines:riZhuStrength.lines.concat(`推荐选字五行：${yong}、${xi}。`)},
    riGan:{name:bazi.day.gan,wuxing:bazi.day.ganWuxing,yinyang:[...'甲丙戊庚壬'].includes(bazi.day.gan)?'阳':'阴',description:`日主${bazi.day.gan}属${bazi.day.ganWuxing}。`},
    riZhuStrength,pattern,zodiac,zodiac_rules,
    shishen:{list:godCounts,pattern:pattern.name},
    kongwang:perPillar(method=>[...chart['get'+method+'XunKong']()]),
    changsheng:perPillar((method,p)=>({position:p.zizuo,description:p.zizuo})),
    shensha:{list:keys.flatMap(([key])=>(bazi[key]?.shensha ?? []).map(name=>({name,position:key,type:'吉',description:name})))},
    xingzuo:{name:xingzuo+'座',date:birth.birthDate.slice(5),element:SIGNS[xingzuo]},
    personality:{positive:[],negative:[],description:''},
  };
}
