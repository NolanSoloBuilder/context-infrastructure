import {d as defineComponent, f as element} from './index-GEgtjqXc.js';

const About = defineComponent({
  name: 'AboutQingyan',
  setup() {
    return () => element('main', {class: 'free-info'}, [
      element('a', {class: 'free-info-back', href: '/mine'}, [
        element('i', {class: 'van-icon van-icon-arrow-left', 'aria-hidden': 'true'}),
        '返回我的',
      ]),
      element('header', null, [
        element('img', {src: '/assets/qingyan-mark.png', alt: '', width: 48, height: 48}),
        element('h1', null, '清言字舍'),
      ]),
      element('section', {id: 'usage'}, [
        element('h2', null, '免费使用'),
        element('p', null, '起名、姓名测评、字典、报告及资料下载均免费开放。无需开通会员、付款或兑换。'),
        element('p', null, '姓名建议、传统五行和五格解读仅供选名时参考。'),
      ]),
      element('section', {id: 'privacy'}, [
        element('h2', null, '数据与隐私'),
        element('p', null, '历史、收藏和报告通过当前浏览器的设备会话保存在本地服务。可在「我的」查看和清除起名历史。'),
        element('p', null, '提交 AI 起名时，姓氏、性别、已填出生信息、定字、偏好及合法候选会发送给 Vercel AI Gateway 生成建议。'),
      ]),
      element('section', {id: 'licenses'}, [
        element('h2', null, '数据来源与许可'),
        element('p', null, [
          '诗词数据使用 ',
          element('a', {href: 'https://github.com/chinese-poetry/chinese-poetry'}, 'chinese-poetry'),
          '。古籍、字典和公开数据的来源与许可沿用各资料附带的说明。',
        ]),
      ]),
    ]);
  },
});

export default About;
