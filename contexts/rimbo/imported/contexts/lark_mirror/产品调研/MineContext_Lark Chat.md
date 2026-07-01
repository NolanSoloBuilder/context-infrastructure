<!-- lark-mirror obj_token=VynTdGtp0ooWaCxN8YRjXyXNpye space=产品调研 synced=2026-05-18T07:54:44Z -->

<title>MineContext_Lark Chat</title>



两部分内容：  
**（1）从群聊中系统提取用户反馈点（问题/需求点 + 出现频率 + 原文 quote）**  
**（2）从这些反馈中提炼 MineContext 的核心需求与 Request（需求主题 → 用户真实意图）**

---

# **① MineContext 用户反馈点（按主题聚类 + 频率 + 原文 quote）**

来源：群聊 PDF 《MineContext.pdf》 

---

## **A. TODO 功能（识别、查找、导出、准确性）**

### **反馈点 A1：TODO 识别准，但查找困难 / 只按当天粒度 / 无历史回溯**

**频率：4+**

- “当前 TODO 设计的粒度是当日，比如我突然发现3天前识别出的一个任务，我找不到了。”
- “长期使用 proactive feed 太多不好查找。”

### **反馈点 A2：希望支持导出 / 同步到飞书 / 表格 / 云端**

**频率：5+**

- “这个 todo 能导出到飞书文档吗？”
- “想复制/导出的原因是… 不然历史 todo 找不到。”
- “未来能否打通飞书云文档，把每日日志自动同步到云文档里？”

### **反馈点 A3：TODO 数量过多、重复、垃圾内容多 / 准确性问题**

**频率：7+**

- “一天没管，给我生成了超过一百多条的海量Todo…很多Todo意思差不多。”
- “这种上下文方式不优化的话，最终会生成一堆垃圾，都懒得去看了。”
- “实际生成的TODO不太准确，即使我接入了ActivityWatch的数据。”

### **反馈点 A4：希望手动管理：优先级、编辑、补充业务字段**

**频率：3**

- “有没有办法设定一下优先级，有些任务只是摸鱼产生的。”
- “未来是否能支持手动生成 TODO、调整优先级、附加预估耗时等字段？”

---

## **B. 截屏 / 录屏机制（token 消耗、存储、安全、无效截图）**

### **反馈点 B1：Token 消耗过快 / 不可控**

**频率：8+（最高频）**

- “才几个小时就消耗了100W token，这正常吗？”
- “一天 token 消耗 600 万…恐怖如斯。”
- “最近两天 token 消耗量 1800w…花费太高。”

### **反馈点 B2：无效截图（锁屏/屏保/无变化画面）仍被截取**

**频率：6+**

- “锁屏还是会截图的。”
- “息屏状态下还是会录屏并消耗 token 吗？”
- “希望加入判断：如果页面没有改变就不要上传解析。”

### **反馈点 B3：截图内容过多占用本地存储 / 希望自定义存储策略**

**频率：4**

- “之前用过类似产品，本地磁盘可用空间被快速蚕食。”
- “MineContext 是否有本地存储统计和清理？”
- “希望自定义存储路径。”

---

## **C. 隐私 / 安全（公司电脑、模型上传、合规）**

### **反馈点 C1：担心截图会造成公司安全风险 / 合规问题**

**频率：4**

- “开启录屏会不会有合规风险…怕被查水表。”
- “上传给大模型的数据是否有隐私风险？”

---

## **D. 数据同步 / 多设备支持**

### **反馈点 D1：多设备键同一个 API key 但无法“无感同步”**

**频率：3**

- “家里电脑和公司电脑…是否支持无感体验，todo 同步？”
- “目前还不支持云同步。”

---

## **E. Daily Report（日报）质量问题**

### **反馈点 E1：时间线不准确 / 未按真实顺序**

**频率：3**

- “Daily Report 里面的时间线回顾完全是错误的。”
- “更像是把一天的事情套在上午下午晚上的模板。”

### **反馈点 E2：希望可视化 / 深度分析更强（screen time 分析）**

**频率：5+**

- “能不能往 Rize 那样的 screen time 做？”
- “希望 MineContext 告诉我无意识摸鱼时间、看 paper 时间等。”

---

## **F. Creation / 内容深度能力不足**

**频率：3**

- “Creation 这个功能有点不知道怎么用。”
- “内容的 deep research 会有的，OCR必要性一般。”

---

