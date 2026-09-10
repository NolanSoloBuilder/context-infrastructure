# Pi 与 MkAgent 本地启动

2026-09-09，按用户要求安装并打开两个应用，未修改项目代码、切换分支或提交。

- Pi：全局 npm 安装 `@earendil-works/pi-coding-agent`，版本 `0.85.1`，安装时使用 `--ignore-scripts`。命令 `/opt/homebrew/bin/pi`，在 Terminal 中启动；进程已确认运行。体验目录 `/Users/xuhao/Documents/pi-agent-playground`。Terminal 不允许 CUA 读取，因此未验证其可见界面或模型调用。
- MkAgent：官方 GitHub Release `v0.1.1` 的 Apple Silicon ZIP，SHA-256 与官方 `SHA256SUMS` 一致。安装位置 `/Applications/MkAgent.app`，bundle ID `app.mkagent.desktop`。已通过 CUA 确认中文欢迎界面；随后用户操作进入 ChatGPT 连接流程，停止进一步点击，交给用户完成登录。未验证模型回复。

再次启动：终端执行 `pi`；或从 Applications 打开 MkAgent。

官方来源：https://github.com/earendil-works/pi 、https://github.com/MkThingsHQ/mkagent/releases/tag/v0.1.1 。

## 登录卡住的恢复

同日用户反馈已授权但持续连接中。Chrome 回调页显示授权成功，MkAgent 仍等待。重新加载旧回调后，应用显示 `ChatGPT OAuth flow expired`。从应用重新发起登录，使用已有账户完成授权，再刷新当前回调页面后，MkAgent 成功进入 Default 工作区与会话列表。已验证界面登录完成，尚未验证模型实际回复。旧流程过期已确认；首次回调未及时完成的更深原因尚未确认。未修改应用代码或订阅配置，未记录授权码或令牌。

## 定制判断

当前官方 LICENSE 为 Apache-2.0，允许修改和商业分发，分发时需遵守许可证、修改声明及适用 NOTICE 等要求。基于官方架构文档判断：界面、提示词、Skills 和已支持的模型连接定制相对容易；新增业务工具与 API 集成需要贯穿工具执行和权限；团队账号、云同步、多租户隔离、远程运行及替换 Agent 后端涉及更大改造。前端使用 React，桌面壳为 Electron，运行时为 Bun/Pi。个人桌面工作台是较匹配的定制方向，企业协作平台不能仅按 UI 改造估算。此处为架构层判断，尚未进行完整源码可维护性审计。

核验来源：https://github.com/MkThingsHQ/mkagent/blob/main/LICENSE 、https://github.com/MkThingsHQ/mkagent/blob/main/docs/architecture.md 。

## ChatGPT 订阅接入机制（本机 v0.1.1 代码核验）

`dist/main.cjs` 的 `chatgpt-oauth-config.ts` 使用 Codex CLI 公共 OAuth client ID，授权端点为 `auth.openai.com/oauth/authorize`，回调为 `localhost:1455/auth/callback`。`prepareChatGptOAuth` 生成 state 与 PKCE challenge/verifier；`exchangeChatGptTokens` 用授权码和 verifier 向 OAuth token 端点兑换令牌，并有 refresh token 刷新逻辑。`bootstrap-preload.cjs` 的 `startChatGptOAuth` 负责本地回调服务、打开浏览器，再通过 `chatgpt.COMPLETE_OAUTH` 完成服务端流程。Pi subprocess 内 `openaiCodexProvider` 使用 `openai-codex` provider、`https://chatgpt.com/backend-api` base URL 和 Codex Responses 协议适配器。此链路使用 Codex 订阅访问能力，不是模拟网页聊天，也不是将订阅兑换成通用 API 额度。技术实现已核验，不据此推断第三方商业再分发的授权范围或服务承诺。

## GitHub fork 与本地源码

按用户要求创建 `NolanSoloBuilder/mkagent` fork，并克隆到 `/Users/xuhao/Documents/Other/mkagent`。`origin` 指向个人 fork，`upstream` 指向 `MkThingsHQ/mkagent`。初始检出 `main`，HEAD `1890e70f282ad0989a17326335877b85515df7ea`，工作区干净。此次仅获取源码，未安装依赖、修改源码或创建需求分支；后续代码任务需另行确认分支绑定。
