export const elements = ['木', '火', '土', '金', '水'];
export const methods = {
  bazi: {label: '八字起名', root: '/bazi-naming', caption: '根据生辰排盘，按喜用五行筛选用字。'},
  poetry: {label: '诗词起名', root: '/naming', caption: '从古籍与本地字库中挑选音义合适的名字。'},
  ai: {label: 'AI 起名', root: '/naming-ai', caption: '把家长的偏好和用字条件交给模型，生成候选与推荐理由。'},
};

export function methodFor(path) {
  return path.startsWith('/bazi-naming/') ? 'bazi' : path.startsWith('/naming-ai/') ? 'ai' : 'poetry';
}

export function resultPath(mode, batch, page = 1) {
  const params = new URLSearchParams({[mode === 'ai' ? 'session_id' : 'historyId']: batch});
  if (page > 1) params.set('page', page);
  return methods[mode].root + '/result?' + params;
}

export function detailPath(mode, batch, id, page = 1) {
  const params = new URLSearchParams(mode === 'ai' ? {id} : {name_id: id});
  if (batch) params.set('history_id', batch);
  if (page > 1) params.set('page', page);
  if (mode === 'bazi') params.set('from', 'bazi-naming');
  return (mode === 'ai' ? '/naming-ai/detail?' : '/naming/detail?') + params;
}

export async function request(path, {body, signal} = {}) {
  const response = await fetch(path, {
    method: body === undefined ? 'GET' : 'POST', signal,
    ...(body === undefined ? {} : {headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)}),
  });
  const result = await response.json();
  if (!response.ok || result.code !== 0) throw new Error(result.message || '请求没有成功，请重试。');
  return result.data;
}

export async function generateAi(input, onEvent, signal) {
  const response = await fetch('/api/v1/naming_ai/generate-stream', {
    method: 'POST', headers: {'Content-Type': 'application/json', Accept: 'text/event-stream'},
    body: JSON.stringify(input), signal,
  });
  if (response.status === 429) {
    const error = await response.json().catch(() => null);
    throw new Error(error?.message || '请求较多，请稍后再试。');
  }
  if (!response.ok || !response.body || !response.headers.get('content-type')?.includes('text/event-stream')) {
    throw new Error('AI 起名服务暂时不可用，请稍后重试。');
  }
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let pending = '';
  let complete = false;
  try {
    for (;;) {
      const {done, value} = await reader.read();
      pending += done ? decoder.decode() : decoder.decode(value, {stream: true});
      let end;
      while ((end = /\r?\n\r?\n/.exec(pending))) {
        const frame = pending.slice(0, end.index);
        pending = pending.slice(end.index + end[0].length);
        const json = frame.split(/\r?\n/).filter(line => line.startsWith('data:')).map(line => line.slice(5).trimStart()).join('\n');
        if (!json) continue;
        const event = JSON.parse(json);
        if (event.type === 'error') throw new Error(event.message || '生成已中断，请重试。');
        onEvent(event);
        if (event.type === 'done') complete = true;
      }
      if (done) break;
    }
    if (!complete) throw new Error('生成未完成，请重试或查看已收到的候选。');
  } finally {
    await reader.cancel().catch(() => {});
    reader.releaseLock();
  }
}

function stringValue(value) {
  return typeof value === 'string' ? value.trim() : '';
}

export function sourceFor(row) {
  const reference = row.reference || (typeof row.source === 'object' ? row.source : null);
  if (stringValue(reference?.poem)) return {
    kind: 'literary', title: stringValue(reference.title), quote: reference.poem.trim(),
    author: stringValue(reference.author), dynasty: stringValue(reference.dynasty), book: stringValue(reference.book),
  };
  if (row.poem?.has_poem && stringValue(row.poem.verse)) return {
    kind: 'literary', title: stringValue(row.poem.source), quote: row.poem.verse.trim(),
    author: stringValue(row.poem.author), dynasty: stringValue(row.poem.dynasty), book: '',
  };
  return {kind: 'combination', text: row.source_kind === 'combination' ? stringValue(row.source) : ''};
}

function compactMeaning(value) {
  return stringValue(value).replace(/^(?:用作人名意指|用于人名意指)/, '')
    .replace(/[。！？]+$/, '').replace(/之义$/, '');
}

export function candidateFor(row) {
  const fullName = row.full_name || row.name_card?.full_name || '';
  const givenName = row.given_name || row.name_card?.name ||
    (typeof row.name === 'string' ? row.name : '') || fullName.slice(row.surname?.length || 1);
  const characters = (row.characters || row.chars || []).map(char => ({
    char: char.char || char.character, pinyin: char.pinyin, wuxing: char.wuxing,
    strokes: char.strokes, radical: char.radical,
    meaning: char.name_meaning || char.connotation || char.meaning || '',
    dictionaryMeaning: compactMeaning(char.meaning) !== compactMeaning(char.name_meaning || char.connotation || char.meaning) ? char.meaning : '',
  }));
  return {
    id: String(row.id ?? ''), fullName, givenName,
    surname: row.surname || row.name_card?.surname || fullName.slice(0, fullName.length - givenName.length),
    pinyin: row.pinyin || row.name_card?.pinyin || '',
    elements: row.char_wuxing_combo || (Array.isArray(row.wuxing) ? row.wuxing.join('') : '') ||
      characters.map(char => char.wuxing || '').join(''),
    meaning: stringValue(row.ai_reason || row.overall_meaning || row.meaning?.brief || row.meaning).split('\n使用提醒：')[0],
    caution: stringValue(row.ai_tradeoff),
    source: sourceFor(row), characters,
    score: Number.isFinite(row.score?.total) ? row.score.total : Number.isFinite(row.score) ? row.score : null,
    scoreNote: stringValue(row.score?.comment),
    isCollected: Boolean(row.is_collected || row.isFavorite),
  };
}

export function fetchName(mode, id, signal) {
  return request(mode === 'ai' ? '/api/v1/naming_ai/names/' + encodeURIComponent(id)
    : '/api/v1/naming/detail?' + new URLSearchParams({name_id: id}), {signal});
}
