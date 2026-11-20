import {readFileSync, writeFileSync} from 'node:fs';
import {performance} from 'node:perf_hooks';
import {DatabaseSync} from 'node:sqlite';
import {generateAiCandidates, handleNaming} from '../local/naming.mjs';

const [samplePath, outputPath] = process.argv.slice(2);
if (!samplePath || !outputPath) {
  throw new Error('用法：node scripts/replay-ai-naming.mjs <对照样本 JSON> <输出 JSON>');
}
const samples = JSON.parse(readFileSync(samplePath, 'utf8'));

function compare(names, originalNames = []) {
  const originalRanks = new Map(originalNames.map((name, rank) => [name, rank]));
  const matches = names.filter(name => originalRanks.has(name.given_name));
  let comparablePairs = 0;
  let sameOrderPairs = 0;
  for (const [index, name] of matches.entries()) {
    for (const other of matches.slice(index + 1)) {
      comparablePairs++;
      if (originalRanks.get(name.given_name) < originalRanks.get(other.given_name)) sameOrderPairs++;
    }
  }
  return {
    count: names.length,
    overlap: matches.length,
    comparablePairs,
    sameOrderPairs,
    hasSourceText: names.filter(name => Boolean(name.source)).length,
    verifiedLiterarySource: names.filter(name => name.reference?.poem?.includes(name.given_name)).length,
  };
}

function detailSections(name) {
  return Object.entries({
    来源: name.source,
    寓意: name.overall_meaning,
    单字: name.characters?.length === 2,
    音律: name.phonetics,
    字形: name.shape_analysis,
    五格: name.wuge,
    喜用: name.yongshen?.length,
    使用提醒: name.ai_tradeoff,
  }).filter(([, value]) => value).map(([label]) => label);
}

const reports = [];
for (const sample of samples) {
  const {id, input, inputStatus, missing, original} = sample;
  if (inputStatus === 'exact' && missing?.length) throw new Error(id + ' 标记为完全同输入但仍有缺失字段');
  const db = new DatabaseSync(':memory:');
  const sent = Symbol();
  const events = [];
  const ctx = {
    db, session: id, sent, body: async () => input,
    fail: (_code, message) => { throw new Error(message); },
  };
  const endpoint = path => new URL('http://127.0.0.1/api/v1/naming_ai/' + path);
  const response = {
    writeHead() {},
    write(content) {
      if (content.startsWith('data: ')) events.push(JSON.parse(content.slice(6)));
      return true;
    },
    end() {},
  };
  const start = performance.now();
  try {
    const target = {AI1: 10, AI2: 20, AI3: 30}[input.package_code] || 20;
    const candidatePool = generateAiCandidates(input, target).names;
    await handleNaming({method: 'POST'}, response, endpoint('generate-stream'), ctx);
    const names = events.filter(event => event.type === 'batch').flatMap(event => event.names);
    const details = await Promise.all(names.map(name => handleNaming({method: 'GET'}, {}, endpoint('names/' + name.id), ctx)));
    const {names: originalNames, ...originalMetrics} = original ?? {names: []};
    const report = {
      id, inputStatus, missing, original: {...originalMetrics, count: originalNames.length},
      seconds: Math.round((performance.now() - start) / 100) / 10,
      model: events[0]?.model, events: events.map(event => event.type),
      error: events.find(event => event.type === 'error')?.message,
      candidatePool: compare(candidatePool, originalNames),
      result: compare(names, originalNames),
      detail: details.map((item, index) => ({
        rank: index + 1, sections: detailSections(item),
        sourceKind: item.source_kind ?? (item.reference ? 'literary' : null),
        hasPhoneticSection: Boolean(item.phonetic),
        hasGlyphSection: Boolean(item.glyph),
      })),
    };
    reports.push(report);
    const {detail, ...summary} = report;
    console.log(JSON.stringify({...summary, topDetailSections: detail[0]?.sections ?? []}));
    if (events.at(-1)?.type !== 'done' || names.length !== target) process.exitCode = 1;
  } finally {
    db.close();
  }
}
writeFileSync(outputPath, JSON.stringify(reports, null, 2) + '\n', {mode: 0o600});
