<!-- lark-mirror obj_token=Fl0XdynmaoBRWrxI8fHjwYagpCh space=产品调研 synced=2026-05-18T07:54:44Z -->

<title>信源评分标准prd</title>

---

# **背景与目标**

## **1.1 文档目的**

本文档定义 Rimbo 信源筛选、打标与评分的完整规则，作为产品、研发、运营三方的共同依据。

覆盖范围：

- 哪些信源可以进入信源库（准入标准）
- 每个信源如何被分类和打标（分类体系）
- 每个信源的可信度如何量化（评分体系）
- 信源质量如何动态维护（衰减与治理规则）

不覆盖：单条内容的评分逻辑（Signal Score）、用户个性化匹配逻辑（L4），这两部分在内容评分 PRD 中单独定义。

## **1.2 核心问题**

Rimbo 的目标是帮用户从海量信息中找到真正有决策价值的信号。要做到这一点，系统必须先回答一个前置问题：**这个信源整体可信吗？**

没有信源层的评估，内容层的评分就没有地基——一条来自公关号的「独家消息」和一条来自监管文件的披露，不能用同一套内容标准衡量。

## **1.3 设计原则**

- 运营痕迹比公开声明更可信：招聘变化、专利申请、开源动态往往比 PR 稿早 3–6 个月反映真实意图
- 独立性比接近性更重要：一个有利益冲突的一手信源，不一定比一个独立的二手信源更可信
- 分类是骨架，评分是血肉：Tier 分层决定信源的基准可信度区间，五维度评分在区间内做精细化区分



**信源库链路**

抓取原始内容

↓

标准化整理

↓

AI 快速分类：不打分不写理由

↓

这条信息是否和某个 Channel 相关？

↓

如果相关，进入该 Channel 的评分池

如果不相关，只入库或进入其他 Channel

↓

AI 多维评分：

↓

代码计算最终分：

↓

精选判定

↓

写入数据库

↓

推送/展示

# **信源分类体系**

投资人视角：只相信一手体感，只相信数据。

![](https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=MDJlZmJkMzMwYmM1Njk0ODQ0ODg0NDViNzc2MTVhNzBfODNkMGMyYWQ3NjgxOGY1ZWY3NjdhY2RlZTVjZTA3MDZfSUQ6NzYzNzA3OTcxMTg0MzE3NTk1OV8xNzc5MDkwOTk0OjE3NzkwOTQ1OTRfVjM)

## **2.1 两个维度打标签：**



- 播客：podcast
- 社交媒体：social_media
- 公司官网：company_website
- newsletter
- blog
- IR官网：IR_website
- community_platform



<sheet sheet-id="WhllkJ" token="VQMLsf7aEh3Biqt521qjXxsupMh"></sheet>

# **信源准入标准**

## **3.1 准入流程**

<sheet sheet-id="AQ2G9A" token="VQMLsf7aEh3Biqt521qjXxsupMh"></sheet>

## **3.2 核心准入维度**

**① 信源质量**

近期内容是否有信息增量？是否对目标用户的决策有帮助？

<sheet sheet-id="hE7wia" token="VQMLsf7aEh3Biqt521qjXxsupMh"></sheet>

**② 信源独立性**

是否存在明显利益立场？严重程度决定处理方式：

<sheet sheet-id="IMNqVE" token="VQMLsf7aEh3Biqt521qjXxsupMh"></sheet>

**④ 可持续性**

更新频率是否稳定？停更或低频信源需评估原因：

<sheet sheet-id="PmFo9n" token="VQMLsf7aEh3Biqt521qjXxsupMh"></sheet>

## **3.3 准入后的质量监控与降级规则**

**status 字段定义**

<sheet sheet-id="LBSWZN" token="VQMLsf7aEh3Biqt521qjXxsupMh"></sheet>

**触发警告的条件（满足任一即触发）：**

- 持续低质量内容（内容变水、无增量）
- 长期不更新（非 Event-driven 型信源 90 天无新内容）
- 被用户手动标记「不准确」累计超过 10 次

