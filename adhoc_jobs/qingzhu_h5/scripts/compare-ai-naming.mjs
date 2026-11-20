import {readFileSync,writeFileSync} from 'node:fs';
import {generateLocalNaming} from '../local/naming.mjs';

const file = process.argv[2];
const referenceFile=process.argv[3]||'.local/original-name-ranking-sample.json';
if(!file) throw new Error('用法：node scripts/compare-ai-naming.mjs <本地实测 JSON> [原站匿名样本 JSON]');
const live=JSON.parse(readFileSync(file,'utf8'));
const original=JSON.parse(readFileSync(referenceFile,'utf8')).ai;
const modelNames=live.records.filter(row=>row.type==='batch').flatMap(row=>row.names);
const baseline=generateLocalNaming(live.body,{mode:'ai',count:20}).names;
const candidates=generateLocalNaming(live.body,{mode:'ai',count:120}).names;
const originalNames=original.ranked.map(([name])=>name);
const originalSet=new Set(originalNames);
function analyze(names) {
  const matched=names.filter(row=>originalSet.has(row.given_name)).map(row=>row.given_name);
  const positions=names.map(row=>originalNames.indexOf(row.given_name)).filter(index=>index>=0);
  let concordant=0,totalPairs=0;
  for(let i=0;i<positions.length;i++) for(let j=i+1;j<positions.length;j++) {
    totalPairs++;
    if(positions[i]<positions[j]) concordant++;
  }
  return {
    count:names.length,unique:new Set(names.map(row=>row.given_name)).size,
    matchingOriginal:matched.length,matchingNames:matched,
    matchedPairOrder:totalPairs?{concordant,totalPairs}:null,
    hasVerifiedSource:names.filter(row=>!!row.reference?.poem).length,
    secondaryCharacters:new Set(names.flatMap(row=>[...row.given_name].filter(char=>char!==live.body.fixed_char.char))).size,
    scores:[Math.min(...names.map(row=>row.score)),Math.max(...names.map(row=>row.score))],
    topFive:names.slice(0,5).map(row=>({name:row.given_name,score:row.score})),
  };
}
const model=live.records.find(event=>event.type==='init')?.model;
const report={
  model,elapsedSeconds:live.seconds,originalCount:originalNames.length,
  source:'previous authenticated original-site AI record, anonymized',
  limitations:[
    '原站样本的完整出生信息和全部偏好没有保存，比较使用相同姓氏、性别、指定字与土火范围，不能视为完全同输入实验。',
    '原站分数、本地规则分与模型分代表不同评判方式，数值不能直接比较。',
    '原站完整解读曾读取一条，当前持久样本仅保留候选和字段摘要，无法逐句评审。',
    '只有一组真实模型调用，重合率和多样性不能代替人工质量评价。',
  ],
  original:{count:originalNames.length,scores:original.listScores},
  baseline:analyze(baseline),modelResult:analyze(modelNames),candidatePool:analyze(candidates),
};
writeFileSync('.local/ai-model-comparison.json',JSON.stringify(report,null,2)+'\n',{mode:0o600});
console.log(JSON.stringify(report,null,2));
