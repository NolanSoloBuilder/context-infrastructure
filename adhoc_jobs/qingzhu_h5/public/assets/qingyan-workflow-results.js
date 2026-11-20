import {d as defineComponent, j as h, r as ref, v as computed, M as watch, q as useRoute, u as useRouter} from './index-GEgtjqXc.js';
import {methods, methodFor, resultPath, detailPath, request, candidateFor, fetchName} from './qingyan-workflow-data.js';

const size = 30;
const paperSourceLabel = source => source.kind === 'literary' ? '古籍出处' : '选字依据';
const readableElements = value => Array.isArray(value) ? value.join('、') : [...(value || '')].join(' · ');

function markedQuote(quote, name) {
  const start = name ? quote.indexOf(name) : -1;
  return start < 0 ? quote : [quote.slice(0, start), h('mark', null, name), quote.slice(start + name.length)];
}

function sourceCard(candidate) {
  const {source, givenName, characters} = candidate;
  const literary = source.kind === 'literary';
  const metadata = [source.dynasty, source.author, source.title && '《' + source.title + '》'].filter(Boolean);
  return h('section', {class: 'paper-sheet paper-source', 'aria-labelledby': 'paper-source-heading'}, [
    h('h2', {id: 'paper-source-heading'}, paperSourceLabel(source)),
    literary ? [
      h('blockquote', null, markedQuote(source.quote, givenName)),
      metadata.length ? h('p', {class: 'paper-citation'}, metadata.join(' · ')) : null,
      h('p', {class: 'paper-muted'}, source.quote.includes(givenName) ?
        '取字关系：原句中的「' + givenName + '」相连。下方寓意是对这个名字的解读。'
        : '取字关系：这段引文提供用字参考，名字中的两个字在引文里未相连。'),
    ] : [
      h('p', {class: 'paper-muted'}, '这个名字由单字组合，暂无可核验的古籍原句。'),
      source.text ? h('p', null, source.text)
        : characters.length ? h('ul', {class: 'paper-source-characters'}, characters.map(char =>
          h('li', null, [h('strong', null, char.char), h('span', null, [char.wuxing, char.meaning].filter(Boolean).join(' · '))]))) : null,
    ],
  ]);
}

function progressMessage(element, message) {
  return h('p', {class: element, role: element === 'paper-error' ? 'alert' : 'status'}, message);
}

function queryWithFull(route, input = {}) {
  return route.path + '?' + new URLSearchParams({...input, ...route.query, view: 'full'});
}

function shortSource(candidate) {
  return candidate.source.kind === 'literary'
    ? (candidate.source.title ? '《' + candidate.source.title + '》' : '古籍原句')
    : '由字义组合';
}

function selectionFor(key) {
  try {
    const value = JSON.parse(sessionStorage.getItem(key));
    return Array.isArray(value) ? value.filter(row => typeof row.id === 'string' && typeof row.fullName === 'string').slice(0, 3) : [];
  } catch {
    return [];
  }
}

