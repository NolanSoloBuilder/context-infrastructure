# Design QA

日期：2026-07-14  
参考站：https://www.yencheng.dev/  
实现：http://127.0.0.1:4175/

## Source of truth

- 完整源码快照：`../../tmp/yencheng_site_source/`（HTML、CSS、JavaScript chunks、字体与可见资产）
- 桌面首屏：`../../tmp/xuhao_personal_site_capture/source-desktop-full.png`
- 桌面作品集：`../../tmp/xuhao_personal_site_capture/source-desktop-after-intro.png`
- 移动首屏：`../../tmp/xuhao_personal_site_capture/source-mobile-hello.png`
- 移动作品集：`../../tmp/xuhao_personal_site_capture/source-mobile-portfolio-settled.png`

## Final implementation captures

- 桌面首屏：`qa-desktop-hello-final.png`（1440 × 1000）
- 桌面作品集：`qa-desktop-portfolio-final.png`（1440 × 1000）
- 移动首屏：`qa-mobile-hello.png`（390 × 844）
- 移动作品集：`qa-mobile-portfolio-fixed.png`（390 × 844）
- 注释修复后首屏：`qa-click-hint-800x1226.png`（800 × 1226）
- 注释修复后移动首屏：`qa-click-hint-mobile.png`（390 × 844）
- 作品内容清空与 Dock 圆角：`qa-portfolio-empty-rounded-800x1226.png`（800 × 1226）
- 两条真实作品：`qa-portfolio-projects-800x1226.png`（CSS 视口 800 × 1226）
- Selected Work 项目详情：`qa-selected-work-projects-800x1226.png`（CSS 视口 800 × 1226）
- 移动端真实作品：`qa-portfolio-projects-mobile-390x844.png`（CSS 视口 390 × 844）

## Side-by-side comparisons

- `qa-comparison-desktop-hello.png`
- `qa-comparison-desktop.png`
- `qa-comparison-mobile-hello.png`
- `qa-comparison-mobile-portfolio.png`
- `qa-comparison-click-hint-800x1226.png`
- `qa-comparison-click-hint-focused.png`（底部 CTA 与 Click 提示局部对照）
- `qa-comparison-click-hint-mobile.png`
- `qa-comparison-portfolio-empty-rounded-800x1226.png`
- `qa-comparison-dock-rounded-focused.png`（原站与实现 Dock 局部对照）
- `qa-comparison-portfolio-projects-scoped-800x1226.png`（上一轮已验收空态与本轮真实作品的同状态对照）
- `qa-comparison-portfolio-projects-scoped-focused.png`（项目窗口与 Dock 局部对照）
- `qa-comparison-portfolio-projects-800x1226.png`（原站整体外壳与本轮实现对照；项目内容差异为用户信息替换）

## Findings and fixes

- P0：无。
- P1：初版横向轨道按 viewport 宽度平移，在移动端会落到相邻屏幕之间；改为固定 500% 轨道与每屏 20% 宽度后，所有断点均按容器比例移动。
- P1：首屏最初偏离参考站的白底、字号、居中节奏和底部 CTA；按参考页面的实际响应式尺寸重做了首屏层级、米白色按钮和底部提示。
- P2：参考站自身的移动作品集截图存在相邻 carousel 内容露出；实现保留横向叙事，但修复为单屏对齐，不复制该缺陷。
- P2：移除不属于参考体验的可见进度点，保留箭头、Dock、键盘和触摸导航。
- P2：浏览器注释指出 `↑ Click` 风格不一致。源码表明参考站使用独立的全宽 `bottom-5` 容器、Lucide `ArrowUp`、3.5 描边、14px 文本和 Tailwind `bounce 1s infinite`；实现原先使用文本箭头、13px 文本与自定义 1.6s 动画。已改为 `lucide-react` 的真实图标、20/16px 响应式尺寸、源码一致的描边、颜色、20px 底距、1s bounce 和 1.15s 入场延迟。
- P2：GitHub Dock 图标缺少原站 `rounded-xl` 裁切。已按源码为全部 Dock 图片统一设置 12px 圆角，避免单个方形资源破坏图标体系。
- P1：项目卡片内容未经用户确认。已删除推断生成的项目数组，作品面板保留标题和空白内容区；Selected Work 页面也在空数组下隐藏选项、详情和底栏，不显示占位文案。
- P1：用户确认目前可公开展示的真实作品为 `CHINA METRO TYPING` 与 `Cited Alpha`。已从 Cloudflare 当前项目、Worker 配置和两个线上站点的公开元信息核对名称、定位与 URL，再写入 `projects` 数据层；未恢复此前推断生成的项目。
- P2：项目卡片只有说明文字时无法完成作品集的访问任务。已在 Portfolio 卡片和 Selected Work 详情中增加明确的 Live 链接，使用现有 `ArrowSquareOut` 图标与既有色彩、字号和交互样式。

