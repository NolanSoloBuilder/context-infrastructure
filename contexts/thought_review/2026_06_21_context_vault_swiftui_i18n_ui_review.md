# Context Vault SwiftUI / i18n / UI Review

日期：2026-06-21

## 结论

Context Vault 当前最需要补的不是第三方 SwiftUI 控件库，而是产品级设计系统、组件拆分、多语言边界和性能边界。第一阶段应继续坚持 native SwiftUI，因为这个 App 的信任核心是本地、安全、可审计，过早引入重 UI 框架会增加维护面和安全审查面。

已经落地的第一步：

- 增加 SwiftPM localized resources，使用 `en.lproj` 和 `zh-Hans.lproj` 的 `Localizable.strings` 按系统语言匹配。
- 增加 `L10n` helper，先覆盖 shell、首页、安全边界、Migration Guide、Quick Actions、summary metrics 等第一屏内容。
- 增加 `L10n.dynamic(_:)`，把模型层保留为稳定英文语义值，UI 渲染时再按系统语言翻译。这样既不破坏测试断言，也能覆盖 migration lane、onboarding step、quick action、restore status 这类运行时字符串。
- 增加 `DesignSystem.swift`，提供 `AppTheme`、`AppBackground`、`AppPanel`、`StatusPill`、`HeroMetric`。
- 主界面从单纯灰色卡片升级为 material panel、状态色边框、metric card、更现代的 sidebar，以及 Environment 首页的控制中心 hero。

## 多语言方案

当前项目是 Swift Package executable，不是 Xcode project。为了保持 `swift test`、`scripts/package_app.sh`、release verification 都可用，第一阶段使用 SwiftPM resources：

- `Package.swift` 设置 `defaultLocalization: "en"`。
- `Sources/ContextVaultApp/Resources/en.lproj/Localizable.strings`
- `Sources/ContextVaultApp/Resources/zh-Hans.lproj/Localizable.strings`
- `L10n.text(_:fallback:)` 通过 `Bundle.module.localizedString` 读取系统语言对应资源。

这个方案可以直接随 app bundle 打包，不依赖 Xcode String Catalog 编辑器。后续如果迁移到 `.xcodeproj` 或 Xcode-managed app target，再切到 Apple 推荐的 String Catalog。Apple 官方方向是 String Catalog 集中管理本地化字符串，并让 Xcode 自动提取 SwiftUI 文本、提供翻译上下文和完整性检查。

打包时还需要把 `.lproj` 同时复制到 app 主 bundle 的 `Contents/Resources/`。原因是 SwiftPM resource bundle 可以服务 `L10n.text`，但 SwiftUI 的 `Text("literal")` 默认查主 bundle。两边都放资源后，显式 `L10n` 和 SwiftUI 自动本地化都能工作。

下一步要做的是把硬编码字符串继续收敛到 `L10n`，优先级为：

1. Navigation / Environment / Storage / Doctor 这些一级页面。
2. 用户会频繁点击的按钮、空状态、warning。
3. Activity / debug / report 里偏工程内部的文本。
4. 测试里增加 `AppleLanguages` smoke，确认中英文资源可被加载。

## SwiftUI 技术选型

当前建议：

- 基础 UI：继续使用 SwiftUI native controls，不引入重型 UI framework。
- 图表：如果后续做资产分布、风险趋势、同步历史，用 Apple Swift Charts。
- AppKit 边界：只在必须控制底层 `NSScrollView`、window、split behavior 时考虑 `swiftui-introspect`。这个库仍活跃，但它本质上依赖底层 UIKit/AppKit hierarchy，应作为边界补丁，而不是核心架构。
- Navigation 动效：暂时不引入 `swiftui-navigation-transitions`。这个 App 是工具型 Mac App，效率和可预测性优先。
- 数据和状态：继续用 `ObservableObject` + `@StateObject`，因为当前 target 是 macOS package app，已有模型较大。未来可逐步迁移到 Observation API，把大 `AppViewModel` 拆成 feature models。

需要重构的技术债：

