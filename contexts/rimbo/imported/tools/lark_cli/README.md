# tools/lark_cli — Lark CLI 主路径

基于 [`@larksuite/cli`](https://github.com/larksuite/cli) 的薄包装。这是 rimbo 集成 Lark 的**默认路径**：起草 PRD、推回文档、发 IM、读 wiki，AI 都从这里走。

> 与 `tools/lark/`（Python tenant_access_token 路径）的关系：lark-cli 是个人 OAuth 身份，覆盖人工交互场景；`tools/lark/` 仅作 fallback，用于无人值守 cron 等 lark-cli 不适用的场景。详情见 [`../lark/README.md`](../lark/README.md)。

## 安装

仓库根：

```bash
npm install
```

`@larksuite/cli` 在 `package.json` 的 devDependencies。安装后通过 `npx lark-cli` 调用，不污染全局。

## 一次性配置

### 1. 配 app（绑定开发者应用）

```bash
npx lark-cli config init --new --brand feishu --lang zh
```

`--brand feishu`（国内）或 `--brand lark`（国际版 larksuite.com）。命令会阻塞并在终端打印 user_code + 浏览器 URL（`https://open.feishu.cn/page/cli?user_code=...`），打开该 URL 选一个已有的开发者应用绑定（或新建）。完成后写到 `~/.lark-cli/config.json`。

### 2. OAuth 登录（Device Flow）

```bash
npx lark-cli auth login --domain docs,wiki,drive,im,contact
```

`--domain` 是 Lark **业务域**，不是租户域。上面是 PRD 流程必需的最小集；按需加 `calendar` / `mail` / `task` 等。

命令再次阻塞并打印 device verify URL，浏览器打开后**勾选所有请求的 scope**。

> ⚠️ 即便授权成功，如果同意页漏勾任意 scope，CLI 会以 exit code 3 打印"授权结果异常"。只要 `lark-cli auth status` 返回 `tokenStatus: valid`，就忽略 exit code——授权已生效。

token + refresh token 写到 `~/.lark-cli/config.json`（普通文件，**不是** macOS Keychain）。

### 3. 验证

```bash
npx lark-cli auth status        # tokenStatus: valid
npm run lark:whoami             # 拿 user_info
```

## 脚本入口

`tools/lark_cli/` 下的 shell 脚本是对常用命令的语义封装，AI 和人都从这里调：

| 脚本 | 作用 | 备注 |
|---|---|---|
| `pull.sh <doc-id> [out]` | 拉单文档为 markdown | `<doc-id>` 是 Lark URL 里的 obj_token；`out` 不指定输出 stdout |
| `push.sh <doc-id> <file>` | 推单文档（覆盖远端） | **内置 git clean 检查**，本地有未提交 / 未 push 的改动时会拒绝 |
| `im_send.sh [--no-tag] <chat-id> <text>` | 发 IM 文字消息（默认带 AI 标签） | 默认包装成 `[AI] <text>\n— <handle> / via lark-cli`；caller 手发不想被标 AI 时加 `--no-tag` |
| `whoami.sh` | 查当前登录身份 | OAuth 验证用 |

直接调原生命令也行：

```bash
# 拉文档（v2 + markdown）
npx lark-cli docs +fetch --doc <url-or-token> --doc-format markdown --api-version v2

# 推文档（覆盖整篇正文）
npx lark-cli docs +update --doc <url-or-token> --command overwrite \
    --content @path/to/file.md --doc-format markdown --api-version v2

# 发群消息
npx lark-cli im +messages-send --chat-id <oc_xxx> --text "build green"
```

但通过包装器走能保住 git 安全约束（push 场景）和团队约定的命名习惯。

## 设计要点

- **OAuth 个人身份**：每个开发者用自己的账号登录，能读到的内容受其 Lark 权限决定。如果 A 拉到的 PRD B 拉不到，是 Lark 端权限问题，不是 CLI bug
- **token 在 `~/.lark-cli/config.json`**：明文文件（含 app_secret + token）。cron 能读但 device flow 需要交互完成首次授权——首次必须人工跑一次。token 7 天内会自动 refresh
- **`push.sh` 的 git 守护**：Lark 写回前必须先 commit + push + merge 到 origin/main。这条约束写在 `rules/skills/lark_write.md` 里，包装器是它的执行点
- **wiki URL 也能用**：`docs +fetch` 接受 docx URL、wiki URL、纯 obj_token。包装器内部不做 URL 解析，直接传给 CLI

## 关联

- [`rules/skills/lark_read.md`](../../rules/skills/lark_read.md) — 怎么读 Lark
- [`rules/skills/lark_write.md`](../../rules/skills/lark_write.md) — 怎么写回 Lark（git 顺序约束）
- [`tools/lark/README.md`](../lark/README.md) — fallback Python 路径
- [`setup_guide.md`](../../setup_guide.md) — Step 2.5 的授权指引
