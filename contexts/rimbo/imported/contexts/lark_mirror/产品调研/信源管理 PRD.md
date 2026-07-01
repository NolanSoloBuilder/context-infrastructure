<!-- lark-mirror obj_token=WfhTdHrUYoklujxjfyMjc5WDp3c space=产品调研 synced=2026-05-18T07:54:44Z -->

<title>信源管理 PRD</title>

# **基本信息**

| **时间** | **版本号** | **负责人** | **更新内容** |
|-|-|-|-|
| 2026/05/08 | V1.0 | coco | 信源管理功能（RSS上传、推特信源、动态管理面板） |

# 信源管理架构与交互逻辑 

1. 信源管理界面与入口

双层管理架构确立：确立“全局信源库”与“频道内局部信源管理”的双层结构。全局信源管理作为四大核心入口之一（首页频道、Skills、信源管理、知识库），频道内添加信源采用弹窗形式，全局信源管理采用独立页面形式。

1. 账号授权与信源原子化

账号解构为原子信源：推翻了将账号（如 Twitter、YouTube）整体打包的逻辑，决定将账号授权解构为原子化信源。即用户授权后，系统自动将其关注列表或频道列表拆解为独立的信源条目，以便 Agent 进行精细化利用。

信源标准化处理：明确所有信源（RSS、Podcast、YouTube、Twitter）最终均转化为标准化的数据结构进行交互，以确保底层处理逻辑的一致性。



# **功能清单**

| **功能模块** | **功能点** | **简要说明** |
|-|-|-|
| 侧边栏 | 连接更多自有信源 | Connect your sources 面板，支持 X / YouTube / GitHub / Gmail OAuth 授权，账号解构为原子化信源 |
| 侧边栏 | 全局信源管理 | 侧边栏「信源」入口，展示所有信源，支持搜索、Pin to top、Delete |
| 侧边栏 | 全局RSS / Podcast / YouTube 格式信源添加 | 粘贴 URL 解析添加，支持自定义标题，导入后归入 Customised 分类 |
| 侧边栏 | 导入 OPML | 粘贴 OPML 文件内容批量导入，导入后归入 Customised 分类 |
| 侧边栏 | 导出 OPML | 导出全部信源为 OPML 文件，文件名含日期 |
| 频道内 | 频道内信源管理和添加 | +N sources 入口，Add your source / List 两个 tab，支持搜索添加和 Pin to top / Delete管理操作 |

红色为还未在预览图上实现的功能

