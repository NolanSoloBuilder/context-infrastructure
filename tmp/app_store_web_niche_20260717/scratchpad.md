# Scratchpad

## Claim Extraction

| Claim | 来源层级 | 验证通道 | 当前状态 |
|---|---|---|---|
| App Store 排名可以发现真实任务需求 | Apple 榜单与产品页（Tier 1） | 评分量、低分评论、社区主动求助、付费价格 | 部分验证；只能做候选入口 |
| Chrome/Web 能替代大量工具 App | Chrome/MDN 官方能力文档（Tier 1） | 真实文件/麦克风原型和 iOS/desktop benchmark | 能力边界已确认；尚未做候选原型 |
| local-first 能形成差异 | App 产品描述与竞品卖点（Tier 1-2） | 用户评论中的隐私/上传担忧、转化测试 | 未独立验证 |
| 中后排付费工具包含低竞争 niche | 2026-07-17 美国 Paid 分类榜（Tier 1） | SERP 竞品密度与社区使用行为 | 混合；许多方向已有 Web 竞品 |

## Live dataset

- 30 个 chart/category 请求全部成功。
- 2,983 条排名记录。
- 2,454 个唯一 App。
- Apple Lookup 补齐 2,454 个 App 的价格、评分量、描述和更新时间。
- 12 个候选进入 review evidence queue；公开 RSS 实际返回 122 条书面评论，集中在 Print to Size、StitchSketch 和 Pinhole Assist。

## Important contradictions

1. 越容易纯 Web 化的任务，越容易已经出现大量 browser-native 竞品。
2. 越专业、付费越明确的现场工具，越可能依赖手机、麦克风姿势、相机、离线和单手操作。
3. 排名较低不代表竞争较低；CNC、HVAC、PDF、exact-size printing 的 Web SERP 已经非常密集。
4. App 的低分评论常指向更好的 wedge，而不是复制整款 App。例如 StitchSketch 的痛点集中在 fabric count、颜色表、fractional stitches、PDF 导出和数据丢失。

## Current thesis

工作流应寻找“专业输出合同”，而不是“功能名称”。优先任务满足：输入边界清楚、前台可完成、输出能直接进入下游工作、现有 Web 方案缺少该职业语境。通用转换器和通用计算器只适合做流量入口，难以独立成为产品。