**警告期处理：**

status 标注为 degraded，继续观察 30 天。期间 L1 基准分不变，但在摘要中降低展示优先级。

**警告期结束：**

<sheet sheet-id="nzqKLW" token="VQMLsf7aEh3Biqt521qjXxsupMh"></sheet>

**下线后复活：**

已下线信源可由运营手动复活，重新进入准入审核流程，走完整审核后重新激活。

# **信源评分体系**

## **4.1 总体说明**

信源评分（Source Score）是对每个信源整体可信度的量化评估，不针对具体内容。每个信源接入时初始化评分，后续根据历史表现动态更新。

输出结果为六个字段：

```Plain Text
D1_score    # 核验流程分       0.00–1.00
D2_score    # 更正机制分       0.00–1.00
D3_score    # 历史准确率分     0.00–1.00
D4_score    # 独立性分         0.00–1.00
D5_score    # 更新节奏稳定性分 0.00–1.00
L1_score    # 综合分           0.00–1.00
```

## **4.2 五个评分维度**

<sheet sheet-id="XsHUMn" token="VQMLsf7aEh3Biqt521qjXxsupMh"></sheet>

## **4.3 各维度打分参考标准**

### **D1 核验流程**

<sheet sheet-id="clpGXY" token="VQMLsf7aEh3Biqt521qjXxsupMh"></sheet>

### **D2 更正机制**

<sheet sheet-id="lnP1eB" token="VQMLsf7aEh3Biqt521qjXxsupMh"></sheet>

### **D3 历史准确率**

<sheet sheet-id="tJTn1e" token="VQMLsf7aEh3Biqt521qjXxsupMh"></sheet>

### **D4 独立性**

<sheet sheet-id="3YCu5n" token="VQMLsf7aEh3Biqt521qjXxsupMh"></sheet>

### **D5 更新节奏稳定性**

<sheet sheet-id="mqui5h" token="VQMLsf7aEh3Biqt521qjXxsupMh"></sheet>

## **4.4 L1综合分公式**

公式结构统一，权重按 Tier 分别设定：

```Plain Text
L1 = w1×D1 + w2×D2 + w3×D3 + w4×D4 + w5×D5
约束：w1+w2+w3+w4+w5 = 1.0
```

**各 Tier 权重分配：**

<sheet sheet-id="CXpozg" token="VQMLsf7aEh3Biqt521qjXxsupMh"></sheet>

**权重设计逻辑：**

- **T1 Primary**：D4独立性权重最高（0.50）。官方一手信源的核心风险是利益冲突——创始人表态、公司公告本身就是高利益相关方，独立性是最关键的折扣因子
- **T2 Professional**：D1核验流程权重最高（0.30）。专业媒体的核心价值就是编辑规范和独立核实，这是T2区别于其他Tier的本质
- **T3 Frontline**：D4独立性权重最高（0.45）。运营痕迹类信源（招聘/专利/开源）的最大优势是独立性强、不可伪造，这个优势需要在评分中体现
- **T4 Community**：D3历史准确率权重最高（0.35）。社区信号噪音高，唯一可靠的过滤机制是历史记录——爆过几次料、兑现了几次

## **4.5 T3 Frontline 特殊处理规则**

Frontline 层的三类信源在五个维度上有特殊的评估方式：

**公司/创始人博客（CompanyBlog）**

- D1 核验流程：无编辑流程，默认 0.10–0.20；但内容为技术文档或产品发布说明时可提至 0.40
- D2 更正机制：以文章修订记录（edit history）替代传统更正机制
- D4 独立性：创始人博客默认 Conflicted，interest_flag 强制标注 

**开源动态（OpenSource）**

- D1 核验流程：以 code review / PR 审核流程替代编辑核验，有 review 机制的仓库评分更高
- D2 更正机制：以 commit log / changelog 替代传统更正机制，版本记录完整即高分
- D4 独立性：开源项目通常 Independent，除非明显由单一商业公司主导

