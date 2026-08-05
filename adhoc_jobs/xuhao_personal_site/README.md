# Nalon 个人网站

一个可直接运行的个人网站原型。视觉与交互语言参考 [yencheng.dev](https://www.yencheng.dev/) 的全屏横向叙事、桌面窗口和命令面板，但公开品牌、文案、内容与响应式实现均围绕 Nalon 重新构建。

生产地址：[https://nalon.forgepane.com](https://nalon.forgepane.com)。站点构建产物由相邻的 `forgepane_site` Cloudflare Worker 通过静态资产 binding 发布；根域名 `forgepane.com` 和 `www.forgepane.com` 的品牌页逻辑保持独立。

## 运行

```bash
npm install
npm run dev
```

构建校验：

```bash
npm run build
```

## 内容维护

个人资料、关注方向与项目集中在 `src/content.js`。首屏使用徐昊确认的 GitHub、[LinkedIn](https://www.linkedin.com/in/web-xuhao/)、[X](https://x.com/NolanBuilder01) 与[小红书](https://www.xiaohongshu.com/user/profile/676aae57000000001801c80d)公开地址；Notes 进入站内占位页。项目集合只展示徐昊明确确认的内容，目前包括 [CHINA METRO TYPING](https://metro.forgepane.com/) 与 [Cited Alpha](https://cited-alpha.forgepane.com/)；Projects 窗口以真实产品截图、能力标签和线上入口呈现。

页面共有四段：

1. Hello / 个人入口
2. My Portfolio / macOS 风格桌面工作区
3. Notes / 文章列表与占位文章详情
4. 结束页

桌面 Dock 只保留 Finder、Projects、GitHub 与 Toolbox。点击应用不会离开作品集页，而是在模拟桌面中打开或切换对应窗口；窗口支持关闭、最小化和最大化。首屏 Notes 按钮进入站内文章占位页，文章列表和详情由 `src/content.js` 的 `notes` 数据维护。页面同时支持箭头、键盘左右方向键与触摸横向滑动。

## 设计与资产决策

- 保留参考站“单屏、横向切换、强视觉容器”的核心体验，但修复了参考站移动端横向错位的问题。
- 参考站 HTML、CSS、JavaScript chunks、字体和可见资产保存在本机私密目录 `~/Library/Application Support/context-infrastructure/reference_snapshots/yencheng_site_source/`；第三方页面源码可能嵌入 provider credential，不进入 Git。细节实现优先读取源码中的组件结构与响应式 token，不再只凭截图推断。
- 壁纸由内置 ImageGen 根据参考截图的蓝青、奶油色和深靛色气质重新生成，不复刻原站壁纸。
- `public/assets/` 中的 dock 图标来自参考页面和对应产品，仅用于本地原型与设计验证；公开发布前应确认授权或换成自有/开源资产。
- 不热链原站资源，运行时所需资产全部本地化。
- 项目展示使用产品真实页面与仓库内真实界面截图，不使用占位卡片；截图统一放在 `public/assets/projects/`。
- 当前项目主图以徐昊提供的截图为准：地铁线路实玩画面用于 CHINA METRO TYPING；黑色金融研究首页与带引用的 Tesla 投资备忘录用于 Cited Alpha。
- Instagram、旅行、咖啡等私人应用不进入公开作品集 Dock。
- `public/.assetsignore` 同时阻止这些私人应用图片和未使用的参考/占位图片进入 Cloudflare 静态资产清单，避免无界面入口的文件仍可被公开直链访问。
- 原站名称、头像、经历与社交身份没有复制，避免造成身份混淆。

最终桌面与移动端验收记录见 `design-qa.md`。
