<!-- lark-mirror obj_token=RI02ddbJwo3FsGx2YB5jgmvHpPe space=产品调研 synced=2026-05-18T07:54:44Z -->

<title>交易追踪 Task PRD</title>

# 基础信息

| 时间 | 版本号 | 负责人 | 更新内容 |
|-|-|-|-|
| 2026/5/15 | V2.0 | coco | Task 功能 |

背景与目标：深入用户具体的信息使用场景，增加可视化输出，提升信息提取的效率



# 范围

需求范围：本次包含Agent Plaza的推荐Channel Agent功能中的track deal 类型



# 核心解决方案

在Agent Plaza 选择一个功能

run：

此功能自动加入用户已有chan



## 功能列表：

<sheet sheet-id="T0gRQe" token="C6QnspEhdhGNmUtGJ1ZjUtqlpuG"></sheet>



## 页面原型与交互说明：

<table><colgroup><col/><col/><col/></colgroup><tbody><tr><td>功能模块</td><td>预览图</td><td>说明</td></tr><tr><td>Agent Plaza广场</td><td><img name="image.png" href="https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=OTZjNjJhZjkwY2M2MzM3ZDIwOGU4MDJlNzM1OGZjZGNfMTYyNTBkMmQ0MmJiNTE2MjljYmRjMzU5OWQ1MDU1MmJfSUQ6NzY0MTA2OTUzNTM4MjA0ODI4Ml8xNzc5MDkxMDM3OjE3NzkwOTQ2MzdfVjM" mime="image/png" scale="1.000000" src="AzghbgGs0oLcgVxwMOxjd8Cgp9e"/></td><td><ol><li> 添加channel task<ol><li>用户在 Agent Plaza 找到目标 Agent，看到可操作按钮：Run now / Schedule / View details。<ol><li>用户点击 <b>Run now</b> ：系统将 Agent 添加到用户已有频道，成为一个 Channel Task →<ol><li>成功：跳转对话框页面，用户可选择一项或多项标准选项，也可选择“其他”输入自定义交易类型；记录用户选择，后续抓取交易信息时匹配所选类型</li><li>失败：显示错误提示</li></ol></li><li>用户点击 <b>Schedule</b> ：弹出时间选择弹窗 → 用户选择提醒时间 → 提交 → 系统保存配置 → 页面显示确认提示。默认情况下，频道内内容更新的时间维持默认设置，不被 Schedule 覆盖。</li><li>用户点击 <b>View details</b> ：弹出 Agent 详情页面，展示功能描述、来源、最近更新时间等信息。</li></ol></li></ol></li></ol></td></tr><tr><td>频道内</td><td></td><td></td></tr><tr><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td></tr></tbody></table>

# Track Deal  

## 字段定义