**科技产业动态（IndustrySignal）**

- D1 核验流程：招聘数据/专利申请为公开可观察数据，无需核验流程，D1 固定为 0.70（可观察即可信）
- D2 更正机制：数据类信源以数据源更新机制替代，数据源稳定可靠即高分
- D5 更新节奏：按数据源的抓取频率评估，而非内容发布频率

## **4.6 L1基准分初始化**

信源接入时，L1基准分按所属 Tier 的区间初始化。运营在审核时对五个维度逐一打分，系统按对应 Tier 的权重公式计算 L1 初始值。

<sheet sheet-id="bHTYnY" token="VQMLsf7aEh3Biqt521qjXxsupMh"></sheet>

**越界处理：**

如果公式计算结果超出所属 Tier 的区间上限，截断至上限；低于下限时不截断，允许低于下限作为异常信号，触发运营复核。

---

## **4.7 L1动态更新规则**

L1 不是静态分，接入后根据信源的实际表现持续调整。触发更新的条件分为两类：

**自动触发（系统执行）：**

<sheet sheet-id="fD1sxw" token="VQMLsf7aEh3Biqt521qjXxsupMh"></sheet>

**人工触发：**

<sheet sheet-id="Er03zk" token="VQMLsf7aEh3Biqt521qjXxsupMh"></sheet>

---

## **4.8 credibility_trend 字段**

每个信源维护一个 credibility_trend 字段，反映近期 L1 变化趋势，共三个值：

<sheet sheet-id="zSYfv5" token="VQMLsf7aEh3Biqt521qjXxsupMh"></sheet>

credibility_trend 显示在信源管理页，用于运营日常巡检。

# **信源打标字段**

## **5.1 字段总表**

每个信源接入时初始化以下字段，部分字段后续动态更新：

<sheet sheet-id="sYGzTn" token="VQMLsf7aEh3Biqt521qjXxsupMh"></sheet>

## **5.2 字段更新频率说明**

<sheet sheet-id="tuF1gp" token="VQMLsf7aEh3Biqt521qjXxsupMh"></sheet>

## **5.3 字段枚举值扩展规则**

以下字段的合法值需要严格管控，不允许随意新增：

- **source_tier**：四个值固定，不可扩展，新增层级需产品评审
- **source_type**：17个值固定，新增分类需产品评审并同步更新权重规则
- **interest_flag**：三个值固定，不可扩展
- **status**：三个值固定，不可扩展

以下字段可由运营按需扩展，无需评审：

- **domain_coverage**：新增领域标签直接添加
- **geo_scope**：新增地域范围直接添加

好，第六个模块：**衰减与动态调整规则**。

---

# **衰减与动态调整规则**

## **6.1 信源可信度衰减**

与内容衰减不同，信源可信度的调整是**离散的、事件驱动的**，不使用连续衰减公式。

具体触发规则见4.7节。

以下是补充的边界规则：

**衰减下限：**

L1_score 有下限保护，不同 Tier 的下限如下：

<sheet sheet-id="D3hXda" token="VQMLsf7aEh3Biqt521qjXxsupMh"></sheet>

**恢复上限：**

L1_score 单次复核的提升幅度上限为 +0.15，防止运营误操作导致分数异常跳升。连续提升需间隔 30 天以上。

**跨领域准确率隔离：**

同一信源在不同领域的 D3 历史准确率独立计算，互不影响。例如：Bloomberg 科技报道准确率高，不影响其政治报道的 D3 分。

---

## **6.2 credibility_trend 与 status 的联动**

<sheet sheet-id="sXiOwe" token="VQMLsf7aEh3Biqt521qjXxsupMh"></sheet>

# **信号增强与信源评分的关系**

## **7.1 说明**

信号增强机制属于内容层评分，不在本 PRD 的覆盖范围内。本节只说明增强机制与信源评分之间的接口关系。

## **7.2 增强记录对 D3 的影响**