## **G. 自定义能力（prompt / model / endpoint）**

**频率：6**

- “是否支持自定义 endpoint？”
- “能否开放配置？我们用 openrouter / azure token。”
- “能否写 prompt 让 MineContext 在什么情况下主动提示？”

---

## **H. 知识库管理（查看、导入、改错、删除）**

**频率：5**

- “能不能查看/导出知识库？”
- “是否支持导入 markdown？导入 GPT memory？”
- “能把无效信息修改/删除吗？”

---

## **I. 产品形态（移动端 / 菜单栏模式 / 云托管版）**

**频率：4**

- “会考虑出移动端 app 吗？”
- “希望常驻菜单栏而不是 dock。”
- “未来会做云同步的付费托管版吗？”

---

# **② 从反馈中提取 MineContext 的“核心需求” + “需求 Request”**

这些是真正的用户 intent（不是功能层的表面需求）

---

# **【核心需求 1】可靠、可控的「个人工作日志生成系统」**

用户真正想要的是：  
**“MineContext 必须稳定、可查、可回溯，不会丢数据、不制造噪音。”**

### **表现为：**

- 历史 TODO 无法找回
- Daily Report 时间线错误
- Token 消耗无法预估
- 垃圾信息太多

### **潜在 Request：**

- 建立“时间轴数据库”：可索引、可筛选、可搜索
- 高质量的事件识别（少噪音、可追踪）
- 可控的采集策略（时间窗口 / app whitelist / 变化检测）

---

# **【核心需求 2】工作效率洞察（Screen Time × AI Insight）**

用户频繁提到 Rize / ActivityWatch，本质需求是：  
**“帮我看清我的时间去哪了，帮我管理注意力。”**

### **表现为：**

- 希望分析摸鱼、paper、debug 时间分布
- 提高 screen time 可视化
- 自动提示“超时”任务

### **潜在 Request：**

- 自动分类 screen time
- Attention report（注意力得分）
- 任务时长跟踪 + 超时提醒

---

# **【核心需求 3】降低使用成本（token、存储、隐私、合规）**

用户本质上想：  
**“我愿意用，但不能让我付出不可控的代价。”**

### **表现为：**

- token 流失
- 截屏过多
- 对大模型上传敏感内容的担忧
- 存储暴涨

### **潜在 Request：**

- 局部屏幕捕获 / 特定应用捕获
- 本地模型
- 截图差分（无变化不处理）
- 可控的上传策略
- 隐私模式

---

# **【核心需求 4】跨平台、跨设备统一的「个人上下文系统」**

使用多个设备的人希望：  
**“我的工作流是连续的，不随设备而割裂。”**

### **表现为：**

- 多设备同步
- 云托管版
- 移动端版本

### **潜在 Request：**

- 云端上下文数据库
- 多端一致的 Todo & 日报
- 手机端捕获“应用内时间分布”

---

# **【核心需求 5】用户主导的定制化能力（Prompt、规则、个性化模型）**

用户希望 AI 按“我的方式”工作：  
**“我想让 MineContext 按我的工作方式总结和提醒。”**

### **表现为：**

- 修改 prompt
- 自定义 endpoint
- 定义提醒逻辑（如“超过预估时间自动提醒”）
- 手动属性（业务字段、优先级）

### **潜在 Request：**

- 规则配置中心（If-This-Then-That）
- 用户级 Prompt 与模板库
- 插件化 Endpoint（local model / openrouter / azure）

---

# 原文

这个 todo 识别挺准的   个人体验比 `mirix`好。

这个 todo 能导出到飞书文档吗

Baite Huang

Oct 10, 9:50 AM

<cite type="user" user-id="ou_55601f6f108d9add7479a5d9f0184dc6"></cite> mirix应该没有todo生成吧我记得，这个我们之后会做成半透明桌面卡片的形式，所以一开始没想着导出到飞书，不过这个需求可以记一下，提供一个复制

乐臣

Oct 10, 9:53 AM

<cite type="user" user-id="ou_83298d44e2c40eb1ba8e39618d812d69"></cite> 是的 没有 todo, 我是深度mirix 用户， 个人 profile 那一块 能逐步建立 本地个人的 信息图谱 这一点 体感很好。  
minecontext 目前最好的是 TODO, 怎么说呢 用了一个星期  很怕深入用了数据没了，所以才会说 同步飞书表格。

Baite Huang

Oct 10, 9:56 AM

