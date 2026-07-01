# birdclaw 调研 manifest

日期：2026-06-23

## 产出文件索引

| 文件 | 路径 | 说明 |
|---|---|---|
| Scratchpad | `tmp/birdclaw_survey_20260623/scratchpad.md` | 主线程研究笔记、claim extraction、源码观察 |
| Search Manifest | `tmp/birdclaw_survey_20260623/search_manifest.md` | 本文件 |
| 最终报告 | `contexts/survey_sessions/birdclaw_survey_20260623.md` | 给用户的内部调研备忘录 |
| 临时源码镜像 | `tmp/birdclaw_survey_20260623/repo/` | `git clone --depth 1 https://github.com/steipete/birdclaw.git` 的静态检查副本 |

## 方法说明

当前工具策略不允许在用户未明确要求时主动派 sub-agent，因此本次没有使用并行 sub-agent。调研仍按证据层级执行：

- Tier 1: 官网、README、docs、release notes
- Tier 3/4: GitHub issues/PR/release/CI、源码、package metadata、同类项目公开状态
- 独立社区讨论：检索到的主要是 Reddit 的 OpenClaw 工具集合讨论，信号偏弱，仅作背景，不作为核心验证依据

## 主要 URL

| 类型 | URL | 用途 |
|---|---|---|
| 官网 | https://birdclaw.sh/ | 项目定位、功能 claim |
| GitHub repo | https://github.com/steipete/birdclaw | README、stars/forks、源码入口 |
| Install docs | https://birdclaw.sh/install.html | 安装要求、Node、xurl/bird/OpenAI |
| Quickstart | https://birdclaw.sh/quickstart.html | archive-first 使用路径 |
| Spec | https://birdclaw.sh/spec.html | goals/non-goals/decisions |
| CLI spec | https://birdclaw.sh/cli.html | command tree、JSON envelope claim |
| Data architecture | https://birdclaw.sh/data-architecture.html | Effect/runtime/database 架构 |
| Release v0.8.5 | https://github.com/steipete/birdclaw/releases/tag/v0.8.5 | 最新 release proof |
| CI run | https://github.com/steipete/birdclaw/actions/runs/27920819997 | 最新 release CI 状态 |
| Issue #45 | https://github.com/steipete/birdclaw/issues/45 | 第三方发现 docs/CLI mismatch |
| Issue #61 | https://github.com/steipete/birdclaw/issues/61 | 第三方发现 backup JSONL bug |
| Issue #65 | https://github.com/steipete/birdclaw/issues/65 | 当前 open feature boundary |
| npm latest API | https://registry.npmjs.org/birdclaw/latest | 包版本、engine、tarball、dependencies |
| GitHub API | https://api.github.com/repos/steipete/birdclaw | repo metadata |
| Reddit background | https://www.reddit.com/r/WebAfterAI/comments/1t5fzci/peter_steinberger_openclaw_creator_just_shipped_a/ | 社区背景，非核心证据 |
| twitter-to-sqlite | https://github.com/dogsheep/twitter-to-sqlite | 同类老牌 SQLite 工具 |
| twitter-to-sqlite issue #54 | https://github.com/dogsheep/twitter-to-sqlite/issues/54 | 老工具受 archive 格式变化影响 |
| twarc | https://github.com/DocNow/twarc | 同类学术归档工具状态 |
| xf | https://github.com/Dicklesworthstone/xf | 现代 archive search 对照 |
| tweetxvault | https://github.com/lhl/tweetxvault | 现代 sync/search 对照 |

## 本地命令摘要

- `npm view birdclaw --json`
- `curl -s 'https://registry.npmjs.org/birdclaw/latest'`
- `brew info steipete/tap/birdclaw`
- `curl -s 'https://api.github.com/repos/steipete/birdclaw'`
- `curl -s 'https://api.github.com/repos/steipete/birdclaw/releases?per_page=10'`
- `curl -s 'https://api.github.com/repos/steipete/birdclaw/issues?state=all&per_page=100'`
- `curl -s 'https://api.github.com/repos/steipete/birdclaw/actions/runs?per_page=10'`
- `git clone --depth 1 https://github.com/steipete/birdclaw.git tmp/birdclaw_survey_20260623/repo`
- `rg`, `sed`, `find` 静态检查源码结构

## 覆盖评估

已覆盖：

- 官方功能定义
- install/quickstart/auth/sync/backup/media/inbox docs
- GitHub release/CI/issue/PR
- npm/Homebrew 包状态
- 源码架构与局部风险
- 主要同类工具

未覆盖：

- 未运行 birdclaw，原因是本机 Node `v25.2.1` 低于项目 `>=25.8.1 <27` 要求
- 未用真实 Twitter/X archive 做 import/sync 验证
- 未验证 `xurl` / `bird` 当前登录与 X API/GraphQL 运行状态

