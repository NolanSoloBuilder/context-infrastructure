# Rimbo Figma 设计规范提取

来源：Figma `Untitled`，file key `bf3TCW9HFvAxqfWbzvW18p`。本规范以 `V2` 区域为主，参考 `component` 区域的 Sidebar 与 Chat 组件变体。

这份文档可以直接交给设计稿生成 agent 使用。agent 只需要读取整篇文档，把它当作 Rimbo 页面生成的唯一设计基准；不要再维护单独 prompt，不要在每次生成页面时重新发明视觉风格。

## 设计定位

Rimbo 的界面是一个桌面端 AI 信息工作台，视觉目标是克制、工具化、信息密度高。页面不做营销式视觉表达，主要靠左侧导航、白色工作区、轻量卡片、表格、列表、右侧 Chat 面板来组织复杂信息。

整体气质接近 macOS/iOS 工具界面：大面积白色和浅灰背景，黑色文字建立信息权重，蓝色只承担主行动、链接、选中和智能状态提示。除弹窗、卡片和输入框外，避免重阴影、强渐变和高饱和装饰。

## 画布与全局布局

默认桌面画布为 `1440 x 900`。页面背景使用 `#F9F9F9`。

基础 Shell：

- 左侧 Sidebar：`300 x 900`
- 右侧工作区：`1140 x 900`
- 工作区 padding：`top 16 / right 16 / bottom 16 / left 0`
- 工作区内部横向 gap：`12`

常用页面布局有三种。

第一种是双栏工作台：

- 主内容容器：`712 x 868`，白底，圆角 `16`
- 右侧 Chat 容器：`400 x 868`，白底，圆角 `20`
- 两栏之间 gap `12`

第二种是全宽详情页：

- 内容容器：`1124 x 868` 起，白底，圆角 `16`
- 内部 padding 通常 `16 / 16 / 40 / 16`
- 正文内容不要铺满容器，核心正文列控制在约 `820-1000px`

第三种是 Modal 流程：

- 页面原内容保留，叠加半透明黑色遮罩
- 大弹窗：约 `1078 x 747`，padding `32`，圆角 `20`
- 表单弹窗：约 `589 x 715`，padding `32`，圆角 `20`
- 弹窗居中，关闭按钮放右上，标题居中

## 色彩 Token

主背景与容器：

- App background：`#F9F9F9`
- Surface / Card：`#FFFFFF`
- Subtle surface：`#F8F8F9`
- Muted surface：`#F2F2F7`
- Hover / selected grey：`#EAEAEC`
- Divider / Border：`#E5E5EA`
- Stronger border：`#D1D1D6`

文字：

- Text primary：`#000000`
- Text body：`#34343B`
- Text secondary：`#8E8E93`
- Text tertiary：`#AEAEB2`
- Text inverse：`#FFFFFF`

品牌与状态：

- Primary blue：`#0088FF`
- Action blue：`#007AFF`
- Brand light blue：`#6EB6FF`
- Blue tint：`#6EB6FF` with `15%` opacity
- Success：`#34C759`
- Success tint：`#34C759` with `15%` opacity
- Warning / community：`#FF8D28`
- Warning tint：`#FF8D28` with `15%` opacity
- Error：`#FF383C` / `#D8001A`

使用规则：

- 蓝色主要用于链接、主按钮、选中 check、智能提示和少量徽标。
- 黑色按钮用于最高权重或付费转化动作，比如 `升级到 Max`、`提交获取定制方案`。
- 选中态优先用浅灰背景或蓝色 check，少用整块蓝色。
- 表格、输入框、卡片边界统一使用 `1px #E5E5EA`。

## 字体与排版

文件中混用了 `SF Pro` 与 `Inter`。生成新页面时建议统一为：

- 中文和系统 UI：`SF Pro`，fallback `Inter, sans-serif`
- 数据表格、英文密集信息：`Inter`

常用文字层级：

- Modal title：`28-32px / 150%`，Bold，居中
- Page title：`24px / 150%`，Bold
- Article title：`20px / 150%`，Bold 或 Semi Bold
- Section title：`16px / 20-24px`，Semi Bold/Bold
- Body large：`16px / 150%`，Regular
- UI body：`14px / 20px`，Regular
- Sidebar item：`14px / 20px`，Regular 或 Medium
- Caption / meta：`12px / 16px`，Regular/Medium
- Tiny tag：`10px / 100%`，Medium

