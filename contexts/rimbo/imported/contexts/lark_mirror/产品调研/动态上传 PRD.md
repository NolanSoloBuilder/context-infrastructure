<!-- lark-mirror obj_token=FG06dNagIojWd9xbx7tjFMUNpxg space=产品调研 synced=2026-05-18T07:54:44Z -->

# 动态上传 PRD

**在对话中嵌入交互组件 (In-chat Components)：** 让用户在不离开聊天界面的情况下完成复杂配置。

**明确的工具选择 (Explicit Tool Selection)：** 将 AI 的分析能力具象化为用户可勾选的“工具”。

**主动反馈 (Proactive Feedback)：** 每一步都让用户感受到助手的智能和下一步的清晰。







## 上传文件

上传文件跳转：

![](https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=NTIyZWY0MzJkYzViOGMwZmMyZjBkM2I4N2MxZDViMzBfMWUwMWI3NmFkZWE0ZjFmYTlhMDQ2NmMyNGJiODBkYWJfSUQ6NzYzMzM0OTE5MjUxMzYwNTE0Nl8xNzc5MDkwOTg1OjE3NzkwOTQ1ODVfVjM)

### **业务逻辑**

**用途1：单次分析（Ad-hoc Analysis）** 用户上传一份文件，Rimbo 对这份文件做一次性分析，结果直接输出在对话里。不进入信源列表，不持续追踪。

> 例：上传一份 Earnings Call PDF → Rimbo 结合channel里的信息分析→ 输出分析结果

**用途2：丰富用户画像（Profile Enrichment）** 用户上传关注实体相关的文件（公司资料、投资组合、关注列表），Rimbo 提取其中的实体信息，丰富用户的关注对象数据库，影响后续所有 Brief 的个性化程度。

**用途3：未来用户的知识库建设** 用户上传的所有文件随时间积累，形成个人知识资产。Rimbo 将这些文件的提取内容与历史 Brief、用户标注的信号结合，逐步构建用户专属的知识图谱，使后续分析越来越精准。

支持格式

| **格式** | **类型** | **信源层级** | **处理说明** |
|-|-|-|-|
| PDF | 文档 | 一手 | 全文提取后直接输出分析结果；或提取其中的公司/人物实体丰富关注列表 |
| Word (.docx) | 文档 | 一手 | 文本+结构提取；适用于内部备忘录、访谈文字稿的一次性深度分析 |
| TXT / Markdown | 文档 | 一手 | 纯文本接入；适用于 Notion 导出的关注列表、投资组合记录 |
| MP3 / MP4 / M4A | 音视频 | 一手 | Whisper 转录后输出分析结果；不持续存储，分析完即用 |
| YouTube 链接 | 视频链接 | 聚合 | 自动提取字幕后分析；适用于公开访谈、会议演讲 |
| XLSX / CSV | 数据文件 | 一手 | 提取实体数据（公司名/人物/赛道）写入用户关注列表，影响后续所有 Brief |

### 上传流程

用户上传文件

      ↓

系统识别内容类型

      ↓

      ├── 分析性内容（Earnings Call / 访谈 / 报告）

      │   → 直接进入分析流程

      │   → 结合当前频道的信息分析

      │   → 结果输出在对话里

      │   → 不持续存储

      │

      **├── 结构化实体数据（关注列表 / 投资组合 / CSV）**

      **│   → 提示用户：是否将实体加入关注列表？**

      **│   → 用户确认后写入画像**

      **│   → 影响后续所有 Brief 个性化**

      **│**

      **└── 知识类内容（笔记 / 研究报告 / 行业文档）**

          **→ 写入用户知识库**

          **→ 与历史 Brief 和信号关联**

          **→ 持续影响分析深度**

**后面两点先不考虑**



### 限制与错误处理

| **限制项** | **限制值** | **错误行为** |
|-|-|-|
| 最大文件大小 | 每个文件 50MB | 显示错误：「文件超过 50MB，请压缩或拆分文档。」 |
| 音视频时长 | 最长 4 小时 | 显示错误并提供上传前剪切选项 |
| 不支持的格式 | 任何未列出的类型 | 显示支持格式列表；提供格式转换指引 |
| 提取失败 | 扫描版 PDF / 损坏文件 | 标记为「提取失败——需人工审查」；不允许静默跳过 |
| 语言 | 非英文内容 | 处理并标注语言；Brief 以用户界面语言生成 |

