# 第一层：系统工具链迁移决策与安装 Prompt

状态：待用户确认。本文只处理 CLI、语言运行时、构建工具和本地基础服务，不处理 GUI App、账号登录、SSH、项目仓库、Codex Skills 或个人数据。

## 决策原则

- 只声明直接依赖；Homebrew 自动解析的底层库不单独迁移。
- 全局 Node 统一使用 Homebrew Node，所有 CLI 安装到该全局环境，不使用 `sudo npm install -g`。
- 只固定确实存在兼容边界的 major version，例如 PostgreSQL 16；其余默认安装新机器当时的稳定版本。
- CLI 安装和账号认证分离。本层不复制 token，也不执行登录。
- 安装本地服务，但本层不自动启动常驻服务。

## 迁移决策表

| 分类 | 工具 | 当前来源 | 建议 | 原因 |
|---|---|---|---|---|
| 系统底座 | Xcode Command Line Tools | Apple | 迁移 | Homebrew、Git 和原生编译的前置条件 |
| 系统底座 | Homebrew + Bundle | Homebrew | 迁移 | 第一层声明式安装入口 |
| 版本控制 | `git` | Homebrew | 迁移 | 核心开发工具 |
| 版本控制 | `git-lfs` | Homebrew | 迁移 | 仓库可能包含 LFS 对象 |
| 版本控制 | `gh` | Homebrew | 迁移 | GitHub CLI；认证放到后续层 |
| Shell 工具 | `ripgrep` | Homebrew | 迁移 | Codex 和日常检索依赖 |
| Shell 工具 | `autojump` | Homebrew | 不迁移 | 非必需旧式 shell 增强，先保持新环境干净 |
| 通知 | `terminal-notifier` | Homebrew | 迁移 | 保留本机自动化和 Codex 通知能力 |
| 证书 | `mkcert` | Homebrew | 迁移 | 本地 HTTPS 开发需要；CA 在新机器重新生成 |
| 媒体处理 | `imagemagick` | Homebrew | 迁移 | 图片处理脚本和工具链需要 |
| Node | `node` / `npm` | Homebrew | 迁移 | 唯一全局 Node 环境和全局 CLI 底座 |
| Node 版本管理 | `fnm` | Homebrew | 不迁移 | 避免与 Homebrew Node 双轨；遇到项目版本约束再启用 |
| Python | `pyenv` | Homebrew | 迁移 | 保留多项目 Python 版本能力；本层暂不安装具体 Python 版本 |
| Go | `go` | Homebrew | 迁移 | 当前已有直接安装，保留 Go CLI/项目能力 |
| Ruby | `ruby` | Homebrew | 不迁移 | 不建立独立全局 Ruby；CocoaPods/Fastlane 由 Homebrew 管理 |
| Java | `openjdk` | Homebrew | 待确认 | 当前是非 LTS 版本，不应无条件复制到新机器 |
| Java | `openjdk@11` | Homebrew | 待确认 | 只为明确依赖 Java 11 的旧项目保留 |
| Java | `jenv` | Homebrew | 待确认 | 只有确认需要多 JDK 共存时才有价值 |
| Java | `maven` | Homebrew | 待确认 | 只有 Java/Maven 项目需要 |
| iOS/RN | `cocoapods` | Homebrew | 迁移 | iOS/RN 原生依赖安装 |
| iOS/RN | `fastlane` | Homebrew | 迁移 | iOS 构建、签名和发布流程 |
| RN | `watchman` | Homebrew | 迁移 | React Native 文件监听 |
| 本地服务 | `postgresql@16` | Homebrew | 迁移 | 保留确定的数据库 major version；本层不启动 |
| 本地服务 | `redis` | Homebrew | 迁移 | 本地服务链路需要；本层不启动 |
| AI CLI | `opencode` | Homebrew | 迁移 | 当前 AI 工具链组成部分 |
| 密钥工具 | `1password-cli` | Homebrew cask | 迁移 | 后续恢复 secrets 的入口；本层不登录 |
| 云工具 | `gcloud-cli` | Homebrew cask | 迁移 | GCP CLI；本层不登录 |
| Codex CLI | `@openai/codex` | npm global | 迁移 | 新机器执行后续迁移 Prompt 的核心工具 |
| 飞书 CLI | `@larksuite/cli` | npm global | 迁移 | 飞书工作流基础工具；本层不登录 |
| DevSpace | `@waishnav/devspace` | npm global | 迁移 | 当前 MCP/开发环境能力 |
| XURL | `@xdevplatform/xurl` | npm global | 迁移 | 只保留 npm 版本，避免重复安装 cask |
| 内部 CLI | `@xhs/codewiz-cc` | npm global | 迁移 | 当前工作流依赖；认证失败时记录并继续 |
| 内部 CLI | `@xhs/hi-cli` | npm global | 迁移 | 当前工作流依赖；认证失败时记录并继续 |
| 内部 CLI | `@xhs/skillhub-upload` | npm global | 迁移 | Skill 发布工作流依赖 |
| AI CLI | `agent-browser` | npm global | 迁移 | 浏览器自动化 CLI 能力 |
| Cloudflare | `cloudflared` | npm global | 迁移 | Tunnel/本地联调能力 |
| Expo | `eas-cli` | npm global | 迁移 | Expo 构建和发布能力 |
| Cloudflare | `wrangler` | npm global | 迁移 | Workers 开发和部署能力 |
| 脚手架 | `degit` | npm global | 不迁移 | 低频工具，改为按需使用 `npx degit` |
| AI CLI | `@aisa-one/cli` | npm global | 待确认 | 当前用途尚未确认，不默认复制 |
| GUI 工具 | Flipper | Homebrew cask | 本层不迁移 | 放到第二层 App 清单 |
| GUI 工具 | React Native Debugger | Homebrew cask | 本层不迁移 | 放到第二层 App 清单 |
| XURL cask | `xurl` | Homebrew cask | 不迁移 | 与 npm 版本重复，且需要额外信任 tap |
| Homebrew taps | `xdevplatform/tap` 等 | Homebrew | 不迁移 | 第一层不引入非必要第三方 tap |
| 传递依赖 | OpenSSL、ICU、FFmpeg、Python formula 等 | Homebrew | 不单独迁移 | 由直接工具的依赖解析自动安装 |