| 字段 | 定义 | 信源来源 | 输出要求 | 朔源要求 |
|-|-|-|-|-|
| Company | 被投的公司名称 | T2 专业媒体 + T3 Pitchbook交叉验证 | 标准化英文名 | 片段级溯源：NER 提取自新闻正文，携带 source_id + raw_hash |
| Amount | 融资金额 | T1 公司官网/官方社交账号（一手）；T2 专业媒体（二手）；T3 Crunchbase（补全） | 统一换算为美元，注明原始币种 | 数据级溯源：标注原始币种、换算汇率、数据截止时间；推理链溯源：记录换算计算步骤 |
| Round | 轮次 | T2 专业媒体（一手）；T3 Crunchbase/PitchBook（补全） | 标准化枚举值（天使/Pre-A/A/B…） | 片段级溯源：NER 提取自正文，标注 retrieval_score；人工修正需保留 diff |
| Announced Date | 官宣日期 | T1 公司官网/官方社交账号（最优先）；T2 专业媒体（次选） | YYYY-MM-DD 格式 | 实时溯源验证：优先取官方公告日期，API timestamp 标注抓取时间；过期数据自动标红 |
| Category | 赛道 行业分类 | AI 模型基于正文自动分类 | 标准化枚举值(参考下图） | 片段级溯源：AI 分类模型版本需记录（parser_version）；人工校验修正保留 diff |
| Investor | 投资方 | T1 公司官网/官方社交账号（一手）；T2 专业媒体（二手）；T3 Crunchbase/PitchBook（补全） | 支持多个，逗号分隔；区分 Lead/Follow | 片段级溯源：NER 提取自正文，携带 source_id；多信源冲突时保留最高 Tier 来源 |
| Source URL | 新闻原文链接 | T1 公司官网/官方社交账号（最优先）；T2 专业媒体（次选） | 保留原始链接 显示字段：source tier+source \_origin | 实时溯源验证：支持原文高亮回显；原始文档更新时自动提示引用内容可能失效 |
| Post- Money Valuation | 投后估值 | T1 公司官网/IR（披露时）；T2 专业媒体（转述）；T3 Crunchbase/PitchBook（估算） | 统一换算为美元，注明原始币种，注明是否披露 | 数据级溯源：标注披露来源、币种、统计口径；未披露标注「未披露」；推理链溯源：记录估值计算依据 |

Category 枚举值



| **标签值** | **定义** |
|-|-|
| **Foundation Model** | 大语言模型、多模态基础模型公司 |
| **Agent** | AI Agent、Workflow 自动化、垂直 AI 助手 |
| **Enterprise** | AI 赋能企业软件、SaaS、行业解决方案 |
| **Robotics** | 具身智能、工业机器人、消费级机器人 |
| **Infrastructure** | AI 算力、芯片、MLOps、数据标注、向量数据库 |
| **Consumer** | 面向 C 端的 AI 产品（教育、创作、搜索等） |
| **Healthcare** | AI 医疗影像、药物研发、临床决策 |
| **Autonomous Vehicle** | 自动驾驶、智能座舱、车载 AI |
| **Other** | 不属于以上类别的 AI 相关融资 |

## Case 

I've reviewed **X sources** across your AI Deal channel, covering **10 funding updates** in the past 24 hours.

Today's signals converge on these themes: **Robotics dominates deal flow**, **mega-round concentration at the top**, **Hillhouse most active investor**.

I'd recommend prioritizing your focus on: **Physical Intelligence B轮 \$400M** — closest competitor to your Robotics portfolio, and **OpenAI \$40B E轮** — valuation gap with Tier 2 is widening faster than expected.

<sheet sheet-id="0xfcfA" token="C6QnspEhdhGNmUtGJ1ZjUtqlpuG"></sheet>





# 针对NVIDIA AI 业务竞争格局分析

在run之前用弹窗对话框的形式，和用户确定范围：

1. 确定分析主体：单一目标公司+竞争对手
2. 竞品范围：自定义；用户提议 ai确认；尽量覆盖全
3. 确定业务重点

![](https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=MDcyYzI5ZDM4MmNiMTkxNTYzNmVlYjRiZWY4OTc4ZjlfMmVhN2EyMjE4OGVkMjQyOThlZGQ3ZmI1YjkxYWEyOWFfSUQ6NzYzOTY2ODE3NzM3MDM1MzE3OF8xNzc5MDkxMDM3OjE3NzkwOTQ2MzdfVjM)

## 模块定义

## News（以时间轴的形式展示）



## 竞争格局快照（Competitive Landscape Snapshot）

**定义**：汇总竞对在市场份额、主力产品、执行可信度、毛利率等维度的状态。



## 横向对比矩阵（Cross-Comparison Matrix）

**定义**：从多个维度对竞争对手进行横向对比，便于快速判断各玩家在态等方面的相对优势。



## 护城河仪表盘（Moat Dashboard）

**定义**：分析 NVIDIA 的竞争优势和壁垒，判断其长期战略稳定性。



## **追踪队列（Watchlist / Next Focus）**

**定义**：列出下期关注的事件。



# Case: 

https://nvidia-competitive.vercel.app/