每次内容层的信号被验证为真实或被推翻，结果会回写到信源的 D3 历史准确率：

<sheet sheet-id="Lhf93i" token="VQMLsf7aEh3Biqt521qjXxsupMh"></sheet>

**7.3 回写规则**

- 回写以**信源为单位**，不以单条内容为单位
- 同一信源在不同领域的兑现记录独立维护，互不影响（见6.4跨领域准确率隔离）
- 回写触发 D3 变化后，系统重新计算 L1_score，并更新 credibility_trend

# **自动化实现链路**

## **8.1 总体流程**

```Plain Text
信源发现 → 审核 → 评分初始化 → 持续监控 → 状态维护
```

## **8.2 Step 1：信源发现**

系统通过以下方式自动发现候选信源，推送运营审核队列：

<sheet sheet-id="1mwiMh" token="VQMLsf7aEh3Biqt521qjXxsupMh"></sheet>

候选信源进入审核队列后，系统自动预填以下字段供运营参考：

<sheet sheet-id="ryYdmt" token="VQMLsf7aEh3Biqt521qjXxsupMh"></sheet>

## **8.3 Step 2：审核**

在审核界面完成以下操作：

<sheet sheet-id="W2j9t1" token="VQMLsf7aEh3Biqt521qjXxsupMh"></sheet>

## **8.4 Step 3：评分初始化**

审核通过后系统执行：

```Plain Text
1. status → active
2. 按 source_tier 对应权重计算 L1_score
3. credibility_trend → Stable（初始值）
4. created_at → 当前时间戳
5. last_reviewed_at → 当前时间戳
```

## **8.5 Step 4：持续监控**

信源激活后系统持续监控以下信号，触发对应动作：

<sheet sheet-id="d6pXqg" token="VQMLsf7aEh3Biqt521qjXxsupMh"></sheet>

## **8.6 Step 5：状态维护**

<sheet sheet-id="Y02ZsX" token="VQMLsf7aEh3Biqt521qjXxsupMh"></sheet>

# **9. 场景示例**

## **9.1 典型信源打分示例**

### **示例一：SEC EDGAR（T1 Primary / RegulatoryDoc）**

背景：SEC EDGAR 是美国证券交易委员会的官方文件数据库，收录上市公司强制披露文件。

<sheet sheet-id="N0JJtb" token="VQMLsf7aEh3Biqt521qjXxsupMh"></sheet>



```Plain Text
T1 权重：D1×0.10 + D2×0.10 + D3×0.20 + D4×0.50 + D5×0.10
L1 = 0.95×0.10 + 0.90×0.10 + 0.95×0.20 + 0.95×0.50 + 0.90×0.10
L1 = 0.095 + 0.090 + 0.190 + 0.475 + 0.090 = 0.94
```

interest_flag：Independent 

credibility_trend：Stable

---

### **示例二：The Information（T2 Professional / PremiumMedia）**

背景：The Information 是专注科技行业的付费专业媒体，以独家报道和深度调查著称。

<sheet sheet-id="KaA31t" token="VQMLsf7aEh3Biqt521qjXxsupMh"></sheet>

```Plain Text
T2 权重：D1×0.30 + D2×0.20 + D3×0.25 + D4×0.15 + D5×0.10
L1 = 0.85×0.30 + 0.80×0.20 + 0.85×0.25 + 0.85×0.15 + 0.80×0.10
L1 = 0.255 + 0.160 + 0.213 + 0.128 + 0.080 = 0.84
```

interest_flag：Independent 

credibility_trend：Stable

---

### **示例三：Stripe Engineering Blog（T3 Frontline / CompanyBlog）**

背景：Stripe 官方技术博客，发布产品更新、技术架构和工程实践内容。

<sheet sheet-id="FELSUR" token="VQMLsf7aEh3Biqt521qjXxsupMh"></sheet>

