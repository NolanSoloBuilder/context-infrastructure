---
title: Rimbo.ai 产品入口
owner: xu
status: approved
version: v0.1
created: 2026-05-18
updated: 2026-05-18
---

# Rimbo.ai

> AI 驱动的个人信息助手。用 Channel 定义关注 → 跨平台 Follow 信源 → 捕捉 Change → 解释 Importance → 沉淀 Memory。

**目的：** 让 AI 一进入这个目录就知道 Rimbo.ai 是什么、当前在哪个阶段、关键文档在哪里。

## 当前阶段

**MVP / 阶段一·Track**。验证 AI + 订阅 > 订阅，让用户不漏关键变化。详见 [`../../../rules/TEAM.md`](../../../rules/TEAM.md)。

## 核心对象模型

| 对象 | 含义 |
|---|---|
| Channel | 用户定义的长期跟进容器（围绕一个问题 / 任务） |
| Source | 频道订阅的内容来源（RSS / 邮件 / 播客 / YouTube / Twitter / 公众号 / 自定义） |
| Change | 信源出现的值得告知用户的增量 |
| Importance | 相对 channel 目标，系统给出"为什么这条值得看"的解释 |
| Evidence | 重要性判断背后的可回溯原文 |
| Memory | channel 长期沉淀的判断与上下文（后置能力） |

**用户闭环：** Define → Follow → Track → Explain →（Confirm → Memory）

## 仓库内文档现状

> 本仓库的 `contexts/products/rimbo/` 目录目前只搭了空骨架（`prd/`、`rfc/`、`decisions/`）。**真实的 PRD / 规划 / 调研当前都在飞书 wiki，已镜像到 [`contexts/lark_mirror/产品调研/`](../../lark_mirror/产品调研/) 和 [`contexts/lark_mirror/研发部门/`](../../lark_mirror/研发部门/)。**

迁移策略：先用 lark_mirror 作为只读事实源，逐步把活跃文档以仓库版重写到 `prd/` / `rfc/` / `decisions/`，老的留在 lark_mirror 作为历史。

## 关键文档导航（指向 lark_mirror 镜像）

**产品定位与规划**

- [`产品规划.md`](../../lark_mirror/产品调研/产品规划.md) — 核心问题、解决方案、对象模型、迭代路径（**首选**）
- [`Rimbo PRD.md`](../../lark_mirror/产品调研/Rimbo%20PRD.md) — 顶层 PRD（含 API 契约草稿）
- [`MVP产品需求文档：智能信息助手.md`](../../lark_mirror/产品调研/MVP产品需求文档：智能信息助手.md)
- [`MVP目标以及用户问题.md`](../../lark_mirror/产品调研/MVP目标以及用户问题.md)
- [`市场调研和MVP切入点定义.md`](../../lark_mirror/产品调研/市场调研和MVP切入点定义.md)

**功能模块 PRD**

- [`PRD_智能信息流首页.md`](../../lark_mirror/产品调研/PRD_智能信息流首页.md)
- [`PRD_订阅源识别与管理.md`](../../lark_mirror/产品调研/PRD_订阅源识别与管理.md)
- [`PRD_卡片落地页（可交互阅读器）.md`](../../lark_mirror/产品调研/PRD_卡片落地页（可交互阅读器）.md)
- [`PRD_意图收集功能.md`](../../lark_mirror/产品调研/PRD_意图收集功能.md)
- [`PRD_登录模块.md`](../../lark_mirror/产品调研/PRD_登录模块.md)
- [`Discovery 广场设计prd.md`](../../lark_mirror/产品调研/DIscovery%20广场设计prd.md)
- [`Skills 广场设计prd.md`](../../lark_mirror/产品调研/Skills%20广场设计prd.md)
- [`动态上传 PRD.md`](../../lark_mirror/产品调研/动态上传%20PRD.md)
- [`冷启动PRD.md`](../../lark_mirror/产品调研/冷启动PRD.md)

**信源 / 内容**

- [`信源库建设PRD.md`](../../lark_mirror/产品调研/信源库建设PRD.md)
- [`信源管理 PRD.md`](../../lark_mirror/产品调研/信源管理%20PRD.md)
- [`信源评分标准prd.md`](../../lark_mirror/产品调研/信源评分标准prd.md)
- [`内容筛选prd.md`](../../lark_mirror/产品调研/内容筛选prd.md)
- [`卡片内容生成.md`](../../lark_mirror/产品调研/卡片内容生成.md)

**研发**

- [`Rimbo架构图.md`](../../lark_mirror/研发部门/Rimbo架构图.md)
- [`Mindspace核心技术框架方案和要点.md`](../../lark_mirror/研发部门/Mindspace核心技术框架方案和要点.md)
- [`后端mvp开发版本文档.md`](../../lark_mirror/研发部门/后端mvp开发版本文档.md)
- [`Twitter Sources API.md`](../../lark_mirror/研发部门/Twitter%20Sources%20API.md)

完整列表见 [`contexts/lark_mirror/产品调研/`](../../lark_mirror/产品调研/)（81 篇）和 [`contexts/lark_mirror/研发部门/`](../../lark_mirror/研发部门/)。

## 团队近期讨论焦点

> 由群聊镜像 `contexts/lark_mirror/chats/rimbo_core/` 推出的当前推进方向。

- **Channel 定位调整为更接近 "task"**：不只是"长期跟进话题"，而是带具体场景目标（5/12 群聊讨论）
- **Discovery 广场金融场景切入**：以"追踪 AI deal"为首个具体 task case（5/12-5/14）
- **底层能力已就位，瓶颈在数据来源**：5/13 Evan 反馈，研报 / 券商行研平台是下一步要打通的源

更新这份摘要前先看最新一份群聊镜像。

## 关联

- [`../../../rules/TEAM.md`](../../../rules/TEAM.md) — 团队画像（含成员、阶段、术语）
- [`../../lark_mirror/`](../../lark_mirror/) — 飞书镜像（只读，由 lark_sync / lark-cli pull 维护）
- [`../../lark_mirror/chats/rimbo_core/`](../../lark_mirror/chats/rimbo_core/) — 团队核心群聊镜像
- [`../../team_config.yml`](../../team_config.yml) — 群 / 通知配置
- [`../../capabilities/`](../../capabilities/) — 项目阶段交付的对内能力