正文写作区允许更高行距，列表和表格保持紧凑。中文长段落使用 `16px / 150%`，不要用过大的标题层级填充后台界面。

## 圆角、描边与阴影

圆角：

- App panel：`16`
- Chat panel / Modal：`20`
- Card：`12-16`
- Sidebar selected item：`8`
- Button / Chip：`999` 或半高圆角
- Icon button：`32 x 32`，圆形或胶囊
- Avatar / source icon：`24-48`，圆形或 `8-12` 圆角

阴影：

- 默认不用明显阴影，用描边和背景区分层级。
- 弹窗、悬浮菜单可以使用轻阴影：`0 1px 12px rgba(99, 99, 105, 0.10)`。
- 小菜单可叠加 `0 2px 5px rgba(0,0,0,0.15)`，但不要让阴影成为主视觉。

## 间距系统

使用 `4px` 基础栅格。

常用间距：

- 细小内部间距：`4`
- 列表行内间距：`8`
- 组件组间距：`12`
- 容器 padding：`16`
- 内容块间距：`24`
- 弹窗和大卡片 padding：`32`

页面生成时优先使用 auto-layout。横向工作区 gap 固定 `12`，页面边缘和容器 padding 固定 `16`，内容块之间用 `16/24/32` 控制节奏。

## 核心组件

### Sidebar

组件尺寸为 `300 x 900`，支持 `channel` 和 `chat` 两类样式，以及 `Default / hover / More` 状态。

结构：

- 顶部 brand bar：`300 x 36`，左右 padding `12`，内容两端对齐
- 中部导航区：高度约 `784`，纵向 gap `20`
- 底部账号/设置区：`300 x 32`，左右 padding `12`
- 一级导航行：高度 `32`，宽度约 `276`，图标 `20/24`
- 选中行：浅灰背景 `#EAEAEC`，圆角 `8`
- 分组标题：`12px`，`#8E8E93`
- 频道列表：`/AI Search/` 这类名称用 `14px` 黑色，行高约 `32`

生成规则：Sidebar 一直固定在左侧，不随内容滚动；工作区滚动发生在右侧白色容器内部。

### Chat Panel

组件尺寸为 `400 x 868`，白底，圆角 `20`，padding `16`，纵向 gap `16`。已有状态包括：

- `Default`
- `Add your sources`
- `skills`
- `chat`
- `Capsule Bubble`
- `Filter information sources`
- `confirm`
- `Thinking process`
- `Go to channel`

结构：

- 空状态：中央 mascot + 标题，标题约 `20px` Bold
- 文件卡片：小白卡或浅灰卡，图标方块 + 文件名 + meta
- Prompt capsule：浅灰描边胶囊，作为快捷建议
- 输入框固定底部，圆角大，含 `+`、`@`、附件、麦克风、发送按钮
- 发送按钮为圆形灰底或深色激活态

生成规则：右侧 Chat 不要变成普通表单区，它始终是任务编排入口。即使页面主要是表格或列表，也保留可以向 agent 追问或添加文件的输入 affordance。

### 主内容容器

详情页主容器通常白底、圆角 `16`，内部从左上开始排版。常见结构：

- 返回按钮
- 标题，例如 `/ Track AI Deals/`
- 状态行：绿色 live 点 + `LIVE · UPDATE 2M AGO`
- 来源头像组 + `+ 7 Sources` 胶囊按钮
- 正文区：Signal、Snapshot、Table、Watchlist、Timeline

正文块之间使用 `24-32` 间距。标题和正文保持左对齐，不需要额外装饰。

### Snapshot 指标卡

用于展示少量关键指标。

- 宽度约 `190`
- 高度约 `124`
- 白底或 `#F8F8F9`
- 描边 `1px #E5E5EA`
- 圆角 `12`
- label：`16px`，`#8E8E93`
- value：`24px`，Bold，黑色
- 横向排列，gap `12`

### 表格

表格用于交易、来源、监控结果等高密度信息。

- 表头使用非常浅的暖灰/浅灰背景
- 表头文字 `12-14px` Medium，正文 `12-14px`
- 行分隔线 `#E5E5EA`
- 数据徽标使用 tint 背景，例如蓝、绿、橙的 `15%` 透明底
- 表格不要加重卡片阴影，靠容器、分隔线和文字权重区分

### 资源列表

信源管理页使用两列资源条目。

