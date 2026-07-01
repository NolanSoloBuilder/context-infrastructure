<!-- lark-mirror obj_token=X6FEd3yGFo3WjUxQg0CjlCCvpJh space=产品调研 synced=2026-05-18T07:54:44Z -->

<title>Gmail 提取深层信息策略</title>



# Gmail 提取深层信息策略

## 目前标签系统的局限：

1. 意图/action的视角错位，系统读取的是发件方的推销意图，而非收件人的真实意图。![](https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=OGQ2ZDNjZTUzN2JmNzYxOGI1OGE1ZGFiNzRiZTUzNjdfNGNiNWQ3ZDdlMzEyNmUxZDg3MDQzMzZlNzUxOGU2ZmRfSUQ6NzU2NjQzMjY0NDQ1MjQ4NjY3NV8xNzc5MDkwOTQxOjE3NzkwOTQ1NDFfVjM)
2. 受投放策略影响：高频发送的营销邮件淹没低频高质内容。算法会成为发送方投放策略的镜像，用户对促销邮件的厌烦或无视，仍会被误判为"购物兴趣"。![](https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=NGEyM2ZmM2M5OTBiODA2Zjc4YTk0MDNmMzQzMGY2YTZfZDkxZDM2MjdhNjEyOTUxNTdiNjZmZTliZjA4NmUzMzNfSUQ6NzU2NjQzMzM2NjAwMjc0ODk0N18xNzc5MDkwOTQxOjE3NzkwOTQ1NDFfVjM)
3. 静态/ 孤立：将每封邮件视为孤立事件，无法识别系列邮件背后的统一项目，也无法区分深度关注与被动接收。



## 优化策略

#### **数据采集增加用户行为数据，用于分析用户与信源和内容的强度**

- 扫描收件箱，获取邮件头（发件人、主题、日期）和正文内容
- 订阅行为：订阅时间、来源、频率（日/周/月）。

  - 打开行为：打开次数、打开延迟（从收到到打开的时间）、打开时长、打开时间点（工作日/周末）。
  - 点击行为：邮件内链接点击次数、点击链接的类型（正文/CTA/导航）。
  - 互动行为：回复、转发、标记星标/重要、移动到文件夹。
  - 终止行为：退订、标记为垃圾邮件。**目标**：在每一个邮件类型内部，通过量化指标和模式识别，推断用户的潜在意图和兴趣强度。
  
    1. **信息关系模式**： 这定义了用户与**信息源的长期关系。**
  
    - 深耕型关系：信号 = `长期订阅稳定性` + `高平均打开率` + `高链接点击率`
    - 探索型关系：信号 = `近期订阅` + `中等/波动的打开率`
    - 监护型关系：信号 = `长期订阅但低打开率`（仪式性维护）
    - 交易型关系：信号 = `一次性互动`（完成后即终止）
  
    1. **信息处理强度**：这定义了用户处理信息时的**投入程度。**
  
    - 深度处理：信号 = `高链接点击率` + `重复打开次数` + `回复/转发行为`
    - 瞬时处理：信号 = `极短打开延迟` + `单次打开` + `无点击`
    - 忽略处理：信号 = `永不打开` 或 `立即删除`
    - 

#### **对邮件进行分类，对不同类型的潜在用户意图识别进行区分处理；**

#### **用户的核心画像分层：构建一个从“短期目标”到“长期身份”的画像作为每一次输入context**

**短期越趋向执行，时效性越强；越偏向身份，兴趣和关注越持久，系统性。**

<sheet sheet-id="bqvEri" token="GrjwsQaIuhykcdtAIHjj41zcprg"></sheet>







### Prompt参考（Reasoning Prompt）

### 角色与目标设定

**角色：** 你是一名专业的数字行为分析师和用户体验研究员。

 **任务：** 你的任务是分析用户的邮箱收件箱数据，**从用户的视角**（即收件人的真实意图和行动潜力），而不是发件人的营销目的，来推断用户的**信息需求、潜在行动意图和真实兴趣**。

###  输入数据（上下文）

你将收到一封或一系列邮件的数据，请使用以下格式进行分析：

```Plain Text
[邮件ID]
- 邮件主题：[Subject Line]
- 发件人/领域：[Sender/Domain]
- 接收时间：[Timestamp]
- 用户操作（Open/Click/Reply/Delete/Ignore）：[User Action]
- 邮件内容摘录（Keywords/Topics）：[Key Content Terms]
- [若为系列邮件，则包含] 邮件历史数据：[Relevant past emails and user actions]
```

### 推理步骤

请严格按照以下三个步骤进行推理分析：

1. **意图/视角矫正与去噪（Intent/Perspective Correction & Denoising）**

   - **发件方意图（Sender Intent）：** 首先，根据主题和发件人识别这封邮件最直接的**发件方意图**（如：促销、通知、确认、请求）。
   - **收件人倾向（Recipient Predisposition）：** 分析用户的历史行为：该用户对来自此发件人或此类邮件（如所有促销邮件）的**平均操作倾向**是什么（高打开率、快速删除、从不回复等）？
   - **真实意图推断（Actual Intent Deduction）：** 将发件方意图与用户倾向结合。如果是一封“促销”邮件，但用户将其**标记为垃圾邮件或连续忽略**，则用户的真实意图/行动应被分类为：“**厌恶/规避**”。如果用户**连续点击**某类促销，则可确认为“**购物兴趣**”。
2. **序列/项目上下文识别（Sequence/Project Context Recognition）**

   - **静态/孤立问题解决：** 检查历史数据。这封邮件是否属于一个**可识别的连续项目或主题**？（例如：一个持续数周的“软件部署”项目邮件链，一个“旅行规划”的系列确认邮件，同一活动/系列/活动漏斗阶段（如邀请→提醒→最后通知）等。
   - **深度关注 VS 被动接收：** 如果用户在系列邮件中对某一主题（例如：公司A的软件）持续**保持回复或点击链接**（深度关注），则将意图强度评级为“高”。如果仅是**被动接收**且**间歇性打开**（例如：每周的例行新闻简报），则评级为“低/信息接收”。
3. **最终用户画像和行动潜力（Final User Profile & Action Potential）**根据步骤 1 和 2 的推理，给出最终的分析结果：

   - **推断的真实用户意图（Actual User Intent）：** 用户的真正行动目标是什么？（例如：购买、研究、协调、取消服务、信息收集）。
   - **信息需求（Information Need）：** 用户目前缺乏或正在寻求的关键信息是什么？（例如：价格比较、产品规格、会议时间确认、教程）。
   - **真实兴趣（Genuine Interest）：** 用户表现出持久兴趣的主题领域（例如：健身器材、企业级SaaS、某个学术领域）。
   - **行动潜力（Action Potential）：** 预测用户在接下来的24-48小时内采取下一步行动的可能性和类型。（例如：高，回复邮件请求报价；中，访问网站浏览更多文章）。























# Twitter 信号/意图提取策略

### 信号识别

<sheet sheet-id="7RHz9o" token="GrjwsQaIuhykcdtAIHjj41zcprg"></sheet>

### 产品驱动策略

<sheet sheet-id="DZwOiu" token="GrjwsQaIuhykcdtAIHjj41zcprg"></sheet>