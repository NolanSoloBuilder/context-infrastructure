<!-- lark-mirror obj_token=DJMedwK9loaak4xx1LJj5HAupZb space=研发部门 synced=2026-05-18T07:53:01Z -->

# APP 验收测试步骤

## 核心测试场景

### 🔐 场景1: 认证与引导流程

**目标**: 确保新老用户都能顺利进入应用

#### 1.1 新用户完整流程

**步骤**:

1. 启动应用 → 看到登录页
2. 选择登录方式 (Apple/Google/Email)
3. 授权成功后 → 自动跳转到"设置用户名"页 [app/guide/name.tsx]
4. 输入用户名 → Next
5. 进入 Welcome 页 [app/guide/welcome.tsx]
6. Next → 进入 Onboarding 流程 [app/guide/onboarding.tsx]:

   - **Step 1**: 查看欢迎语 + 示例 → 输入目标 (如 "Track AI news")
   - **Step 2**: 查看AI回复 → 选择角色(至少1个) + 来源类型(可选)
   - **Step 3**: 查看推荐源列表 → 选择源(至少1个) → Create Channel
7. 显示"Creating..."加载状态
8. 后台轮询 `/channel/get_channel` (每10秒)
9. 检测到频道创建成功 → 跳转主页并显示庆祝动画

**预期结果**:

- ✅ 每个步骤都能正常跳转,无卡顿
- ✅ 必填项验证正确(用户名不能为空,Step2必须选角色,Step3必须选源)
- ✅ 轮询期间可以看到"Creating..."提示
- ✅ 创建成功后显示烟花🎉动画和"First Channel Celebration"提示
- ✅ 主页显示新创建的频道

#### 1.2 老用户登录

**步骤**:

1. 启动应用 → 初始化(`initializeApp()`)
2. 刷新用户信息 → 检测到已设置用户名且非新用户
3. 直接跳转主页

**预期结果**:

- ✅ 显示 SplashScreen 闪屏
- ✅ 初始化完成后直接进入主页,不经过引导流程
- ✅ 主页显示用户的所有频道

**关键代码位置**:

- 初始化逻辑: [store/useAuthStore.ts:131-162]
- 导航判断: [app/\_layout.tsx:39-59]

#### 1.3 登录异常处理

**测试用例**:

<sheet sheet-id="AhtaSK" token="KrImsPky2h7TWNt7w62jRY34pQh"></sheet>

---

### 📱 场景2: 主页功能

**目标**: 确保主页正确显示频道列表和更新

#### 2.1 主页加载

**步骤**:

1. 进入主页 [app/(drawer)/index.tsx]
2. 调用 `/channel/get_channel` API
3. 显示频道列表

**预期结果**:

- ✅ 首次加载显示骨架屏 [HomeSkeleton]
- ✅ 加载成功显示:

  - 顶部问候语 "Hi {username}!" + 总更新数
  - 频道卡片列表 (标题、更新数、来源图标、Brief要点)
  - 右下角"智能助手"浮动按钮
- ✅ 如果无数据,显示"No channels available"
- ✅ 如果出错,显示错误信息 + Retry按钮

#### 2.2 下拉刷新

**步骤**:

1. 主页下拉触发刷新
2. 重新调用 API

**预期结果**:

- ✅ 显示刷新动画
- ✅ 刷新成功后更新频道列表
- ✅ 3秒内不重复刷新 (防抖机制)

#### 2.3 页面焦点刷新

**步骤**:

1. 从其他页面返回主页

**预期结果**:

- ✅ 自动刷新频道列表(如果距离上次刷新>3秒)
- ✅ 首次进入不刷新(已在 useEffect 中加载)

#### 2.4 侧边栏抽屉

**步骤**:

1. 点击左上角菜单图标 或 从左侧边缘滑动
2. 打开抽屉侧边栏

**预期结果**:

- ✅ 平滑滑出抽屉(slide效果)
- ✅ 显示用户信息和导航菜单
- ✅ 点击遮罩层或返回键关闭

---

### 📺 场景3: 频道详情页

**目标**: 确保频道详情正确展示和交互

#### 3.1 进入频道详情

**步骤**:

1. 主页点击频道卡片
2. 路由到 `/channel/{id}` [app/channel/[id].tsx]
3. 调用以下API:

   - `/channel/detail` - 获取频道详情
   - `/channel/grouped-feeds` - 获取分组feeds
   - `/channel/item-objects` - 获取tab列表

**预期结果**:

- ✅ 显示加载骨架屏 [ChannelDetailSkeleton]
- ✅ 加载成功显示:

  - 频道标题 + LIVE状态 + 最后更新时间
  - 前5个来源图标 + "+ N Sources"按钮
  - **AI Brief** 区域 (信号摘要,每条包含 headline + detail)
  - 点赞/点踩按钮 + "Tailor Brief"按钮
  - Tab区域 (动态生成,从 item_objects)
  - Feed内容列表

