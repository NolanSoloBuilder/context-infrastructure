---
title: AIsa API / Skills / LLM Gateway 接入指南
category: API Guide
tags: [aisa, llm-gateway, agent-skills, api-key, search, models]
difficulty: Medium
created: 2026-06-17
updated: 2026-06-17
---

# AIsa API / Skills / LLM Gateway 接入指南

## When to Use

当需要在本机 agent 环境里接入 AIsa 的统一 LLM gateway、AIsa Agent Skills、search / scholar / Tavily / Perplexity 等资源时使用本指南。

本指南基于 `https://aisa.one/docs/llms.txt` 及其引用文档整理。AIsa 的模型列表和价格会变化，生产路由前要重新看 `https://aisa.one/models` 或 AIsa dashboard。

## 当前本机状态

已完成：

- 已安装 AIsa CLI：`aisa`，版本 `0.2.0`
- 已安装到 Codex skill root：`~/.agents/skills/llm-router`
- 已安装到 Codex skill root：`~/.agents/skills/multi-source-search`
- 两个 skill 的脚本都已通过 `--help` 验证
- AIsa key 启用后，`aisa models` 已验证可列出 81 个模型
- `qwen-flash` 和 `deepseek-v4-flash` 的 chat completion smoke test 已验证成功
- `multi-source-search` 的 web search smoke test 已验证成功

未完成：

- 未登录 AIsa CLI

本机注意事项：

- 当前 `python3` 的默认 OpenSSL cafile 为空，运行 AIsa skill 脚本时需要加 `SSL_CERT_FILE=/etc/ssl/cert.pem`。
- `gpt-5-mini` 当前会返回上游 OpenAI organization verification 限制；日常 smoke test 先用 `qwen-flash`。

新开 Codex session 后，`llm-router` 和 `multi-source-search` 才会进入自动 skill discovery。

## 安全原则

1. 不把 `AISA_API_KEY` 写进仓库、`.zshrc`、脚本参数或聊天记录。
2. 本地优先用 1Password secret reference 加 `op run` 按进程注入。
3. AIsa key 应按用途拆分：`codex-local`、`ci-tests`、`prod-service` 分开创建。
4. 创建 key 时设置低额度 spend cap 和模型 allowlist；本地测试 key 默认只开低成本模型。
5. 真实调用前先跑低成本、短输出 smoke test，再扩大到搜索、研究或多模型比较。
6. Twitter 发帖、邮件发送、portfolio 修改、交易相关动作默认视为有副作用，除非用户明确授权，否则只读使用。

## API Key 配置

AIsa docs 规定所有 API 用同一个 Bearer token：

```bash
Authorization: Bearer $AISA_API_KEY
```

推荐在仓库外创建 1Password env file：

```bash
mkdir -p ~/.config/op
chmod 700 ~/.config/op
```

然后在 `~/.config/op/env.aisa` 写入 secret reference，而不是明文 key：

```dotenv
AISA_API_KEY=op://dev/dev-api-keys/aisa_api_key
```

文件权限：

```bash
chmod 600 ~/.config/op/env.aisa
```

使用时按命令注入：

```bash
op run --env-file ~/.config/op/env.aisa -- aisa whoami
op run --env-file ~/.config/op/env.aisa -- env SSL_CERT_FILE=/etc/ssl/cert.pem python3 ~/.agents/skills/llm-router/scripts/llm_router_client.py chat --model qwen-flash --message "Reply with: ok"
```

如果暂时不用 1Password，也可以只在当前 shell 注入：

```bash
export AISA_API_KEY="sk-aisa-..."
aisa whoami
```

不要把这行写进仓库文件。

## LLM Gateway

AIsa 的 OpenAI-compatible base URL 是：

```txt
https://api.aisa.one/v1
```

Chat Completions endpoint：

```txt
POST https://api.aisa.one/v1/chat/completions
```

最小 `curl` smoke test：

```bash
op run --env-file ~/.config/op/env.aisa -- curl -sS https://api.aisa.one/v1/chat/completions \
  -H "Authorization: Bearer $AISA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen-flash",
    "messages": [{"role": "user", "content": "Reply with exactly: ok"}],
    "stream": false,
    "max_tokens": 8
  }'
```

Python SDK 方式：

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["AISA_API_KEY"],
    base_url="https://api.aisa.one/v1",
)

