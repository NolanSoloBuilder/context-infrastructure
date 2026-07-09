# dawei008/openbook 上下文支持

日期：2026-06-18

对象：`https://github.com/dawei008/openbook`

本次记录基于 GitHub 当前元数据、本地浅克隆源码和仓库内 Markdown/mdBook 配置。临时克隆位置：`tmp/openbook_context/openbook/`，当前 HEAD 为 `53ad1d6d94dc8b8f356ad45358b42a3ff89a0b41`。

## 结论

`openbook` 是一本围绕 AI Agent Harness 工程学的开源书，不是可直接安装的 Agent 框架。它最适合作为本 workspace 里讨论 Agent runtime、工具系统、权限、安全、多 Agent、记忆、MCP、Skills、Plugin 和云上 sandbox 时的结构化参考上下文。

它的核心价值在于把 Agent 产品中 LLM 之外的运行时工程抽象成一套章节化地图：`Agent = LLM + Harness`。对我们当前的上下文体系来说，它可以补一层“Agent Harness 设计模式索引”，用于产品/架构讨论和技术方案推演。

使用时要保留一个边界：书中大量内容来自对某个生产级 Agent 系统的架构分析，并用伪代码表达。它适合作为模式参考，不适合作为某个闭源产品当前实现的事实来源。凡是涉及具体产品内部实现、2026 年之后的 API 状态、MCP/Agents SDK 最新规范，都需要再查官方文档或真实代码。

## 当前项目状态

GitHub 当前元数据：

- 创建时间：2026-03-16
- 默认分支：`main`
- 最新 push：2026-04-12
- Stars：29
- Forks：7
- Open issues：0
- Open PR：0
- Latest release：无
- License：GitHub API 未返回 license
- Primary language：HTML
- 仓库描述：`OpenBook: AI Agent Harness Engineering -- an open-source book on building production-grade Agent Harnesses (26 chapters, bilingual CN/EN)`

仓库不是代码库形态。主要文件是：

- `README.md`：中文主页、章节目录、定位说明
- `SUMMARY.md`：mdBook 中文目录
- `book.toml`：mdBook 配置
- `part-*/`：中文正文，9 个 Part、26 章
- `appendix/`：4 个附录
- `en/`：英文翻译，44 个 Markdown 文件
- `OpenBook-zh.pdf` / `OpenBook-en.pdf`：PDF 成品
- `.github/workflows/deploy.yml`：GitHub Pages 构建发布
- `TRANSLATE_PROMPT.md`：中译英任务说明

本机验证：

```bash
git clone --depth 1 https://github.com/dawei008/openbook.git tmp/openbook_context/openbook
git -C tmp/openbook_context/openbook rev-parse HEAD
gh repo view dawei008/openbook --json nameWithOwner,description,stargazerCount,forkCount,createdAt,pushedAt,defaultBranchRef,licenseInfo,primaryLanguage,latestRelease,issues,pullRequests,url
```

`mdbook --version` 在本机失败，原因是当前环境没有安装 `mdbook`。我没有临时修改全局环境。仓库 CI 使用 `peaceiris/actions-mdbook@v2` 安装 `mdbook 0.4.43` 后执行 `mdbook build`，这说明标准构建路径是 mdBook + GitHub Pages。

## 内容地图

全书目录围绕 9 个 Part 展开：

| Part | 文件 | 主题 | 用途 |
|---|---|---|---|
| Part I | `part-1/` | 什么是 Agent Harness | 建立 `Agent = LLM + Harness` 心智模型 |
| Part II | `part-2/` | Agent Loop | 理解消息、LLM 调用、工具结果和错误恢复的循环 |
| Part III | `part-3/` | 工具系统 | 参考 Tool interface、注册、调度、并发、结果预算 |
| Part IV | `part-4/` | 安全与权限 | 参考权限模式、风险分级、自动审批、Hooks |
| Part V | `part-5/` | 多智能体 | 参考子 Agent fork、隔离、后台任务、Team/Swarm |
| Part VI | `part-6/` | System Prompt 与记忆 | 参考 prompt 组装、动态上下文、记忆发现 |
| Part VII | `part-7/` | 扩展机制 | 参考 MCP、Skills、Commands、Plugin 体系 |
| Part VIII | `part-8/` | 前沿与哲学 | 参考 Dream、设计原则和能力边界 |
| Part IX | `part-9/` | OpenHarness 实战部署 | 参考云上 sandbox、验证、自修复和任务队列 |

