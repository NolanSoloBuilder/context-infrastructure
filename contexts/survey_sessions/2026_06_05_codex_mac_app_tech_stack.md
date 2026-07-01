# Codex Mac App 技术选型记录

日期：2026-06-05

这份记录基于本机 `/Applications/Codex.app` 的安装包、`Info.plist`、`app.asar`、运行进程和内置二进制做观察。它描述的是当前安装版本的技术事实，不等同于 OpenAI 官方架构文档；后续版本升级后需要重新验证。

## 结论

Codex Mac App 是一套 Electron 桌面应用。外壳负责窗口、系统权限、协议注册、更新和 Chromium 多进程运行；应用主体由 Vite 打包进 `app.asar`；本地 agent 能力由内置 `codex` CLI、`app-server`、Node runtime、PTY、SQLite 和 native addon 共同支撑。

一句话概括：它是 `Electron + Vite/React UI + Node app-server/CLI + 本地 SQLite + native macOS addon + MCP/工具子进程` 的桌面架构。

## 版本与基础信息

本机安装包信息来自 `/Applications/Codex.app/Contents/Info.plist`：

- App 版本：`26.602.30954`
- Bundle ID：`com.openai.codex`
- Bundle executable：`Codex`
- Chromium 版本：`149.0.7827.54`
- Bundle version：`3575`
- URL scheme：`codex://`
- 最低 macOS：`12.0`
- 更新框架：`Sparkle.framework`

`Info.plist` 里有 `ElectronAsarIntegrity`、`Resources/app.asar`、`BrowserCrApplication`、`Codex Framework.framework` 等字段。结合 bundle 结构和运行进程，可以确认它不是纯原生 App，而是 Electron/Chromium 外壳。

## 应用打包与前端层

`/Applications/Codex.app/Contents/Resources/app.asar` 是主体应用包。解析 `app.asar` header 后，顶层目录包括：

- `.vite/`
- `native-menu-locales/`
- `node_modules/`
- `package.json`
- `skills/`
- `webview/`

`app.asar` 内的 `package.json` 关键信息：

- package name：`openai-codex-electron`
- product name：`Codex`
- main：`.vite/build/bootstrap.js`
- Electron：`42.1.0`
- Vite：`8.0.3`
- 构建链路：`electron-forge` + `@electron-forge/plugin-vite`
- 测试链路：`vitest`、`playwright`

这说明 UI 和主进程代码经过 Vite/Electron Forge 构建后进入 `app.asar`。bundle 内还能看到 React 相关运行时代码痕迹，例如 `react-dom`、`useState`、`useEffect`、`createElement`。终端/会话相关 bundle 里有 `xterm` 代码痕迹，符合 Codex 内置终端和会话输出的产品形态。

## 本地运行时与工具链

`/Applications/Codex.app/Contents/Resources/` 里内置了几类关键二进制：

- `node`：本机版本为 `v24.14.0`
- `codex`：本机版本为 `codex-cli 0.137.0-alpha.4`
- `node_repl`
- `rg`：本机版本为 `ripgrep 15.1.0`
- `codex_chronicle`

运行进程里可以看到主应用之外还有多个 `codex app-server` 进程：

```text
/Applications/Codex.app/Contents/Resources/codex app-server --analytics-default-enabled
/Applications/Codex.app/Contents/Resources/codex app-server --listen stdio://
```

这说明桌面 App 并不只是在 renderer 里调用 API。它有本地 app-server/CLI 层，负责线程、工具、MCP、终端和本地状态等能力的编排。当前会话里还能看到 `node_repl` 和 MCP server 进程，例如 `tracking-kit` 通过内置 Node 启动。

## Native 模块与 macOS 集成

`app.asar.unpacked/node_modules` 和 `Resources/native` 里包含 native 能力：

- `node-pty`：终端 PTY
- `better-sqlite3`：本地 SQLite 状态库
- `objc-js`：JavaScript 调 Objective-C / macOS API
- `@worklouder/device-kit-oai`：外设集成
- `sparkle.node`
- `devicecheck.node`
- `browser-use-peer-authorization.node`
- `input-monitoring-permission.node`
- `remote-control-device-key.node`
- `sky.node`
- `native/bare-modifier-monitor`
- `native/launch-services-helper`

这层解释了 Codex 为什么能做很多普通 Web App 做不到的事：打开本地工程、跑终端、管理工具进程、调用系统权限、控制本机 App、处理输入监控权限、注册协议和更新。

