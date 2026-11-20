import {
  d as defineComponent, j as h, r as ref, u as useRouter,
  bb as confirmDialog, e as api,
} from './index-GEgtjqXc.js';

const recordLinks = [
  {label: '起名历史', detail: '回看八字、诗词与 AI 起名结果', path: '/mine/naming-history', icon: 'clock-o'},
  {label: '我的收藏', detail: '查看收藏的姓名和汉字', path: '/mine/favorites', icon: 'star-o'},
  {label: '我的报告', detail: '查看和下载已生成的姓名报告', path: '/mine/reports', icon: 'description'},
];

const referenceLinks = [
  {label: '起名资料包', detail: '下载用字字典、热门姓名和核对清单', path: '/mine/materials', icon: 'down'},
  {label: '免费使用说明', detail: '了解数据保存方式、来源与许可', path: '/mine/about', icon: 'info-o'},
];

function icon(name) {
  return h('i', {class: ['van-icon', 'van-icon-' + name], 'aria-hidden': 'true'});
}

export default defineComponent({
  name: 'QingyanPersonalArchive',
  setup() {
    const router = useRouter();
    const clearing = ref(false);
    const notice = ref('');

    function row({label, detail, path, icon: symbol}) {
      return h('li', {key: path}, [
        h('a', {
          class: 'qy-archive-link', href: path,
          onClick(event) {
            if (event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
            event.preventDefault();
            router.push(path);
          },
        }, [
          h('span', {class: 'qy-archive-icon'}, [icon(symbol)]),
          h('span', {class: 'qy-archive-label'}, [
            h('strong', null, label),
            h('span', null, detail),
          ]),
          icon('arrow'),
        ]),
      ]);
    }

    async function clearHistory() {
      if (clearing.value) return;
      clearing.value = true;
      notice.value = '';
      try {
        await confirmDialog({
          title: '清除诗词和 AI 起名历史？',
          message: '其中已收藏的姓名也会一起删除。此操作无法撤销。',
          showCancelButton: true,
          confirmButtonText: '清除历史',
          cancelButtonText: '取消',
          confirmButtonColor: '#9f3d31',
        });
        try {
          const result = await api.delete('/v1/naming/history');
          notice.value = result?.deleted_count ? `已清除 ${result.deleted_count} 条起名记录。` : '暂无可清除的诗词或 AI 起名记录。';
        } catch {
          notice.value = '清除失败，请重试。';
        }
      } catch {
        // Dismissing the confirmation leaves the records intact.
      } finally {
        clearing.value = false;
      }
    }

    return () => h('main', {class: 'qy-archive'}, [
      h('header', {class: 'qy-archive-header'}, [
        h('div', null, [
          h('h1', null, '我的'),
          h('p', null, '起名记录和收藏保存在当前浏览器。'),
        ]),
        h('img', {src: '/assets/qingyan-mark.png', alt: '', width: 30, height: 30}),
      ]),
      h('section', {class: 'qy-archive-section', 'aria-labelledby': 'qy-archive-records'}, [
        h('h2', {id: 'qy-archive-records'}, '起名档案'),
        h('ul', null, recordLinks.map(row)),
      ]),
      h('section', {class: 'qy-archive-section', 'aria-labelledby': 'qy-archive-references'}, [
        h('h2', {id: 'qy-archive-references'}, '资料与说明'),
        h('ul', null, referenceLinks.map(row)),
      ]),
      h('details', {class: 'qy-archive-management'}, [
        h('summary', null, ['记录管理', icon('arrow-down')]),
        h('ul', null, [
          row({label: '历史订单', detail: '查看以前保存在此浏览器的订单', path: '/mine/orders', icon: 'orders-o'}),
        ]),
        h('button', {
          class: 'qy-archive-clear', type: 'button', disabled: clearing.value, onClick: clearHistory,
        }, '清除诗词和 AI 起名历史'),
        h('p', {class: 'qy-archive-status', role: 'status'}, notice.value),
      ]),
    ]);
  },
});