<table><colgroup><col/><col/><col/></colgroup><tbody><tr><td>功能模块</td><td>预览图</td><td>说明</td></tr><tr><td>侧边栏 </td><td><img name="image.png" href="https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=NzE5NjA5Y2NkNjdjOTFmM2U2MTliZTE0YmZiMmEwM2VfMjQ4NDNkYjI5YmQyYTUwNzJlNDllZjJjYWJiZjA4OTJfSUQ6NzYzNzc4MjkxMjU1MjY2ODY5OF8xNzc5MDkxMDMxOjE3NzkwOTQ2MzFfVjM" mime="image/png" scale="1.000000" src="FTUSb9qy2oef1vxfqSOjTP1Wpie"/><img name="image.png" href="https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=MzQ0NjQ5MDExYjUyZDYzNmUwYzc4NzE4YWRjN2IxMGFfMzdkMzJjMzhkMWI5YTNkNTFjZWUwZmE3YzEzM2JlOTJfSUQ6NzYzNzQ2ODY0MjYwMjc4MjIzMV8xNzc5MDkxMDMxOjE3NzkwOTQ2MzFfVjM" mime="image/png" scale="1.000000" src="KSQobaEvOoFvEUxLgNijJH0hp1f"/></td><td><ol><li><b>接入自有信源</b><ul><li>入口为侧边栏connect your source，点击跳转弹窗 </li><li>每一条信源显示分为两种状态：<ul><li> 已连接：右侧蓝色实心圆点 ●，已连接信源不重复展示授权入口，仅展示已连接状态</li><li> 未连接，点击进入 OAuth 流程</li></ul></li><li>将账号授权解构为原子化信源。即用户授权后，系统自动将其关注列表或频道列表拆解为独立的信源条目</li></ul></li></ol></td></tr><tr><td><b> </b><br/>侧边栏</td><td><img name="image.png" href="https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=MTFkMDgwZjVlZWRkZDI1NTk4MTE4ZjJiMGY3YTdmMGRfYjBkZGVhZjM4OTZjYjMwNjk3NTcyN2YyMjA3NTJiN2FfSUQ6NzYzNzc2OTU1NTY3MDEyNjEwM18xNzc5MDkxMDMxOjE3NzkwOTQ2MzFfVjM" mime="image/png" scale="1.000000" src="RzgGb2pjSo1t3wxX4PrjZSdRpqd"/></td><td><ol><li><b>“我的信源”面板（全局信源管理面板）</b><ul><li>页面标题：Source management，副标题：添加、管理、导入和导出你希望 Rimbo 追踪的信源。</li><li>操作按钮三个：「+ 添加信源」/ 「导入 OPML」/ 「导出 OPML」。</li><li>Tab 两个：「List」（默认选中）/ 「Discover」。</li><li>按照信源层级分类展示全局所有信源，customize为 用户自己添加的信源，每条信源展示：图标、名称、标签（source_type 和 Source_origin)，但是要根据用户特点展示最相关的信源</li><li>每条信源支持以下2种操作：<b>Pin to top</b>：该信源优先展示在频道和 chat 结果中，Delete：删除信源，不再展示，不可恢复。以上状态可随时切换，实时生效</li><li>搜索框：按名称或URL 搜索，右侧有搜索按钮。搜索范围为 Rimbo 内部信源库（非全网抓取），匹配字段为信源名称和 URL。搜索结果如下：<ul><li>返回匹配结果列表展示在下方，替代下面本来的陈列页面，展示格式同下，可进行相同操作</li><li>搜索返回结果为空时，提示文案：「Rimbo 信源库中未找到相关信源，请点击「添加信源」手动添加。」</li></ul></li></ul></li></ol></td></tr><tr><td>侧边栏</td><td><img name="image.png" href="https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=ZjBjNzVkYzg4NzQ2NmI2ZDhiZTNmN2VkMDgyNmE1ZTVfYWNkZDk1OWVjYWY2ZTA3MjhiZTkyNDk5OTNkZjViMzhfSUQ6NzYzNzczMzU4MzM4NTQxNTE5NF8xNzc5MDkxMDMxOjE3NzkwOTQ2MzFfVjM" mime="image/png" scale="1.000000" src="MdjubTAHQoWy0dxkU4Ij8JOdpdh"/><br/>更多设置（折叠框）<img name="image.png" href="https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=NmNjNWJmMGUyNDBjMjZkZTAyOWRlNmVhMDIxNGM2MjRfNDhiNzBiYTA3ODRmZWVkM2I3OWI0MDg4ODllOTAyMmFfSUQ6NzYzNzc3MTMyNjc1NjkxNjc2Ml8xNzc5MDkxMDMxOjE3NzkwOTQ2MzFfVjM" mime="image/png" scale="1.000000" src="Tw6WblZB8oEQTMxLl6YjCwBUp6q"/><img name="image.png" href="https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=ODMwMTI4MDZiYTk2YzRkMzczZTc5NzNlODQyODY3MDFfNWNiYjRlZTNjZWM2YjA5ODY0ODM0M2U1OTY5MWZlYzJfSUQ6NzYzNzc3MTU4MDE1OTg4ODkyMF8xNzc5MDkxMDMxOjE3NzkwOTQ2MzFfVjM" mime="image/png" scale="1.000000" src="A28tb0rZDosGBWx7FH3jtC6dpQf"/><img name="image.png" href="https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=N2U5NWY5ZmZhMzcxMDFlZDc1OTliYWQxNTQwNjQzMjRfMDkwNTFlYzVjMGI0YzFkOWNiMWMyMGJmY2MxYTBlODJfSUQ6NzYzNzc3MTc1MTMyOTQxODc3NV8xNzc5MDkxMDMxOjE3NzkwOTQ2MzFfVjM" mime="image/png" scale="1.000000" src="QnqkbAx9xo081OxyGx9jSxIZpHb"/></td><td><ol><li><b>添加信源 按钮</b></li></ol><ul><li>页面标题：添加信源<ul><li>副标题：支持添加 RSS、播客或 YouTube 信源。</li><li>模块一：信源链接，<ul><li> 副标题：支持网站链接、RSS 、Podcast和 Youtube 频道。</li><li>placeholder 为 <code>https://example.com/feed.xml</code>，点击「解析」按钮后自动识别信源内容。</li><li>未输入时提示：请输入 feed URL（红色）</li><li>解析成功后右侧显示「最新内容：xxx」</li><li>无法解析时显示：*Source addition failed. Please check your URL.</li><li>确定导入后进入信源管理面板的 customise分类</li></ul></li><li>模块二：信源标题<ul><li>解析成功后「标题」字段自动填充信源标题</li><li>支持用户自定义输入信源标题</li></ul></li><li>模块三：更多设置（折叠）<ul><li>自动刷新间隔：为当前信源单独设置刷新频率，不影响全局设置。<ul><li>选项：<ul><li>从密到疏覆盖完整区间：5分钟 /  30分钟 / 1小时 / 2小时 / 6小时 / 12小时 / 24小时/自定义。</li><li>选择「自定义」后展开输入框，可手动填写数字并选择单位（分钟 / 小时 / 天）。</li><li>选择「使用全局设置」时，旁边标注当前全局实际值（如：当前 1小时），方便用户了解实际生效频率。</li></ul></li></ul></li><li>自动删除周期：控制单个信源的历史内容保留时长，超过设定时间的内容自动清理。<ul><li>选项：<ul><li>默认为 1个月。可选范围：关闭 / 1天 / 1周 / 1个月 / 3个月 / 自定义。</li><li>选择「自定义」后展开输入框，可手动填写数字并选择单位（天 / 周 / 月）。</li></ul></li></ul></li><li>最大保留单挑数：控制单个信源最多保存的内容数量，超出上限后自动移除最旧的条目。<ul><li>选项：<ul><li>默认为 50 items。可选范围：不限 / 10 / 25 / 50 / 100 / 200 items / 自定义。</li><li>选择「自定义」后展开输入框，可手动填写具体数量。</li><li>选择「不限」则不限制条数，配合自动删除周期使用。</li></ul></li></ul><p></p></li></ul></li></ul></li></ul></td></tr><tr><td>侧边栏</td><td><img name="image.png" href="https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=ZTRiZTc0YzBmZmJkMmJhODA2NDM0YzFkNDNhNDY3YjJfNTM3YWQ1NTkwZGRiZDQ4ZTg3MDU0Y2ZhNDZkMWRmYjZfSUQ6NzYzNzc4MDI1MjQ5MTc2MzIyNl8xNzc5MDkxMDMxOjE3NzkwOTQ2MzFfVjM" mime="image/png" scale="1.000000" src="TTOlbzOh3oJo4ExkKt5jWTFvpQf"/></td><td><ol><li>导入OPML<ul><li>副标题：粘贴从 RSS Dashboard 或其他阅读器导出的 OPML 文件内容。</li><li>无法导入时显示：*Source addition failed. Please check your OPML.</li><li>确定导入后进入信源管理面板的 customise分类</li></ul></li></ol></td></tr><tr><td>侧边栏</td><td>直接跳转下载</td><td><ol><li>导出OPML<ul><li>将当前所有已添加的 RSS 信源导出为 OPML 格式文件，可用于备份或迁移至其他 RSS 阅读器。</li><li>点击「导出 OPML」后直接下载文件，文件名默认为 <code>rimbo_feeds_[日期].opml</code>。导出内容包含所有信源的名称、链接、</li><li>导出范围为当前账号下的全部信源。</li></ul></li></ol></td></tr><tr><td>频道</td><td><img name="image.png" href="https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=ZWQyZjkwYjhmNTI2OTRmYjdiZDYzYTI4MDU3YjNiYmFfMTk0NTIwMjJkYzcxODA2MjU4NTVmZTA1OTUwODk2YjhfSUQ6NzYzNzc4ODI1Njg5MDYzNzg1MF8xNzc5MDkxMDMxOjE3NzkwOTQ2MzFfVjM" mime="image/png" scale="3.244444" src="CGvEb7vQ2oNoTjxRiwyj1oj4pwf"/><img name="image.png" href="https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=MmQ1N2UzM2M3MTI2YTkyZDQ1Mjc2ODEwYTQ1ZDNlZmJfZjhjNDk2OGY0MTE3MGZlNWQ3NTY0ZmNmMTc0NTY0MjVfSUQ6NzYzNzgwMDg2MTY4NjYzMTk2Ml8xNzc5MDkxMDMxOjE3NzkwOTQ2MzFfVjM" mime="image/png" scale="1.000000" src="OefubtN6EoHltkxDEsMj2xbypch"/></td><td><ol><li>频道内信源添加<ul><li>进入频道后，顶部显示当前频道已关联的信源头像列表，点击「+N sources」展开信源管理入口。</li><li>弹出「Add your source」面板，包含两个 tab：Add your source（当前）/ List。</li><li>Add your source 页面完全同上 只是针对范围 为频道内</li></ul></li></ol></td></tr><tr><td>频道</td><td><img name="image.png" href="https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=ZjVjNWU2ZjgyZDJkODQ4OThjZDEwYmE4ZTZiMmVmZDVfMTExZWExZmVmM2Y5NDFlOThkMWM3YWJjODU4ZmYyZWRfSUQ6NzYzNzc5NTcxMjk1MjAxMjMxNF8xNzc5MDkxMDMxOjE3NzkwOTQ2MzFfVjM" mime="image/png" scale="1.000000" src="U8DQbm1DjoaKm9xK4G3jEDMVptW"/></td><td><ol><li>频道内信源管理<ul><li>展示范围为channel内容的信源来源</li><li>每条信源展示：图标、名称、标签（source_type 和 Source_origin)</li><li>每条信源支持以下2种操作：<ul><li><b>Pin to Top</b>：该信源优先展示在频道和 chat 结果中</li><li>Delete：删除信源，不再展示，不可恢复</li><li>以上状态可随时切换，实时生效</li></ul></li></ul></li></ol></td></tr></tbody></table>

# 边界条件与异常处理

**边界条件与异常处理**

<sheet sheet-id="g53Vj6" token="AexksKzbyh3FTTtjGDSjsx1gpje"></sheet>



Sonnet 4.6