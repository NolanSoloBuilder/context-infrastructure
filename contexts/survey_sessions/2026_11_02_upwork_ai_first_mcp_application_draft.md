# Upwork AI-First Full-Stack Engineer 英文申请草稿

2026-11-02。状态：给用户审阅，未提交。每周10–20小时来自用户确认；时薪尚未由用户选定，正文不承诺费率。

岗位：[AI-First Full-Stack Engineer — TypeScript + GCP + ADK + MCP](https://www.upwork.com/freelance-jobs/apply/First-Full-Stack-Engineer-TypeScript-GCP-ADK-MCP-Ongoing-Revenue-Share-Potential_~022115518625323846427/)。按当日已读取原帖的四项问题组织，按要求以PILOT开头。

## 英文正文

用户已确认下方原稿内容基本准确；随后要求进一步精简。直接投递版如下，仍未提交。

### 精简投递版

PILOT

I build full-stack agent products and can commit 10–20 hours per week. Your mix of MCP infrastructure, agent architecture, and frontend work fits my recent projects.

**Project and frontend example:** I’m building [BeamJoin](https://forgepane.com/), a React/TypeScript 3D design workbench with an AI agent and MCP tools. I built the interface, backend APIs, and agent workflow. The hardest part was keeping model-generated edits consistent with the saved design; I addressed this with revision-bound proposals, server-side validation, and idempotent commits. The public site includes an interactive product walkthrough.

I also integrated the open-source DevSpace MCP server with ChatGPT using OAuth and Streamable HTTP. In Cited Alpha, my research-agent project, I worked on GCP Cloud Run services, resumable runs, source-linked reports, and authenticated document access. My orchestration experience is primarily with custom runtimes and Vercel AI SDK, which I’d bring to your Google ADK stack.

**AI-assisted workflow:** I use Codex and Claude Code, define architecture and acceptance criteria, delegate independent tasks to agents, and review the integrated changes. Verification covers tool calls, API behavior, persisted data, and the UI.

**Multi-account MCP design:** Keep the transport stateless, validate OAuth tokens, and enforce account access server-side on every tool call. Model-supplied account IDs must never establish permission. Keep Amazon credentials server-side and tenant-scope database queries, caches, and jobs. Add authorization checks, idempotency keys, audit logs, and cross-account isolation tests.

I’m happy to start with a small paid test covering one MCP tool, its UI, and account isolation end to end.

### 原稿（保留审阅记录）

PILOT

I’m an independent full-stack builder working on agent-powered products. Your combination of MCP infrastructure, agent architecture, and frontend ownership closely matches the work I’ve been doing. I can commit 10–20 hours per week.

**Relevant project: BeamJoin**

I’m building [BeamJoin](https://forgepane.com/), a browser-based 3D design workbench with an integrated AI agent. My work spans the React/TypeScript interface, backend APIs, MCP tools, and the agent’s tool loop and context management.

The difficult part is keeping model-generated edits consistent with the actual design. I implemented revision-bound proposals, server-side validation, and idempotent commits, with the editor and agent using the same application services. This gives tool-driven changes the same rules as manual edits.

BeamJoin is also my frontend example: an interactive 3D workspace with object selection, property editing, change review, and material lists. The public site includes an interactive product walkthrough.

**MCP and cloud experience**

Separately, I integrated the open-source DevSpace MCP server with ChatGPT over OAuth and Streamable HTTP, including workspace access boundaries and protocol-level smoke tests.

For Cited Alpha, my financial research-agent project, I worked on services deployed to GCP Cloud Run, resumable research runs, source-linked reports, and authenticated document access. My agent orchestration experience is primarily with custom runtimes and the Vercel AI SDK; I would bring that experience to your Google ADK stack.

**My AI-assisted development workflow**

I use Codex and Claude Code for implementation, debugging, and review. I define the architecture and acceptance criteria, split independent work across agents, then review the integrated changes. For tool-driven features, I check the protocol, API, and persisted results alongside the UI. I remain responsible for the final implementation and verification.

**How I’d isolate multiple client accounts**

I’d keep the Streamable HTTP layer stateless and derive identity from a validated OAuth access token. Each tool invocation would resolve the user’s permitted client accounts server-side and check access to the requested resource. An account ID supplied by the model would never establish permission.

Amazon credentials would remain server-side, scoped to the authorized account. Database queries, caches, and background jobs would carry the same tenant boundary. Writes would have explicit authorization checks, idempotency keys, and audit records, with tests covering cross-account access attempts.

I’m happy to start with a small paid test focused on one MCP tool and its UI, including account isolation and a working end-to-end flow.

## 事实依据与边界（不随申请发送）

### Upwork个人资料填写进度

用户随后授权协助完成Upwork注册，并明确选择公开时薪$40/小时。当前通过用户已有Chrome登录页操作：

- 类别：Web, Mobile & Software Dev；专长：AI Apps & Integration、Web Development。
- 技能：Artificial Intelligence、AI Agent Development、React、TypeScript、Python、Node.js、API Integration。
- 标题：AI Agent & Full-Stack Developer | MCP, TypeScript, React。
- 简介：基于用户确认的BeamJoin、Cited Alpha、DevSpace集成经历整理，公开可提供每周10–20小时远程合作。
- 语言：英语Conversational、中文Native or Bilingual。英语按“可英文沟通”暂设，未自行声称Fluent。
- 用户同意填写BeamJoin个人项目经历，要求使用领英头像，并确认当前所在地为页面默认的Singapore。项目记录填写Independent Full-Stack & AI Agent Developer / BeamJoin (Independent Project)，从2026年9月起至今（按已有项目实现记录），地点Singapore。
- 已从用户确认的领英个人主页读取并下载头像，使用系统文件选择器上传并保存。Chrome扩展自动上传因本地文件权限未启用而失败，未扩大扩展权限，改走原生上传。
- 已进入注册第4/5步personal-info，页面要求出生日期、详细地址、邮编与手机号；已请用户在页面自行填写，或提供希望提交给Upwork的具体信息。未猜测或从其它私密来源查找这些字段。
- 尚未完成或发布资料，没有提交职位申请。后续状态应以实际页面回读为准。进度截图保存在本聊天visualizations目录的upwork-profile-step4.jpg，不在仓库保存敏感资料。

- BeamJoin：本轮读取实际React/TypeScript依赖、MCP注册与认证说明、项目归属检查、设计提案/修订/幂等合同，以及Agent文档。当前外部MCP为stdio，申请没有将其写成远程OAuth MCP。部分完整编辑器与真实模型验收历史仍有失败，不宣称全面可靠或成熟商业成功。
- 远程MCP：依据本仓库 `contexts/thought_review/2026_06_19_devspace_mcp_x_tutorial.md` 和 `adhoc_jobs/devspace_chatgpt_adapter/README.md`。明确属于第三方DevSpace集成，不将上游作者实现归为本人原创，也不把它说成多租户SaaS。
- GCP/Cited Alpha：依据 `contexts/survey_sessions/cited_alpha_agent_redesign/36_production_full_function_20260914.md` 中Cloud Run发布、真实失败恢复、私有文件授权与报告来源验收记录。它是受限个人项目，不声称有大规模客户或完整开放产品。本次未重新运行线上研究任务。
- 本轮公开读取 `https://forgepane.com/` 成功，内容含实时模型和设计导览。没有重新做浏览器交互验收；站点的导览属于展示，不用其模拟对话证明任意Agent任务成功。工作台和Cited Alpha入口未通过web工具读取，因此正文仅附已读取的公共首页。
- Google ADK没有查到直接交付证据；MCP Apps交互式UI没有查到充分交付证据，不写成已交付能力。多租户段是拟议设计，不是过往实现自述。
- 没有披露公司内部代码、客户数据、账号、令牌或私有项目地址；未编造工龄、营收、用户数、平台评级或性能提升数字。