export const Results = defineComponent({
  name: 'QingyanCandidates',
  setup() {
    const route = useRoute();
    const router = useRouter();
    const mode = computed(() => methodFor(route.path));
    const batch = computed(() => String(route.query.session_id || route.query.historyId || route.query.history_id || ''));
    const page = computed(() => Math.max(1, Math.floor(Number(route.query.page)) || 1));
    const storageKey = computed(() => 'qingyan.compare.' + mode.value + '.' + batch.value);
    const selected = ref([]);
    const data = ref(null);
    const loading = ref(true);
    const error = ref('');
    const sourceFilter = ref(false);
    const dialog = ref(null);
    const comparison = ref([]);
    const comparisonLoading = ref(false);
    let comparisonRequest;
    const extending = ref(false);
    const reload = ref(0);
    const notice = ref('');

    watch(storageKey, key => { selected.value = selectionFor(key); sourceFilter.value = false; }, {immediate: true});
    watch([mode, batch, page, reload], async ([kind, key, current], _, cleanup) => {
      const controller = new AbortController();
      cleanup(() => controller.abort());
      loading.value = true;
      error.value = '';
      try {
        if (!key) throw new Error('找不到这批候选，请从起名历史进入或重新起名。');
        const query = '?page=' + current + '&page_size=' + size;
        if (kind === 'bazi') {
          const endpoint = '/api/v1/bazi-naming/history/' + encodeURIComponent(key);
          const first = await request(endpoint, {signal: controller.signal});
          data.value = current === 1 ? {...first, names: first.names.slice(0, size)}
            : {...first, ...await request(endpoint + '/names' + query, {signal: controller.signal})};
        } else if (kind === 'ai') {
          const result = await request('/api/v1/naming_ai/sessions/' + encodeURIComponent(key), {signal: controller.signal});
          data.value = {...result.session, names: result.names, total: result.names.length};
        } else {
          data.value = await request('/api/v2/naming/history/' + encodeURIComponent(key) + '/names' + query, {signal: controller.signal});
        }
      } catch (failure) {
        if (!controller.signal.aborted) error.value = failure.message;
      } finally {
        if (!controller.signal.aborted) loading.value = false;
      }
    }, {immediate: true});

    const visible = computed(() => (data.value?.names || []).map(candidateFor)
      .filter(candidate => !sourceFilter.value || candidate.source.kind === 'literary'));

    function toggle(candidate) {
      const exists = selected.value.some(row => row.id === candidate.id);
      if (!exists && selected.value.length >= 3) {
        notice.value = '最多同时比较 3 个名字。';
        return;
      }
      selected.value = exists ? selected.value.filter(row => row.id !== candidate.id)
        : [...selected.value, {id: candidate.id, fullName: candidate.fullName}];
      notice.value = '';
      try { sessionStorage.setItem(storageKey.value, JSON.stringify(selected.value)); } catch {}
    }

    async function compare() {
      if (selected.value.length < 2 || dialog.value.open) return;
      comparisonRequest?.abort();
      const controller = new AbortController();
      comparisonRequest = controller;
      comparison.value = [];
      comparisonLoading.value = true;
      dialog.value.showModal();
      const entries = selected.value.slice();
      const rows = await Promise.all(entries.map(async entry => {
        try {
          return candidateFor({...await fetchName(mode.value, entry.id, controller.signal), id: entry.id});
        } catch (failure) {
          return {...entry, error: failure.message};
        }
      }));
      if (controller.signal.aborted) return;
      comparison.value = rows;
      comparisonLoading.value = false;
    }

    async function extend() {
      if (extending.value) return;
      extending.value = true;
      notice.value = '';
      try {
        const total = data.value.total;
        const added = await request('/api/v2/naming/history/' + encodeURIComponent(batch.value) + '/extend', {body: {nameCount: 60}});
        notice.value = '已追加 ' + added.addedCount + ' 个候选。';
        const next = Math.floor(total / size) + 1;
        if (next === page.value) reload.value++;
        else router.push(resultPath(mode.value, batch.value, next));
      } catch (failure) {
        notice.value = failure.message;
      } finally {
        extending.value = false;
      }
    }

    const comparisonFields = [
      ['读音', row => row.pinyin],
      ['用字五行', row => readableElements(row.elements)],
      ['取名来源', row => [paperSourceLabel(row.source), shortSource(row)].join(' · ')],
      ['原句或选字依据', row => row.source.kind === 'literary'
        ? markedQuote(row.source.quote, row.givenName) : row.source.text || row.characters.map(char => char.char + '：' + char.meaning).join('；')],
      ['名字寓意', row => row.meaning],
      ['本批参考分', row => row.score === null ? '' : row.score + ' 分'],
    ];

    function renderComparison() {
      const columns = comparison.value;
      return h('dialog', {class: 'paper-compare-dialog', 'aria-labelledby': 'paper-compare-heading', ref: dialog,
        onClose: () => comparisonRequest?.abort()}, [
        h('div', {class: 'paper-dialog-heading'}, [h('h2', {id: 'paper-compare-heading'}, '并排比较'),
          h('button', {type: 'button', class: 'paper-secondary', onClick: () => dialog.value.close()}, '关闭')]),
        comparisonLoading.value ? progressMessage('paper-muted', '正在读取姓名详情…') :
          h('div', {class: 'paper-compare-content', style: {'--paper-columns': String(columns.length || 2)}}, [
            h('div', {class: 'paper-compare-row paper-compare-names'}, columns.map(row =>
              h('a', {href: detailPath(mode.value, batch.value, row.id, page.value)}, row.fullName))),
            ...comparisonFields.map(([label, read]) => h('section', {class: 'paper-compare-section'}, [
              h('h3', null, label),
              h('div', {class: 'paper-compare-row'}, columns.map(row => h('p', null, row.error || read(row) || '暂无资料'))),
            ])),
          ]),
      ]);
    }

    return () => {
      const kind = mode.value;
      const result = data.value;
      const total = result?.total ?? 0;
      const favorable = result?.xiyong_shen || result?.xiyong_shen_list || result?.wuxing_analysis?.yongshen || [];
      const pages = Math.ceil(total / size);
      return h('main', {class: ['paper-workflow paper-results', selected.value.length ? 'paper-has-tray' : '']}, [
        h('div', {class: 'paper-topline'}, [h('a', {href: methods[kind].root + '/form'}, '重新起名'), h('a', {href: '/mine/favorites'}, '我的收藏')]),
        h('header', {class: 'paper-title'}, [
          h('h1', null, '姓名候选'),
          h('p', null, methods[kind].label + (result?.surname ? ' · ' + result.surname + '姓' : '') + (total ? ' · ' + total + ' 个候选' : '')),
        ]),
        result && !loading.value && !error.value ? h('div', {class: 'paper-results-tools'}, [
          favorable.length ? h('p', {class: 'paper-muted'}, '用字参考：' + readableElements(favorable)) : null,
          h('label', {class: 'paper-filter'}, [
            h('input', {type: 'checkbox', checked: sourceFilter.value, onChange: e => sourceFilter.value = e.target.checked}),
            pages > 1 && kind !== 'ai' ? '本页仅看有古籍出处' : '仅看有古籍出处',
          ]),
          kind === 'bazi' || kind === 'ai' ? h('a', {href: queryWithFull(route)}, '完整分析') : null,
          kind === 'bazi' ? h('a', {href: '/bazi-naming/character-library?' + new URLSearchParams({historyId: batch.value})}, '查看完整字典') : null,
        ]) : null,
        result?.generation?.status === 'partial' ? progressMessage('paper-muted', '这次生成中断，以下是已收到的候选。') : null,
        error.value ? progressMessage('paper-error', error.value) : loading.value ? progressMessage('paper-muted', '正在读取候选…') : [
          visible.value.length ? h('div', {class: 'paper-result-list'}, visible.value.map(candidate => {
            const picked = selected.value.some(row => row.id === candidate.id);
            return h('article', {class: ['name-card paper-candidate', picked && 'is-picked'], key: candidate.id}, [
              h('div', {class: 'paper-candidate-heading'}, [
                h('div', null, [h('h2', null, candidate.fullName), candidate.pinyin ? h('p', {class: 'paper-pinyin'}, candidate.pinyin) : null]),
                h('button', {type: 'button', class: 'paper-secondary paper-pick', 'aria-pressed': picked,
                  'aria-label': (picked ? '移出对比 ' : '加入对比 ') + candidate.fullName, onClick: () => toggle(candidate)}, picked ? '已加入' : '对比'),
              ]),
              candidate.elements ? h('p', {class: 'paper-candidate-elements'}, '用字五行 ' + readableElements(candidate.elements)) : null,
              h('div', {class: 'paper-candidate-source'}, [
                h('span', {class: ['paper-source-tag', candidate.source.kind]}, paperSourceLabel(candidate.source)),
                h('span', null, shortSource(candidate)),
              ]),
              candidate.source.kind === 'literary'
                ? h('p', {class: 'paper-card-quote'}, markedQuote(candidate.source.quote, candidate.givenName))
                : candidate.meaning ? h('p', {class: 'paper-card-quote'}, candidate.meaning) : null,
              h('a', {class: 'paper-detail-link', href: detailPath(kind, batch.value, candidate.id, page.value)}, '查看详情'),
            ]);
          })) : progressMessage('paper-muted', sourceFilter.value ? '本页暂无带古籍出处的候选。' : '这批暂无候选，请调整条件后重试。'),
          total && pages > 1 && kind !== 'ai' ? h('nav', {class: 'paper-pages', 'aria-label': '候选分页'}, [
            page.value > 1 ? h('a', {href: resultPath(kind, batch.value, page.value - 1)}, '上一页') : h('span', null, '上一页'),
            h('span', null, page.value + ' / ' + pages),
            page.value < pages ? h('a', {href: resultPath(kind, batch.value, page.value + 1)}, '下一页') : h('span', null, '下一页'),
          ]) : null,
          kind === 'poetry' && total > 0 && total < 800 ? h('button', {type: 'button', class: 'paper-secondary paper-extend',
            disabled: extending.value, onClick: extend}, extending.value ? '正在追加…' : '免费追加候选') : null,
        ],
        notice.value ? progressMessage('paper-notice', notice.value) : null,
        selected.value.length > 0 ? h('aside', {class: 'paper-tray', 'aria-label': '已选对比候选'}, [
          h('div', {class: 'paper-tray-names'}, selected.value.map(entry => h('button', {type: 'button',
            title: '移出对比', 'aria-label': '移出对比 ' + entry.fullName, onClick: () => toggle(entry)}, entry.fullName + ' ×'))),
          h('button', {type: 'button', class: 'paper-button', disabled: selected.value.length < 2, onClick: compare},
            '对比 ' + selected.value.length + ' 个'),
        ]) : null,
        renderComparison(),
      ]);
    };
  },
});