### 过程状态定义

| **状态** | **用户可见标签** | **说明** |
|-|-|-|
| 上传中 | 上传中... | 文件 >1MB 时显示进度条 |
| 提取中 | 正在提取内容 | PDF / 音频处理阶段显示 |
| 索引中 | 正在索引信号 | 内容正在与频道实体进行比对分析 |
| 就绪 | 信源已激活 | 信源已上线，将纳入下一次   Brief 生成 |
| 失败 | 处理失败 | 显示具体错误 + 建议解决方案 + 重试选项 |
| 部分完成 | 部分处理完成 | 已提取部分内容；向用户展示已提取和未提取的内容 |

### 参考图

![](https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=ODU4ZmQ2YTZlY2ViZjczY2Q4NDUwYjVkODNhZWNlYWRfMGMxZjUzODUzNDI5ODk1YzVlZDViNzc0M2Y3MWViZDVfSUQ6NzYzMzM0MjIzMTkyNzE2NDQ0Ml8xNzc5MDkwOTg1OjE3NzkwOTQ1ODVfVjM)

## 信源全局添加

跳转信源管理页面——点击右上角的add your source——选择具体的source来源

![](https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=NjRkOTQwOTVhZGM2ZjgwOGJkMzlmODVkNzA5NWQxYTBfODc4Y2RkODUyYTcwNTgxZDE4MmY0ZmI1NzE2YWI5YjNfSUQ6NzYzMzM3ODgyMzQ5MjUwNTExMV8xNzc5MDkwOTg1OjE3NzkwOTQ1ODVfVjM)

![](https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=NGE5NzYzZjRiYmIyZjBiYTI3MmJmOTMyZGJlZjFmZDZfMGUyMzVjY2M1NzYzODY3ZTlkMjRiOTczZTM1NjQ5ZjVfSUQ6NzYzMzM3ODg4NzkxNzE5NDc3NV8xNzc5MDkwOTg1OjE3NzkwOTQ1ODVfVjM)

## 信源局部添加

目前先实现的：

![](https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=YzcwZGI4NzQ1ZDFjZjZmZTZmN2U1NTliZGUwMDJhMmJfMzI0NjgxMWVkNzNkMjVjMDIyMzIwYTdiOTZiY2JjNGJfSUQ6NzYzMzM3NDIwNTkzODg4MDAyM18xNzc5MDkwOTg1OjE3NzkwOTQ1ODVfVjM)



未来希望实现的理想态：

<grid>
<column width-ratio="0.500000">
![](https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=N2IyN2M1MTExY2UzODJjNGY0NGQ3OGMzNDU2MDBhYmNfZjUxZThlNjNiMDlkNjg3ZmJjYzJjYjk3NTYwN2MyYWRfSUQ6NzYzMzM1NjA2ODc1NTcyMTc1MV8xNzc5MDkwOTg1OjE3NzkwOTQ1ODVfVjM)
</column>
<column width-ratio="0.500000">
![](https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=MzRkM2QxZmFmMzMzOWJiYjE2MmVkOTQ1ODQ2Yjc2MTRfOWRjN2M1MDI0OGQ3NmY4OWM2ODA1NDk4NDc5MTZjMWRfSUQ6NzYzMzM1NjE4NzA3NzI2Njk2N18xNzc5MDkwOTg1OjE3NzkwOTQ1ODVfVjM)
</column>
</grid>

<grid>
<column width-ratio="0.500000">
![](https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=ZTg1ZGVhNWJlYTI0YTJjNjNiYWY5YTVkNmYxZjU4MDdfNDRlNzMyM2U3ZDYxOTYwMDRkZTJjZDExMDFlNGVmMDFfSUQ6NzYzMzM1NjI2ODY4MDgxMDAwOF8xNzc5MDkwOTg1OjE3NzkwOTQ1ODVfVjM)
</column>
<column width-ratio="0.500000">
![](https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=OThiODI0ZGI4ZWM0ZWFkMGFjZTQ0YzhmNGM5NDNkZGJfZjJhNmQ1NGM2YjkzYmRiM2NhZmNmZTY3NzBhNWE0MDJfSUQ6NzYzMzM1NjI4NTg2MTQ5ODM5NF8xNzc5MDkwOTg1OjE3NzkwOTQ1ODVfVjM)
</column>
</grid>