#### 3.2 Tab切换

**步骤**:

1. 横向滚动Tab栏
2. 点击不同Tab
3. 加载对应Tab的内容

**预期结果**:

- ✅ Tab样式切换 (选中: 黑底白字, 未选中: 灰底黑字)
- ✅ 显示该Tab的 feed items
- ✅ 内容加载时显示骨架屏 [ChannelFeedListSkeleton]

#### 3.3 无限滚动加载更多

**步骤**:

1. 滚动到页面底部
2. 触发加载更多

**预期结果**:

- ✅ 距离底部100px时自动加载
- ✅ 显示加载骨架屏
- ✅ 追加新内容到列表末尾
- ✅ 如果无更多数据(next_cursor为空),不再加载

#### 3.4 点赞/点踩

**步骤**:

1. 点击点赞或点踩按钮
2. 调用 `/channel/{id}/like` 或 `/channel/{id}/dislike`

**预期结果**:

- ✅ 显示"Thanks for your feedback!" Toast
- ✅ 接口调用成功

#### 3.5 Tailor Brief定制

**步骤**:

1. 点击"Tailor Brief"按钮
2. 打开 [TailorBriefModal] 弹窗
3. 查看当前anchors (关键词)
4. 添加/删除anchors
5. 选择Style (Brief/Detail)
6. 点击"Apply Your Customization"

**预期结果**:

- ✅ 显示当前的anchors (从 `/channel/anchors` 获取)
- ✅ 可以删除单个anchor (DELETE `/channel/anchors?anchor=xxx`)
- ✅ 可以清空所有 (DELETE `/channel/anchors`)
- ✅ 提交成功后刷新频道详情,显示更新后的AI Brief
- ✅ 关闭弹窗

#### 3.6 Feed Item点击

**步骤**:

1. 点击Feed Item卡片

**预期结果**:

- ✅ 如果有 `item_id` 和 `source_id`,跳转到详情页 `/channel/item/{item_id}`
- ✅ 否则,在浏览器中打开 `item_url`

---

### 📄 场景4: 文章阅读页

**目标**: 确保文章阅读和聊天功能正常

#### 4.1 打开文章

**步骤**:

1. 从主页或频道详情点击文章卡片
2. 路由到 `/article/{id}` [app/article/[id].tsx]
3. 调用 `/card/get_article_detail` (如果未从路由传入数据)

**预期结果**:

- ✅ 显示加载骨架屏 [ArticleSkeleton]
- ✅ 显示文章标题 + 日期
- ✅ 显示两个Tab: "Easy Digest" (默认) 和 "N Sources"

**关键代码位置**: [app/article/[id].tsx:162-187]

#### 4.2 Easy Digest Tab

**步骤**:

1. 默认显示 Easy Digest Tab
2. 查看Markdown渲染的文章内容
3. 点击复制按钮

**预期结果**:

- ✅ 文章内容支持Markdown格式 (引用脚注 `[1]` 可点击)
- ✅ 点击复制显示"Copied successfully" Toast
- ✅ 底部显示聊天输入框
- ✅ 底部白色渐变背景

**关键代码位置**: [app/article/[id].tsx:242-323]

#### 4.3 与文章聊天

**步骤**:

1. Easy Digest Tab
2. 输入问题,如"总结这篇文章的要点"
3. 发送

**预期结果**:

- ✅ 创建或使用已有 `chat_session_id`
- ✅ 用户消息立即显示在对话区域
- ✅ 显示"打字中"动画 [TypingIndicator]
- ✅ AI回复流式显示 (SSE)
- ✅ 支持引用来源 (显示参考链接)
- ✅ 滚动到对话底部

**关键代码位置**:

- 聊天Hook: [hooks/useChat/useChat.ts]
- 消息气泡: [components/ui/chat/MessageBubble.tsx]

#### 4.4 Sources Tab

**步骤**:

1. 点击"N Sources" Tab
2. 查看文章来源列表

**预期结果**:

- ✅ 显示所有来源,包含:

  - 来源图标
  - 来源名称
  - 引用ID [1], [2]...
- ✅ 点击来源卡片在浏览器中打开
- ✅ 隐藏聊天输入框
- ✅ 隐藏白色渐变背景

**关键代码位置**: [app/article/[id].tsx:326-331]

#### 4.5 从历史会话跳转 (scroll_to_chat)

**步骤**:

1. 从聊天历史侧边栏点击 chat-card 类型的会话
2. 路由到文章页,携带参数 `scroll_to_chat=true` 和 `session_id`

**预期结果**:

- ✅ 自动切换到 Easy Digest Tab
- ✅ 加载历史对话消息
- ✅ 自动滚动到对话区域开始位置

**关键代码位置**: [app/article/[id].tsx:104-146]

---

### 🤖 场景5: AI助手 (Agent Chat)

**目标**: 确保AI助手聊天和工具调用正常

#### 5.1 打开AI助手

