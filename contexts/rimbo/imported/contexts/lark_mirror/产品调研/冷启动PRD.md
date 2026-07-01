<!-- lark-mirror obj_token=Byjhdaw1IoIHwHxF4bVjvSaWpdh space=产品调研 synced=2026-05-18T07:54:44Z -->

<title>冷启动PRD</title>

# 一、业务逻辑

1. 用户完成追踪问题或者任务输入→系统提取主题关键词
2. 让用户选择身份信息，以及偏好的信源类型
3. 主题关键词、用户身份、信源类型将作为推荐信源包的核心输入，去生成相关的信源包回来
4. 信源包的勾选状态，将作为AI后续信息抓取、简报生成的核心输入条件
5. 频道创建后，系统实时（24/7）监控更新

 ![](https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=NDhjN2M5MzM5YzFjNGQwZDI1MjQ2Mzk0OWUyMDQyZWZfNmVkNGUxYTIwYWQ1MTk4ZTdlOTI0Zjc2ZDMwN2U5MTVfSUQ6NzU4NzI5MTA3OTExNzAxNjU5NV8xNzc5MDkxMDA2OjE3NzkwOTQ2MDZfVjM)

# 二、实现方案

### Step 1：用户描述想追踪的任务

用户登录后(登录时要写昵称) 

Hi XX!

对话（预设-AI助手引导语）：

“I'm your AI Task Assistant. Tell me in one sentence what you're tracking.I'll turn it into a channel and keep you updated with briefs.”

步骤进度组件：step1

输入任务组件：引导用户输入自己的任务，并且send，当send状态时，底部对话框的发送键变成处理加载态，交互 需要补充处理加载态

示例组件：2个showcase的词，支持可配置

状态及动作引导组件：COMPLETE STEP 1/3 TO CONTINUE



### Step 2：用户输入轻量画像 

对话（预设-引导语）："Quick check: this helps me tune sources and briefs."

你是：Engineer / PM / Investor / Founder / Other（单选）

你偏好的信源类型 多选（支持类型可配置）



### Step 3：用户确认信源包，输入自己偏好的具体信源

（1）核心流程

主题关键词、用户身份、信源类型将作为推荐信源包的核心输入，去生成相关的信源包回来，信源包里推的信源以信源类型为优先来排序

展示 3个 Source Packs（每包默认展示 6 个来源 + More(20+)），用户只需勾选

信源包=主题及预设人群对应的信源包维度，具体数据生产逻辑如下：

| A 目标人群 | B 人群关注的维度 | C 主题词 | 信源包维度 =  BXC |
|-|-|-|-|
| 产品经理 | 行业洞察：赛道趋势、技术落地场景、行业报告  <br/>产品实战：产品设计、迭代策略、落地方法论  <br/>商业与竞争：商业政策、竞品动态、商业模式 | 250个种子主题词 | 例：  <br/>行业洞察×主题词  <br/>→输出“AI Search Industry Insights”  <br/>产品实战×主题词→输出“AI Search Product Practice”  <br/>商业与竞争×主题词→输出“AI Search Business & Competition” |
| 研发 | 技术原理：核心技术底层逻辑、算法架构、理论研究  <br/>开源方案：开源项目、代码实现、技术工具适配  <br/>研发进展：技术迭代、落地难点、行业技术突破 | 250个种子主题词 | 例：  <br/>技术原理×主题词  <br/>→输出“AI Search Tech Principles”  <br/>开源方案×主题词  <br/>→输出“AI Search Open Source Solutions”  <br/>研发进展×主题词  <br/>→输出“AI Search R&D Progress |
| 投资人 | 融资动态：赛道融资事件、轮次金额、投资方信息  <br/>商业价值：赛道市场规模、盈利模式、增长潜力  <br/>政策导向：行业监管政策、扶持政策、政策解读 | 250个种子主题词 | 例：  <br/>融资动态×主题词→输出“AI Search Funding Dynamics”  <br/>商业价值×主题词→输出“AI Search Commercial Value”  <br/>政策导向×主题词→输出“AI Search Policy Trends” |

（2）兜底策略：当预设的信源包并不匹配用户主题词时，就不要信源包分类的概念，就变成已经为你筛选全网信源

[已为你筛选80+优质信源]

默认展示10个高质量信源，点击展开全部信源



（3）新增自定义信源输入框，交互未画

用户输入“信任信源名字”（Hardfork 等）或者支持粘贴信源链接



Create Channel（loading：Creating…）



技术可行性讨论

有 > **可用范围** > 质量



目前是有RSS链接的信源，稳定、合规、成本低；如果站点没有RSS链接才有第三方的API

我们目前有多少的站点是没有RSS链接的，业界是怎么处理？

怎么做到实时？