## Comparison history

1. 首轮发现横向轨道移动端错位、首屏视觉漂移和额外进度点，分别修复轨道比例、首屏响应式 token 与可见控件，桌面/移动对照通过。
2. 浏览器注释复查发现底部提示依赖截图推断，文本箭头和动画与源码不一致；下载并读取完整源码后按组件结构重建。
3. 修复后在 800 × 1226 与 390 × 844 同视口重新截图，并完成全屏与底部局部并排比较；箭头、文字、底距、动画容器和 CTA 对齐，无剩余 P0/P1/P2。
4. 浏览器注释要求 Dock 图标圆角并清空未经确认的项目内容。实现改为源码一致的 12px 图标圆角，`projects` 为空数组；800 × 1226 全屏和 Dock 局部对照确认圆角一致，空内容区无卡片、占位文案或布局崩坏。
5. 用户随后明确提供两个 Cloudflare 子域名产品。实现只新增这两条真实项目数据及 Live 链接；同一 800 × 1226 状态与上一轮空态并排比较，窗口、标题、壁纸、Dock、圆角和整体布局保持不变。390 × 844 移动端改为单列卡片，无水平溢出。

## Fidelity surfaces

- 字体与排版：复用原站 Nunito Bold；Click 为源码一致的 14px，About Me 在 640px 以上为 20px、以下为 14px。
- 间距与布局：About Me 距底 88px；Click 容器距底 20px并全宽居中。
- 颜色与 token：参考首屏为 `#fafafa`，实现保留既有近白背景 `#fcfcfc`（可接受 P3）；CTA `#f2e9e3`、CTA 前景 `#916651`、Click 前景 `#1a1a1a` 与源码一致。
- 图片与图标：Click 使用 `lucide-react` 的 `ArrowUp`，不再使用文本字符模拟；桌面 20px、移动 16px、描边 3.5。
- 文案：保留参考组件的 `About Me` 与 `Click`；作品内容仅包含徐昊确认的 `CHINA METRO TYPING` 与 `Cited Alpha`。英文说明来自两个线上产品的公开元信息与已核验产品定位。

## Interaction coverage

- `About Me`：Hello → Portfolio。
- Portfolio 前后箭头与 Dock 快捷入口。
- Selected Work 可在 `CHINA METRO TYPING` 与 `Cited Alpha` 间切换，选中项会同步更新详情和 Live 链接。
- Portfolio → Work → Now → End → Back to start 完整链路。
- 390 × 844 移动视口无横向错位；1440 × 1000 桌面视口布局稳定。
- 最终浏览器日志仅包含 Vite 连接和 React DevTools 提示，无应用错误。
- 注释修复后再次点击 `About Me`，成功进入 `#portfolio`；浏览器错误日志为空。
- 作品面板验证：项目卡片数量为 0，只保留 `SELECTED PROJECTS` 标题；GitHub 图标计算圆角为 12px。
- Selected Work 验证：选项、详情、底栏数量均为 0；页面可正常进入且浏览器错误日志为空。
- 本轮作品面板验证：项目卡片数量为 2，链接分别为 `https://metro.forgepane.com/` 与 `https://cited-alpha.forgepane.com/`；两个线上入口均返回 HTTP 200。
- 本轮 Selected Work 验证：两个选项均可切换；选中 `Cited Alpha` 后详情标题与链接同步更新为对应产品。页面无 Vite error overlay。
- 本轮移动端验证：CSS 视口 390 × 844，卡片数量为 2，`body.scrollWidth` 为 391（1px 为浏览器取整），没有可见横向溢出或遮挡。

## Final result

final result: passed
