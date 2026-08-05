# Animal Island UI 衍生产品扫描

日期：2026-07-30

## 结论

`animal-island-ui` 已经从一个 React 组件库发展成一套可跨技术栈传播的视觉语言。当前公开衍生主要分为四类：

1. 官方同作者移植：Vue 组件库。
2. 社区技术栈移植：Android Compose、Flutter、Taro/微信小程序、Tailwind + Radix、Vanilla Web、uni-app。
3. 使用该组件库的完整应用：儿童英语、数学练习、博客、桌面提醒、游戏资源站、音乐时钟、新标签页。
4. 设计语言移植：Astro/Hexo 博客主题、JetBrains/Typora 主题。

主仓库 README 当前列出 15 个 Usage Cases。GitHub 对精确字符串 `animal-island-ui` 的仓库搜索还能发现几十个未被官方收录的实验项目，但其中不少只有极少提交或没有发布版本，因此下文优先保留来源明确、形态有代表性的项目。

## 官方同作者产品

### React 主库

- [animal-island-ui](https://github.com/guokaigdg/animal-island-ui)
- [在线演示](https://guokaigdg.github.io/animal-island-ui/#/)
- React + TypeScript 组件库，同时提供 design system、one-click prompt、Agent Skill 和设计工具 prompts。

### Vue 移植

- [animal-island-vue](https://github.com/guokaigdg/animal-island-vue)
- [在线演示](https://guokaigdg.github.io/animal-island-vue/)
- 同作者维护的 Vue 3 + TypeScript + Less 移植版，可安装 `animal-island-vue` npm 包。

## 跨端组件库与技术栈移植

- [AnimalIslandUI](https://github.com/liuyuhong0324/AnimalIslandUI)：Android Jetpack Compose 组件库，包含主题、Button、Card、Icon、Modal 等原生组件。
- [animal_island_flutter](https://github.com/ohmangocat/animal_island_flutter)：Flutter/Dart 组件库。当前 README 声称有 74 个组件页面，已经明显超出简单 demo。
- [animal-island-ui-taro-port](https://github.com/Gospelion/animal-island-ui-taro-port)：Taro React 与微信原生组件双线移植，覆盖 H5、Taro 小程序、微信原生小程序。
- [animal-island-ui-tailwind](https://github.com/lifeodyssey/animal-island-ui-tailwind)：使用 Tailwind CSS v4 + Radix UI 重写的 React 版本，包含 25 个组件、Storybook、交互测试和视觉回归。
- [animal-island-vanilla](https://github.com/sunstarpony/animal-island-vanilla)：不依赖 React 的原生 HTML/CSS/JavaScript 版本。
- [animal-island-uniapp](https://github.com/leepule/animal-island-uniapp)：从 Vue 版移植到 uni-app，目标覆盖 H5、小程序和 App。
- [animal-island-ui-vue](https://github.com/yanstu/animal-island-ui-vue)：社区独立维护的另一套 Vue 3 实现，和同作者的 `animal-island-vue` 不是同一个项目。

## 完整应用

以下项目由主仓库 README 明确列为 Usage Cases。

### 浏览器与个人站点

- [Animal Island New Tab](https://ashleycry.github.io/AnimalIslandNewTab/) / [源码](https://github.com/AshleyCry/AnimalIslandNewTab)：浏览器新标签页；`package.json` 直接依赖 `animal-island-ui`。
- [ac-site-template](https://github.com/yunxinz/ac-site-template)：Astro + TailwindCSS + DaisyUI 的动森风个人网站模板。它属于视觉语言衍生，不直接依赖 React 组件包。
- [ItbugShop](https://itbug.shop/)：个人博客，主仓库只提供在线案例链接。
- [animal-island-blog](https://github.com/guokaigdg/animal-island-blog) / [演示](https://guokaigdg.github.io/animal-island-blog/)：组件库作者自己的动森风博客，直接依赖 `animal-island-ui`。
- [Island Life Journal](https://github.com/TIUCSIB/animal-island-blog) / [演示](https://animal-island-blog.pages.dev)：图片日志与博客，直接依赖 `animal-island-ui`。
- [portal-os](https://github.com/guowenju/portal-os)：桌面式博客界面，主仓库称其为 Animal desktop blog。

### 儿童教育

- [HiKid](https://github.com/xiaochong/hi-kid) / [产品页](https://xiaochong.github.io/hi-kid)：面向非英语国家儿童的 AI 英语口语与听力桌面应用；当前是衍生项目里成熟度和关注度最高的一个，`package.json` 直接依赖 `animal-island-ui`。
- [KidsMathQuest](https://github.com/bk4ice/KidsMathQuest)：小学生加减乘除练习 Web 应用，可自动生成题目，直接依赖 `animal-island-ui`。

### 工具、内容与娱乐

- [Animal Crossing BGM Player](https://github.com/skyboooox/Animal-Crossing-Player)：环境时钟与整点音乐播放器，直接依赖 `animal-island-ui`。
- [Awesome-splatoon3](https://github.com/961853266hyt/awesome-splatoon3) / [演示](https://awesome-splatoon3.961853266.workers.dev/)：Splatoon 3 资源导航站，直接依赖 `animal-island-ui`。
- [callai](https://github.com/YuniqueUnic/callai)：Tauri 桌面应用 + CLI，用来定时唤醒 AI CLI、提醒休息、播放声音或运行本地自动化；直接依赖 `animal-island-ui`。

## 博客与编辑器主题

- [Acorn](https://github.com/Mystic-Stars/acorn-theme)：Astro 博客主题，直接依赖 `animal-island-ui`，主仓库已经将它列入 Usage Cases。
- [hexo-theme-animal-island](https://github.com/timoforge/hexo-theme-animal-island)：Hexo 博客主题，包含纸片卡片、昼夜模式、搜索和目录。
- [Animal Island Theme](https://plugins.jetbrains.com/plugin/31905-animal-island-theme) / [源码](https://github.com/wyrmjin/animal-island-theme)：JetBrains IDE 浅色/深色主题，明确注明灵感来自 Animal Island UI。
- [typora-theme-animal-island](https://github.com/YanyingWei1997/typora-theme-animal-island)：Typora 浅色/深色主题，把奶油底色、薄荷绿强调色和软质阴影迁移到 Markdown 阅读体验。

## 值得关注的产品方向

从衍生项目分布看，这套风格尤其适合：

- 儿童学习与亲子产品：圆润控件、低压力反馈和强角色感天然匹配。
- 个人知识、日记、照片与博客：风格能把普通 CRUD 变成“岛屿生活”叙事。
- 桌面小工具：计时、提醒、音乐、状态面板和 AI companion。
- 主题与模板：IDE、Markdown 编辑器、博客主题、浏览器新标签页。
- 轻量游戏化工具：习惯养成、待办、情绪记录、情侣互动、资源收藏。

最有产品启发的三个案例是：

1. `HiKid`：证明这套风格能承载完整 AI 教育产品，而不只是一组展示组件。
2. `callai`：把风格用于桌面自动化与 AI companion，产品形态更有原创性。
3. `animal_island_flutter`：说明它的设计系统足够完整，可以扩展到复杂移动端业务组件。

## License 与商业使用边界

主仓库当前 `LICENSE` 和 README 标注为 `CC BY-NC 4.0`，明确要求署名并禁止商业使用、二次售卖、企业项目、对外服务和付费模板。早期介绍文章或第三方页面仍可能写成 MIT，那些信息已经过时。

部分衍生仓库各自标注 MIT、GPL 或没有可识别许可证。这并不自动消除上游素材和设计实现的授权约束。准备做正式商业产品时，更合适的路径是：

1. 只研究其视觉原则，重新建立独立的设计 token、造型和资产。
2. 不复制上游图标、字体、CSS 数值、clip-path 与组件实现。
3. 避免直接使用 Nintendo 的角色、名称、图形与官方素材。
4. 如果希望直接复用组件库，先向作者取得商业授权并保存书面许可。

## 证据来源

- 主仓库 README、Usage Cases、License 与免责声明
- 各衍生仓库 README、`package.json` 和 GitHub repository metadata
- GitHub 精确仓库/代码搜索
- JetBrains Marketplace 产品页