```Plain Text
T3 权重：D1×0.10 + D2×0.10 + D3×0.25 + D4×0.45 + D5×0.10
L1 = 0.30×0.10 + 0.40×0.10 + 0.80×0.25 + 0.20×0.45 + 0.70×0.10
L1 = 0.030 + 0.040 + 0.200 + 0.090 + 0.070 = 0.43
```

interest_flag：Conflicted ⚠️ 

credibility_trend：Stable

注：D4 独立性低拉低了整体 L1，但技术内容本身准确率高。

使用时需结合 interest_flag 标注，用户看到的是「来自 Stripe 官方，利益相关」的明确提示。

---

### **示例四：Hacker News（T4 Community / DevCommunity）**

背景：Y Combinator 旗下科技社区，聚集大量开发者和创业者，早期信号丰富但质量参差。

<sheet sheet-id="zHdG6L" token="VQMLsf7aEh3Biqt521qjXxsupMh"></sheet>

```Plain Text
T4 权重：D1×0.20 + D2×0.15 + D3×0.35 + D4×0.20 + D5×0.10
L1 = 0.10×0.20 + 0.20×0.15 + 0.55×0.35 + 0.70×0.20 + 0.80×0.10
L1 = 0.020 + 0.030 + 0.193 + 0.140 + 0.080 = 0.46
```

interest_flag：Independent 

credibility_trend：Stable

好，第二部分：**边界场景处理**。

---

## **9.2 边界场景处理**

### **场景一：同一信源跨领域表现差异大**

情况：Bloomberg 科技报道准确率高，但政治报道偶有偏差。

处理规则：

- D3 历史准确率按领域独立维护，互不影响
- 系统存储结构为 `D3_score_by_domain`，例如：

```Plain Text
D3_score_by_domain: {
  AI: 0.88,
  FinTech: 0.85,
  Politics: 0.62,
  General: 0.78
}
```

- L1 计算时取**用户当前查看内容所属领域**的 D3 分，而非全局平均值
- 若内容领域无对应记录，取 General 值作为默认

---

### **场景二：信源改版或调性发生重大变化**

情况：某科技媒体被收购后，编辑方针从独立报道转向商业推广内容为主。

判断标准：满足以下任一条件即视为重大变化：

- interest_flag 发生档位变化（如 Independent → Conflicted）
- 近 30 天内容中 PR 通稿比例超过 50%
- 核心编辑团队发生重大人事变动

处理方式：

- 运营触发全量重新打分，D1–D5 全部重置
- 重新打分结果与历史分值偏差 ≥0.20 时，系统推送变更通知
- 历史 D3 记录保留，但在重新打分后降低历史记录权重（近期表现权重更高）

---

### **场景三：创始人个人账号 vs 公司官方账号**

情况：同一家公司，创始人个人 X 账号和公司官方账号都在发布内容，应该作为一个信源还是两个？

处理规则：作为**两个独立信源**分别建档打标。

<sheet sheet-id="RBB7r1" token="VQMLsf7aEh3Biqt521qjXxsupMh"></sheet>

关键区别：创始人个人账号有时发布非官方信息（观点、预告），公司官方账号发布的内容具有更强的法律约束力。两个信源独立评分，内容层再做去重处理。

---

### **场景四：信源短期内大量低质量内容涌入**

情况：某媒体在热点事件期间大量发布未经核实的快讯，质量明显下滑。

处理规则：

- 短期波动（≤14 天）不触发 D3 调整，等待事件平息后评估
- 超过 14 天仍持续低质量 → 触发 D3 −0.03，标注「近期表现下降」
- 热点期间的内容在内容层单独降权，不回写至信源 D3（避免短期事件污染长期记录）

---

### **场景五：匿名信源的处理**

情况：某 Blind 帖子爆料某公司即将裁员，来源完全匿名。

处理规则：

- 匿名信源归入 T4 Community / IndustryInsider
- D4 独立性默认 Related（动机不明，无法判断是否有利益立场）
- D3 历史准确率初始值为 0.30，需积累足够记录后才能调整
- 内容层必须等待运营痕迹数据（如 LinkedIn 招聘变化）交叉验证后才能提升信号分级
- 匿名信源永远不触发 Insider Boost