## 权限与系统能力

`Info.plist` 里可以看到这些系统权限声明：

- `NSAppleEventsUsageDescription`：用于代表用户控制 Mac App
- `NSAppleScriptEnabled`
- `NSMicrophoneUsageDescription`
- `NSCameraUsageDescription`
- `NSAudioCaptureUsageDescription`
- `NSAppTransportSecurity.NSAllowsArbitraryLoads`
- `ASWebAuthenticationSessionWebBrowserSupportCapabilities`

它还声明了文件类型处理，包括 folder、CSV、TSV、XLS、XLSX 等。这和 Codex 可以打开 workspace、处理文档/表格类输入的体验一致。

更新上使用 Sparkle：

- `Sparkle.framework`
- `SUPublicEDKey`
- `codexSparkleFeedUrl`: `https://persistent.oaistatic.com/codex-app-prod/appcast.xml`

崩溃上报来自 Chromium Crashpad 和 Sentry 相关依赖。运行进程里能看到 `browser_crashpad_handler`，asar package 里有 `@sentry/electron` 和 `@sentry/node`。

## 运行时进程形态

运行中能看到典型 Electron/Chromium 多进程结构：

- 主进程：`/Applications/Codex.app/Contents/MacOS/Codex`
- Renderer：`Codex (Renderer)`
- GPU process：`Codex (Service) --type=gpu-process`
- Network utility：`--utility-sub-type=network.mojom.NetworkService`
- Storage utility：`--utility-sub-type=storage.mojom.StorageService`
- Audio utility：`--utility-sub-type=audio.mojom.AudioService`
- Crashpad handler
- `codex app-server`
- `node_repl`
- MCP server 子进程

这套进程形态说明 Codex 的桌面层和 agent 执行层是分开的。Electron 负责用户界面和系统集成，`codex app-server` 负责本地 agent runtime，工具与 MCP 再作为子进程挂在 runtime 后面。

## 依赖侧画像

`app.asar` 内保留的 `node_modules` 很少，主要是 native/runtime 依赖：

- `@worklouder/device-kit-oai`
- `better-sqlite3`
- `bindings`
- `file-uri-to-path`
- `node-addon-api`
- `node-pty`
- `objc-js`
- `tslib`

这意味着主前端和大部分 TypeScript 代码已经 bundle 进 `.vite/build/*.js`，未以完整源码/依赖树的形式散落在安装包里。需要调试 UI 依赖时，直接看 `node_modules` 会低估实际依赖；应以 `.vite/build` 和 source map 状态为准。

## 对产品架构的判断

Codex Mac App 的关键设计不是“把网页套进桌面壳”。更准确地说，它把三个层次组合在一起：

第一层是桌面容器。Electron 提供 Chromium UI、窗口生命周期、系统权限、URL scheme、文件关联、自动更新和 crash reporting。

第二层是本地 agent runtime。内置 `codex` CLI 和 `app-server` 运行在本机，负责线程状态、工具调用、终端、workspace、MCP 和本地数据库。`node-pty` 与 `better-sqlite3` 是这一层的关键基础设施。

第三层是外部能力桥接。MCP server、`node_repl`、浏览器控制、Computer Use、Apple Events、input monitoring、外设 integration 都通过子进程或 native addon 接到 runtime。这样做让 Codex 可以把本地系统视作 agent 的执行环境，而不是只把模型回复显示在聊天窗口里。

这也解释了为什么 Codex 的 Mac App 比普通 Web Chat 更重：它需要稳定地管理本地进程、权限、数据库、终端和工具调用，而这些能力天然属于桌面 runtime 的职责。

## 复核命令

后续版本升级后，可以用下面几组命令重新确认：

```bash
plutil -p /Applications/Codex.app/Contents/Info.plist
find /Applications/Codex.app/Contents/Resources -maxdepth 2 -type f | sort
/Applications/Codex.app/Contents/Resources/node --version
/Applications/Codex.app/Contents/Resources/codex --version
/Applications/Codex.app/Contents/Resources/rg --version
ps aux | rg '/Applications/Codex.app|com.openai.codex|Codex \\(Renderer\\)|codex app-server'
```

如果需要进一步分析 UI 依赖，可以解析 `app.asar` header，读取其中的 `package.json` 和 `.vite/build` 文件列表。这里要注意 Electron asar 的 header/data offset，直接 `strings app.asar` 会混出大量第三方 notice 和 bundle 字符串，只适合做快速线索扫描。
