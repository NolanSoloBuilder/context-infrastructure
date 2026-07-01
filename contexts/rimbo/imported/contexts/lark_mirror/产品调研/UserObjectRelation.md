<!-- lark-mirror obj_token=ULyqdpLz6owLbjxx00pj3KjXpsq space=产品调研 synced=2026-05-18T07:54:44Z -->

# UserObjectRelation

## 背景与目标

### 1.1 背景

Mindspace 从用户授权的第三方平台（MVP 先从 Gmail Inbox）中，理解用户**真实的信息需求**：

- 用户在**追什么主题 / 实体 / 信息源**？
- 这些关系是 **订阅、追随、实际使用还是一次性路过**？
- 这些信息需求发生在 **工作语境** 还是 **个人/兴趣语境**？
- 当前时刻，哪些是**短期高意图**，哪些是历史背景？

传统推荐系统会用行为日志构建 `user-item` 矩阵；Mindspace 的场景里，“item” 不再只是单个平台上的内容，而是跨平台的：

- **Topic**：AI Agents, SaaS Pricing, 宏观经济…
- **Entity**：OpenAI, Fal, Notion, 某 VC, 某作者…
- **Source**：Lenny’s Newsletter, 某个人博主, Financial Times, 某 Substack 专栏…

我们需要一个统一的数据结构**User–ObjectRelation（UOR）**，承载这些跨平台的“对象”，以及用户对它们的关系。

### 1.2 设计目标

1. **统一抽象**：  
 把用户对“主题 / 实体 / 信息源”的关系统一放在一张表，用于所有上层模块（Gmail 总结、领域态势、Proactive 卡片等）。
2. **多源融合**（MVP 先支持 Gmail）：  
 每封邮件贡献一些 `(user, object)` 的证据，由 UOR 聚合成稳定关系。
3. **可解释 & 可控**：  
 不直接让 LLM“想象兴趣”，而是用 LLM 做内容理解（NER / Topic 抽取 / 邮件类型识别），关系本身是**结构化、可调的特征**，方便下游推荐算法使用和调试。
4. **支持核心卡片切面**（至少覆盖）：

   - Gmail Newsletter · Top Newsletter
   - Gmail 工作往来摘要 & 基于工作往来的延伸信息
   - 意图驱动：领域态势 / 实体追随 / Insights

---

## 核心概念与定义

### 2.1 Object（被关注的“对象”）

统一抽象三类对象：

- `topic`：主题/议题

  - 例：AI Agents, SaaS Pricing, Developer Productivity, 个人知识管理…
- `entity`：实体（公司 / 人物 / 产品 / 服务 / 工具）

  - 例：OpenAI, Anthropic, Fal, Notion, Figma, Lex Fridman…
- `source`：信息源（信息从哪里来）

  - 例：Lenny’s Newsletter, 某 Substack 专栏, A16Z Blog, Financial Times, 某个人博主…

> 备注：后续可进一步加 subtype：`entity_type = company/person/product/...`，`source_type = institution/individual` 等，MVP 非必需。

### 2.2 User–ObjectRelation（UOR）

描述 `(user, object)` 之间的**关系类型 + 强度 + 语境**，用于：

- 画像层：刻画用户的“领域兴趣 / 实体追随 / 信息源依赖”
- 推荐层：做 candidate 筛选、排序时的重要特征
- 卡片触发层：决定哪些 topic/entity/source 值得触发合辑卡片

---

## 范围与非目标

### 3.1 本期范围（MVP）

- **信号来源**：仅 Gmail Inbox

  - Newsletter（订阅类）
  - 工作往来邮件（真实个人对话、有回复的线程）
  - 低信息量邮件（注册 / 发票 / 账户等）：只为 entity/source 提供弱或行为信号
- **对象类型**：`topic / entity / source` 三类
- **输出能力**：

  - 聚合出用户**近期高置信的 topic/entity/source 集合**
  - 每个关系具备：`relation_type`、`context`、`intent`、`confidence` 等字段
  - 能支持以下卡片触发逻辑（不在本 PRD细化）：
  
    - Gmail Newsletter Top 合辑
    - Gmail 工作往来合辑 & 延伸信息
    - 领域态势（topic 为主）
    - 实体追随（entity 为主）
    - Insights（intent=learn 的 topic/entity）

---

## 数据模型设计

### 4.1 Object 表（简要）

> 具体 Object 生产由「内容理解 / 实体识别」模块负责，此处只定义关键字段。

<sheet sheet-id="mASEz1" token="GZe6s4fk1hQ47ct2N5vj6PUSpXb"></sheet>

> LLM 主要作用：从邮件 Subject/Body 中抽取 entity/topic/source，并做归一化合并到 Object 表。

### 4.2 UserObjectRelation 表（核心）

#### 4.2.1 字段

<sheet sheet-id="GiOwwi" token="GZe6s4fk1hQ47ct2N5vj6PUSpXb"></sheet>

#### 4.2.2 枚举字段解释