- `Views.swift` 太大，已经超过一个 feature 文件应承载的范围。应拆成 `ShellView.swift`、`EnvironmentView.swift`、`StorageView.swift`、`DelegationView.swift`、`HandoffView.swift`、`SharedComponents.swift`。
- `AppViewModel` 过大，扫描、Git、restore、handoff、delegation 都混在一个 observable object 里。应拆成 feature stores，减少无关状态变化触发整屏刷新。
- 之前 `scan()` 主线程同步扫描导致 UI 卡死，已经改成后台扫描。后续所有文件 IO、Git、restore 写入都应维持同样边界。
- 大列表使用 `LazyVStack` 是正确方向，但搜索、筛选、排序要避免在 `body` 里重复做重计算。

## UI Review

当前 UI 问题：

- 信息架构像工程调试面板，缺少明确的“用户现在处在哪个迁移阶段”的视觉引导。
- 卡片样式过于统一，重要动作、风险状态、完成状态没有足够层级。
- Mac App 的 sidebar 现在能工作，但视觉上仍偏 prototype；需要更接近现代 Apple 工具型 app：清晰 sidebar、toolbar action、内容区 grouped panels、状态色克制使用。
- 首页把 Onboarding、Migration、Quick Actions、Summary、Tool grid 都塞在一屏，真实数据出来后层级容易拥挤。

## 简化后的信息架构方案

下一版应该把 `Environment` 改名为 `Dashboard` / `仪表盘`。用户打开 App 后看到的不是环境配置页，而是当前 AI 工具上下文的总体状态、下一步动作和工具覆盖情况。

侧边栏只保留五个主入口：

- `仪表盘`：总览状态、下一步动作、工具覆盖、最近同步状态。
- `上下文库`：合并现在的 Inbox 和 Store。Inbox 只是库里的一个筛选状态，不再作为独立导航。
- `转移`：合并 Delegation 和 Handoff。它负责把 Claude Code skill 转 Codex、把 Cursor rule 转 Gemini artifact、把当前任务交给另一个工具继续做。
- `同步与恢复`：合并 Storage 和 Restore。Git repo 设置、export/import、restore review 都属于同一条跨设备同步链路。
- `设置`：本地安全边界、自定义扫描目录、日志、备份、诊断入口。Doctor 和 Activity 不再占侧边栏主入口。

侧边栏点击行为保持简单：点击主入口只切换工作区，不在侧边栏里展开二级树。二级内容放到页面内的 segmented control、toolbar 或右侧 inspector。这样侧边栏负责“我在哪里”，页面负责“我现在处理哪个对象”。

`仪表盘` 只保留三段：

1. 顶部状态：本地安全边界、最近扫描时间、工具数量、资产数量、secret-risk 数量，以及一个主按钮。主按钮永远是推荐下一步，例如“确认边界”“扫描本机”“添加安全资产”“设置 Git repo”“生成恢复计划”。
2. 下一步：只显示一个推荐动作和最多两个次要动作。当前的 Onboarding Progress、Migration Guide、Quick Actions 应合并成一个 `Next Step` 模块，不再三组并列。
3. 工具矩阵：Codex、Claude Code、Cursor、Windsurf、OpenCode、Gemini 等工具按卡片或紧凑列表展示。每个工具只显示三个状态：已检测、可同步、需处理。点击工具进入 `上下文库` 并带上工具筛选。

隐私说明和安全边界只在未确认时作为阻断式提示出现；确认后收进顶部状态或设置页。Migration Guide 也不应常驻首页，它应该被折叠成 `下一步` 的推荐动作。Activity Log 作为底部 toast 的跳转面板或设置页里的审计记录，不再作为主导航。

2026-06-21 已执行第一版收敛：

- 侧边栏主入口从 9 个收敛为 5 个：`仪表盘`、`上下文库`、`转移`、`同步与恢复`、`设置`。
- `Inbox` 和 `Store` 合并到 `上下文库`，用页面内 segmented control 区分 `待确认` / `已保存`。
- `Delegation` 和 `Handoff` 合并到 `转移`，用页面内 segmented control 区分 `工具转移` / `任务交接`。
- `Storage` 和 `Restore` 合并到 `同步与恢复`，用页面内 segmented control 区分 `Git 同步` / `恢复审核`。
- `Doctor` 和 `Activity` 合并到 `设置`，日志从底部 feedback banner 进入设置工作区。
- `仪表盘` 删除常驻的 `Setup Progress`、`Migration Guide`、`Quick Actions` 三组并列模块，改成 `Next Step` 单推荐动作 + 最多两个次要动作。
- `仪表盘` 的工具区改成 `Tool Matrix`，每个工具只显示 `可同步` / `需处理` / `已检测` / `未检测到`，点击工具进入 `上下文库` 并自动带上工具筛选。
- 旧的内部路由仍然保留，例如 restore 按钮可以直接打开 `同步与恢复` 的恢复 tab；侧边栏高亮会归并到对应主入口。

