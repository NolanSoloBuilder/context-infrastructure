<!-- lark-mirror obj_token=UQeOdKN5konxoWxBL3BjtxAfp2c space=产品调研 synced=2026-05-18T07:54:44Z -->

<title>PRD_意图收集功能</title>

# 一、 版本日志

| **时间** | **版本号** | **负责人** | 研发 | **更新内容** |
|-|-|-|-|-|
| Nov/10/2025 | V1.0 | 吴曦 | Evan，徐昊 |  |

# 二、功能概述

提供一个统一的意图输入入口，允许用户随时表达他们希望系统为其追踪或探索的新兴话题或特定信源。该系统将智能判断用户意图类型，并提供确认反馈，以此驱动内容推荐的持续个性化。

# 三、详细规格说明



1.  信息流输入框 (首页信息流触发入口)

<sheet sheet-id="VLIKga" token="D5lysJyhGheFaytvi4xjxziupkc"></sheet>

1. 意图输入界面

<grid><column width-ratio="0.856098"><sheet sheet-id="37e6dM" token="D5lysJyhGheFaytvi4xjxziupkc"></sheet></column><column width-ratio="0.143902"><img name="智能订阅界面.png" caption="意图输入界面&#xA;" href="https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=YmY2NGUwMGY2MTE5ZDU3OGJmZDcxNTVjOGU2ZGFmYjRfOWY4ZGZjNWE0NGM3NDE0YWVmNjg3OWE5N2Q1YTYxY2NfSUQ6NzU3MTIyMjc2NzM0MTY2OTkwOV8xNzc5MDkwODk3OjE3NzkwOTQ0OTdfVjM" mime="image/png" scale="0.287179" src="Mw9Vb7CjvoD0cQxT5j5jBpNEpae"/><p></p></column></grid>



1. 系统处理与反馈逻辑

3.1 意图分类与反馈

系统需对用户输入的文本进行实时判断，并将其分类，随后在UI上给予对应的Toast反馈。

<sheet sheet-id="9AlkbH" token="D5lysJyhGheFaytvi4xjxziupkc"></sheet>

3.2 会话与上下文管理

多次提交：在同一会话（意图输入界面未关闭）中，允许用户连续提交多个意图。

上下文判断：系统需判断新一轮输入是对上一个意图的补充（如："especially in healthcare"）还是一个全新的意图。

补充意图：应合并到上一个意图中进行处理。

全新意图：应作为独立的意图请求处理，并刷新输入框。