附录用途：

- `appendix/appendix-a.md`：架构总览图与数据流图
- `appendix/appendix-b.md`：关键类型定义速查
- `appendix/appendix-c.md`：Feature Flag 清单
- `appendix/appendix-d.md`：从零构建 Mini Agent Harness

## 在本 workspace 中怎么用

当讨论 Agent 产品架构时，优先把 `openbook` 当作章节索引和问题清单，而不是当作结论来源。推荐用法是先根据问题定位章节，再回到当前项目的真实代码或官方文档做验证。

典型路由：

| 当前问题 | 先读章节 | 之后验证 |
|---|---|---|
| Agent runtime 应该如何建模 | `part-1/chapter-01.md`、`part-1/chapter-02.md` | 当前产品的 session/run/task 数据结构 |
| Agent loop 怎么做流式、重试和压缩 | `part-2/chapter-03.md` 到 `chapter-05.md` | 当前 SDK/API 的 streaming event 和 token budget |
| 工具系统怎么设计 | `part-3/chapter-06.md` 到 `chapter-08.md` | 本地工具 schema、权限、并发和输出截断实现 |
| 权限系统怎么分层 | `part-4/chapter-09.md` 到 `chapter-11.md` | 真实 sandbox、审批、hook、policy 代码 |
| 多 Agent 怎么隔离 | `part-5/chapter-12.md` 到 `chapter-15.md` | 当前 subagent、worktree、mailbox、background task 实现 |
| Prompt/记忆怎么组织 | `part-6/chapter-16.md`、`chapter-17.md` | 本 workspace 的 `rules/`、`contexts/memory/` 和 skill 加载链路 |
| MCP/Skill/Plugin 怎么分层 | `part-7/chapter-18.md` 到 `chapter-20.md` | 官方 MCP spec、Codex plugin/skill 当前实现 |
| 云上执行环境怎么约束 Agent | `part-9/chapter-23.md` 到 `chapter-26.md` | Kubernetes/IAM/CI/CD 的真实配置 |

结合本仓库已有上下文，`openbook` 最能补的是 `rules/skills/` 和 `contexts/thought_review/` 之间的中间层：它不是一个可执行 skill，但可以作为写新 skill、设计 Agent workflow、审查 Agent 产品方案时的参考书。

## 2026-07-06 本地成书版补充

本次新增本地成书版来源，已归档到仓库：

- Markdown：`contexts/source_materials/openbook/openbook_zh.md`
- PDF：`contexts/source_materials/openbook/openbook_zh.pdf`
- 原始来源路径：`/Users/xuhao/Downloads/OpenBook-zh.md`、`/Users/xuhao/Desktop/OpenBook-zh.pdf`

处理策略：后续需要读内容时以仓库内 Markdown 为主，PDF 只作为页数、标题、目录和末页版式的验证来源。当前报告仍保留 license 未确认的边界；引用或对外改编时，不直接搬运大段原文。

本机验证结果：

- `OpenBook-zh.md` 是 UTF-8 文本，约 788 KB，13,122 行，456,663 个字符。
- Markdown 中保留 313 个分页符，包含 `Appendix D`、`参考文献` 和末尾 `# Progress` 附录文本。
- `OpenBook-zh.pdf` 是 PDF 1.5，标题为 `OpenBook: 构建 AI Agent 的 Harness 工程学`，313 页，创建时间为 2026-04-12 09:56:56 CST，生成链路为 LaTeX via pandoc / `xdvipdfmx`。
- 入仓副本已用 `cmp` 与原始文件逐字节校验一致。Markdown sha256 为 `23c189c725eb417e65f5c3946c141d15edaa6476130565b579353bf428cce487`，PDF sha256 为 `7e7a0f8af76d3bde8aee87e161b53643180a9df6fd73cf853c09124a3947f92c`。
- 用 `pdftoppm` 渲染了第 1、3、313 页到 `tmp/pdfs/openbook_zh_verify/`。封面标题、目录页和末页参考文献版式正常，第 3 页目录与 Markdown 开头目录一致，PDF 末页与 Markdown 结尾的参考文献段落一致。
- 当前环境有 `pdfinfo` 和 `pdftoppm`，没有 `pdftotext`；因此 PDF 验证采用元数据 + 视觉抽样，而不是 PDF 文本抽取。

本地 Markdown 的实用定位方式：

