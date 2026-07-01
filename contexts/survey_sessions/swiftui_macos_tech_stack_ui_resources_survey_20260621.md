# SwiftUI 与 Mac App 技术栈、UI 参考资源速查

日期：2026-06-21

这份记录回答一个比较实际的问题：现在如果要做 SwiftUI / macOS App，技术栈该怎么理解，哪里能看高质量 UI 和真实项目。信息以 Apple 官方资料为主，第三方资料用于补充生态和示例。

## 结论

如果目标是做一个 macOS-first、体验和系统融合优先的 App，默认路线是 `SwiftUI + AppKit fallback`。SwiftUI 已经适合大部分新界面、设置页、窗口、菜单栏工具、文档类 App 和跨 Apple 平台复用；AppKit 仍然是复杂文本编辑、复杂表格/outline、高度定制窗口、成熟菜单/响应链、拖放、输入法细节和老系统兼容的补位层。

如果目标是跨平台工具、AI agent、Web-first SaaS companion，`Electron` 仍然是生产力最高的路线，代价是体积、内存和 Mac 原生质感。`Tauri` 是更轻的 Web UI + native shell 路线，适合愿意写 Rust/系统层胶水的团队。`Flutter`、`React Native macOS`、`Qt` 能做跨平台，但要做出真正像 Mac 的体验，成本会落在细节上。

截至 2026-06-21，Apple release 页显示 `Xcode 26.6 RC 2` 在 2026-06-18 发布，`Xcode 27 beta`、`macOS 27 beta` 在 2026-06-08 发布。`Xcode 27 beta` 带来 Swift 6.4 和新 SDK；生产项目应把这些视为前瞻 API，除非明确接受 beta toolchain。

## SwiftUI / 原生 Mac App 栈

| 层 | 默认选择 | 什么时候换 |
|---|---|---|
| 语言与 IDE | `Swift 6.x`、`Xcode`、`Swift Package Manager` | 多人复杂工程可加 `Tuist` 或 `XcodeGen` 管 project structure |
| UI 框架 | `SwiftUI` | 复杂文本、表格、响应链、窗口行为、历史组件复用时接 `AppKit` |
| macOS App 生命周期 | `App`、`Scene`、`WindowGroup`、`Settings`、`Commands`、`MenuBarExtra`、`DocumentGroup` | 老项目或强 AppKit 依赖用 `NSApplicationDelegate` / `NSWindowController` 混合 |
| 状态与数据流 | `Observation` / `@Observable`、`@State`、`@Binding`、`Environment` | 大型业务状态、复杂 effect、严格测试可考虑 `The Composable Architecture` |
| 持久化 | `SwiftData`、`AppStorage`、`SceneStorage` | 复杂查询、已有 SQLite schema、可迁移性要求高时用 `GRDB`；老项目继续 `Core Data` |
| 并发 | `async/await`、`Task`、`Actor`、`MainActor`、Swift strict concurrency | 旧 Combine pipeline 可保留，但新代码优先 async sequence / structured concurrency |
| 系统集成 | `App Intents`、`Shortcuts`、`Spotlight`、`WidgetKit`、`Quick Look`、`ShareLink` | 需要深系统权限、全局快捷键、辅助功能、屏幕录制时接 AppKit / Carbon / Accessibility API |
| AI 能力 | `Foundation Models framework`、`App Intents`、Apple Intelligence integration | 云模型、多模型路由、RAG、工具调用复杂时自建服务或本地 helper |
| 图形与媒体 | `Canvas`、`Swift Charts`、`Metal`、`AVFoundation`、`ScreenCaptureKit` | 高性能 2D/3D 或视频编辑直接进 Metal / AVFoundation |
| 测试 | `Swift Testing`、`XCTest`、UI test、Instruments、Accessibility Inspector | 复杂 UI 回归可加 snapshot testing |
| 发布 | App Store / TestFlight，或 Developer ID + notarization + Sparkle | 企业内部分发可走 MDM、私有 updater、直接 DMG |

