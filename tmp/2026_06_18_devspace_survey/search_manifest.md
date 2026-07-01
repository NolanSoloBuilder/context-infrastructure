# DevSpace 调研 Search Manifest

日期：2026-06-18

## 产出文件索引

| 文件 | 路径 | 说明 |
|---|---|---|
| Scratchpad | `tmp/2026_06_18_devspace_survey/scratchpad.md` | 主线程研究笔记、claim extraction、本地验证记录 |
| Search Manifest | `tmp/2026_06_18_devspace_survey/search_manifest.md` | 本文件 |
| Clone | `tmp/2026_06_18_devspace_survey/repo` | `Waishnav/devspace` 浅克隆源码 |
| 最终报告 | `contexts/survey_sessions/2026_06_18_devspace_survey.md` | 面向后续决策复用的内部调研报告 |

## 主要来源

| 类型 | URL | 用途 |
|---|---|---|
| GitHub repo | https://github.com/Waishnav/devspace | 项目元数据、源码入口 |
| README | https://github.com/Waishnav/devspace/blob/main/README.md | 官方定位、安装方式、功能主张 |
| Release | https://github.com/Waishnav/devspace/releases/tag/v1.0.0 | 初始 release 描述 |
| npm package | https://www.npmjs.com/package/@waishnav/devspace | published package 版本核验 |
| Issue #2 | https://github.com/Waishnav/devspace/issues/2 | OAuth client_id 重启失效问题 |
| Issue #3 | https://github.com/Waishnav/devspace/issues/3 | `devspace` command not found 安装问题 |
| PR #1 | https://github.com/Waishnav/devspace/pull/1 | single-user OAuth 引入记录 |
| CI workflow | https://github.com/Waishnav/devspace/blob/main/.github/workflows/ci.yml | 官方自测矩阵 |
| Security doc | https://github.com/Waishnav/devspace/blob/main/docs/security.md | 安全模型和 shell 边界 |
| Coding workflow doc | https://github.com/Waishnav/devspace/blob/main/docs/chatgpt-coding-workflow.md | workspace/worktree/skills 模型 |

## 本地验证命令

```bash
gh repo view Waishnav/devspace --json nameWithOwner,description,url,stargazerCount,forkCount,issues,licenseInfo,defaultBranchRef,pushedAt,createdAt,updatedAt,latestRelease,languages
gh api 'repos/Waishnav/devspace/issues?state=all&per_page=20'
gh api 'repos/Waishnav/devspace/releases?per_page=5'
gh run list --repo Waishnav/devspace --limit 5 --json databaseId,status,conclusion,createdAt,updatedAt,headSha,event,workflowName,url
git clone --depth 1 https://github.com/Waishnav/devspace.git tmp/2026_06_18_devspace_survey/repo
npm view @waishnav/devspace version dist-tags time license dependencies --json
npm ci
npm run typecheck
npm test
npm run build
npm audit --json
npm ls protobufjs ws
DEVSPACE_ALLOWED_ROOTS="$PWD" DEVSPACE_OAUTH_OWNER_TOKEN="test-owner-token-that-is-long-enough" DEVSPACE_PUBLIC_BASE_URL="http://127.0.0.1:17676" PORT=17676 node dist/cli.js doctor
DEVSPACE_ALLOWED_ROOTS="$PWD" DEVSPACE_OAUTH_OWNER_TOKEN="test-owner-token-that-is-long-enough" DEVSPACE_PUBLIC_BASE_URL="http://127.0.0.1:17676" PORT=17676 node dist/cli.js serve
curl -sS http://127.0.0.1:17676/healthz
```

## 覆盖评估

- 已覆盖：源码主路径、安装包元数据、release、issues、CI、typecheck/test/build/doctor/server health。
- 未覆盖：真实 ChatGPT remote MCP OAuth 端到端接入、Cloudflare Tunnel/ngrok 外网链路、ChatGPT Apps widget 真实渲染。
- 边界：本报告判断的是项目实现和本地可运行性，不等同于已验证 ChatGPT 生产连接稳定性。