2026-06-21 第二轮 UI 修正：

- `仪表盘` 顶部始终展示隐私/本地访问说明。未确认时显示唯一主按钮 `确认并继续`；确认后保留轻量说明，不再显示“已确认 / 零遥测”这类状态 pill。
- 删除 `稍后查看` 和关闭按钮。隐私边界是扫描前置条件，不应提供无意义的绕过入口。
- 确认动作改为 `acceptSafetyBoundaryAndDismissGuide()`，确认本地安全边界后同时关闭首次说明，避免“确认按钮无效”的感知。
- Hero 区去掉状态 pill，改为标题、说明、主扫描按钮和四个轻量指标。指标不再是卡片套卡片。
- `Next Step` 从大卡片 + 小卡片混排改成更轻的操作面板：一个推荐动作 + 两个次要动作，减少抢焦点元素。
- `Settings` 不再直接展示 `Doctor / Activity` 两个 tab，而是先给 `隐私与数据 / 扫描目录 / 备份 / 诊断 / 活动` 五个入口。
- `Storage` 默认隐藏 Git pull/commit/push、repo health、local backups、Git log 等高级信息，主路径保留 repo、验证、导出和导入。

第一阶段改造方向：

- 使用 `regularMaterial` panel，统一 8px radius。
- Summary 改成 metric cards，状态一眼可扫。
- Safety Boundary / Migration Lane / Quick Action 使用状态色边框，而不是大面积色块。
- Sidebar 增加 app identity 和本地优先提示。
- Environment 首页改成“AI 工具上下文控制中心”：顶部大 hero 承载状态、主动作和关键指标，下面才是隐私说明、设置进度、迁移路径和快捷操作。

这轮参考了几个线上产品的公开界面/文档：

- Codex app：重点不是传统文件管理，而是 skills、automations、inbox、agent task 的控制台。对 Context Vault 的启发是把 skill/context sync 做成可操作的工作台，而不是设置页。
- Claude Desktop / Claude Code：Chat、Cowork、Code 分区说明了桌面 AI 工具正在按工作模式组织入口。对 Context Vault 的启发是分清扫描、委派、交接、恢复这些不同工作模式。
- Cursor：公开首页展示的是 desktop/CLI agent interface 和 in-progress task cards。对 Context Vault 的启发是让“正在处理什么、下一步能做什么”成为第一屏信号。
- Notion：sidebar 是 workspace 内容组织中心，可以隐藏以获得更专注的工作区。对 Context Vault 的启发是 sidebar 负责位置感，内容区负责当前任务，不把导航和表单混在一起。

第二阶段改造方向：

- 首页改成三段式：顶部状态总览，中部迁移路径，底部工具分布。
- Delegation 做成 source -> transform -> target 的 pipeline UI。
- Storage 做成 Git repo health dashboard，不再只是表单和日志。
- Doctor 做成 grouped findings，按安全、同步、恢复、工具环境四类聚合。
- 增加 Skill Controls：单独展示可迁移 skills、来源工具、目标工具支持矩阵、最后同步时间、风险状态。这个比把 skill 藏在 Delegation asset list 里更符合产品定位。

## 设计原则

这个 App 不是营销型产品，也不是通用漂亮 dashboard。它是本地工具环境的控制台。视觉上应该是：

- 安静、可信、可审计。
- 信息密度高，但状态层级明确。
- 操作前给 preview 和 rollback。
- 对 secret-risk、Git export、restore overwrite 使用清晰的风险标记。
- 视觉资产服务于“我的 AI 工具环境是否可迁移、可恢复、可委派”这个判断。

## 参考来源

