<!-- lark-mirror obj_token=SQBudoIrGoKkhEx0FpDjgrcppIf space=产品调研 synced=2026-05-18T07:54:44Z -->

<title>PRD_卡片落地页（可交互阅读器）</title>



# 一、 版本日志

| **时间** | **版本号** | **负责人** | 研发 | **更新/提示** |
|-|-|-|-|-|
| Nov/9/2025 | V1.0 | 吴曦 | Evan，徐昊 | 待确认：是否可通过合辑溯源，订阅该内容源？ |

# 二、功能概述

本阅读器是用户从首页点击任一合辑卡片后进入的落地页。其核心目标是提供一个沉浸式、可交互且信息透明的阅读体验，使用户不仅能深入理解内容，还能主动探索信息背后的来源与细节。

# 三、规格详情



1. 顶部标题区

标题：显示合辑卡片的原标题。

阅读时长：以 `· X min read` 格式显示，例如 `· 8 min read`。

辅助操作 (MVP隐藏)：

在标题右侧预留图标位：收藏（♡）、分享（↗）。

MVP状态：图标可见但置灰，点击无响应，或点击后显示Toast提示：“此功能即将上线”。

1. Tab 1: 交互式总结

<grid><column width-ratio="0.800000"><p>此Tab为核心交互区，整合了AI总结与信息溯源。<ol><li>Tab 1: 扩展总结区块<ol><li>内容：展示比首页卡片简介更详细、结构化的AI总结。</li><li>格式：采用分段式文章或要点列表等易读格式。</li><li>核心交互1 - 对单个回答点赞点踩（MVP不做复制/转发）</li><li>核心交互2 - 溯源Tag：<ol><li>显示：在总结正文中，对于引用的关键事实、数据或观点，使用可点击的内容源标签。</li><li>tag要素：头像+名称（见示例）</li><li>交互：用户点击内容源标签后，从屏幕底部激活一个内容卡片半浮层，展示该段内容的原始出处详情。</li></ol></li><li>内容卡片半浮层 (溯源详情)<sheet sheet-id="WhfdQf" token="Fkg7spQ5ZhXkkotZPhOjuGW9pOd"></sheet></li></ol></li></ol></p></column><column width-ratio="0.200000"><img name="Screenshot 2025-11-09 at 3.52.57 PM.png" caption="Tab 1: AI总结（待更新）&#xA;" href="https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=MWQwZmI5YjQ4ODFiNzBmNjNiZDZiMmUwOGRjZjg0YzlfNjM0ZmNhNjViMzM1ZjVhN2NhNzgxYzk2M2Q5YzYyNDBfSUQ6NzU3MTIxNzA5MjQ1Njc0NjUxN18xNzc5MDkwODk0OjE3NzkwOTQ0OTRfVjM" mime="image/png" scale="0.613181" src="WtN3bUcMPokVL8x0mZljH0kEpjc"/><p></p><img name="image 42.png" caption="溯源tag&#xA;" href="https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=ZTMyNDY1MTk1Y2FkNWNhMmI3YjM0NDE3NzU3ZTA1NjBfMmQ5ODRkMDAwMGY3YThkYmNiZDA0M2RiMzNiYmMxMWFfSUQ6NzU3MTIxNzQ5NDQxMzc1Nzk3M18xNzc5MDkwODk0OjE3NzkwOTQ0OTRfVjM" mime="image/png" scale="1.313253" src="TkKvbWL7jo9KQgxXnzljTQzKpjh"/><p></p><img name="文章来源预览卡片.png" caption="内容卡片半浮层&#xA;" href="https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=MWQ4NzQ1YjFkNjVjMmFmYmYwNGFlZGE1YjBhOTVhMTFfN2UwNTk3ZTM0MzgwYzkxY2QwNzEyMzY1OWU2MjdkNDFfSUQ6NzU3MTIxNzkzMjQ5MjAwMDc4OV8xNzc5MDkwODk0OjE3NzkwOTQ0OTRfVjM" mime="image/png" scale="1.000000" src="GNbmbuKYKoEDdYxe5K4jBPxwpHd"/><p></p></column></grid>

<grid>
<column width-ratio="0.800000">
1. Tab 1: 对话探索区功能：支持用户就该合辑卡片的内容进行多轮追问。输入框：会话逻辑：对话的上下文必须严格限制在本合辑卡片所引用的源内容范围内，保证回答的准确性与信息不混淆。系统日志：用户的每一次追问与交互作为意图信号写入日志，用于优化未来的内容推荐。

   占位符文案：追问任何细节.. . 或 Ask me anything about this...

   功能：支持文本输入与语音输入.
</column>
<column width-ratio="0.200000">
![](https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=ZWFiZGQ5ZTcxMTM2OGE5NGJkYzdiM2Y0NmMzNjgzZThfMzBlODVmM2YwNDNmNTU3YjE2MWU4MzkxY2FlOTdkY2NfSUQ6NzU3MTIxODczNTY1MDg1MjM3Ml8xNzc5MDkwODk0OjE3NzkwOTQ0OTRfVjM)
</column>
</grid>

1. Tab 2: 信息溯源

   <grid>
   <column width-ratio="0.800000">
   - 内容：以简洁的列表形式，清晰展示生成本合辑摘要所引用的全部来源链接。
   - 列表项元素：
   
     - 来源图标/头像
     - 发布者名称
     - 内容标题
     - 来源域名
     - 订阅状态与操作区 （ + ）
   2. 交互
   - 交互1 (主要操作)：用户点击列表项的主体区域（如标题、域名），直接在系统浏览器中跳转至原文。
   - 交互2 (订阅操作)：
   
     - 状态显示：在每个列表项的右侧，显示用户的当前订阅状态。
     
       - 若未订阅，显示一个 “+” 按钮
       - 若已订阅，显示一个 “✓” 图标
     - 订阅动作：用户点击 “+” 按钮，即可将该来源一键加入订阅。按钮状态随即变为 “✓” 已订阅状态。
     - 交互反馈：成功订阅后，可伴随一个轻微的动画效果或Toast提示（如“已订阅 [发布者名称]”）。
   </column>
   <column width-ratio="0.200000">
   ![](https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=ZWRiNGQ3MmU2NDI3YmY2YjA0ZGQyNDE2YjM0YzA4YjRfMDQ3NjBmMzI0ZWQzNjgwMzdmMzA3NWEzYmZlMWM3YjRfSUQ6NzU3MTIxMjMwMDUwNjQ2Nzg1OV8xNzc5MDkwODk0OjE3NzkwOTQ0OTRfVjM)
   </column>
   </grid>