## 给新电脑 Codex 的安装 Prompt

将下面整段发送给新电脑上的 Codex。它只执行表中“迁移”的项目；“待确认”和“本层不迁移”项目不会安装。

```text
你正在一台新的 Mac 上执行我的第一层环境恢复：系统工具链。请直接完成安装、验证和结果记录，不要只给操作建议。

边界：
1. 本层只安装 CLI、语言基础环境、构建工具和本地服务软件。
2. 不安装 GUI 开发 App，不克隆项目，不迁移 Codex Skills/记忆，不复制 SSH key、token、Keychain、浏览器状态或任何 secret。
3. 不执行 gh、gcloud、1Password、npm 私服、Lark、Cloudflare、Vercel 等账号登录。
4. 不启动 PostgreSQL、Redis 等常驻服务。
5. 不安装“待确认”项目：openjdk、openjdk@11、jenv、maven、@aisa-one/cli。
6. 不安装：autojump、fnm、独立 Homebrew Ruby、degit、xurl cask、Flipper、React Native Debugger、第三方 Homebrew tap。

执行要求：
- 先检查 macOS 版本、CPU 架构和现有命令，采用幂等方式执行；已正确安装的项目不要重复破坏。
- 如未安装 Xcode Command Line Tools，触发官方安装流程。如果系统弹窗需要我操作，明确告诉我完成后如何继续，然后停止在该阻塞点。
- 如未安装 Homebrew，只能使用 Homebrew 官方安装脚本。Apple Silicon 使用 /opt/homebrew，Intel 使用 /usr/local。
- 将 brew shellenv 以幂等方式写入 ~/.zprofile，并让当前 shell 立即生效。不要重复追加相同配置。
- 使用 Homebrew Node 作为唯一全局 Node。不要安装 fnm/nvm，不要使用 sudo npm install -g。安装后确认 npm prefix -g 属于当前 Homebrew 前缀。
- Homebrew 只声明直接依赖，让 Homebrew 自动解析底层依赖。
- 遇到单个内部 npm 包因网络、公司私服或认证失败时，不得输出 ~/.npmrc 或 token，不得阻塞其他公开工具安装；记录失败项并继续。
- 不修改现有项目文件，不覆盖用户已有 shell 配置；必须修改时先备份并只做最小追加。

需要安装的 Homebrew formula：
git
git-lfs
gh
ripgrep
terminal-notifier
mkcert
imagemagick
node
pyenv
go
cocoapods
fastlane
watchman
postgresql@16
redis
opencode

需要安装的 Homebrew cask（虽然是 cask，但这里都是 CLI）：
1password-cli
gcloud-cli

需要安装到 Homebrew Node 全局环境的 npm CLI：
@openai/codex
@larksuite/cli
@waishnav/devspace
@xdevplatform/xurl
@xhs/codewiz-cc
@xhs/hi-cli
@xhs/skillhub-upload
agent-browser
cloudflared
eas-cli
wrangler

执行顺序：
1. 采集安装前状态，只记录版本、路径和是否存在，不读取 secret。
2. 安装/初始化 Xcode Command Line Tools 和 Homebrew。
3. 生成一个临时的、只含上述直接依赖的 Brewfile，执行 brew bundle；不要加入第三方 tap。
4. 确认 node 和 npm 来自 Homebrew，再分“公开 npm CLI”和“可能需要公司网络/认证的内部 CLI”两批全局安装。
5. 执行 git lfs install，但不要修改任何仓库。
6. 不运行 mkcert -install，因为它会修改系统信任库；只确认 mkcert 已安装。
7. 不启动 postgresql@16 和 redis，不执行 brew services start。
8. 运行完整 doctor，并把结果写到 ~/Documents/CodexMigration/layer-01-system-toolchain-report.md。

doctor 至少检查：
- xcode-select -p
- brew --version、brew doctor、brew bundle check --file=<本次生成的临时 Brewfile 路径>
- command -v 和版本：git、git-lfs、gh、rg、terminal-notifier、mkcert、magick、node、npm、pyenv、go、pod、fastlane、watchman、psql、redis-server、opencode、op、gcloud
- npm prefix -g
- npm ls -g --depth=0，并逐项确认上面的 npm CLI
- brew services list，确认 PostgreSQL 和 Redis 没有因本次操作被自动启动

最终回复必须包含：
- 成功安装项目
- 原本已存在项目
- 失败或跳过项目及准确原因
- 需要我后续手动完成的系统弹窗或认证事项
- report 文件绝对路径
- 明确说明没有安装哪些待确认项目、没有启动哪些服务、没有读取或迁移哪些 secrets

除 Xcode Command Line Tools 系统弹窗和真实权限阻塞外，不要停在计划阶段，继续执行到 doctor 和报告完成。
```

## 待确认项

在正式执行前，只需要确认下面四组判断是否调整：

1. 是否现在就安装 Java LTS；若需要，建议改为明确的 `openjdk@17` 或项目要求的版本，而不是复制当前非 LTS `openjdk`。
2. 是否保留 Java 11、jenv 和 Maven。
3. 是否确认 `@aisa-one/cli` 的用途并迁移。
4. 是否确实希望第一层安装 PostgreSQL 16 和 Redis，还是等项目层按需安装。
