# TEAM.md - rimbo 团队画像

_这份文件是给 AI 读的：每次 session 启动都会被动加载，作为团队层面的全局上下文，让 AI 在做产品决策、写文档、回复消息时有正确的视角。改动属敏感清单，必须 PR + review。_

## rimbo 是什么团队

rimbo 是 Mindspace-ai 旗下的小团队，正在做 **Rimbo.ai** —— 一个以 AI 为核心的个人信息助手。当前阶段是 **MVP（产品迭代路径阶段一·Track）**，目标是验证「AI + 订阅 > 订阅」：先让用户不漏关键信息变化，能 follow，能在频道里持续沉淀。

## Rimbo.ai 是什么产品

> 一个"主动感知 + 整理 + 沉淀"的个人信息助手。

**核心问题：** 用户信息过载、分散、缺少沉淀。各平台对个性化的理解仅限本平台行为，用户跨多源（Twitter / 公众号 / RSS / newsletter / 邮件 / 播客 / YouTube）获取信息成本高，长周期问题（研究 / 投资 / 产品 / 学习 / 职业）缺少持续追踪与判断收敛的载体。

**解决方案：** 用户用 **频道（Channel）** 定义自己的关注问题 / 项目 / 任务。系统跨平台 follow 信源（Source），捕捉关键变化（Change），交付"变化 + 重要性 + 可回溯"的简报，并在频道里沉淀为长期信息资产（Memory）。

**用户闭环：** Define → Follow → Track → Explain →（Confirm → Memory）

**核心对象模型：** `Channel` / `Source` / `Change` / `Importance` / `Evidence` / `Memory`

详细产品规划见 [`contexts/products/rimbo/README.md`](../contexts/products/rimbo/README.md) 和 [`contexts/lark_mirror/产品调研/产品规划.md`](../contexts/lark_mirror/产品调研/产品规划.md)。

## 当前阶段

**MVP / 阶段一·Track**：先让用户"不再错过关键变化"，能 follow。

- **产品验证目标**：AI + 订阅 > 订阅；验证一手信源（含播客、YouTube、自定义 RSS）的价值
- **技术验证目标**：个性化订阅漏斗 + 自动化高质量信源抓取 + 个性化推荐能力
- **后续阶段（仅作上下文，非当前重点）**：阶段二 Archive（融合用户私域碎片，主动推荐）→ 阶段三 Network（频道可分享 / 共建 / 分发）

## 团队成员

| 名字 | handle | 主要视角 | 备注 |
|---|---|---|---|
| 徐昊 | [xu](./members/xu.md) | engineer + pm | rimbo work context 仓库 owner，关注 AI 工程化、全栈基建 |
| 刘可欣（coco） | [coco](./members/coco.md) ⚠️ | pm / 产品 | 主导 PRD（Discovery 广场、追踪 task 场景等），跨 case 设计 |
| Evan Liu | [evan](./members/evan.md) ⚠️ | engineer | 后端 / ML 后端核心贡献者（GitHub `Evan-master`），底层能力实现 |
| Mandy Hu | [mandy](./members/mandy.md) ⚠️ | pm / 业务 | 业务场景、数据来源、用户调研衔接 |
| Qihang | [qihang](./members/qihang.md) ⚠️ | engineer | 信源工具 / 评测 / LLM 应用（GitHub `qihang-zhang`） |
| murphy shen | [murphy](./members/murphy.md) ⚠️ | engineer | ML / 召回 / 信源标签（GitHub handle 待本人确认） |
| 玉敏（yumin） | [yumin](./members/yumin.md) ⚠️ | gtm / 运营 | 社媒 / TikTok / 邮件营销 / 海外（印度）市场拓展 |

> 注：⚠️ 标记表示 profile 是 AI 代写骨架，待本人接手补全。详细个人 profile 见 [`members/<handle>.md`](./members/)。

**主要工作群（详见 [`contexts/team_config.yml`](../contexts/team_config.yml)）：**