<cite type="user" user-id="ou_55601f6f108d9add7479a5d9f0184dc6"></cite>   
都存在本地吧，而且开源了release，数据感觉应该一直能在

Baite Huang

Oct 10, 10:01 AM

<cite type="user" user-id="ou_55601f6f108d9add7479a5d9f0184dc6"></cite> 这个应该比较快，你目前用下来觉得按照优先级 Urgent粒度复制好，还是任务粒度复制好，还是全局复制好。我目前觉得可以按照优先级粒度，Urgent，Medium，low这样

乐臣

Oct 10, 10:05 AM

<cite type="user" user-id="ou_83298d44e2c40eb1ba8e39618d812d69"></cite> 想复制 导出的原因是， 当前 TODO 设计的粒度是当日， 比如我突然发现 3 天前 识别出的一个 xxxx 任务，我找不到了；

另外 长期使用 `proactive` feed  太多 不好查找 

![](https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=MGY3YmY4NTI0YjcxMzAyN2QxYjRkYzlkM2M3NjQzMjFfMTViZmUxMWEzNTMyNjJmNTk0MWYyYjk3Yzg2NGY3ZjlfSUQ6NzU4MDI2MjQxOTMxMDU5NTYwNV8xNzc5MDkwOTc5OjE3NzkwOTQ1NzlfVjM)



<cite type="user" user-id="ou_83298d44e2c40eb1ba8e39618d812d69"></cite> 请问  
这个支持 自定义 endpoint 的吗

<cite type="user" user-id="ou_55601f6f108d9add7479a5d9f0184dc6"></cite> 其实是支持的，底层是openai的通用API，但是我们还没有测过，所以先没对外暴露



1. gemini  2.x flash(pro) 都支持 Mirix 主推这个
2. 建议开放配置 是因为 可能 openai 系列 使用的是 `azure` 不是官方 token, gemini 系列使用 openrouter
3. 我在我们团队内 推广使用这个 目前俩说 能很好的在 工作心流之外 辅助发现自己的工作情况







taosu

后面会有Windows的release吗[Sob]

Baite Huang

一定会的，最高优需求！





