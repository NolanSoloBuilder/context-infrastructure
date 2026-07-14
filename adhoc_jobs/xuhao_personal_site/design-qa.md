# Design QA

日期：2026-07-14  
参考站：https://www.yencheng.dev/  
实现：http://127.0.0.1:4175/

## Source of truth

- 桌面首屏：`../../tmp/xuhao_personal_site_capture/source-desktop-full.png`
- 桌面作品集：`../../tmp/xuhao_personal_site_capture/source-desktop-after-intro.png`
- 移动首屏：`../../tmp/xuhao_personal_site_capture/source-mobile-hello.png`
- 移动作品集：`../../tmp/xuhao_personal_site_capture/source-mobile-portfolio-settled.png`

## Final implementation captures

- 桌面首屏：`qa-desktop-hello-final.png`（1440 × 1000）
- 桌面作品集：`qa-desktop-portfolio-final.png`（1440 × 1000）
- 移动首屏：`qa-mobile-hello.png`（390 × 844）
- 移动作品集：`qa-mobile-portfolio-fixed.png`（390 × 844）

## Side-by-side comparisons

- `qa-comparison-desktop-hello.png`
- `qa-comparison-desktop.png`
- `qa-comparison-mobile-hello.png`
- `qa-comparison-mobile-portfolio.png`

## Findings and fixes

- P0：无。
- P1：初版横向轨道按 viewport 宽度平移，在移动端会落到相邻屏幕之间；改为固定 500% 轨道与每屏 20% 宽度后，所有断点均按容器比例移动。
- P1：首屏最初偏离参考站的白底、字号、居中节奏和底部 CTA；按参考页面的实际响应式尺寸重做了首屏层级、米白色按钮和底部提示。
- P2：参考站自身的移动作品集截图存在相邻 carousel 内容露出；实现保留横向叙事，但修复为单屏对齐，不复制该缺陷。
- P2：移除不属于参考体验的可见进度点，保留箭头、Dock、键盘和触摸导航。

## Interaction coverage

- `About Me`：Hello → Portfolio。
- Portfolio 前后箭头与 Dock 快捷入口。
- Selected Work 项目切换，`Mindspace Workspace` 可选中并更新详情。
- Portfolio → Work → Now → End → Back to start 完整链路。
- 390 × 844 移动视口无横向错位；1440 × 1000 桌面视口布局稳定。
- 最终浏览器日志仅包含 Vite 连接和 React DevTools 提示，无应用错误。

## Result

passed
