import {u as useRouter,q as useRoute,f as h,d as defineComponent} from './index-GEgtjqXc.js';
import {N as NavBar} from './index-CSoH_th2.js';
import {k as component} from './index-GEgtjqXc.js';

const articles=[
  {id:'bazi-calendar',title:'公历、农历和出生时辰怎么填',description:'用实际出生日期排盘，出生时辰不确定时先保留三柱。',
    paragraphs:['表单的日期按公历填写。家里只有农历日期时，可先确认这一年是否有同名闰月，再比对公历日期。','子时跨越午夜。界面区分晚子时和早子时，以便保留日柱换日的计算口径。未知时辰可以选择「不清楚」。'],
    route:'/bazi-naming/form',label:'打开八字起名'},
  {id:'name-review',title:'从读音、字形和场景看一个名字',description:'把姓和名连在一起读，多看几个实际使用场景。',
    paragraphs:['单独读名时顺口，和姓氏连读后也要再听一遍。大声读、快速连读，用家里的方言读，能发现不同的谐音。','写出全名，看看笔画密度和辨识度。给几位亲友只看写法、再让他们试读，有助于发现生僻读音。'],
    route:'/test/form',label:'打开姓名测评'},
  {id:'poetry-source',title:'怎样核对诗词起名的出处',description:'先确认句子、篇名和上下文，再决定是否适合名字。',
    paragraphs:['两个字出现在一首作品里，未必原本就是一个词。查看引用原句，确认名字表达的意思在上下文中成立。','起名时也可以分别选字，逐字解释寓意。页面有可核对原句时才展示出处。'],
    route:'/naming/form',label:'打开诗词起名'},
  {id:'nicknames',title:'小名适合短一点，也可以更自由',description:'试试同一个小名在家里、幼儿园和公共场合的感觉。',
    paragraphs:['小名通常用于日常称呼，易读易喊比结构严谨更重要。可以呼应正式名字，也可以来自季节、食物或孩子喜欢的事物。','把候选放在一句平常的话里试着喊，确认听起来亲昵、没有容易误会的谐音。'],
    route:'/nickname/form',label:'打开起小名'},
];
const textStyle={lineHeight:1.8,color:'#53605b'};
export const Library=defineComponent({
  setup(){
    const route=useRoute(),router=useRouter();
    return ()=>{
      const detail=route.params.id?articles.find(a=>a.id===route.params.id):null;
      const title=detail?.title||'起名知识';
      const link=(label,path)=>h('a',{href:path,onClick:event=>{event.preventDefault();router.push(path);},style:{color:'#397b60'}},label);
      const content=detail
        ? [h('h2',null,title),...detail.paragraphs.map(text=>h('p',{style:textStyle},text)),link(detail.label,detail.route)]
        : route.params.id
          ? [h('p',{style:textStyle},'这篇文章暂不可读。'),link('返回起名知识','/tools/articles')]
          : articles.map(item=>h('article',{style:{padding:'16px 0',borderBottom:'1px solid #e2eae4'}},[
              h('h3',null,[link(item.title,'/tools/article/'+item.id)]),h('p',{style:textStyle},item.description),
            ]));
      return h('div',null,[component(NavBar,{title,'left-arrow':true,onClickLeft:()=>router.back()}),
        h('main',{style:{maxWidth:'620px',margin:'0 auto',padding:'24px 18px'}},content)]);
    };
  },
});