- `rimbo_core`（coco / Evan / Mandy / xu）—— PRD / 决策 / 产品对齐
- `rimbo_dev`（Evan / qihang / murphy / xu 等）—— 研发讨论、信源 / 召回 / 评测
- `mindspace`（含 yumin / Mandy / coco / Evan / 徐昊）—— 上层组织群、运营 / 增长 / 海外市场

## 我们在做什么

1. **产品**：MVP 频道系统、信源识别与管理、智能信息流首页、卡片落地页、Discovery 广场、登录 / 订阅 / 动态上传等模块的 PRD 与实现
2. **数据 / 信源**：信源库建设、信源评分、抓取信源站点的主题词体系、Gmail Newsletter 提取、垃圾域名过滤
3. **AI 能力**：内容筛选、卡片生成、详情页 summary、频道生成 prompt、Tailor brief、订阅源识别
4. **业务场景**：早期金融场景（投资人追踪、AI deal 追踪、券商研报）作为切入点
5. **协作 infra**：rimbo work context 仓库（本仓库），让团队的 PRD / 调研 / 决策 / 能力交付物与 AI 协作有共享 workspace

## 我们不做什么

- **不做通用搜索引擎**：rimbo 是基于用户定义的 Channel 做主动 follow 与沉淀，不是被动 query-response
- **不做内容平台**：信源是别人产的，rimbo 做的是聚合 / 评分 / 解释 / 推荐 / 沉淀，不自己生产长内容
- **MVP 阶段不做协作 / 分享 / 发布**：阶段三才考虑
- **不做企业 / 团队级账户**：rimbo.ai 是个人信息助手，不是团队工作流工具

## 团队价值观（对 AI 输出的期待）

**对工程产物的要求**：可验证 > 看起来对、契约清晰 > 实现优雅、可演进 > 一次性完美。

**对沟通产物的要求**：直接给结论、附判断依据、不堆砌华丽辞藻。详见 [`COMMUNICATION.md`](./COMMUNICATION.md)。

**对决策的要求**：决策必须留痕（`contexts/products/<x>/decisions/` 或 `contexts/planning/decisions/`），写清"为什么不选另一个选项"。

## 术语习惯

团队反复出现、外部不一定能直接对上的概念，统一登记到 [`../contexts/glossary/`](../contexts/glossary/)。AI 在文档里使用以下词时优先用团队定义而非通用定义：

- **Channel / 频道**：用户定义的、围绕一个问题 / 任务的长期跟进容器（不是 Slack 那种聊天频道，更接近 task / project）
- **Source / 信源**：被 channel 订阅的内容来源（RSS / 邮件订阅 / 播客 / YouTube / Twitter / 公众号 / 自定义站点等）
- **Change / 变化**：信源新增或更新出现的、值得告知用户的内容增量
- **Importance / 重要性**：相对当前 channel 目标，系统给出的"为什么这条值得看"的解释
- **Evidence**：重要性判断背后的可回溯原文 / 引用
- **Memory**：channel 长期沉淀下来的判断与上下文，是 channel 后置能力

## 信息源（AI 在更新这份文件时的事实基础）

这份 TEAM.md 的内容来自：

- 产品规划与 PRD：`contexts/lark_mirror/产品调研/`（81 篇飞书镜像）
- 团队群聊镜像：`contexts/lark_mirror/chats/`（用 `tools/lark_cli/chat_pull.sh` 拉取）
- 团队配置：`contexts/team_config.yml`

更新这份文件时优先看上面三处的最新状态，不要凭印象写。当现实和这份文件冲突，以现实为准并提 PR 同步。

## 关联文档

- [`SOUL.md`](./SOUL.md)：rimbo AI 的人格基调
- [`IDENTITY.md`](./IDENTITY.md)：AI 怎么识别当前 caller
- [`members/`](./members/)：每个成员的个人 profile
- [`WORKSPACE.md`](./WORKSPACE.md)：目录路由表
- [`COMMUNICATION.md`](./COMMUNICATION.md)：沟通风格指南
- [`axioms/team/`](./axioms/team/)：团队公理（从经验中累积）
- [`../contexts/products/rimbo/`](../contexts/products/rimbo/)：Rimbo.ai 产品入口
