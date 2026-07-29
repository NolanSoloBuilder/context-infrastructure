# Search Manifest

## 产出文件索引

| 文件 | 路径 | 说明 |
|---|---|---|
| Scratchpad | `tmp/quiz_theme_survey_20260722/scratchpad.md` | Claim 与平台直接观察 |
| Search Manifest | `tmp/quiz_theme_survey_20260722/search_manifest.md` | 本文件 |
| 内部数据采集器 | `tmp/quiz_theme_survey_20260722/collect_xhs_internal_signals.py` | 固定口径、只读采集与匿名化汇总 |
| 内部数据样本 | `tmp/quiz_theme_survey_20260722/xhs_internal_signals_20260722.json` | 24 词近 7 天返回样本，不含 Cookie 与访问链接 |
| 最终报告 | `contexts/survey_sessions/quiz_theme_market_survey_20260722.md` | 主题排序、产品判断与下一步建议 |

## 调研维度

| 维度 | 主要证据 | 状态 |
|---|---|---|
| 小红书当前主题信号 | 登录态 Chrome 站内搜索 + 内部内容广场统一口径采集 | completed + refreshed |
| 测评产品与传播机制 | 16Personalities、SBTI、Love Type 16、Attached、Truity、Gallup | completed |
| 科学性与授权边界 | IPIP、O*NET、VIA、Gallup、Myers-Briggs、ECR-R 研究 | completed |

## Subagent 原始产出

| Agent | 任务 | URLs | 状态 |
|---|---|---:|---|
| `xhs_topic_signals` | 小红书主题、互动与“十大天赋”来源 | 20+ | completed |
| `quiz_competitors` | 热门竞品、传播机制、商业化 | 20+ | completed |
| `assessment_validity` | 量表效度、题量、版权与合规 | 20+ | completed |

## 数据覆盖说明

- 小红书综合搜索受个性化、时间和账号状态影响。本次数据用于验证内容存在、相对传播强弱和定义一致性，不作为全平台绝对排行榜。
- 2026-07-22 11:29 新增内部内容广场样本：24 个关键词、每词最多 50 条、近 7 天、按曝光排序，得到 992 篇去重笔记；接口存在语义扩展，报告中的相关样本由标题规则二次复核。
- 内部数据 artifact 不保存 Cookie、作者身份或带鉴权参数的笔记链接；笔记 ID 仅用于去重。
- 厂商用户数、准确率和转化数据均标注为厂商自报，不能单独证明科学有效性。
- 精确的全平台笔记量、曝光量、收藏量和搜索指数需要官方商业数据或合规第三方数据服务。本轮没有把搜索结果卡片数量外推成平台总量。
