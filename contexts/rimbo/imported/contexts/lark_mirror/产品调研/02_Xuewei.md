<!-- lark-mirror obj_token=Kxb1dXxVCoReOuxNQuHjC3a4pkd space=产品调研 synced=2026-05-18T07:54:44Z -->

# 02_Xuewei

邮箱标注：<cite doc-id="Bt2GwAazYiCwx8kDsSOjd17Jp1d" file-type="wiki" title="原始数据标注_Gmail" token="AbAMsJJuphKkalt3usWjZWGrped" type="doc"></cite>

访谈Transcript：https://lxblog.com/efficiency/U/xnvvPMC9BdqM9dIF5aYTGOBrtSyb2JzX



## 一、个性化兴趣标签的识别

### 洞察：

用户对“个性化兴趣”的判断主要基于发件人身份、内容主题和历史互动行为，而非单纯的关键词或邮件类型。

### 证据与引用：

1. 技术类内容（如ByteByteGo、NVIDIA）

   - 用户表示：“*是技术类的文章，找工作期间会看的更多。现在不在找工期所以不需要，但是也不会退订，以防以后需要。*”（CSV条目：ByteByteGo）
   - 反映兴趣：是；订阅意图：否。
2. 深度博客/个人观点类（如Moontower、Opinion newsletter）

   - 用户说：“*以前看，现在不怎么看。感觉大部分的内容对自己没什么用。但是会保存以防未来需要，因为认可这个发布者的质量。*”（CSV条目：Moontower）
   - 反映兴趣：是；订阅意图：是（但阅读频率低）。
3. 新闻类（如WSJ 10-Point）

   - 用户解释：“*不会在手机上阅读：因为新闻字很多，大部分新闻不感兴趣；会在PC端直接上网站看自己关心的板块。*”（CSV条目：WSJ 10-Point）
   - 反映兴趣：是；订阅意图：是（但阅读方式不同）。
4. 特定服务/产品相关（如Planit摄影App）

   - 用户提到：“*能反映是这个产品的购买者。*”（CSV条目：Apple交易确认）
   - 反映兴趣：是；订阅意图：否。

---

## 二、订阅意图的判别机制

### 洞察：

用户的“订阅意图”不仅体现在是否订阅，更体现在是否主动阅读、是否保留以备未来使用，以及是否通过标签或归档进行分类管理。

### 证据与引用：

1. “保留但不阅读”的情形

   - 用户说：“*有些内容我不想看，但我觉得他的内容本身质量你是认可的，所以就是把它保留着。*”（Transcript P19）
   - 对应邮件：Moontower、ByteByteGo。
2. “标记为重要或星标”的行为

   - 用户提到：“*我会用star，star其实就是优先级最高的那一类。*”（Transcript P5）
   - 说明star用于标记高优先级内容，反映强烈订阅意图。
3. “通过规则自动加label”

   - 用户说：“*我会写一些邮件规则，比如谁谁谁发的，或者是谁提到什么东西，就自动添加label。*”（Transcript P6）
   - 说明用户对某些发件人或主题有持续关注意图。
4. “不在邮件中阅读，但会去官网”

   - 用户表示：“*新闻类的会倾向于直接去官网。*”（Transcript P14）
   - 说明即使不通过邮件阅读，仍存在订阅意图。

---

## 三、噪音与低价值内容的识别

### 洞察：

“噪音”主要来自通用促销、重复性通知、历史遗留订阅和钓鱼/诈骗邮件。

### 证据与引用：

1. 通用促销类

   - 如ZIPAIR、Southwest Airlines、Best Buy等，用户标注为“否”反映兴趣和订阅意图。
   - 用户说：“*广告或者我不想看的内容，就直接删掉。*”（Transcript P3）
2. 系统通知类

   - 如USPS Informed Delivery、CARFAX、Kaiser Permanente，用户标注为“否”，并解释为“通用服务的购买”。
   - 用户行为：“*每每一个都会打开，但看完就删或archive。*”（Transcript P2）
3. 钓鱼/诈骗邮件

   - 如Hyperliquid，用户明确指出：“*地址可疑，是钓鱼邮件，不会打开。*”（Transcript P28）
   - 说明用户对发件人身份敏感，能识别非可信来源。
4. 历史遗留订阅

   - 如Day One、某些Event invitation，用户表示：“*以前用过/参加过，现在不用了，但还是会收到。*”
   - 这类邮件虽曾反映兴趣，但当前已无价值。