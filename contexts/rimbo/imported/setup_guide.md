# Setup Guide: rimbo Work Context

新成员加入 rimbo workspace 的引导。每一步完成后立刻能感受到差异。

完整背景见 [`docs/RIMBO_REDESIGN.md`](docs/RIMBO_REDESIGN.md) 和 [`docs/COLLAB_PROTOCOL.md`](docs/COLLAB_PROTOCOL.md)。

---

## Step 0：clone 仓库（1 分钟）

```bash
git clone git@github.com:Mindspace-ai/rimbo-work-context.git
cd rimbo-work-context
```

如果你之前没配过 GitHub SSH key，先到 GitHub 个人设置加一把。

---

## Step 1：建立身份（必填，5 分钟）

**价值**：本机 AI 立刻能识别你是谁，加载你的 profile，写入归属正确。

### 1a. 写 `.me`

```bash
cp .me.example .me
$EDITOR .me
```

至少填 `handle`（团队内统一短名，如 `xu`、`alice`）。`git_email` 留空时 AI 会从 `git config user.email` 推断。`.me` 不进 git，每个人本机一份。

### 1b. 配置 git author

确保你的 commit 用本人邮箱：

```bash
git config user.name "你的名字"
git config user.email "你的邮箱"
```

**绝不在本机 commit 时假冒别人身份**——这是 `SOUL.md` 里写明的红线。

### 1c. 创建你的 member profile

```bash
cp rules/members/_template.md rules/members/<你的-handle>.md
$EDITOR rules/members/<你的-handle>.md
```

至少填：role、当前关注、沟通偏好、负责的产品 / 领域、避雷点（让 AI 别踩到的沟通方式）。

`rules/members/` 属敏感清单，需要走发布流程提交 PR：

```bash
# 跟 AI 说：「按 workflow_publish 把 rules/members/<handle>.md 发布出去」
# AI 会建分支 -> commit -> PR，等团队 review 后 merge
```

### 1d. 验证

merge 后，在 AI 对话里问「介绍一下你对我的了解」——AI 应当能准确说出你的 role、关注、偏好。如果不行，检查 `.me` 的 handle 和 `rules/members/<handle>.md` 是否对得上。

---

## Step 2：配置凭据（按需，10 分钟）

**价值**：能跑 Lark 集成、调用外部 API。

### 2a. `.env`（个人凭据）

```bash
cp .env.example .env
$EDITOR .env
```

`.env` 不进 git。填什么取决于你要跑什么：

- `LARK_APP_ID` / `LARK_APP_SECRET`：lark-cli 一次性 init 时填一遍（见 Step 2.5），以及 `tools/lark/` fallback 路径会用
- `OPENAI_API_KEY` 等：按需

团队共享的 Lark 应用凭据建议从 1Password 取（见 2b），不要落到个人 `.env` 里。

### 2b. 1Password CLI（团队共享凭据，推荐）

团队共享的凭据（如 Lark 应用 token、共用的 GitHub PAT）放在 1Password 团队 vault，本机用 `op` CLI 取。

```bash
brew install 1password-cli
op signin
```

具体用法见 [`rules/skills/bestpractice_api_key_management_1password_cli.md`](rules/skills/bestpractice_api_key_management_1password_cli.md)。

### 2c. `gh` CLI（必备）

发布流程用 `gh pr create`：

```bash
brew install gh
gh auth login
```

---

## Step 2.5：Lark 授权（PRD / wiki / IM 都依赖，10 分钟）

**价值**：本机 AI 能直接读 Lark 上的 PRD / 会议纪要 / wiki，能把仓库内定稿文档推回 Lark，能在群里发通知。这是 PRD 起草 / 评审 / 归档 / 状态变更四类流程的入口。

