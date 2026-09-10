# phone-harness 仓库分析

调查日期：2026-08-11  
上游仓库：[ShawnPana/phone-harness](https://github.com/ShawnPana/phone-harness)  
核对提交：[`4d2de7a`](https://github.com/ShawnPana/phone-harness/commit/4d2de7a4b8780a386545c986543c83dda66764dd)

## 结论

`phone-harness` 是一层让 Coding Agent 操作真实 iPhone 的本地控制桥。它没有接入 iOS 内部 UI 树，也没有在手机里安装 Agent。它把 macOS 的 iPhone Mirroring 窗口当成唯一传输面：截取窗口、用 Apple Vision OCR 识别文字与坐标，再向镜像窗口注入点击、拖动和键盘事件。

它相对人工操作的核心价值是把高层意图变成可重复脚本，并允许 Agent 在每一步重新截图验证。代价是语义、速度、可靠性和安全确认都弱于人直接操作。它更适合低风险、重复性强、只能在 iPhone 完成的最后一公里任务；不适合作为稳定的 iOS 自动化测试框架，也不适合当前就托管付款、发消息、删除、改账号设置等高风险动作。

当前不建议直接按主分支安装。仓库创建时间很短，没有 release、自动化测试或 CI；主分支存在安装依赖错误、中文 macOS 窗口发现失败、锁屏状态误判和 doctor 假成功等已知问题。徐昊当前机器为中文 macOS 27.0，这会同时命中本地化窗口名问题，并扩大私有 SkyLight API 在新系统上失效的风险。

## 它实际做了什么

主链路如下：

1. `CGWindowListCopyWindowInfo` 查找 iPhone Mirroring 窗口。
2. `CGWindowListCreateImage` 或 `screencapture` 截取该窗口。
3. Apple Vision `VNRecognizeTextRequest` 将可见文字转成全局屏幕坐标。
4. `tap_text()`、`open_app()`、`scroll_collect()` 等 helper 将坐标和动作组合成脚本。
5. 每次动作后重新截图或 OCR，靠画面变化判断完成。

仓库当前默认使用 `background.py`。鼠标动作通过 macOS 私有 SkyLight API `SLPSPostEventRecordTo` 直接向 iPhone Mirroring 进程投递事件，键盘通过 `CGEventPostToPid` 投递。这让镜像窗口无需抢占前台，但也把兼容性建立在未公开、可能随 macOS 版本变化的私有事件记录布局上。设置 `PHONE_HARNESS_BACKGROUND=0` 才会退回公开 Quartz API；退回后每次输入都需要把镜像窗口切到前台。

CLI 本身很薄：它读取 stdin，然后在预导入 helper 的 Python 全局命名空间中直接 `exec()`。因此它的可扩展性来自任意 Python，而不是受约束的动作协议。`agent-workspace/agent_helpers.py` 还会在每次运行时自动加载，方便 Agent 自己补 helper，同时也扩大了可执行代码与审计范围。

## 和人工直接操作的区别

| 维度 | 人工直接操作 | phone-harness |
|---|---|---|
| 感知 | 连续画面、图标语义、上下文和手感一起判断 | OCR 文本框 + 截图；没有 iOS accessibility tree |
| 输入 | 真实触控、多点触控、Face ID、相机、触觉反馈 | 鼠标/键盘事件映射；不支持多点触控、相机和 Face ID 流程 |
| 速度 | 连续操作，反馈近乎实时 | 截图 → OCR → 动作 → 等待稳定；每步通常更慢 |
| 容错 | 人会即时发现弹窗、动画、焦点变化 | 重名文字、移动元素、语言变化、空 OCR 会造成误点或误判 |
| 重复任务 | 容易疲劳，难以复现完整过程 | 脚本、循环、长列表采集和固定流程更有优势 |
| 可审计性 | 主要靠人记忆或录屏 | 可以保存脚本和中间结果，但仓库当前没有内建动作日志或 receipt |
| 安全确认 | 人在每一步自然确认 | Skill 文本要求高风险动作前询问，代码层没有硬门禁 |
| 运行边界 | 手机在手即可 | 依赖 Mac、iPhone Mirroring、配对、锁屏状态、窗口状态和 TCC 权限 |

这里最重要的区别是：人工操作属于实时闭环；`phone-harness` 属于离散的截图—动作循环。它能把操作交给 Agent，却没有获得 Appium、XCUITest 或 WebDriverAgent 那种结构化控件树和稳定 selector。OCR 坐标只是当前画面上的临时定位结果。

如果“直接操作”指让 Codex 直接用通用 Computer Use 点 iPhone Mirroring，那么 `phone-harness` 的增量主要有三点：一是把 OCR 坐标和点击封装成可调用函数；二是提供 `scroll_collect()`、`wait_stable()` 等手机特定经验；三是可以在后台投递事件。通用 Computer Use 更直观，但每次任务都要重新理解画面；Harness 更容易复用和循环。二者仍共享同一个根本限制：看到的是视频窗口，而不是 iOS 的真实 UI 结构。

## 当前主分支的关键风险

### 1. 干净安装当前会失败

`pyproject.toml` 和 `install.md` 引用了不存在的 `pyobjc-framework-AppKit`。正确承载 `AppKit` 与 `Foundation` 的包是 `pyobjc-framework-Cocoa`；Fast Path 还漏装了 `pyobjc-framework-ApplicationServices`。本机通过 `pip index` 复核，前者没有可用发行版。见 [issue #3](https://github.com/ShawnPana/phone-harness/issues/3) 和 [PR #11](https://github.com/ShawnPana/phone-harness/pull/11)。

### 2. 中文 macOS 无法发现窗口

主分支用英文字符串 `iPhone Mirroring` 匹配 `kCGWindowOwnerName`。中文 macOS 返回本地化名称，因此 `find_window()` 会误报 `no-window`。当前机器的首选语言是 `zh-Hans-CN`，会直接命中这一问题。按 PID 匹配的修复仍在 [PR #18](https://github.com/ShawnPana/phone-harness/pull/18) 中。

### 3. 连接状态可能被误判为 ready

主分支只靠少数英文 OCR 关键词判断暂停/断连画面。[issue #5](https://github.com/ShawnPana/phone-harness/issues/5) 已验证 Mac 登录锁屏可能被判定为 `ready`，随后 Agent 会把文本输入密码框。PR #18 正在改为结合 macOS accessibility 结构判断，但尚未合入。

### 4. doctor 的成功结论不可信

窗口发现的失败没有折叠进最终 `ok`，部分依赖也在 PASS 之后才导入。因此 doctor 可以显示 FAIL 后仍输出 `all clear`，或直接 traceback。见 [issue #4](https://github.com/ShawnPana/phone-harness/issues/4)。

### 5. 后台模式依赖私有 API

默认后台输入依赖 SkyLight 私有符号和硬编码的 `0xf8` 事件缓冲区偏移。作者已提供公开 Quartz fallback，但没有针对 macOS 27 的兼容性证明。当前机器比 issue 中验证的 macOS 25/26 更新，安装后仍需要真机 smoke，不能从静态代码推断可用。

### 6. 安全规则属于提示词约束

Skill 规定发送、购买、删除、改设置前必须询问，但 `tap()`、`type_text()` 和 stdin `exec()` 没有代码级确认、app allowlist、动作分级、dry-run 或审计 receipt。Terminal/Agent Host 还需要 Accessibility 与 Screen Recording 权限，这些权限覆盖面大于 iPhone 镜像窗口本身。

临时截图默认落在系统临时目录的固定文件名中，运行后不会主动删除；手机上显示的验证码、消息或账号信息可能留在本地临时文件，直到被覆盖或系统清理。

### 7. 工程成熟度有限

核对时仓库创建约三天，默认分支约 1,400 行，没有测试目录、GitHub Actions 或 release。静态 `compileall` 通过，只能证明 Python 语法成立，不能证明依赖安装、TCC 权限、窗口发现、OCR 或真机动作链路成立。

## 适用场景

较合适：

- 读取 iOS-only App 中低敏感信息，并由 Agent 汇总。
- 批量浏览长列表、重复打开页面、收集可见文本。
- 做真实 iPhone 上的探索性 UI smoke，最后由人复核。
- 在明确的测试账号、测试数据和低风险 App 中执行重复流程。

不合适：

- 付款、转账、下单、发消息、发帖、删除内容、改账号或系统设置。
- 需要 Face ID、相机、DRM 视频、多点触控的流程。
- 需要稳定 selector、断言、并行设备和 CI 的正式自动化测试。
- 需要持续无人值守运行的个人手机任务。

## 建议

现在先不要把上游 `main` 直接注册成自动触发 Skill。可以等待安装修复和 PR #18 合并后，再做一个受控试用；或者在独立 venv 中固定 commit，并关闭默认后台模式，先验证公开 Quartz 路径。

试用时把能力合同限制为：只读/导航默认允许；任何输入、提交、发送、购买、删除、设置变更都要求逐次确认；使用测试账号或非敏感 App；每一步保留动作前后截图摘要；结束时清理临时截图；Agent Host 的 TCC 权限按真实进程主体授予并能随时撤销。

若目标是稳定测试自家 App，优先使用 XCUITest/WebDriverAgent；若目标是偶尔让 Agent 处理真实手机上的最后一公里任务，`phone-harness` 的方向有价值，但应该把它视为实验性个人自动化桥，而不是已经成熟的手机执行基础设施。