- Apple Developer：String Catalog / localization 文档。
- Apple Developer：SwiftUI localization 文档。
- Apple Developer：Human Interface Guidelines 和 macOS / iOS design guidance。
- Apple Developer：Design Resources 中的 `macOS 27 UI Kit`，用于校准 macOS sidebar、toolbar、list、form、button、popover、material 等系统组件基线。
- Sketch：`macOS 27 UI Kit` 公开分享链接 `https://www.sketch.com/s/57153a31-3379-4737-8ac6-dbfd6525f052`，用于对照官方 symbol 和状态。
- Apple Developer：Swift Charts 文档。
- Swift Package Index / GitHub：`swiftui-introspect` 活跃状态和适用边界。
- OpenAI：Codex app / Agent Skills / Automations 产品说明。
- Anthropic：Claude Desktop / Claude Code desktop docs。
- Cursor：Cursor homepage desktop agent interface。
- Notion：sidebar navigation help / workspace navigation docs。

## macOS 27 UI Kit 参考

2026-06-21 补充：Apple Developer Design Resources 已发布 `macOS 27 UI Kit` 的 Sketch 版本；Sketch 公开分享链接为 `https://www.sketch.com/s/57153a31-3379-4737-8ac6-dbfd6525f052`。网页抓取不到具体 symbol 内容，但 Apple Design Resources 页面确认 macOS 27 UI Kit 可通过 Sketch 使用；Sketch beta 说明也提到可在 Welcome to Sketch 中安装 Apple 最新 iOS 27 和 macOS 27 UI kits。

这套官方 kit 对 Context Vault 的下一轮 UI 参考价值主要在系统组件校准，而不是直接复制某个画面：

- Sidebar：保持一级导航少而稳定，避免在 sidebar 里做二级树。当前 5 个主入口方向正确，后续要继续减少内部旧路由暴露。
- Toolbar / primary action：主动作应该进入页面 toolbar 或标题区，不应在页面中散落一排按钮。`同步与恢复` 后续要抽成一个状态驱动主按钮。
- Lists / forms：`上下文库`、`设置` 应更接近系统 list/form，而不是工程表格 + 卡片详情。资产列表应通过状态 chip 表达 `待确认 / 已保存 / 需审查`。
- Inspector / popover：资产详情、restore diff、MCP merge、Git log、repo health 这类高级信息适合进入 inspector、popover 或 disclosure，不应默认占据主工作区。
- Materials：Liquid Glass / material 应用于导航、toolbar、浮层和少量核心容器。当前 App 需要避免每个模块都套 panel，减少“卡片堆叠”。
- Buttons：按钮文案要围绕用户任务，例如 `扫描本机`、`加入上下文库`、`导出到 Git`、`预览恢复`；避免暴露实现动作如 `Git Pull`、`Open Manifest` 作为默认入口。

后续实现优先级：

1. 按 macOS 27 UI Kit 校准 sidebar、toolbar、list、form、button、popover 的基础尺寸和状态。
2. 将 `上下文库` 从 `Inbox / Store` 两个旧页面改成单一资产列表 + 状态筛选。
3. 将 `转移` 改成三步 wizard：来源、目标、预览应用。
4. 将 `同步与恢复` 改成状态机驱动的主操作页面，Git 细节收进高级区。
5. 拆分 `Views.swift`，按 `DashboardView`、`ContextLibraryView`、`TransferView`、`SyncRestoreView`、`SettingsView` 管理。

## macOS 27 UI Kit 本地素材判断

本地已拉取 `Apple macOS 27 UI Kit.sketch`，存放在 `adhoc_jobs/ai_tool_environment_sync_app/reference_assets/macos_27_ui_kit/`。该目录已加入 App 项目 `.gitignore`，避免 100MB 级设计素材进入 git。

这个素材可以直接解析 `.sketch` 包结构：包含 `document.json`、`meta.json`、`pages/*.json`、`previews/preview.png`、字体和图片资源。`meta.json` 可读到完整页面目录和 artboard 命名。当前可确认它不是封面图或空壳，而是完整的官方组件库。

已从本地 Sketch 包抽取组件基线，写入 `adhoc_jobs/ai_tool_environment_sync_app/docs/macos_27_component_reference.md`。输入、搜索、选择类组件可确认有具体尺寸、状态和内部层级，例如 `Text Fields/Light/4 Lg/Value + Typing` 是 `120 x 28` 的 `symbolMaster`，内部包含 `Focus Ring` 和 `Stack`，内容区左右 padding 为 `8`。