- `relation_type`（**关系视角**）：

  - `"subscribe"`：用户持续从该 source 接收内容（newsletter、官方更新）
  - `"follow"`：用户希望持续看到该 topic/entity 的信息（topic: follow；entity: follow 人/公司/产品）
  - `"use"`：用户正在使用该产品/服务/工具（由注册/功能邮件推断）
  - `"pay"`：用户为该实体付费过（发票/订阅支付）
  - `"contact"`：工作往来中“真实对话”的个人/公司（有回复的邮件线程）
  - `"mentioned"`：仅有少量弱信号，不足以形成稳定关系（MVP 可不用于触发）
- `intent`（**信息需求视角**）：**用户希望从这个 Object（topic / entity / source）获得什么信息价值 / 体验。**注意：这是**用户视角的“信息需求类型”**，而不是内容本身的类别。同一个 Object 可以有多个 intent（例如对 “AI Agents”：既要 keep_up 最新进展，又要 deep_learn 框架）。`keep_up``deep_learn``discovery``belonging``execute``inspire``unknown`

  - 目标：跟上节奏，知道「最近发生了啥」。
  - 典型内容：新闻、市场动态、产品更新、regulation 变动。
  - 对应价值：**即时态势 / need-to-know**

  - 目标：系统理解一个领域/框架，构建 mental model。
  - 典型内容：长文分析、策略框架、case study、长播客。
  - 对应价值：**深度理解 / learn**

  - 目标：拓展视野和 taste，看“我还不知道但可能有趣/有用”的内容。
  - 典型内容：curated digest、推荐书单/播客、平台推荐 feed。
  - 对应价值：**策展发现 / discovery & taste**

  - 目标：维持与社区/创作者/身份的链接。
  - 典型内容：创作者周记、会员更新、线下活动、社区动态。
  - 对应价值：**社区关系 / belonging**

  - 目标：马上能用来做事，解决具体 task。
  - 典型内容：how-to 教程、prompt 模板、操作 checklist、工具推荐实用指南。
  - 对应价值：**行动 / 执行**

  - 目标：获得灵感、视角或情绪价值，不一定要立刻“有用”。
  - 典型内容：长 essay、故事、评论、艺术/人文内容。
  - 对应价值：**灵感 / 反思**

  - 还没啥信号；用默认值 & 观察点击行为后再慢慢收敛。
- `context`（**场景视角**）：

  - `"work"`：与工作 / 项目 / B2B 工具栈相关（多来自工作往来邮件）
  - `"personal"`：与消费/生活方式或个人兴趣相关
  - `"mixed"`：两者都有
  - `"unknown"`：待后续补全

---

## 信号来源与抽取（概览）

> 详细的信号打分在《Email Signal Strength Scoring Logic》文档，这里只抽关键。

### 5.1 邮件环境信号评估`email_env_for_`（per email）

（先判断是哪个语义环境？再判断每个tag里的权重？）

每封邮件先按 **Sender / Body / 行为 / 时间** 四个维度，分别给出对 3 类 object 的**环境强度（0–3）**，再合成一个该邮件对不同 object 的整体环境分，作为 **“这封邮件整体而言，对某一类 object 的最大可信度环境”**；  
后续在object 级别再看每个具体 topic/entity/source 在正文里的角色，只是在这个环境上再做一个 per-tag 的缩放。

---

#### 环境信号输出

<sheet sheet-id="wKx4Ua" token="GZe6s4fk1hQ47ct2N5vj6PUSpXb"></sheet>

统一用 0–3 档，方便实现：

- `0` = 没有环境信号（基本不能用来判断这个 object）
- `1` = 弱环境信号（可能相关，噪音多）
- `2` = 中等环境信号（有用，但不是特别强）
- `3` = 强环境信号（高度可信）

---

#### Sender 维度环境信号（sender_env）

<sheet sheet-id="dhfccN" token="GZe6s4fk1hQ47ct2N5vj6PUSpXb"></sheet>

---

#### Body 维度环境信号（body_env）

这里的 body_env 是“这封邮件的内容形态对三类 object 的整体解释力”，不是单个UserObjectRelationship的位置（那是下一层）。

<sheet sheet-id="PqBDC6" token="GZe6s4fk1hQ47ct2N5vj6PUSpXb"></sheet>

#### 行为维度环境信号（behavior_env）

行为信号更多是**这封邮件整体是不是“被用户当回事”**，按类型对 3 类 object 做轻微放大/缩小。

<sheet sheet-id="eiPr8C" token="GZe6s4fk1hQ47ct2N5vj6PUSpXb"></sheet>

> 行为的数值是**对已有 sender/body 环境分的加减**，不是独立评分。

---

#### 时间维度环境信号（time_env）

时间主要用来分“当前意图” vs “历史背景”。

<sheet sheet-id="AeRpf2" token="GZe6s4fk1hQ47ct2N5vj6PUSpXb"></sheet>

### 5.2 局部信号local_strength（per email, per object）





---

## 从 Email 信号到 UserObjectRelation 的更新逻辑（补充Evan目前的技术方案）

### 6.1 中间层：Email–Object 信号表

### 6.2 聚合到 UserObjectRelation