rimbo 用 [`@larksuite/cli`](https://github.com/larksuite/cli) 作为 Lark 主路径，**OAuth 个人身份**——你能读到的内容受你自己 Lark 账号的权限决定。

### 2.5a. 装 lark-cli

需要 Node ≥16。`@larksuite/cli` 在 `package.json` 的 devDependencies，仓库根：

```bash
npm install
```

之后通过 `npx lark-cli ...` 调用，不污染全局。

### 2.5b. 配 app（绑定开发者应用）

```bash
npx lark-cli config init --new --brand feishu --lang zh
```

> 国际版（larksuite.com）账号：`--brand lark`。下面浏览器同意页绑定后，CLI 会按账号实际所在租户自动校正。

命令会**阻塞**并在终端输出一段二维码 + 一个验证 URL（`https://open.feishu.cn/page/cli?user_code=...`）。在浏览器打开该 URL：

- 团队成员：选已有的 rimbo 团队应用（不存在则新建一个）
- 自己开发调试：选你自己的开发者应用

绑定成功后 CLI 会自动写入 `~/.lark-cli/config.json`（明文存 app_id 和 app_secret）。

### 2.5c. OAuth 登录（Device Flow）

```bash
npx lark-cli auth login --domain docs,wiki,drive,im,contact
```

`--domain` 这里是 Lark **业务域**（不是租户域），上面是 PRD 流程必需的最小集。命令会输出一个 device verify URL，浏览器打开后**勾选所有 scope** 完成同意。

> ⚠️ 即便授权成功，CLI 也可能因为同意页没勾全所有请求 scope 而 **exit code != 0** 并打印"授权结果异常"——只要 `lark-cli auth status` 返回 `tokenStatus: valid`，就忽略 exit code，授权已生效。

OAuth token + refresh token 写到 `~/.lark-cli/config.json`（不是 Keychain，是普通文件，权限 600）。token 有效期 2h，refresh token 7 天。

### 2.5d. 验证

```bash
npx lark-cli auth status        # 必须返回 tokenStatus: valid
npm run lark:whoami             # 返回 user_info（name / open_id）
```

两条都成功才算齐。失败常见原因：

- `not configured` → 跳过了 2.5b
- `tokenStatus: invalid` → 跳过了 2.5c，或 7 天没用 refresh token 过期了
- `permission denied` 调具体 API 时 → 2.5c 漏勾了对应业务域的 scope，重跑 `auth login` 补勾

### 2.5e. 常用命令一览

封装在 `tools/lark_cli/`：

```bash
# 拉文档为 markdown
./tools/lark_cli/pull.sh <obj_token>           # stdout
./tools/lark_cli/pull.sh <obj_token> tmp.md    # 写文件

# 推文档（前置：本地无未提交改动 + HEAD 已 push 到 origin/main）
./tools/lark_cli/push.sh <obj_token> path/to/file.md

# 发 IM 消息
./tools/lark_cli/im_send.sh <chat_id> "build green"
```

详见 [`tools/lark_cli/README.md`](tools/lark_cli/README.md)。

> **关于 fallback `tools/lark/`**：基于 tenant_access_token 的 Python 路径仅供 cron 等无人值守场景使用，**未在团队充分验证**，日常人工操作不要走这条。详见 [`tools/lark/README.md`](tools/lark/README.md)。

---

## Step 3：选 AI 客户端打开（1 分钟）

Codex / Claude Code / OpenCode / Cursor 任选。打开仓库后 AI 会按 [`AGENTS.md`](AGENTS.md) 加载 L3 全局约束，按 `.me` → `rules/members/<handle>.md` 识别你。

第一次打开后，让 AI 跑一遍：

> 读一下 AGENTS.md 和 SOUL.md，然后告诉我你识别到的 caller 是谁，今天打算怎么和我协作。

如果 AI 答得对，你就 setup 完成了。

---

## Step 4：理解写入流程（必读，10 分钟）

**这一步不写任何代码，但跳过它后续会出问题。**

读 [`rules/skills/workflow_publish.md`](rules/skills/workflow_publish.md) 和 [`docs/COLLAB_PROTOCOL.md`](docs/COLLAB_PROTOCOL.md)。要理解的核心点：

- **三类写入区域**：个人区域直接 commit / 共享区域 auto-merge / 敏感区域 PR + review
- **AI 不能直接 push main**——所有写入走分支 + PR
- **commit author 是你本人**，AI 是工具不是 contributor
- **OBSERVATIONS.md 是 append-only**，绝不修改历史条目
- **Lark 写回必须先经过 git**，不存在 AI 直接写 Lark 的路径

---

## Step 5：配置 cron 任务（可选，15 分钟）

**价值**：每天 / 每周自动跑 observer 和 reflector，沉淀团队记忆。

每个人本机各自配 cron。具体调度建议错开（避免 PR 集中），见 [`docs/COLLAB_PROTOCOL.md`](docs/COLLAB_PROTOCOL.md) 的 cron 调度表。

```bash
crontab -e
```

参考调度（按你的 handle 调整时间）：

```cron
# observer：每日 23:00 写自己的 people/<handle>/
0 23 * * * cd /path/to/rimbo-work-context && python3 periodic_jobs/ai_heartbeat/observer.py >> /tmp/rimbo-observer.log 2>&1

# reflector：每周一 8:00 蒸馏 + 提议晋升（PR）
0 8 * * 1 cd /path/to/rimbo-work-context && python3 periodic_jobs/ai_heartbeat/reflector.py >> /tmp/rimbo-reflector.log 2>&1
```

`periodic_jobs/ai_heartbeat/` 在 Phase 2 落地，目前为占位。先把 cron 框架记下，等脚本到位再启用。

> **Lark 相关 cron 走 fallback 路径**：lark-cli 主路径是 OAuth 个人身份，token 7 天内不调用就过期且只能交互式重授权，不适合无人值守。`periodic_jobs/lark_sync/` 等无人值守同步任务走 `tools/lark/`（tenant_access_token，应用身份），需要 `LARK_APP_ID` / `LARK_APP_SECRET` 在 cron 环境变量里可读。该路径未充分验证，建议先手动跑通再配 cron。日常人工操作（PRD、IM、读 wiki）不要走 cron，直接用 lark-cli 即可。

---

## Step 6：浏览 capabilities 和 skills（推荐，15 分钟）

**价值**：知道团队已经有哪些可调用的能力，避免重复造轮子。

- [`contexts/capabilities/INDEX.md`](contexts/capabilities/INDEX.md) — 团队当前所有 capability（如信源基础设施、内容打分服务）
- [`rules/skills/INDEX.md`](rules/skills/INDEX.md) — 当前所有 skill 分类

接下来工作中遇到「这事有没有现成的能力」时，先查 `capabilities/INDEX.md` 再动手。

---

## 何时你会感受到系统的价值

**配完 Step 1（立刻）**：AI 答你时直接以你的 role 和偏好为前提，不再泛化。

**用 2-3 周后**：`contexts/` 里开始有你和团队的 PRD / decision / research，AI 能引用上下文。

**用 1-2 个月后**：observer 识别出你的工作模式，reflector 把反复出现的判断蒸馏成 skill 或 axiom 提议。

**6+ 个月后**：团队的判断框架开始固化在 `rules/axioms/team/`，新成员入职时立刻能继承。

---

## 常见问题

**Q：我的 AI 客户端不在 Codex / Claude Code / OpenCode / Cursor 里怎么办？**
A：只要它支持读 `AGENTS.md` 或类似入口文件即可。如果不支持，把 `AGENTS.md` 内容粘到它的系统提示里也行。

**Q：`rules/members/<handle>.md` 一定要 PR 吗？不能直接 commit 吗？**
A：必须 PR。`rules/` 全目录属敏感清单——是 L3 全局约束，影响所有人本地的 AI 行为。

**Q：忘了走分支，直接在 main 上改了怎么办？**
A：`git stash`，`git checkout -b <分支名>`，`git stash pop`，再走正常发布流程。如果已经 commit，用 `git reset --soft HEAD~1` 退回再操作。

**Q：能不在本机配 cron，把 observer 跑在云上吗？**
A：不推荐。rimbo 的设计是「分布式 + git 同步」，没有常驻 agent 服务。每个人本机跑自己的 observer，写自己的 `people/<handle>/`，commit 推上去。

**Q：AI 写入时假冒了别人怎么办？**
A：这是红线。立刻 `git reset` 或重写 commit author，并把这件事写到团队的 OBSERVATIONS.md，让 AI 学到。

---

## 下一步

setup 完成后，真正的积累才开始。关键是持续把工作放在这里——PRD 起草、决策记录、用户调研、能力交付——让 git 历史和 AI 记忆共同沉淀团队认知。

详细的工作流见 [`docs/RIMBO_REDESIGN.md`](docs/RIMBO_REDESIGN.md) 第 3 节「个人工作流」。