对 Context Vault 有直接参考价值的页面包括：

- `Sidebars`：可用于校准一级导航、选中态、disabled 态、层级缩进、窗口控制区和 sidebar header。当前 App 的 5 个一级入口方向正确，但样式和 spacing 应继续靠近系统 sidebar。
- `Titlebars and Toolbars`：可用于决定主操作放在标题栏、toolbar 还是页面 header。`同步与恢复` 的主动作应从分散按钮改成状态驱动的 toolbar/header action。
- `Buttons`：可用于统一按钮尺寸、层级和状态。当前 App 需要减少工程按钮文案，把默认按钮改成用户任务语言。
- `Forms`、`Text Fields`、`Search Fields`：可用于重做 `设置`、`上下文库` 筛选和路径配置。它们应更像系统设置列表，而不是卡片堆叠。
- `Popovers`、`Disclosure Controls`、`Menus`：适合承载 restore diff、Git log、MCP merge、资产详情等高级信息，避免默认占据主界面。
- `Materials`：素材包含 `Liquid Glass` 和普通 material 示例。当前实现可先用兼容 SwiftUI material 近似；真正依赖 macOS 27 API 时再做 availability gate 或提高 deployment target。

结论：这个素材值得作为下一轮 UI pass 的基准。它最有价值的不是视觉风格本身，而是让我们停止凭感觉调整 spacing、corner、状态和控件层级。下一轮实现应先抽取 `Sidebars`、`Titlebars and Toolbars`、`Buttons`、`Forms`、`Popovers` 五类规则，再映射到 SwiftUI 组件。

## 上下文库管理对象调整

2026-06-21 补充：上下文库不应以文件明细作为第一层管理对象。不同工具的上下文经常天然形成目录或逻辑包，例如一个 skill 目录、一个 MCP config、一个 rules 文件夹、一个 SQL 上下文目录。把所有文件平铺出来会让用户处理粒度过细，也不符合“跨工具上下文迁移”的真实心智模型。

后续上下文库的默认管理对象是 `Context Unit`，文件是单元内部明细：

- `Skill`：以 `skills/<name>/` 或包含 `SKILL.md` 的目录为单元。
- `MCP`、`Rule`、`Config`、`Command`、`Memory`、`Session`：默认按对应文件或配置根聚合。
- `Folder`：对 SQL、未知文件夹、项目内上下文目录等，以父目录作为单元。
- 单元列表展示工具、类型、根路径、文件数、风险状态；详情面板展示单元内文件。
- `Add Selected`、`Remove Selected` 这类动作应处理整个单元，而不是只处理第一条文件。
- 选中单元内文件后，详情区应提供文件级预览和打开能力。预览只读展示文本内容，文件打开走系统默认应用；这样用户可以按上下文单元管理，同时在需要时下钻到具体文件。

这个调整先在 UI 和 ViewModel 层落地，不改变本地 store schema。底层仍保存 `ContextAsset` 文件资产，页面通过 `ContextUnit` 聚合展示和操作。这样可以保持导出、恢复、secret 扫描、diff 等现有链路稳定，同时把用户管理粒度提升到上下文单元。

## 同步流程与定时同步

2026-06-21 补充：`同步与恢复` 页面必须符合工具真实使用流程，而不是把 Git 操作按钮平铺给用户。主流程应按状态推进：

1. 未扫描：引导用户先扫描本机 AI 工具环境。
2. 已扫描但未入库：引导用户打开上下文库，按 `Context Unit` 选择需要保存和同步的上下文。
3. 已入库但未关联 repo：引导用户选择用户自有 GitHub repo 的本地 clone 路径。
4. 已关联但未验证：引导用户验证 repo，检查 `.git`、可写性、远端、工作区状态和 `context_vault/`。
5. 已验证：提供 `Sync Now`，把本地 store 导出到 `context_vault/`，再通过用户自有 Git repo commit/push。

恢复、导入预览、Git log、manifest、README、本地备份、自定义扫描目录等仍是重要能力，但不应占据主流程第一层。它们适合放在高级详情、恢复页或显式操作里，避免用户在首次使用时被底层 Git 动作打断。