**步骤**:

1. 主页点击右下角"智能助手"浮动按钮
2. 路由到 `/chat/agent` [app/chat/agent.tsx]

**预期结果**:

- ✅ 显示问候语 "Hi, {username}!"
- ✅ 显示提示语 "What can I track for you?"
- ✅ 显示5个示例提示词按钮 (从 `/api/v1/example` 获取)
- ✅ 底部显示聊天输入框
- ✅ 右上角显示"历史"按钮

**关键代码位置**: [app/chat/agent.tsx:103-125]

#### 5.2 发送消息与工具调用

**步骤**:

1. 点击示例提示词 或 输入自定义消息
2. 发送

**预期结果**:

- ✅ 用户消息显示
- ✅ 如果AI需要调用工具 (如搜索、创建频道):

  - 显示工具调用加载动画 [ToolCallLoadingIndicator]
  - 动画显示工具名称,如"Searching sources..."
- ✅ 工具执行完成后,AI回复显示
- ✅ 如果AI提供选项 (user_choice),显示可点击按钮
- ✅ 消息支持Markdown渲染

#### 5.3 用户选择交互

**步骤**:

1. AI回复中显示选项按钮 (如 "Create Channel" / "Modify Sources")
2. 点击选项按钮

**预期结果**:

- ✅ 按钮变为不可点击状态
- ✅ 提交选择到后端
- ✅ 继续对话流程

#### 5.4 查看历史会话

**步骤**:

1. 点击右上角"历史"图标
2. 侧边栏滑出,显示会话列表 [ChatHistorySidebar]
3. 点击不同类型的会话

**预期结果**:

- ✅ 显示会话列表,按类型分组:

  - **agent**: Agent聊天会话 → 在当前页面切换
  - **channel-agent**: 频道Agent会话 → 在当前页面切换
- ✅ 加载历史消息

---

### 🔄 场景6: 数据同步与状态管理

**目标**: 确保应用数据状态正确同步

#### 6.1 Token自动刷新

**测试用例**:

1. Token即将过期时发送请求

**预期结果**:

- ✅ 拦截器自动刷新token
- ✅ 使用新token重试原请求
- ✅ 用户无感知

**关键代码位置**: [service/request/interceptors.ts]

#### 6.2 网络异常处理

**测试用例**:

1. 断网状态下操作

**预期结果**:

- ✅ 显示网络错误Toast
- ✅ 不崩溃
- ✅ 恢复网络后可继续使用

#### 6.3 状态持久化

**测试用例**:

1. 登录后关闭应用
2. 重新打开应用

**预期结果**:

- ✅ 自动登录 (authInfo和userInfo持久化)
- ✅ 不需要重新登录

---

## 数据兼容性测试

针对场景机制机型可选测试

---

## 体验优化检查点

### 🎨 UI/UX检查

#### 响应式布局

- ✅ 不同屏幕尺寸(小屏、大屏)显示正常

#### 加载状态

- ✅ 所有异步操作显示加载状态:

  - 骨架屏 (列表、详情)
  - 加载动画 (按钮、对话)
  - Toast提示 (操作反馈)
- ✅ 加载状态清晰,用户不会困惑

#### 错误处理

- ✅ 所有错误显示友好提示
- ✅ 提供重试机制 (Retry按钮)
- ✅ 网络错误、业务错误、系统错误区分提示

### ⚡ 性能检查

#### 列表渲染

- ✅ 长列表使用虚拟滚动或分页
- ✅ 滚动流畅,无卡顿
- ✅ 图片懒加载

#### 防抖节流

- ✅ 主页刷新防抖 (3秒内不重复)
- ✅ 滚动加载更多节流
- ✅ 按钮点击防抖

## 回归测试清单

### 🚀 发版前必测

#### P0 - 核心流程

-  新用户完整引导流程(登录→设置用户名→Welcome→Onboarding→创建频道)
-  老用户登录→直接进入主页
-  主页加载频道列表
-  频道详情页正常展示
-  文章阅读正常
-  AI助手聊天正常

#### P1 - 重要功能

-  下拉刷新
-  无限滚动加载更多
-  Tab切换
-  Tailor Brief定制
-  与文章聊天
-  查看历史会话
-  点赞/点踩

#### P2 - 辅助功能

-  侧边栏抽屉
-  主题切换
-  复制文章内容
-  打开外部链接

### 🔧 兼容性测试

#### 平台

-  iOS (真机测试)
-  Android (真机测试)

#### 设备

-  iPhone (小屏)
-  iPhone Pro Max (大屏)
-  Android 手机

#### 系统版本

-  iOS 15+
-  Android 10+

### 🌐 网络环境

-  Wi-Fi
-  4G/5G
-  弱网 (3G)
-  离线→在线切换

### 📊 压力测试

-  大量频道 (50+)
-  长文章 (10000+ 字)
-  大量历史消息 (100+ 条)
-  长时间使用 (30分钟+)