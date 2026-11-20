import {d as defineComponent, j as h, r as ref, v as computed, q as useRoute, u as useRouter} from './index-GEgtjqXc.js';
import {elements, methods, methodFor, resultPath, request, generateAi} from './qingyan-workflow-data.js';

const temperaments = ['温润儒雅', '聪慧灵动', '大气稳重', '清雅独立', '豪迈英朗', '坚毅笃行', '文艺浪漫', '沉静谦逊'];
const careers = ['学者教师', '艺术设计', '医生护理', '工程科技', '商业管理', '文化创意', '法律政务', '文学传媒'];
const hours = ['00:00', '02:00', '04:00', '06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00', '22:00', '23:00'];
const hourLabels = ['早子时', '丑时', '寅时', '卯时', '辰时', '巳时', '午时', '未时', '申时', '酉时', '戌时', '亥时', '晚子时'];

function pick(items, value, set, max) {
  return h('div', {class: 'paper-options'}, items.map(item =>
    h('button', {
      type: 'button', 'aria-pressed': value.includes(item),
      onClick: () => set(value.includes(item) ? value.filter(x => x !== item)
        : value.length < max ? [...value, item] : value),
    }, item)));
}

function choices(name, entries, value, set) {
  return h('div', {class: 'paper-options'}, entries.map(([key, label]) =>
    h('label', {class: 'paper-radio'}, [
      h('input', {type: 'radio', name, value: key, checked: value === key, onChange: () => set(key)}),
      h('span', null, label),
    ])));
}

function field(label, control, tip) {
  return h('label', {class: 'paper-field'}, [h('span', null, label), control,
    tip ? h('small', null, tip) : null]);
}

function section(title, description, fields) {
  return h('section', {class: 'paper-form-section'}, [
    h('h2', null, title), description ? h('p', {class: 'paper-muted'}, description) : null,
    h('div', {class: 'paper-fields'}, fields),
  ]);
}

