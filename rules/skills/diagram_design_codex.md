# Diagram Design：Codex 绘图插件

用于把架构、流程、时序、数据模型等内容绘制成可直接打开的独立 HTML（内嵌 SVG）。上游仓库：[cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design)，许可证 MIT。

## 全局安装与更新

此项是 Codex 全局插件安装，不是当前项目的 `.agents/skills` 安装。2026-09-28 已安装插件版本 2.6.34。

```bash
codex plugin marketplace add cathrynlavery/diagram-design
codex plugin add diagram-design@diagram-design
codex plugin list
```

获取上游更新：

```bash
codex plugin marketplace upgrade diagram-design
```

更新后新开 Codex 会话，让插件技能目录重新进入会话可用列表。

## 使用

向 Codex 直接描述图的内容、用途和格式，例如：「用 Diagram Design 把这个工作区的规则、资料、Codex 和输出文件画成一张架构图，尺寸 doc-inline，输出 HTML。」首次使用时按插件提示选择默认配色、网站品牌色或本地设计系统。

先读取插件的 `SKILL.md` 与选定图型的 reference，再生成单文件 HTML；输出前运行插件的 `scripts/self_check.py`，有连接线时再运行插件仓库根目录的 `scripts/verify-geometry.py`。真实预览可用无头 Playwright CLI。

本次示例：[HTML](../../output/diagram_design_codex_demo_20260928.html)。