定时同步的 MVP 规则：

- 用户可以选择关闭、每小时、每天、每周。
- 定时同步只在 App 打开时检查时间间隔；不做后台守护进程，不绕过用户感知。
- 如果 App 关闭期间错过了同步窗口，用户下次打开 App 时检查是否到期，到期则触发同步。
- 触发前必须满足：已有本地上下文库资产、已选择用户自有 Git repo、repo 验证无失败。
- 同步目标仍然只有用户自有 Git repo。本 App 不上传平台数据库，不上报遥测。
- MVP 同步动作是导出本地 store 到 `context_vault/`，执行 commit，再 push。Pull/import/restore 属于显式恢复路径，避免自动覆盖本机内容。

## 主布局、侧边栏和 Tab 规则

2026-06-21 补充：Context Vault 是 macOS 原生 App，根布局不应继续用手写 `HStack + 固定宽度 Sidebar`。这种实现会导致 sidebar 不能关闭、不能拖拽调整宽度，并在右侧内容变宽时互相挤压。主窗口应使用 SwiftUI `NavigationSplitView`：

- Sidebar 使用原生 `List(selection:)` 和 `.listStyle(.sidebar)`，保持系统 source-list 行为。
- Sidebar column 设置 `min / ideal / max` 宽度，允许用户拖拽调整。
- 提供显式 sidebar toggle，支持隐藏和恢复 sidebar。
- Detail 区域承担自定义背景和内容布局，不在 sidebar 上强行覆盖大块自定义 material。
- 主窗口最小宽度要服务于可用性，但不应依赖超宽固定布局来避免溢出。

主体页的内容约束：

- Dashboard 不使用过大的固定宽度和固定横向 metric 行；在较窄 detail 宽度下应自动换行。
- Hero 区的标题/说明和主按钮应使用可适配布局，宽度不足时按钮下移，不挤压文案。
- Workspace header 的 tab 不再使用固定宽度 segmented picker。改为轻量 pill tab strip，支持横向滚动，避免窄宽度下撑爆 header。
- 表格类明细仍可内部横向/纵向滚动，但页面主流程不应因为表格列宽把整页挤出窗口。

## Tab 文案规则

2026-06-21 补充：各 workspace tab 的文案必须短、直观、可行动。不要在页面标题区列技术清单，也不要重复解释“本地优先、不上报平台”等全局原则。默认规则：

- Tab 名称使用 2 到 4 个字，表达用户任务，例如 `待处理 / 已保存`、`转换 / 交接`、`同步 / 恢复`、`检查 / 记录`。
- 页面副标题只保留一句下一步说明，例如“选择要保存的本机上下文”“转换上下文，或保存任务交接”。
- 操作按钮使用动词短词，例如 `预览`、`写入`、`复制`、`打开`、`检查`。
- 空态只告诉用户下一步做什么，不列支持矩阵。
- 支持矩阵、路径细节、Git/MCP 实现细节放进高级区、详情区或错误详情，不放在主流程默认视图。

## 上下文库筛选规则

2026-06-21 补充：上下文库的筛选对象是 `Context Unit`，不只是文件资产。因此筛选条必须支持上下文类型筛选，例如 `Skill / MCP / Rule / Folder / Config / Memory / Command / Session / File`。类型筛选只在上下文库展示，避免转移、恢复等页面被不相关筛选项干扰。

## 文件夹型上下文单元交互

2026-06-21 补充：`Folder` 类型不能只作为普通行展示。当前产品决策采用最直接的 Mac 交互：点击文件夹单元后直接在 Finder 打开对应文件夹。

- 单击文件夹：选中文件夹，并打开 Finder。
- 右侧详情保留为补充信息：展示文件夹概览、风险摘要和文件列表。
- 右侧详情按钮在文件夹单元上显示 `打开文件夹`，在文件单元上显示 `打开文件`。
- 文件夹单元仍支持整体操作：默认添加、移除、同步都是对整个文件夹单元生效。
- 文件级预览作为补充能力，不替代 Finder 浏览。

结论：文件夹不是“点了只选中”的普通行。MVP 优先打开 Finder，后续如果需要更强浏览能力，再做内置文件树 inspector。