export const Detail = defineComponent({
  name: 'QingyanNameReading',
  setup() {
    const route = useRoute();
    const data = ref(null);
    const loading = ref(true);
    const error = ref('');
    const actionError = ref('');
    const saving = ref(false);
    const id = computed(() => String(route.query.id || route.query.name_id || ''));
    const mode = computed(() => route.path.startsWith('/naming-ai/') ? 'ai' : id.value.includes(':') ? 'bazi' : 'poetry');
    watch([mode, id], async ([kind, key], _, cleanup) => {
      const controller = new AbortController();
      cleanup(() => controller.abort());
      loading.value = true;
      error.value = '';
      actionError.value = '';
      try {
        if (!key) throw new Error('未找到这个姓名。');
        data.value = await fetchName(kind, key, controller.signal);
      } catch (failure) {
        if (!controller.signal.aborted) error.value = failure.message;
      } finally {
        if (!controller.signal.aborted) loading.value = false;
      }
    }, {immediate: true});

    async function favorite(candidate) {
      if (saving.value) return;
      saving.value = true;
      actionError.value = '';
      const key = id.value;
      try {
        const result = await request('/api/v1/naming/collect', {body: {name_id: key, action: candidate.isCollected ? 'uncollect' : 'collect'}});
        if (id.value === key) data.value = {...data.value, is_collected: result.is_collected, isFavorite: result.is_collected};
      } catch (failure) {
        actionError.value = failure.message;
      } finally {
        saving.value = false;
      }
    }

    return () => {
      const raw = data.value;
      const candidate = raw ? candidateFor({...raw, id: id.value}) : null;
      const kind = mode.value;
      const batch = String(route.query.history_id || raw?.history_id || (kind === 'bazi' ? id.value.split(':')[0] : ''));
      const back = batch ? resultPath(kind, batch, Number(route.query.page) || 1) : methods[kind].root + '/form';
      const birthDate = String(raw?.name_card?.birth_date || raw?.birth_time || '').slice(0, 10);
      const context = {
        ...(candidate?.surname ? {surname: candidate.surname} : {}),
        ...(raw?.name_card?.gender || raw?.gender ? {gender: raw?.name_card?.gender || raw.gender} : {}),
        ...(/^\d{4}-\d{2}-\d{2}$/.test(birthDate) ? {birth_date: birthDate} : {}),
        ...(kind === 'bazi' ? {from: 'bazi-naming'} : {}),
      };
      const report = candidate ? '/naming/report-select?' + new URLSearchParams({
        ...context, name_id: id.value, history_id: batch, surname: candidate.surname, name: candidate.givenName,
      }) : '';
      return h('main', {class: 'paper-workflow paper-reading'}, [
        h('div', {class: 'paper-topline'}, [h('a', {href: back}, '返回候选'), h('a', {href: '/'}, '首页')]),
        error.value ? progressMessage('paper-error', error.value)
          : loading.value || !candidate ? progressMessage('paper-muted', '正在读取姓名解读…') : [
            h('header', {class: 'paper-reading-hero'}, [
              h('h1', null, candidate.fullName),
              candidate.pinyin ? h('p', {class: 'paper-pinyin'}, candidate.pinyin) : null,
              candidate.elements ? h('p', {class: 'paper-muted'}, '用字五行 ' + readableElements(candidate.elements)) : null,
              h('button', {type: 'button', class: 'paper-secondary', disabled: saving.value, 'aria-pressed': candidate.isCollected,
                onClick: () => favorite(candidate)}, candidate.isCollected ? '取消收藏' : '收藏姓名'),
              actionError.value ? progressMessage('paper-error', actionError.value) : null,
            ]),
            sourceCard(candidate),
            candidate.meaning || candidate.caution ? h('section', {class: 'paper-sheet'}, [
              h('h2', null, '名字寓意'),
              candidate.meaning ? h('p', null, candidate.meaning) : null,
              candidate.caution ? h('p', {class: 'paper-muted'}, '使用提醒：' + candidate.caution) : null,
            ]) : null,
            candidate.characters.length ? h('section', {class: 'paper-sheet'}, [h('h2', null, '单字解读'),
              h('div', {class: 'paper-character-list'}, candidate.characters.map(char => h('article', null, [
                h('h3', null, char.char),
                h('p', {class: 'paper-muted'}, [char.pinyin, char.wuxing && '五行 ' + char.wuxing, char.strokes && char.strokes + ' 画',
                  char.radical && '部首 ' + char.radical].filter(Boolean).join(' · ')),
                char.meaning ? h('p', null, char.meaning) : null,
                char.dictionaryMeaning ? h('p', {class: 'paper-muted'}, char.dictionaryMeaning) : null,
              ]))),
            ]) : null,
            candidate.score !== null && candidate.scoreNote ? h('details', {class: 'paper-sheet paper-score'}, [
              h('summary', null, '本批参考评分 ' + candidate.score + ' 分'),
              h('p', {class: 'paper-muted'}, candidate.scoreNote),
            ]) : null,
            h('div', {class: 'paper-actions paper-reading-actions'}, [
              h('a', {class: 'paper-secondary', href: queryWithFull(route, context)}, '展开更多分析'),
              h('a', {class: 'paper-button', href: report}, '生成完整报告'),
            ]),
          ],
      ]);
    };
  },
});