response = client.chat.completions.create(
    model="qwen-flash",
    messages=[{"role": "user", "content": "Reply with exactly: ok"}],
    max_tokens=8,
)
print(response.choices[0].message.content)
```

Claude native Messages endpoint：

```txt
POST https://api.aisa.one/v1/messages
```

Gemini native endpoint：

```txt
POST https://api.aisa.one/v1/models/{model}:generateContent
```

日常优先用 `/v1/chat/completions`，只有需要 Anthropic native features 或 Gemini native payload 时再切 native endpoint。

## 模型选择

从 AIsa 2026-06-04 静态 catalog 看，常用起点：

- 低成本常规文本：`qwen-flash`、`deepseek-v4-flash`、`gpt-5-mini`
- 编程 / agentic coding：`gpt-5.3-codex`、`qwen3-coder-plus`、`claude-opus-4-8`
- 长上下文中文或双语：`qwen3.7-max`、`qwen3.6-plus`、`MiniMax-M3`
- 视觉 / 文档：`qwen3-vl-plus`、`gpt-5.4`、`claude-opus-4-8`

注意：

- 不要臆造 model id，必须查 AIsa live catalog 或 `docs/guides/models.md`。
- 不要默认用最贵模型做 smoke test。
- 如果 key 配了 model allowlist，`403 model_not_allowed` 说明配置和请求模型不匹配。

## Agent Skills

已安装的两个 AIsa skills：

```bash
aisa skills install llm-router --agent codex
aisa skills install multi-source-search --agent codex
```

实际落点：

```txt
~/.agents/skills/llm-router
~/.agents/skills/multi-source-search
```

`llm-router` 的脚本入口：

```bash
python3 ~/.agents/skills/llm-router/scripts/llm_router_client.py --help
SSL_CERT_FILE=/etc/ssl/cert.pem python3 ~/.agents/skills/llm-router/scripts/llm_router_client.py chat --model qwen-flash --message "Reply with exactly: ok"
SSL_CERT_FILE=/etc/ssl/cert.pem python3 ~/.agents/skills/llm-router/scripts/llm_router_client.py compare --models "qwen-flash,deepseek-v4-flash" --message "Explain API gateways in one sentence."
```

`multi-source-search` 的脚本入口：

```bash
python3 ~/.agents/skills/multi-source-search/scripts/search_client.py --help
SSL_CERT_FILE=/etc/ssl/cert.pem python3 ~/.agents/skills/multi-source-search/scripts/search_client.py web --query "AIsa agent skills"
SSL_CERT_FILE=/etc/ssl/cert.pem python3 ~/.agents/skills/multi-source-search/scripts/search_client.py scholar --query "agent skills specification" --year-from 2024
SSL_CERT_FILE=/etc/ssl/cert.pem python3 ~/.agents/skills/multi-source-search/scripts/search_client.py sonar-pro --query "Compare OpenRouter and AIsa with citations"
```

真实调用时用：

```bash
op run --env-file ~/.config/op/env.aisa -- env SSL_CERT_FILE=/etc/ssl/cert.pem python3 ~/.agents/skills/multi-source-search/scripts/search_client.py web --query "AIsa agent skills" --count 5
```

## Search / Data APIs

AIsa 的非 LLM capability 多数走：

```txt
https://api.aisa.one/apis/v1/...
```

常用只读 endpoints：

- Web search：`POST /apis/v1/scholar/search/web`
- Scholar search：`POST /apis/v1/scholar/search/scholar`
- Smart / hybrid search：`POST /apis/v1/scholar/search/smart` 或文档里的 mixed 变体，调用前以 skill 脚本和 API reference 为准
- Tavily search：`POST /apis/v1/tavily/search`
- Tavily extract：`POST /apis/v1/tavily/extract`
- Perplexity Sonar：`POST /apis/v1/perplexity/sonar`
- Perplexity Sonar Pro：`POST /apis/v1/perplexity/sonar-pro`
- Perplexity Deep Research：`POST /apis/v1/perplexity/sonar-deep-research`

调研场景优先用 `multi-source-search` skill，因为它已经封装了 citation 和常见参数。

## 错误处理

AIsa error response 使用：

```json
{
  "error": {
    "type": "authentication_error",
    "code": "invalid_api_key",
    "message": "...",
    "request_id": "req_..."
  }
}
```

处理规则：

- `400` / `422`：请求参数问题，修 payload，不自动重试。
- `401`：缺 key、key 错、key revoked，检查 `AISA_API_KEY`。
- `403`：权限、模型 allowlist 或区域限制，检查 key scope。
- `404`：endpoint 或 model id 错，回到 docs / model catalog。
- `429`：遵守 `Retry-After`，指数退避加 jitter。
- `5xx`：可短重试 3-5 次，仍失败时保留 `request_id`。

流式请求的 idle timeout 是 60 秒；客户端 read timeout 建议设到 120 秒。

## 速查

```bash
# CLI 状态
aisa --version
aisa skills list
aisa skills show llm-router
aisa skills show multi-source-search

# 鉴权状态
op run --env-file ~/.config/op/env.aisa -- aisa whoami

# 低成本 LLM smoke test
op run --env-file ~/.config/op/env.aisa -- env SSL_CERT_FILE=/etc/ssl/cert.pem python3 ~/.agents/skills/llm-router/scripts/llm_router_client.py chat --model qwen-flash --message "Reply with exactly: ok"

# 只读搜索 smoke test
op run --env-file ~/.config/op/env.aisa -- env SSL_CERT_FILE=/etc/ssl/cert.pem python3 ~/.agents/skills/multi-source-search/scripts/search_client.py web --query "AIsa agent skills" --count 5
```

## 参考文档

- `https://aisa.one/docs/llms.txt`
- `https://aisa.one/docs/guides/getting-started-with-aisa.md`
- `https://aisa.one/docs/guides/authentication.md`
- `https://aisa.one/docs/guides/security.md`
- `https://aisa.one/docs/guides/models.md`
- `https://aisa.one/docs/agent-skills/quickstart.md`
- `https://aisa.one/docs/agent-skills/standards.md`
- `https://aisa.one/docs/api-reference/chat/createchatcompletion.md`
- `https://aisa.one/docs/api-reference/chat/createmessage.md`
- `https://aisa.one/docs/api-reference/chat/generatecontent.md`
- `https://aisa.one/docs/api-reference/rate-limits.md`
- `https://aisa.one/docs/api-reference/errors.md`