WWDC26 的 SwiftUI 重点值得注意：新的 Document API、toolbar customization、reorderable containers、`AsyncImage` HTTP cache、`@State` lazy initialization、`ViewBuilder` / `ContentBuilder` 构建性能改进，以及 SwiftUI 与 AppKit / UIKit 的增量采用路径。对 Mac App 来说，这些变化说明 Apple 仍在把 SwiftUI 推向复杂桌面应用，但官方也在强化与 AppKit 的协作，而不是要求重写。

## Mac App 技术栈分层

| 路线 | 适合场景 | 代价 |
|---|---|---|
| `SwiftUI + AppKit` | 新原生 Mac App、菜单栏工具、文档工具、Apple 平台优先产品 | Apple-only，复杂控件仍要懂 AppKit |
| `AppKit-first` | 专业工具、复杂编辑器、历史 Mac App、大量 NSView/NSDocument 资产 | 开发速度慢，代码心智模型更老 |
| `Mac Catalyst` | 已有 iPad App 想较快进入 Mac | 容易像 iPad App 搬到 Mac，平台细节要补 |
| `Electron` | Web 团队、AI/agent 工具、开发者工具、跨平台 SaaS 桌面端 | 体积和内存重，原生手感需要大量 native integration |
| `Tauri 2` | Web UI + 轻量桌面壳、Rust 后端、追求体积和安全边界 | 生态比 Electron 小，系统能力常要自己接 |
| `Flutter Desktop` | 一个代码库覆盖 mobile/desktop，团队已有 Flutter 能力 | macOS native 细节需要专门打磨 |
| `React Native macOS` | RN 团队复用 React Native 组件和逻辑 | 生态较窄，Mac 端问题排查成本高 |
| `Qt / C++ / Rust GUI` | 工业软件、跨平台专业软件、已有 C++/Rust 内核 | UI 不容易自然贴合 Apple HIG |

一个实用判断：Mac 用户对“像 Mac”很敏感。系统菜单、keyboard shortcut、undo/redo、toolbar、sidebar、窗口恢复、drag and drop、accessibility、Spotlight / Shortcuts 集成，这些细节比视觉皮肤更决定质感。SwiftUI 负责 70% 界面效率，AppKit 负责剩下那些不能糊弄的桌面语义。

## SwiftUI 组件库

SwiftUI 生态里没有一个等价于 Web 世界 `shadcn/ui`、`MUI`、`Ant Design` 的事实标准。原因是 Apple 平台的组件库本来就在系统里：`List`、`Table`、`NavigationSplitView`、`Form`、`Inspector`、`Toolbar`、`Menu`、`Settings`、`Grid`、`Swift Charts`、`SF Symbols`、`Material`、`ControlGroup`、`Picker`、`Stepper`、`Slider`、`Toggle` 这些内置控件已经覆盖了大量生产界面。第三方库更适合做补位，而不是替代整套 HIG。

优先级可以这样排：

