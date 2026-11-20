import {d as defineComponent, j as h, u as useRouter} from './index-GEgtjqXc.js';

const primaryTools = [
  {label: '八字起名', path: '/bazi-naming/form', icon: 'flower-o'},
  {label: '诗词起名', path: '/naming/form', icon: 'notes-o'},
  {label: 'AI 起名', path: '/naming-ai/form', icon: 'edit'},
  {label: '姓名测评', path: '/test/form', icon: 'search'},
];
const otherTools = [
  {label: '起小名', path: '/nickname/form'},
  {label: '起英文名', path: '/english-name/form'},
  {label: '起中文名', path: '/chinese-name'},
  {label: '更多工具', path: '/tools'},
];

function icon(name) {
  return h('i', {class: ['van-icon', 'van-icon-' + name], 'aria-hidden': 'true'});
}

export default defineComponent({
  name: 'QingyanHome',
  setup() {
    const router = useRouter();
    const link = (path, className, children) => h('a', {
      href: path, class: className,
      onClick(event) {
        if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
        event.preventDefault();
        router.push(path);
      },
    }, children);

    return () => h('main', {class: 'qingyan-home'}, [
      h('header', {class: 'qingyan-wordmark'}, [
        h('span', null, '清言字舍'),
        h('img', {src: '/assets/qingyan-mark.png', width: 18, height: 18, alt: ''}),
      ]),
      h('section', {class: 'qingyan-hero', 'aria-labelledby': 'qingyan-home-title'}, [
        h('div', {class: 'qingyan-hero-copy'}, [
          h('h1', {id: 'qingyan-home-title'}, ['给宝宝起个', h('br'), '好名字']),
          h('p', null, ['结合八字、诗词与智能分析，', h('br'), '为宝宝选一个寓意美好、', h('br'), '音形雅正的中文名字。']),
        ]),
        link('/bazi-naming/form', 'qingyan-start', '开始起名'),
      ]),
      h('nav', {class: 'qingyan-primary', 'aria-label': '起名与测评'}, primaryTools.map(tool =>
        link(tool.path, 'qingyan-tool-link', [icon(tool.icon), h('span', null, tool.label)]))),
      h('p', {class: 'qingyan-caption'}, '传统方式仅作参考'),
      h('section', {class: 'qingyan-specimen', 'aria-label': '姓名示例'}, [
        h('p', {class: 'qingyan-sample-name'}, '林知宁'),
        h('p', {class: 'qingyan-sample-pinyin', lang: 'zh-Latn'}, 'lín zhī níng'),
        h('p', {class: 'qingyan-sample-meaning'}, '知学明理，宁静致远，寓意聪慧安和、从容成长。'),
      ]),
      h('nav', {class: 'qingyan-more', 'aria-label': '更多起名工具'}, otherTools.map(tool =>
        link(tool.path, '', tool.label))),
    ]);
  },
});
