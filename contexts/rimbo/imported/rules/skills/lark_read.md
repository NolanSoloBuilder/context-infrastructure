# Skill: lark_read

让 AI 安全、低成本地读 Lark / 飞书文档。

## When to Use

- caller 提到「上次会议纪要」「Lark 上的某个产品文档」
- 写 PRD / 调研报告时需要引用 Lark wiki 里的现存讨论
- 做 deep research 类任务时需要同时检索仓库内产物 + Lark 知识库

## 路径选择：镜像 → lark-cli → fallback

按这个顺序尝试，越靠前越省成本：

1. **镜像（零成本，零延迟）**：`contexts/lark_mirror/<space>/`。如果目标文档在镜像里，且镜像 `_meta.json.last_synced_at` 是几小时内（默认 6h 内），直接读本地 md 文件
2. **lark-cli 实时拉（主路径）**：caller OAuth 个人身份，`tools/lark_cli/pull.sh`，接受 docx URL / wiki URL / obj_token
3. **fallback Python 路径**：仅当 lark-cli 不可用（未授权、token 过期 7 天 + 没 refresh、需要 app 身份的场景）时，回落到 `tools/lark/lark_doc_pull.py`。**该路径未充分验证**，慎用

## 怎么找 obj_token

obj_token 是 Lark 文档 URL 里的 25-32 位字符串。例：

```
https://example.feishu.cn/docx/Abcdefg1234567890
                                ^^^^^^^^^^^^^^^^ 这就是 obj_token
```

如果 caller 给了 URL，AI 自己从 URL 里抠。如果只有标题，先在 `contexts/lark_mirror/` 里 `grep -r "<标题>"` 找镜像版本，从镜像首行 `<!-- lark-mirror obj_token=... -->` 里拿 token。

## 步骤

```bash
# 1) 看镜像新鲜度
cat contexts/lark_mirror/<space>/_meta.json | grep last_synced_at

# 2a) 镜像够新，直接读
cat contexts/lark_mirror/<space>/<title>.md

# 2b) 镜像不够新或不存在 → lark-cli 主路径
./tools/lark_cli/pull.sh <obj_token> /tmp/lark-pull.md
cat /tmp/lark-pull.md
rm /tmp/lark-pull.md  # 用完即丢

# 2c) lark-cli 失败时的 fallback（用户未授权 / cron 环境）
python -m tools.lark.lark_doc_pull --doc-id <obj_token> --out /tmp/lark-pull.md
```

如果首次使用、`npx --no-install lark-cli` 报 "command not found"，引导 caller 走 `setup_guide.md` Step 2.5 完成授权。

## 触发同步（按需）

如果发现 `lark_mirror/` 严重过期（>24h），可以手动触发一次同步。同步走 `periodic_jobs/lark_sync/`，背后是 `tools/lark/` fallback 路径（tenant_access_token，能跑 cron 也能手动）：

```bash
python3 periodic_jobs/lark_sync/run.py --space-id <space_id>
```

同步产物会走 `workflow_publish`，由发布 skill 接手 commit + PR。**绝不在普通对话里直接把镜像更新 commit 进去**——会污染单作者 cron 的产物归属。

## 隐私边界

Lark 上的内容大多是团队内部信息：

- 引用时**用「我们的会议纪要里说...」之类的表述**，不要把整段原文复制到对外发的产物里（公开博客、对外邮件等）
- 涉及人事 / 财务 / 客户敏感信息的文档，AI 读了之后**只在当前 session 内使用**，不要 append 到 OBSERVATIONS.md，不要写到 `contexts/memory/people/<handle>/`（这部分会进 git 历史）
- 不确定是否敏感时直接问 caller
- **OAuth 身份的副作用**：lark-cli 用 caller 个人账号读取，能读到的文档由其 Lark 权限决定。如果拿到一份"超出 caller 工作范围"的文档（比如误点到 HR 群文档），主动提醒是否真的需要读

## 错误处理

| 错误 | 处理 |
|---|---|
| `lark-cli: command not found` / `npx --no-install` 报错 | 引导 caller 走 `setup_guide.md` Step 2.5 装 lark-cli + 授权 |
| `auth: not logged in` 或 `tokenStatus: invalid` | `npx lark-cli auth login --domain docs,wiki,drive,im,contact` |
| `permission denied`（lark-cli） | caller 个人账号没有该文档权限，提醒在 Lark 端申请 |
| `LarkAPIError [99991663]` Permission denied（Python fallback） | 应用没拿到该文档权限，提醒在 Lark 后台给应用加访问权限 |
| `LarkAPIError [1254005]` doc not found | obj_token 错或被删，让 caller 确认 URL |
| Python fallback `runtime error: LARK_APP_ID / LARK_APP_SECRET 未配置` | 配 `.env` 或 1Password vault（见 `tools/lark/README.md`） |

## 关联

- [`tools/lark_cli/README.md`](../../tools/lark_cli/README.md) — 主路径（OAuth 个人）
- [`tools/lark/README.md`](../../tools/lark/README.md) — fallback Python 路径（tenant_access_token）
- [`rules/skills/lark_write.md`](./lark_write.md) — 写回 Lark 的特殊约束
- [`contexts/lark_mirror/README.md`](../../contexts/lark_mirror/README.md) — 镜像目录的只读约定