| 类型 | 推荐库 | 判断 |
|---|---|---|
| 系统补位 / SwiftUI 扩展 | [SwiftUIX](https://github.com/SwiftUIX/SwiftUIX) | 最接近“大而全”的 SwiftUI 扩展库，补 UIKit/AppKit 缺口，支持 macOS；适合拿来补控件和 modifier 缺失 |
| macOS 视觉组件 | [Luminare](https://github.com/MrKai77/Luminare) | macOS SwiftUI translucent design system，适合做带强风格的 Mac 工具；组件列表和文档还不算完整，适合先局部试用 |
| 通用 UI 套件 | [VComponents](https://github.com/VakhoKontridze/VComponents) | buttons、pickers、inputs、containers、modals、indicators 等一套自定义控件；更像 mobile/custom UI 套件 |
| iOS / SwiftUI 组件套件 | [ComponentsKit](https://github.com/componentskit/ComponentsKit) | Alert、Avatar、Badge、Button、Card、Checkbox、Input、Modal、Segmented Control 等；偏 iOS 商业 App 组件，不是 Mac 原生风格优先 |
| Toast / Popup | [Exyte PopupView](https://github.com/exyte/PopupView) | SwiftUI toast、alert、popup；AI chat / productivity 工具里常有用 |
| Chat UI | [Exyte Chat](https://github.com/exyte/Chat) | SwiftUI chat UI framework，适合快速搭 AI chat 原型；生产前要评估和自家消息模型、附件、编辑、引用、虚拟列表的贴合度 |
| Markdown / rich text | [MarkdownUI](https://github.com/gonzalezreal/swift-markdown-ui)、[Textual](https://github.com/gonzalezreal/textual) | MarkdownUI 适合显示 GFM / CommonMark；Textual 是作者后续做的 SwiftUI text rendering engine，长期新项目可以一起评估 |
| 底层控件桥接 | [SwiftUI Introspect](https://github.com/siteline/swiftui-introspect) | 不是组件库，但很有用。它通过公开 API 找到底层 UIKit/AppKit view，让你补 SwiftUI 暴露不出来的设置 |
| 导航 / 状态 | [Swift Navigation](https://github.com/pointfreeco/swift-navigation)、[The Composable Architecture](https://github.com/pointfreeco/swift-composable-architecture) | 不是视觉组件，适合复杂状态、复杂导航、可测试业务流 |
| Mac App 常用能力 | [Settings](https://github.com/sindresorhus/Settings)、[KeyboardShortcuts](https://github.com/sindresorhus/KeyboardShortcuts)、[LaunchAtLogin](https://github.com/sindresorhus/LaunchAtLogin-Modern) | 这些是 Mac App 工程里非常实用的“系统功能组件”：设置窗口、全局快捷键、开机启动 |

我的建议是：Mac App 不要一开始引入一整套强视觉组件库。先用 SwiftUI 系统控件把信息架构、窗口、toolbar、sidebar、settings、keyboard shortcut 做对；遇到具体缺口时再引 `SwiftUIX`、`SwiftUI Introspect` 或单点库。只有产品本身需要强自定义视觉，比如 AI companion、菜单栏工具、创意工具，再考虑 `Luminare` 或自建一层 design system。

如果是做 AI chat / agent 类 Mac App，可以优先评估这组组合：`SwiftUI` 内置控件 + `MarkdownUI/Textual` + `Exyte Chat` 或自研 message list + `PopupView` + `KeyboardShortcuts` + `LaunchAtLogin` + `SwiftUI Introspect`。其中 chat list 和 markdown renderer 是最容易影响体验的两块，值得尽早做技术 spike。

### 原生控件定制 vs 引组件库

SwiftUI 的原生控件可以定制，但定制方式和 Web 不一样。Web 里可以对 `select`、`input`、`button` 大量写 CSS；SwiftUI 更鼓励用系统样式、`ViewModifier`、`ButtonStyle`、`ToggleStyle`、`LabelStyle`、`TextFieldStyle`、`PickerStyle` 和 design token 做一层轻封装。这样能保留 macOS 的键盘导航、focus ring、VoiceOver、菜单行为、hover、disabled、dark mode、窗口层级和 accessibility。

比较稳的做法是先建自己的薄组件层，而不是先引大组件库：

| 需求 | 推荐做法 |
|---|---|
| Button、icon button、toolbar button | 自定义 `ButtonStyle`，封装 `PrimaryButton` / `IconButton` |
| Select / dropdown | 优先用 `Picker` / `Menu` / `MenuButton`，只定制外层 label、尺寸、间距和状态 |
| TextField / SearchField | 用系统 `TextField` / `SearchField` 风格，外层加 token 化 spacing、label、help/error |
| Checkbox / Toggle | 保持系统行为，用 `ToggleStyle` 做轻量视觉调整 |
| Card / panel / sidebar item | 自己写 `View` / `ViewModifier`，这是最适合自定义的部分 |
| Toast、command palette、chat message、markdown renderer | 可以引单点库或自研，因为这些不是系统控件覆盖最好的区域 |

真正要谨慎的是自研 `Select`、`Dropdown`、`Combobox` 这类控件。视觉上它们看起来简单，实际要处理 keyboard navigation、type-ahead、outside click、popover 定位、scroll、accessibility、focus restore、disabled item、menu item shortcut、multi-window 行为。除非产品需要强品牌化或复杂搜索选择器，否则 Mac App 里优先用系统 `Picker` / `Menu`。

是否引组件库，可以用一个简单标准判断：如果只是颜色、圆角、字号、间距、hover、pressed、disabled、loading 这些视觉状态，自己基于原生控件封装；如果是系统没有的复杂交互，比如 markdown 渲染、chat list、toast、command palette、calendar、rich text editor，再引单点库；如果整套产品都要强自定义视觉，再考虑 `Luminare` 这类 design system 或自建组件系统。

## 高质量 UI / 示例资源

### 官方第一优先级

- [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines)：所有 Mac UI 判断的基准。
- [Designing for macOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-macos)：看 Mac 与 iOS/iPadOS 的差异。
- [Apple Design Resources](https://developer.apple.com/design/resources/)：官方 Figma / Sketch 模板、icon、color guide、product bezel。
- [Apple Design Awards](https://developer.apple.com/design/awards/)：每年 Apple 官方筛过的一批高质量 App / Game，适合看 polish 和平台能力使用。
- [Apple Sample Code Library](https://developer.apple.com/documentation/SampleCode)：官方 sample code 总入口。
- [WWDC26 SwiftUI Guide](https://developer.apple.com/wwdc26/guides/swiftui/)：看最新 SwiftUI API 方向。
- [Use SwiftUI with AppKit and UIKit](https://developer.apple.com/videos/play/wwdc2026/272/)：看官方认可的 hybrid 路线。

### SwiftUI 视觉和代码示例

- [Explore SwiftUI](https://exploreswiftui.com/)：SwiftUI 组件和 modifier 的视觉库，有 ready-to-use code，适合快速查“这个控件长什么样”。
- [Hacking with Swift / SwiftUI by Example](https://www.hackingwithswift.com/quick-start/swiftui)：大量短例子，适合查 API 用法。
- [Design+Code SwiftUI](https://designcode.io/)：偏视觉和动效，适合找设计感强的 SwiftUI demo。
- [Kavsoft](https://kavsoft.dev/)：高视觉密度 SwiftUI 动效教程，适合学 micro-interaction。
- [AppLayouts](https://www.applayouts.com/)：iOS/macOS SwiftUI 模板，适合看商业化 App 常见 screen pattern。
- [SwiftUI Lab](https://swiftui-lab.com/)：老但深入，适合理解 SwiftUI 行为边界。

### 真实 Mac App / 开源代码

- [CodeEdit](https://github.com/CodeEditApp/CodeEdit)：开源 macOS code editor，适合看大型原生 Mac App 如何组织 UI 和功能。
- [awesome-swift-macos-apps](https://github.com/jaywcjlove/awesome-swift-macos-apps)：Swift 写的开源 macOS App 集合。
- [open-source-mac-os-apps](https://github.com/serhii-londar/open-source-mac-os-apps)：更宽泛的开源 macOS App 集合，含 native 和 cross-platform。
- [swiftui-macos-resources](https://github.com/stakes/swiftui-macos-resources)：专门收集 SwiftUI for macOS 的资源。
- [TrozWare SwiftUI for Mac](https://troz.net/post/2025/swiftui-mac-2025/)：长期写 SwiftUI on Mac 的实战记录。
- [Nil Coalescing: Build a macOS menu bar utility in SwiftUI](https://nilcoalescing.com/blog/BuildAMacOSMenuBarUtilityInSwiftUI)：菜单栏工具的实用教程。

### UI 灵感网站

- [Mobbin](https://mobbin.com/)：真实产品 screen / flow 库，适合看信息架构、onboarding、settings、billing、empty state。
- [Page Flows](https://pageflows.com/)：按用户流程看产品设计，适合分析完整操作链路。
- [Refero](https://refero.design/)：Web / iOS / 产品界面参考，搜索体验较好。
- [Dribbble macOS app](https://dribbble.com/tags/macos-app)：视觉灵感多，但需要筛掉概念稿和不可实现的炫技稿。
- [Behance UI/UX](https://www.behance.net/search/projects/ui%20ux%20macos)：适合看完整 case study。
- [macOS Icon Gallery](https://www.macosicongallery.com/)：看 Mac App icon 语言。

### 值得直接研究的 Mac 产品官网

这些不一定是 SwiftUI 写的，但它们的产品截图、信息密度、窗口组织、command palette、toolbar、空状态和快捷操作值得看：

- [Raycast](https://www.raycast.com/)
- [Linear](https://linear.app/)
- [CleanShot X](https://cleanshot.com/)
- [Screen Studio](https://www.screen.studio/)
- [Things](https://culturedcode.com/things/)
- [Craft](https://www.craft.do/)
- [Sketch](https://www.sketch.com/)
- [Pixelmator Pro](https://www.pixelmator.com/pro/)
- [Setapp](https://setapp.com/)

看这些站时要分清两件事：官网营销页面的视觉风格，和 App 内的工作界面。做 Mac productivity App 时，真正有价值的是工作界面的密度、快捷键、菜单、toolbar、侧栏和状态反馈。

## 按场景选型

### 菜单栏工具 / 小型系统工具

推荐：`SwiftUI + MenuBarExtra + AppKit fallback + AppStorage/SwiftData + Sparkle`。

重点不是页面数量，而是系统行为：隐藏 Dock、退出入口、global hotkey、权限说明、launch at login、menu bar icon 状态、popover 尺寸、dark/light mode。

### 文档类 / 编辑器 / 知识工具

推荐：`SwiftUI + DocumentGroup / Document API + AppKit text/editor component + SwiftData/GRDB`。

富文本、代码编辑、多级 undo、拖放和文件协调这几件事要尽早验证。SwiftUI 可以承担壳、导航和面板，核心编辑器通常需要 AppKit 或成熟第三方组件。

### AI / Agent Mac App

两条路线都成立：

原生路线：`SwiftUI + App Intents + Foundation Models + 本地 helper / XPC / CLI`。适合 Apple ecosystem 深集成、隐私、本地推理、系统入口。

Web 桌面路线：`Electron` 或 `Tauri + Web UI + local runtime`。适合复杂 chat/workspace UI、终端、插件、MCP、跨平台和频繁迭代。仓库里已有一份本机 Codex Mac App 的技术记录，Codex 当前安装版就是 `Electron + Vite/React UI + Node app-server/CLI + SQLite + native macOS addon + Sparkle`。

### 商业 SaaS 的 Mac companion

推荐：优先看团队资产。如果主产品已经是 React/Web，`Electron` 或 `Tauri` 会快很多；如果 Mac 端是核心产品体验，原生 SwiftUI 更值得投入。

## 推荐阅读顺序

1. 先读 Apple HIG 的 macOS、toolbar、menus、settings、keyboard shortcut、sidebar。
2. 看 `WWDC26 SwiftUI Guide` 和 `Use SwiftUI with AppKit and UIKit`，确认当前 API 方向。
3. 用 `Explore SwiftUI` 查控件和 modifier 的视觉效果。
4. 从 `CodeEdit` 和 `awesome-swift-macos-apps` 找真实代码。
5. 用 Mobbin / Page Flows / Refero 看通用产品流程，用 Apple Design Awards 看平台级 polish。

## 来源索引

- Apple releases: https://developer.apple.com/news/releases/
- Xcode 27 beta release notes: https://developer.apple.com/documentation/xcode-release-notes/xcode-27-release-notes
- Swift 6.4: https://developer.apple.com/swift/whats-new/
- WWDC26 SwiftUI guide: https://developer.apple.com/wwdc26/guides/swiftui/
- Use SwiftUI with AppKit and UIKit: https://developer.apple.com/videos/play/wwdc2026/272/
- SwiftData: https://developer.apple.com/documentation/swiftdata
- Observation: https://developer.apple.com/documentation/observation
- Foundation Models / Apple Intelligence: https://developer.apple.com/apple-intelligence/
- App Intents: https://developer.apple.com/documentation/appintents
- MenuBarExtra: https://developer.apple.com/documentation/SwiftUI/MenuBarExtra
- Swift Testing: https://developer.apple.com/documentation/testing
- Sparkle: https://sparkle-project.org/documentation/
- TCA: https://github.com/pointfreeco/swift-composable-architecture
- GRDB: https://github.com/groue/GRDB.swift
- Tauri: https://v2.tauri.app/
- Electron: https://electronjs.org/
- Flutter macOS: https://docs.flutter.dev/platform-integration/macos/building
- React Native macOS: https://microsoft.github.io/react-native-macos/docs/getting-started