---

### **场景六：信源被恶意刷「不准确」标记**

情况：某高质量信源被异常集中地标记为「不准确」，疑似恶意操作。

处理规则：

- 系统检测单一用户或少数用户集中标记的异常模式
- 异常标记不计入 L1 调整，推送核查
- 判断为恶意标记后，清除该批次记录，不影响 L1_score
- 正常标记的判断标准：来自 ≥3 个不同用户，且标记时间分布在 7 天以上

好，第三部分：**准入判断示例**。

---

## **9.3 准入判断示例**

### **示例一：通过 — Stratechery（个人Newsletter）**

背景：Ben Thompson 个人订阅Newsletter，专注科技行业深度分析，付费订阅用户超10万。

运营对四个准入维度的判断：

<sheet sheet-id="K3EmQ6" token="VQMLsf7aEh3Biqt521qjXxsupMh"></sheet>

审核结论：**通过，直接激活**

初始打标：

```Plain Text
source_tier: Professional
source_type: ProCommentary
interest_flag: Independent
language: EN
geo_scope: US
domain_coverage: AI, Enterprise, Consumer
update_frequency: Weekly
status: active
```

初始 L1 评分：

<sheet sheet-id="9cGHJ3" token="VQMLsf7aEh3Biqt521qjXxsupMh"></sheet>

```Plain Text
T2 权重：D1×0.30 + D2×0.20 + D3×0.25 + D4×0.15 + D5×0.10
L1 = 0.60×0.30 + 0.65×0.20 + 0.80×0.25 + 0.90×0.15 + 0.85×0.10
L1 = 0.180 + 0.130 + 0.200 + 0.135 + 0.085 = 0.73
```

---

### **示例二：拒绝 — 某科技公司官方微信公众号**

背景：某独角兽公司运营的官方微信公众号，内容以融资公告、产品发布和创始人专访为主。

运营对四个准入维度的判断：

<sheet sheet-id="ruoPLG" token="VQMLsf7aEh3Biqt521qjXxsupMh"></sheet>

审核结论：**一票否决，拒绝准入**

拒绝原因：信源独立性严重冲突（明显公关号），同时信源质量不达标，触发双重拒绝条件。

备注：该公司的官方融资公告可通过监管披露渠道（工商股权变更）获取，无需依赖公关号。

---

### **示例三：暂存待议 — 某行业垂直媒体**

背景：专注半导体行业的中文媒体，有一定独家报道，但近期被某半导体厂商战略投资。

运营对四个准入维度的判断：

<sheet sheet-id="Kon3C4" token="VQMLsf7aEh3Biqt521qjXxsupMh"></sheet>

审核结论：**暂存待议，观察 30 天后重新判断**

观察重点：

- 战略投资方相关报道是否出现明显正面偏向
- 竞争对手相关报道是否出现回避或负面倾向
- 30 天后运营重新评估 interest_flag 档位

若 30 天后无明显偏向 → 准入，interest_flag = Related 若发现明显偏向 → 拒绝，或准入但 interest_flag = Conflicted ⚠️

---

### **示例四：通过但降级处理 — 某知名投资人 X 账号**

背景：某头部 VC 合伙人的个人 X 账号，经常发表对科技行业的看法，同时管理多个已投项目。

运营对四个准入维度的判断：

<sheet sheet-id="Wtvem5" token="VQMLsf7aEh3Biqt521qjXxsupMh"></sheet>

审核结论：**通过，interest_flag = Related，内容层需逐条判断利益相关**

初始打标：

```Plain Text
source_tier: Professional
source_type: ProCommentary
interest_flag: Related
language: EN
geo_scope: US
domain_coverage: AI, FinTech, General
update_frequency: Realtime
status: active
```

特别规则：当该信源发布内容涉及其已投项目时，系统自动将该条内容的 interest_flag 升级为 Conflicted ⚠️，独立于信源整体的 Related 标注。