export default defineComponent({
  name: 'QingyanWorksheet',
  setup() {
    const route = useRoute();
    const router = useRouter();
    const mode = computed(() => methodFor(route.path));
    const surname = ref('');
    const gender = ref('');
    const date = ref('');
    const time = ref('unknown');
    const birthStatus = ref('born');
    const datePrecision = ref('day');
    const month = ref('');
    const preferred = ref([]);
    const fixedFirst = ref('');
    const fixedLast = ref('');
    const fixedAny = ref('');
    const fixedPosition = ref('任意');
    const personality = ref([]);
    const career = ref([]);
    const busy = ref(false);
    const error = ref('');
    const analysis = ref(null);
    const submitted = ref(null);
    const aiBatch = ref(null);
    const aiNames = ref([]);
    const controller = ref(null);

    const textInput = (state, config = {}) => h('input', {
      ...config, value: state.value, onInput: event => state.value = event.target.value,
    });

    function readForm() {
      const selected = mode.value;
      const input = {surname: surname.value.trim(), gender: gender.value};
      if (!/^\p{Script=Han}{1,2}$/u.test(input.surname)) throw new Error('请填写一到两个汉字的姓氏。');
      if (!input.gender) throw new Error('请选择性别。');
      const unborn = selected === 'ai' && birthStatus.value === 'unborn';
      const isMonth = unborn && datePrecision.value === 'month';
      const unknown = unborn && datePrecision.value === 'unknown';
      if (isMonth && !month.value) throw new Error('请选择预产年月。');
      input.birthDate = unknown ? 'unknown' : isMonth ? month.value + '-15' : date.value || 'unknown';
      input.birthTime = input.birthDate === 'unknown' || isMonth ? 'unknown' : time.value;
      if (selected === 'bazi') {
        if (input.birthDate === 'unknown') throw new Error('八字起名需要有效的出生日期。');
        input.selectedXiyongShen = preferred.value;
      } else if (selected === 'poetry') {
        input.nameCount = 60;
        input.advancedOptions = {
          preferredChar1: fixedFirst.value.trim(), preferredChar2: fixedLast.value.trim(), preferredWuxing: preferred.value,
        };
      } else {
        input.birth_status = birthStatus.value;
        if (fixedAny.value.trim()) input.fixed_char = {char: fixedAny.value.trim(), position: fixedPosition.value};
        input.personality = personality.value.join('、');
        input.career = career.value.join('、');
      }
      return input;
    }

    async function submit(event) {
      event?.preventDefault();
      if (busy.value) return;
      error.value = '';
      try {
        const selected = mode.value;
        const input = readForm();
        busy.value = true;
        if (selected === 'bazi') {
          const data = await request('/api/v1/bazi-naming/analysis', {body: input});
          submitted.value = input;
          analysis.value = data;
          window.scrollTo({top: 0});
        } else if (selected === 'poetry') {
          const data = await request('/api/v2/naming/generate', {body: input});
          router.push(resultPath(selected, data.history_id));
        } else {
          aiBatch.value = null;
          aiNames.value = [];
          controller.value = new AbortController();
          await generateAi(input, event => {
            if (event.type === 'init') aiBatch.value = event.session_id;
            if (event.type === 'batch') aiNames.value = [...aiNames.value, ...event.names];
            if (event.type === 'done') aiBatch.value = event.session_id;
          }, controller.value.signal);
          router.push(resultPath(selected, aiBatch.value));
        }
      } catch (failure) {
        error.value = failure.name === 'AbortError' ? '已停止生成。' : failure.message;
      } finally {
        controller.value = null;
        busy.value = false;
      }
    }

    async function finishBazi() {
      if (busy.value) return;
      error.value = '';
      busy.value = true;
      try {
        const result = await request('/api/v1/bazi-naming/generate', {body: submitted.value});
        router.push(resultPath('bazi', result.history_id));
      } catch (failure) {
        error.value = failure.message;
      } finally {
        busy.value = false;
      }
    }

    return () => {
      const kind = mode.value;
      const method = methods[kind];
      const isAi = kind === 'ai';
      const isBazi = kind === 'bazi';
      const unborn = isAi && birthStatus.value === 'unborn';
      const hideDay = unborn && datePrecision.value !== 'day';
      const dateOnly = hideDay && datePrecision.value === 'month';
      const pickElements = () => pick(elements, preferred.value, value => preferred.value = value, isBazi ? 2 : 5);

      return h('main', {class: 'paper-workflow'}, [
        h('div', {class: 'paper-topline'}, [h('a', {href: '/'}, '首页'), h('a', {href: '/mine/naming-history'}, '起名历史')]),
        h('header', {class: 'paper-title'}, [
          h('h1', null, method.label),
          h('p', null, method.caption),
          kind === 'poetry' ? h('img', {
            class: 'paper-poetry-portrait', src: '/assets/qingyan-poetry-baby.webp',
            alt: '', width: 1240, height: 698,
          }) : null,
        ]),
        analysis.value && isBazi ? h('section', {class: 'paper-sheet paper-analysis'}, [
          h('h2', null, '核对排盘与用字'),
          h('dl', {class: 'paper-facts'}, [
            h('div', null, [h('dt', null, '四柱'), h('dd', null, analysis.value.bazi_str + (analysis.value.hour_unknown ? ' · 时辰未知' : ''))]),
            h('div', null, [h('dt', null, '系统喜用神'), h('dd', null, analysis.value.xiyong_shen.join('、'))]),
            h('div', null, [h('dt', null, '实际取名依据'), h('dd', null, (submitted.value.selectedXiyongShen.length ?
              submitted.value.selectedXiyongShen : analysis.value.xiyong_shen).join('、'))]),
          ]),
          h('p', {class: 'paper-muted'}, '候选页可以展开完整排盘和查看喜用字典。'),
          error.value ? h('p', {class: 'paper-error', role: 'alert'}, error.value) : null,
          h('div', {class: 'paper-actions'}, [
            h('button', {type: 'button', class: 'paper-secondary', disabled: busy.value, onClick: () => { analysis.value = null; error.value = ''; }}, '修改资料'),
            h('button', {type: 'button', class: 'paper-button', disabled: busy.value, onClick: finishBazi},
              busy.value ? '正在生成…' : '免费生成 60 个名字'),
          ]),
        ]) : h('form', {class: 'paper-worksheet', onSubmit: submit}, [
          h('fieldset', {class: 'paper-fieldset', disabled: busy.value}, [
            section('宝宝资料', '', [
              field('姓氏', textInput(surname, {placeholder: '如 林、欧阳', maxlength: 2, autocomplete: 'off', required: true})),
              h('div', {class: 'paper-field'}, [h('span', null, '性别'),
                choices('gender', [['male', '男宝'], ['female', '女宝']], gender.value, value => gender.value = value)]),
              isAi ? h('div', {class: 'paper-field'}, [h('span', null, '出生状态'),
                choices('birth-status', [['born', '已出生'], ['unborn', '未出生']], birthStatus.value, value => birthStatus.value = value)]) : null,
              unborn ? h('div', {class: 'paper-field'}, [h('span', null, '预产期精度'), choices('precision',
                [['day', '精确日期'], ['month', '仅知年月'], ['unknown', '完全未知']], datePrecision.value, value => datePrecision.value = value)]) : null,
              dateOnly ? field('预产年月', textInput(month, {type: 'month', min: '1950-01', max: '2199-12'}), '仅用于近似排盘，时辰按未知处理。') : null,
              !hideDay ? field(unborn ? '预产期（公历）' : '出生日期（公历）', textInput(date, {type: 'date', min: '1950-01-01', max: '2199-12-31', required: isBazi}),
                !isBazi ? '留空按出生日期未知处理。' : null) : null,
              !hideDay ? field(unborn ? '预计时辰' : '出生时辰', h('select', {value: time.value, onChange: e => time.value = e.target.value}, [
                h('option', {value: 'unknown'}, '时辰未知'),
                ...hours.map((value, index) => h('option', {value}, hourLabels[index] + ' · ' + value)),
              ])) : null,
            ]),
            section('用字偏好', isBazi ? '默认采用系统喜用，已有结论时可自选最多两项。' : '可选。指定用字会作为筛选条件。', [
              isBazi ? h('div', {class: 'paper-field'}, [h('span', null, '指定喜用五行'), pickElements()]) : null,
              kind === 'poetry' ? h('div', {class: 'paper-pair'}, [
                field('名的首字', textInput(fixedFirst, {placeholder: '不限', maxlength: 1})),
                field('名的末字', textInput(fixedLast, {placeholder: '不限', maxlength: 1})),
              ]) : null,
              kind === 'poetry' ? h('div', {class: 'paper-field'}, [h('span', null, '偏好五行'), pickElements()]) : null,
              isAi ? field('固定用字', textInput(fixedAny, {placeholder: '如 宁', maxlength: 1})) : null,
              isAi && fixedAny.value ? h('div', {class: 'paper-field'}, [h('span', null, '固定位置'), choices('fixed-position',
                [['首', '首位'], ['末', '末位'], ['任意', '任意']], fixedPosition.value, value => fixedPosition.value = value)]) : null,
              isAi ? h('div', {class: 'paper-field'}, [h('span', null, '期望性格（最多 3 项）'),
                pick(temperaments, personality.value, value => personality.value = value, 3)]) : null,
              isAi ? h('div', {class: 'paper-field'}, [h('span', null, '职业方向（最多 3 项）'),
                pick(careers, career.value, value => career.value = value, 3)]) : null,
            ]),
          ]),
          error.value ? h('p', {class: 'paper-error', role: 'alert'}, error.value) : null,
          isAi && error.value && aiNames.value.length && aiBatch.value ? h('a', {href: resultPath('ai', aiBatch.value)}, '查看已收到的候选') : null,
          h('div', {class: 'paper-form-actions'}, [
            h('button', {type: 'submit', class: 'paper-button', disabled: busy.value},
              busy.value ? isAi ? '正在生成…' : '处理中…' : isBazi ? '开始八字分析' : '免费生成候选'),
            isAi && busy.value ? h('button', {type: 'button', class: 'paper-secondary', onClick: () => controller.value?.abort()}, '停止生成') : null,
          ]),
          isAi && busy.value ? h('section', {class: 'paper-generation', role: 'status', 'aria-live': 'polite'}, [
            h('p', null, aiNames.value.length ? '已收到 ' + aiNames.value.length + ' 个候选' : '正在筛选可用字与组合'),
            aiNames.value.length ? h('p', null, aiNames.value.map(name => name.full_name).join('、')) : null,
          ]) : null,
        ]),
      ]);
    };
  },
});