```bash
rg -n "Chapter 18|MCP|Skills|Plugin|四根支柱|AGENTS.md|Dream|记忆系统|权限模型|工具编排" contexts/source_materials/openbook/openbook_zh.md
sed -n '6040,6890p' contexts/source_materials/openbook/openbook_zh.md  # Part VI / VII 周边
sed -n '8670,9560p' contexts/source_materials/openbook/openbook_zh.md  # Part IX / AGENTS.md 周边
```

对本 workspace 最值得优先引用的成书章节：

| 主题 | 优先章节 | 使用方式 |
|---|---|---|
| System Prompt 与动态上下文 | Chapter 16 | 对照本仓 `rules/`、AGENTS 加载、缓存分区和动态 section 设计 |
| 文件型记忆系统 | Chapter 17 | 对照 `contexts/memory/OBSERVATIONS.md`、L1/L2/L3 记忆和 Dream 整合 |
| MCP / Skills / Plugin 分层 | Chapter 18-20 | 讨论连接外部能力、安装工作流知识和打包能力边界时先查 |
| 多 Agent 编排 | Chapter 12-15 | 讨论 subagent、后台任务、Team/Swarm 和 Coordinator 边界时先查 |
| 云上 Agent Harness | Chapter 23-26 | 讨论 `CONSTRAIN / INFORM / VERIFY / CORRECT`、双 Pod、AGENTS.md 治理和自修复循环时先查 |
| 最小实现教程 | Appendix D | 写内部 workshop 或最小 Agent Harness 教学时先查，但代码需要按当前 SDK/API 重写 |

已同步新增轻量 skill：`rules/skills/openbook_agent_harness.md`，并在 `rules/skills/INDEX.md` 登记。后续遇到 Agent Harness、Agent runtime、MCP、Skills、Plugin、多 Agent、记忆系统或云上 sandbox 相关问题时，先通过这个 skill 路由章节，再查真实代码或官方文档。

## 可复用判断

第一，`Agent = LLM + Harness` 这个表达适合沉淀为长期概念。它把模型能力和工程运行时分开，能避免把 Agent 失败简单归因到 prompt 或模型。后续做 Agent 产品设计时，应先问 Harness 是否提供了足够的工具、权限、上下文、验证和恢复机制。

第二，`MCP / Skills / Hooks / Plugins` 的分层对当前 workspace 有直接参考价值。MCP 解决外部能力连接，Skills 解决工作流知识注入，Hooks 解决执行过程约束，Plugins 解决多能力打包。这个分层可以用于审查我们自己的 skill/plugin 设计是否把不同层级混在一起。

第三，Part IX 的 `CONSTRAIN / INFORM / VERIFY / CORRECT` 可以作为云上 Agent 系统的架构 checklist。它的价值不在于具体 AWS/Kubernetes 写法，而在于把 Agent runtime 的职责拆成约束、上下文、验证、纠错四类。

第四，Appendix D 适合作为教学和最小实现参考。如果要写内部“从零构建 Agent Harness”的 skill 或 workshop，可以从这里提取骨架，但要按当前实际 API 重写代码。

## 可信边界

需要注意这些限制：

- 仓库没有 GitHub API 可识别的 license。正式复用大段内容或改编出版前，需要人工确认许可边界。
- 内容使用伪代码，不提供可运行框架。
- 作者声明不复制 proprietary source code，但书中声称的生产级系统规模、调用量和内部实现细节不能从仓库本身独立验证。
- 仓库最近 push 在 2026-04-12，MCP、OpenAI Agents SDK、Anthropic API、Codex/Claude Code 等仍在快速变化。涉及最新 API 或产品能力时，要实时核验。
- 本机没有安装 `mdbook`，本次没有完成本地构建 smoke test。若后续要改书或发布，需要先安装 `mdbook 0.4.43` 并执行 `mdbook build`。

## 后续动作

如果后续要把它纳入长期上下文，建议做三件事：

1. 在 `rules/skills/` 增加一个轻量 skill：当用户问 Agent Harness、Agent runtime、MCP/Skills/Plugin 分层、多 Agent 编排时，先使用这份上下文定位章节，再查真实代码或官方文档。
2. 选择 3-5 个最相关章节做更细的读书笔记，优先是 `chapter-06` 工具系统、`chapter-09` 权限模型、`chapter-12` 子 Agent、`chapter-18` MCP、`chapter-19` Skills。
3. 如果要引用或改编内容，先确认 license；如果只是内部阅读和上下文索引，当前报告已经足够作为入口。