- 页面标题区：标题 + 说明
- 顶部页签：文字页签，active 下划线
- 分类 chip：active 为黑底白字，inactive 为白底描边灰字
- 资源条目：图标 `48`，标题 `16px` Bold，说明 `14px` 灰色
- 添加态：右侧灰底 `+` icon button
- 已选态：右侧蓝色 check，不用整行蓝底

### Pricing Modal

套餐选择是大弹窗模式。

- 标题居中，下面一行灰色说明
- 分段控制器使用灰色背景，active 为白底
- 套餐卡三列排列，gap `16`
- 卡片白底、描边 `#D1D1D6`、圆角 `16`
- 价格使用大号黑字，按钮宽度撑满
- Basic 禁用按钮为浅灰；Pro 主按钮蓝色；Max 主按钮黑色

### 表单 Modal

联系销售弹窗是窄弹窗模式。

- 宽度约 `589`
- padding `32`
- 表单纵向排列，gap `12-16`
- label：`14px` Semi Bold
- input 高度约 `44`
- textarea 高度约 `112`
- 输入框白底、`1px #D1D1D6`、圆角 `8`
- 提交按钮黑底白字，高度约 `48`
- 辅助说明 `12px` 灰色，链接用蓝色

## Agent 执行协议

生成任何 Rimbo 新页面时，agent 按下面协议执行。

第一步，先判定页面类型。

- 如果页面需要用户和 AI 一起完成配置、追问、添加文件或下达任务，使用双栏工作台：左侧主内容 `712 x 868`，右侧 Chat `400 x 868`。
- 如果页面以阅读、分析、表格、时间线、详情正文为主，使用全宽详情页：主内容 `1124 x 868`，白底圆角 `16`。
- 如果页面是套餐、支付、确认、销售表单、危险操作确认，保留底层页面并叠加 Modal。
- 如果页面是资源选择、信源管理、频道管理，使用全宽容器，并用顶部页签、分类 chip、双列资源列表组织。

第二步，搭建固定 Shell。

1. 创建 `1440 x 900` 桌面画布，背景 `#F9F9F9`。
2. 放置 `300 x 900` Sidebar，选中当前导航项。
3. 创建 `1140 x 900` 右侧工作区，padding `16/16/16/0`。
4. 在工作区内放置对应页面容器。双栏 gap 固定 `12`，全宽容器宽度固定 `1124`。
5. 所有容器优先使用 auto-layout，页面内不要靠绝对坐标堆元素。

第三步，填充页面内容。

- 页面标题放在主容器左上，详情页标题格式可以使用 `/ Channel Name/`。
- 标题下方放状态行、更新时间、来源组或说明文案。
- 信息块按「标题、正文、卡片/表格/列表」排列，块间距使用 `24-32`。
- 数据概览用 Snapshot 指标卡，复杂数据用表格，来源和任务用列表。
- 只在需要 agent 协作的页面放右侧 Chat；Chat 输入固定底部。
- 所有 CTA 明确分级：蓝色用于普通主行动，黑色用于最高优先级或付费转化行动，灰色用于当前方案、禁用或次要行动。

第四步，做视觉一致性检查。

- 页面整体应该像后台工具，不像 landing page。
- 除 Modal 和悬浮菜单外，避免明显阴影。
- 不使用大面积渐变、装饰图形、营销式 hero、彩色背景板。
- 正文列不要过宽，详情正文优先控制在 `820-1000px`。
- 字号不要跳出 `12/14/16/20/24/28-32` 这组层级。
- 蓝色占比要低，只服务于链接、选中、行动和智能状态。
- 所有卡片、输入框、表格、chip 都使用本文档定义的圆角、描边和间距。

第五步，交付时说明页面类型、使用的核心组件和任何偏离规范的原因。没有明确原因时，不要偏离本规范。

## 快速判断清单

- 是否使用 `1440 x 900 + 300 Sidebar + 1140 Workspace`？
- 工作区外边距是否为 `16`，双栏 gap 是否为 `12`？
- 主容器是否白底、圆角 `16/20`、弱描边？
- 字号是否集中在 `12/14/16/20/24`？
- 蓝色是否只用于可点击、选中、智能状态？
- 卡片、表格、输入框是否主要靠描边和浅灰背景区分？
- Chat 面板是否保留 agent 输入和文件/快捷指令 affordance？
- Modal 是否居中、白底、圆角 `20`、padding `32`？
