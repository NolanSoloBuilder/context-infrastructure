<!-- lark-mirror obj_token=IU8xdANaRoFDwyxWf56jzX4mpeh space=产品调研 synced=2026-05-18T07:54:44Z -->

# chat链路



设计重点在于：

**在对话中嵌入交互组件 (In-chat Components)：** 让用户在不离开聊天界面的情况下完成复杂配置。

**明确的工具选择 (Explicit Tool Selection)：** 将 AI 的分析能力具象化为用户可勾选的“工具”。

**主动反馈 (Proactive Feedback)：** 每一步都让用户感受到助手的智能和下一步的清晰。





### Chat 中的“频道创建”链路逻辑



#### **第一步：身份/目标识别**

- **用户：** “我想追踪 Apple 和 Tesla。”
- **AI (主动识别)：** “没问题！我发现你比较关注这两家的**财务表现**和**市场口碑**，你是以**投资者**还是**科技爱好者**的视角来追踪？”
- **用户点击按钮：** `[ 投资者 ]`

#### **第二步：Tools 勾选与信源确认 (核心 UI 组件)，作为情报维度预览（Insight Dimensioning）**

AI 发送一个组合卡片，用户不需要打字，直接勾选：

> **AI:** “已为你匹配**投资情报包**。请勾选你希望我激活的‘情报工具’：”

- **信源区：** 自动填入 `Apple IR`, `Tesla Investor Relations`, `SEC RSS Feed`。
- **样式：** 带有图标和简单描述的 Toggle 开关。**交互：** 用户点击开启/关闭，体现“自定义助手”的掌控感。
- **工具区 (Tools)：** \* [Checked] `财报解读` (AI 自动生成财报季 Summaries)

  - [Unchecked] `异动预警` (股价或高管减持主动通知)
  - [Checked] `解读官` (将晦涩的官方通告翻译成大白话)

#### **第三步：频道生成 (The Channel Creation)**

- **AI:** “配置完成！你的\*\*‘Apple & Tesla 投资内参’\*\*频道已建立。由于明天有 Apple 的财报会议，我已预设了自动追踪任务。”
- **UI 动作：** 对话框收起，界面下方滑出一个**频道预览入口**。



### 动态 Tools 列表配置表

系统会根据对话中识别的人群标签，自动调取对应的“工具卡片”供用户勾选：

<sheet sheet-id="ewAwdw" token="AzLosB5DvhmNgHtsBsejP3OcpwN"></sheet>

导出到 Google 表格



![](https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=NTEzNGEwZDNlNzljMWYxYzEwN2ZiZTE0MDg0OGMyZGFfZTFhMzE5ZGZjY2QwZWYwNTIzN2UxZTU5OGJmOWE1MWFfSUQ6NzU5MzYzNDE2MjMzMDg5Nzk0MF8xNzc5MDkxMDE4OjE3NzkwOTQ2MThfVjM)