乐臣： 请教下 \`**Creation**\` 这个功能 咋用呀 有点没用明白

Baite Huang： 不过目前Creation的产品功能建设的还不多，未来预计能够让收集到的Context辅助你的创作

![](https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=YjJlZjY5MzY5YTk1YzU5ODY0NGJiYThmZGU4Y2VhOTFfYzc4MjQyNTgxNjkwMDQxZmZjMDcyMGZiOWVjMTg2ZDZfSUQ6NzU4MDI2Mjg0MDIxNzQwNjk5Nl8xNzc5MDkwOTc5OjE3NzkwOTQ1NzlfVjM)

 @ 乐臣 好的， 这个功能确实有点不知道怎么用

@ 乐臣 大家看看会比较想要这个指标统计和类Github热力图的功能么[Thinking]

![](https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=ODc2ZTFmNWE1YTg2OTZjYjlmNjc5ZDU0YTg1Y2Q5OWJfYzdiOWNlMzE0NDlkMGJjNzBkNTlmZWU1MTdjN2Q5MDhfSUQ6NzU4MDI2MzM3NDEwMjEzODM4OV8xNzc5MDkwOTc5OjE3NzkwOTQ1NzlfVjM)

下面是我们正在/将要做的开源项目的介绍：

1. VikingDB（开源向量数据库）：面向生成式AI时代的向量数据库，主攻「海量索引」、「极低成本」、「安全可信」，与传统向量数据库 Milvus/Qdrant 形成错位竞争。
2. OpenContext（开源开发者框架）：全模态全周期的上下文管理框架，支持上下文的捕获，加工，存储管理，智能召回和消费。作为AI时代的关键基础设施，服务于千千万万上层AI应用的搭建。未来希望能够成为走向AGI的关键一环。
3. MineContext（开源客户端应用）：结合Context-Engineering和MineCraft理念的 Context-Aware AI Partner，帮助你在无负担收集海量的信息后，从chaos中获得Insight和Clarity，并能够使用上下文和AI能力进行数字世界的创造。未来希望能够革了Notion和Obsidian的命，成为PKM的新时代答案。



乐臣： 如果没有开启录屏 期望不推送 `tip` `日常总结`

Baite Huang我们下个版本（本周）会上生成时间和关闭推送的

![](https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=OTEwYmE1Zjc1OGE1MDJmNmU0NWI3MTdkM2MzMTRkZDlfMWE4MDM4NjAzYzc5NTVhMTgzNzU2MjAxMDFiOTU5NGZfSUQ6NzU4MDI2Mzg5NzM0MTM5ODU0OF8xNzc5MDkwOTc5OjE3NzkwOTQ1NzlfVjM)

请问下 MineContext 的数据完全本地化，那上传给大模型的数据有隐私数据吗？公司电脑开发的时候能确保隐私问题吗？

Haojie Qin@Passion & Young 现在的模型是请求官方的豆包模型或者openai模型，这里讨论的是全本地的方案，或者公司对模型服务有管控的情况～并不存在数据安全问题

Passion & Youngopenai 模型是公司内部部署的么？

Haojie Qin@Passion & Young 像较大的公司会部署，其他的公司未必会单独部署，因为需要GPU资源

Passion & Young唔。。其实我是想了解下，我在公司电脑上安装 MineContext 并开启录屏的话，会不会有合规风险（怕被查水表，所以了解清楚才敢开始使用）[Facepalm]

Haojie Qin@Passion & Young 嗷嗷，我私发你



Larkin LI

有每小时预估token的消耗量么，开了几个小时感觉用的还挺快的，两个屏幕

View earlier 1 reply

Baite Huang把截图时间延长到15s吧

Zhiheng Liu@Baite Huang 最近的版本把图片压缩去了吗？token 消耗比第一版显著涨了



汪文皓

Oct 14, 11:44 AM

家里电脑和公司电脑，不同电脑，不同配置，不同环境，用同一个 api key，初始配置后是否支持无感的体验，todo 同步更新等

7 thread replies

Haojie Qin

Oct 14, 11:44 AM

现在还是纯本地的，没有云同步的功能～

Baite Huang

Oct 14, 11:45 AM

目前还不支持，这需要云同步，不过可以给我们记一个feature的issue，考虑看能不能操作数据库实现

Maojia Sheng

Oct 14, 11:45 AM

嗯，如果需要的话，我们可以后面推出支持云同步的付费托管版

汪文皓

Oct 14, 11:47 AM

想了解这个数据库支持本地部署吗？是不是好像后续会支持本地模型？这样用自己的本地数据库，本地模型就行了吧？

Baite Huang

Oct 14, 11:48 AM

<cite type="user" user-id="ou_11d531388d728efa19076b40260d676c"></cite> 就是本地数据库，sqlite和chormdb

汪文皓

Oct 14, 11:48 AM

<cite type="user" user-id="ou_83298d44e2c40eb1ba8e39618d812d69"></cite> 有什么操作手册吗？或者教程吗？研究一下独立部署

Baite Huang

Oct 14, 11:49 AM

<cite type="user" user-id="ou_11d531388d728efa19076b40260d676c"></cite> 不需要手动部署，安装完打开就是部署在本地，现在数据不会上云



可以设置快捷键，我不用的时候停止录屏吗。不想让他录无效的context

杨小龙希望能加入判断，如果录制的页面没有改变，就不要上传解析了。

Haojie Qin@杨小龙 现在是有重复截图分析的，相同的截图会被删除



彭曲波

可以自己查看/导出知识库吗？

可以把一些无效或者错误的信息进行修改/删除吗？

Haoyu Wang+1，希望能把gpt里的memory导入或者粘贴进来

马龙(Marlon)加一

Baite Huang@Haoyu Wang 未来预计会支持两类Context源 1. 基于浏览器插件，捕获所有的网页端LLM（ds，openai，claude）对话记录 2. 对话json文件上传

巢毅宁@Baite Huang 能增加导入本地markdown文件吗，我想把obsidian中写的日记导入进去





汪文皓

目前作为一个 app 常驻 dock。有没有可能后续放到菜单栏，走通知，快捷键打开软件页面

Baite Huang在开发后台处理了





Nick

会一直截屏我的屏保怎么办？



彭曲波

Oct 15, 11:35 AM

有没有办法设定一下优先级，然后有一些任务只是因为闲逛或者摸鱼产生的[Facepalm]

9 thread replies

汪文皓

Oct 15, 11:35 AM

哈哈哈哈哈

Baite Huang

Oct 15, 11:35 AM

目前的一个想法是，让你输入职业以及当前的工作重心，做一个约束。

汪文皓

Oct 15, 11:36 AM

<cite type="user" user-id="ou_83298d44e2c40eb1ba8e39618d812d69"></cite> 将职业补充到提示词中吗？

Baite Huang

Oct 15, 11:36 AM

<cite type="user" user-id="ou_11d531388d728efa19076b40260d676c"></cite> 是的，会更个性化一些，在引导中让用户输入职业和阶段性目标，然后也支持settings修改

汪文皓

Oct 15, 11:37 AM

<cite type="user" user-id="ou_83298d44e2c40eb1ba8e39618d812d69"></cite> 什么时候会上啊

Baite Huang

Oct 15, 11:37 AM

下周吧

Nacho

Oct 15, 11:40 AM

哈哈哈笑死，试用以后本来想和团队分享的，结果一样发现截了好多摸鱼的图[Enough]；





关于“屏幕截图”的本地存储空间占用问题。

之前用过类似的产品，本地磁盘的可用空间快速的被蚕食。

不知咱MineContext是否有本地存储占用统计和清理的功能，我有些PTED了（Post-Traumatic Embitterment Disorder）。

View earlier 4 replies

王辰辰@Haojie Qin 你看，锁屏还是会截图的。[Image]

Haojie Qin@王辰辰 这个是屏保期间，下个版本修复了

灵太@Haojie Qin 做个设置呗，我是收集狂，喜欢会看过去几年的某天在做什么。我有大硬盘可以存储图片的

Haojie Qin@灵太 好的，我们会增加这个选项

王辰辰@Haojie Qin 别忘了存储路径，最好也可以自定义。

息屏状态下还是会录屏并消耗 token 吗？

昨天到现在都没用电脑，然后刚刚一看发现耗掉了 6 百多万的 token。。。。

View earlier 5 replies

王辰辰[Image]仅一天的Tokens消耗量，恐怖如斯。

Haojie Qin@王辰辰 图片转成 base64 编码会比较消耗token

王辰辰





王辰辰

一天没管，给我生成了超过一百多条的海量Todo，麻了……

里面有很多Todo属于文字不完全相同，但意思差不多的待办事项。

Haojie Qin感觉是走到截到todo->生成todo了，我优化下

邓岳州这种上下文方式不优化的话，最终会生成一堆垃圾，都懒得去看了

邓岳州关键是还太消耗token

乐臣@邓岳州 +1 以前 2 个屏幕 一天 todo 20 多个， 今天我 0.1.1 版本 几十个了没法看了





汪文皓

todo list 左边的圆点会根据不同的 todo 内容显示的居中位置。但是一个列表里面有很多是我做完的，或者识别有出入的。我鼠标不能放在一个位置一直点掉它。建议：是否可以将圆点保持在这一条的第一行文字的左边。



Jay Dang

能不能尝试往Rize那样的screen time监控的方向做呢，我周围的人都非常在意个人效率，会定期检查并调整自己时间分配的方式。感觉这个完全就是上位替代，能分的更细更准



Jay Dang

Oct 23, 4:46 PM

能不能尝试往Rize那样的screen time监控的方向做呢，我周围的人都非常在意个人效率，会定期检查并调整自己时间分配的方式。感觉这个完全就是上位替代，能分的更细更准

 

8 thread replies

Baite Huang

Oct 23, 4:47 PM

我们调研看看

岳雯楠

Oct 24, 1:45 PM

<cite type="user" user-id="ou_e2ff080ac1f8766ccfa897ee0aa659cf"></cite> 被安利了,谢谢

six-6

Oct 27, 2:20 PM

差不多，我以前用的是ActivityWatch，发现MineContext能看的更清楚。可惜token消耗太大，家里没有高级显卡跑本地vlm

Baite Huang

Oct 27, 2:21 PM

<cite type="user" user-id="ou_c3f656e2817d9fb4cb9e764e572e159f"></cite> token的成本其实应该还好，doubao-flash，0.15元/百万token

灵太

Oct 29, 2:46 PM

<cite type="user" user-id="ou_e2ff080ac1f8766ccfa897ee0aa659cf"></cite> 我是用的是ManicTime，现在正在希望能使用这个替代掉ManicTime

Jay Dang

Oct 29, 2:48 PM

 <cite type="user" user-id="ou_400b88150644635f844396c09870d8db"></cite> 我感觉这个潜力蛮大的，上一代软件的问题是只能追溯到app name，但是app内的use case不能细分

Baite Huang

Oct 29, 2:50 PM

可以多帮我们提提建议来着，比如更可视化的总结，提到github的feature上

Jay Dang

Oct 29, 2:53 PM

主要看这个项目的目标吧 毕竟是字节的项目组哈哈哈



黄子榕

大佬，我这里提一个功能建议，未来能否打通飞书云文档，把每日日志自动同步到云文档里？可以方便搭建个人知识库，做知识问答，省了手动去粘贴的事。



![](https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=MTk2OWNjNTAzYjVhMzU1YzQ0Y2IzYzFlNTExNGViODdfMTEzMDE3YzQzYWE5MGRlZmUxYzg4YjhiNjdhNmM2MjhfSUQ6NzU4MDI2NzUyNTAxMTc3MDkwMV8xNzc5MDkwOTc5OjE3NzkwOTQ1NzlfVjM)

【用户建议】参考iOS闹钟设计的录屏时间：每一天的开始时间和结束时间都可以调整。这样比如每周五有固定的组会，所以每周五下午我是知道我要开1小时组会的，所以我不需要MineContext告诉我这周/今天我花了多少时间开组会，我单独可以把周五的录屏时间缩短。我需要的是MineContext告诉我我无意识中花了多久时间摸鱼，花了多久时间看paper，花了多久时间debug。



请问后续会考虑出手机端app吗？也很想了解自己用手机都在做些什么[Pleading]如果能和pc端联动就更好了～



想问下为啥**Daily Report**里面的**时间线回顾**完全是错误的呀？没有按照真实的时间线梳理

Ruishu Qin更像是把一天做的事情套在了上午、下午、晚上几个时间段内

Haojie Qin和activity对不上吗

Haojie Qin用的什么模型

Ruishu Qin@Haojie Qin Doubao

建议截图自动隐藏桌面壁纸和桌面文件，以提高识别准确度



有没有计划做更深层的 insight，比如图片 ocr 以及对于内容的 deep research 等

Baite Huang：内容的deep research 会有的，OCR感觉必要性一般



目前有部分内容只是刚好在操作时被截到了。但不是核心内容就会被总结进去。考虑加上时间聚合一下嘛。



最近两天的token消耗量都在1800w左右，是不是有点多，然后一天就能消耗10块钱，然后看了火山引擎发现是这个32k以内推理（输出）消耗了挺多，花费了8元左右，有什么原因会导致这个吗；





大家好,请问字节跳动内部有没有AI辅助工具可以创建聊天助手?希望在有新消息时,不用打开个别聊天记录逐条阅读,就能自动标记出需要回复的消息,并总结飞书聊天中的关键信息。我试过Screen Monitor,但它似乎不支持这个功能。





这....我是默认的，然后我看才几个小时就消耗了100W这正常吗[Facepalm]

傅雅真：明白，那说可以自己调整提示词，是要咋整呀，对应是不是可以弄一个本地的知识库啊



孙啸宇minecontext生成的每日报告，可以导出吗，本地能找到吗

Baite Huang可以的，可以打开localhost:1733找到，然后复制就行



是否有考虑过加入ActivityWatch的数据，这个是我二次开发的效果，prompt还没有优化到特别好

生成日报时遇到一些问题：

使用1.6-flash，prompt过大导致上下文溢出，实际效果不好

切换1.5-vision-pro，上下文大小应该更大了所以解决了问题，但是不支持agent聊天

![](https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=NTA2YzE3OWIzN2RhMzQ0NWI2NzFjYzcxZmJjOWU4ODJfMjUxMDMwMzM4NzM2OTg5OWRjOTZmNjIyNjhhNDQyNTZfSUQ6NzU4MDI2OTEyOTM2MjQ3NjU2M18xNzc5MDkwOTc5OjE3NzkwOTQ1NzlfVjM)

提几个我遇到的问题，我的运行环境是ubuntu，打包遇到问题，所以是开发环境使用的（但这不重要）

如果是开发环境才有的问题或者兼容性问题，我觉得不重要\~

 

1. 删除日报后，刷新又回来了（feed同理）
2. 设置了api_key，重启又要再次设置
3. 实际生成的TODO不太准确，即使我接入了ActivityWatch的数据

 

未来有无规划：

1. 手动生成TODO、调整优先级，甚至附加自己的业务字段（比如预估耗时）
2. 支持更多用户定制化功能，比如写一段prompt让MineContext在什么情况下主动提示什么内容 如主动提示“已经在某件事情上耗费时间超过预期”