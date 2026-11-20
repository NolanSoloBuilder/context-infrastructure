import {d as defineComponent, f as element} from './index-GEgtjqXc.js';

const FreeHomeCard = defineComponent({
  name: 'FreeHomeCard',
  setup() {
    return () => element('section', {class: 'free-home-card'}, [
      element('div', null, [
        element('strong', null, '所有功能免费'),
        element('p', null, '起名、测评、工具和报告均可直接使用。'),
      ]),
      element('a', {href: '/mine/about'}, '使用说明'),
    ]);
  },
});

export {FreeHomeCard as H};
