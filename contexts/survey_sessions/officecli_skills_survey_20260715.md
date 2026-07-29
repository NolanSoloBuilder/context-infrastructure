# OfficeCLI Skills 调研：一套垂直文档运行时的 Agent 控制面

调研日期：2026-07-15  
代码快照：[`4ba79f0`](https://github.com/iOfficeAI/OfficeCLI/commit/4ba79f0b984e141f57f58d4398ba2df29e8187e8)，release [`v1.0.136`](https://github.com/iOfficeAI/OfficeCLI/releases/tag/v1.0.136)

## 结论

[OfficeCLI skills](https://github.com/iOfficeAI/OfficeCLI/tree/main/skills) 最值得研究的部分，是把 Agent 文档生产做成了一套闭环：少量 trigger 常驻上下文，场景规则按需加载，运行时 `help` 作为命令 schema 真源，最终经过 `save/close → validate → render → visual audit` 交付。它比普通的 Office Prompt 集合多了一层真正的运行时控制面。

我的判断是：**值得借鉴架构，不建议把整套 skills 原样引入当前 context-infrastructure。** 其中的 help-first、按需 disclosure、显式 reverse handoff、artifact-specific Delivery Gate 都可复用；巨型单文件 Skill、隐式继承、默认远程自举、自动覆盖本地 Skill，以及人工镜像同步，都不适合作为长期基础设施。

若要引入 OfficeCLI 本身，现阶段适合有人审阅的普通 DOCX/PPTX 和简单 XLSX 试点。复杂财务模型、复杂 chart、raw XML round-trip、加密文档和 Windows resident automation 仍需要真实 Word/Excel/WPS 或独立 reader 复核，不能把 `validate` 或内置 HTML preview 当成最终真值。

## 它实际是什么

OfficeCLI 不是给每种格式拼一组 Python/Node 工具，而是用一个自包含 binary 提供统一的 OOXML DOM、路径寻址、JSON、resident mode、render、validate、formula engine 和 MCP transport。根 [`SKILL.md`](https://github.com/iOfficeAI/OfficeCLI/blob/4ba79f0b984e141f57f58d4398ba2df29e8187e8/SKILL.md) 给出 umbrella 路由；[`SkillInstaller.cs`](https://github.com/iOfficeAI/OfficeCLI/blob/4ba79f0b984e141f57f58d4398ba2df29e8187e8/src/officecli/Core/SkillInstaller.cs) 把 10 个场景 Skill 内嵌进 binary，并向 MCP 常驻描述只注入短 trigger。源码对这套设计的概括是 “push minimal trigger, pull the detail”。

加载链路分成四级：

1. 常驻 trigger 只告诉模型有哪些场景。
2. `load_skill` 无参数返回路由 catalog。
3. `load_skill <name>` 返回完整 `SKILL.md`，同时删除已经无意义的安装段。
4. `load_skill <name> --path <relpath>` 再读取按需 reference；二进制资产要求显式落盘安装。

这比把完整 Skill 塞进每轮 system prompt 合理得多。[Issue #69](https://github.com/iOfficeAI/OfficeCLI/issues/69) 正是从“根 Skill 常驻约 4k tokens”的真实集成成本出发，推动了后续按需加载设计。

## Skill 资产分层

当前 `skills/` 有 11 个一级目录。`skills/officecli/SKILL.md` 是指向根 Skill 的 symlink；`load_skill` 实际可路由 10 个 specialized skills。

| 层级 | Skill | 主要职责 |
|---|---|---|
| Format base | `word` / `pptx` / `excel` | 三种格式的通用读写、设计规范与 QA |
| Scene layer | `academic-paper` / `pitch-deck` / `financial-model` / `data-dashboard` / `morph-ppt` | 在格式能力上增加领域合同 |
| Extension | `morph-ppt-3d` | GLB、camera、3D Morph |
| Independent | `word-form` | SDT、FormField、MERGEFIELD、文档保护 |

目录共 121 个 blob、约 1.65 MB，其中 65 个 Markdown 约 590 KB。10 个 specialized `SKILL.md` 合计约 61,886 words；8 个超过 Agent Skills 文档建议的 500 行，最大 `pitch-deck` 为 809 行、66.7 KB。官方 [Agent Skills specification](https://github.com/agentskills/agentskills) 的核心是 progressive disclosure，而这里大多数细节仍集中在单一 `SKILL.md`。`morph-ppt` 是例外，它把 helper、decision rules、设计参考和 51 套 style 目录放进 reference/assets，最接近长期合理的 Skill 形态。

## 最值得复用的设计

### 1. Schema 真源在 runtime，不在 Skill

每个 specialized Skill 都强调：Skill 负责“什么是好产物”，具体 property、enum、alias 以当前 binary 的 `officecli help` 为准。历史 issue 证明这并非形式要求：[#97](https://github.com/iOfficeAI/OfficeCLI/issues/97) 和 [#100](https://github.com/iOfficeAI/OfficeCLI/issues/100) 都出现过 Skill 示例与 CLI 实际参数不一致。把 runtime help 设为权威来源，能把静态知识和快速变化的命令合同分开。

### 2. `load` 与 `install` 分开

[`Program.cs`](https://github.com/iOfficeAI/OfficeCLI/blob/4ba79f0b984e141f57f58d4398ba2df29e8187e8/src/officecli/Program.cs#L120-L201) 明确区分纯读取的 `load_skill` 和有写入副作用的 `skills install`。这条边界简单，却能避免“为了读一份指南，顺手修改全局 agent 配置”。

### 3. Delivery Gate 针对产物语义

这些 Skill 不只检查命令成功。DOCX 会检查真实 Heading、TOC、PAGE field 和 token leak；XLSX 会检查 formula error、cache、print area 和数值合理性；PPTX 强制 visual audit；financial model 再增加 statement integrity、hardcode zone 和 sensitivity 检查。这里体现了一个可复用原则：门禁应绑定产物的原子语义，而非只绑定文件存在或 exit code。

### 4. 明确 reverse handoff

各 Skill 会写清楚什么时候应回到 base skill、什么时候切到相邻 scene。对于 Agent 路由，`DO NOT invoke` 和 reverse handoff 通常比继续增加正向 trigger 更有效。

## 已确认的设计问题

### Scene 继承合同互相矛盾

根 Skill 说 scene 已包含 base 规则，因此一个 artifact “load one skill, never stack”。但 `academic-paper`、`pitch-deck`、`financial-model`、`data-dashboard`、`morph-ppt` 都明确写着基础规则 “inherited, not re-taught”，并要求先读 base Skill。实际 loader 不会自动拼接依赖，也没有真正的 rules persistence。

这不是文案瑕疵，而是执行合同没有唯一真源。长期方案只能二选一：构建时把 inherited contract 物化进 scene；或者由 loader 显式解析依赖并按确定顺序组合。当前介于两者之间，模型可能少读关键规则，也可能重复加载大量上下文。

### Umbrella 路由遗漏 `word-form`

[`SkillMap`](https://github.com/iOfficeAI/OfficeCLI/blob/4ba79f0b984e141f57f58d4398ba2df29e8187e8/src/officecli/Core/SkillInstaller.cs#L44-L57)、MCP trigger 和 CLI catalog 都包含 `word-form`，根 Skill 的 Specialized Skills 表却没有它。只安装 umbrella、没有 MCP trigger 的 agent 不容易发现 fillable form 能力。此前 commit [`dc5ea9b`](https://github.com/iOfficeAI/OfficeCLI/commit/dc5ea9b0472567634d7789f1a4c0b65866fb41af) 还修过一次“目录已存在但 catalog 不可见”，说明手写多份 registry 已经产生实际 drift。

### Specialized Skill 过大

单个场景 Skill 常在 5,000–10,000 words。按需加载解决了非文档任务的常驻成本，却没有解决一次文档任务内部的 context 占用。更合理的边界是：`SKILL.md` 保留 identity、决策树、build order 和 Delivery Gate；CLI recipes、格式细节、known issues、style catalog 下沉到按需 references；确定性操作进一步变成 script/workflow。

### 自动更新会覆盖本地修改

[`UpdateChecker.cs`](https://github.com/iOfficeAI/OfficeCLI/blob/4ba79f0b984e141f57f58d4398ba2df29e8187e8/src/officecli/Core/UpdateChecker.cs#L59-L70) 默认每天后台检查更新，版本变化后会刷新已安装 Skill。好处是 binary 与 Skill 不易错位；代价是本地修改缺少稳定所有权和可复现版本。企业使用应固定版本与 hash，把上游 Skill 当 vendored/generated artifact，不在安装目录直接定制。

### Morph 二进制资产安装存在高置信源码缺陷

源码知道 `.pptx` 等二进制资产不能通过文本通道返回，但全树安装路径仍用 `StreamReader.ReadToEnd()` 读取、`File.WriteAllText()` 写回。Morph 树当前含 27 个 `.pptx`。从 [`SkillInstaller.cs`](https://github.com/iOfficeAI/OfficeCLI/blob/4ba79f0b984e141f57f58d4398ba2df29e8187e8/src/officecli/Core/SkillInstaller.cs#L658-L776) 推断，安装副本会经过文本解码/重编码而损坏。本轮未执行官方 binary 做落盘复核，因此把它标为高置信源码缺陷，而非已完成 runtime 复现。

## 成熟度与真实边界

项目创建于 2026-03-15，到 7 月 14 日已发布 `v1.0.136`，约四个月 130 个 GitHub releases。修复速度快，行为合同也仍在快速变化。当前仓库没有 committed test project；[build workflow](https://github.com/iOfficeAI/OfficeCLI/blob/main/.github/workflows/build.yml) 覆盖 8 个 RID、macOS 签名/公证、基础文档和安装 smoke，却没有复杂 Office 语义、Skill 路由、reference byte parity 或真实 Office/WPS E2E。增加 E2E 的 [PR #132](https://github.com/iOfficeAI/OfficeCLI/pull/132) 仍未合入。

几个 issue 能准确说明边界：

- [#191](https://github.com/iOfficeAI/OfficeCLI/issues/191)：Skill 同时使用两种分页机制，OOXML validate 通过，真实 Word 多出空白页；已修复。
- [#192](https://github.com/iOfficeAI/OfficeCLI/issues/192)：大号粗体并不等于真实 Heading，TOC 更新后报“未找到目录项”；已修复。
- [#189](https://github.com/iOfficeAI/OfficeCLI/issues/189)：sheet rename 后 chartEx 仍引用旧名，`validate` 通过但 Excel 出现 `#REF!`；已修复。
- [#207](https://github.com/iOfficeAI/OfficeCLI/issues/207)：Windows 非交互管道中，简单 view/get 可延迟约 61 秒退出；修复 PR 尚未进入本次快照。
- [#213](https://github.com/iOfficeAI/OfficeCLI/issues/213)：财务函数静默忽略 `type` 参数，可能给出外观可信的错误数字；当前未修复。
- [#217](https://github.com/iOfficeAI/OfficeCLI/issues/217)：Word/PPT HTML preview 的 theme tint/shade 计算错误；当前未修复。

因此，`validate` 证明的是 OOXML/schema 基础合法性；内置 preview 证明的是近似 renderer 的当前输出；resident 内存态还要经过 `save/close` 才能证明磁盘内容。生产交付需要把这三层分开验收。

## 安全与分发

积极面包括：release 提供 SHA256SUMS；安装器优先使用不可变的 versioned URL；macOS binary 有 Developer ID 签名和 notarization；CodeQL 与多平台安装 smoke 均在运行。

风险来自产品选择。所有主 Skill 默认允许 Agent 执行 `curl | bash` / `irm | iex`。[Issue #87](https://github.com/iOfficeAI/OfficeCLI/issues/87) 中，企业用户明确提出供应链顾虑，维护者选择保留无人值守 bootstrap，把禁用策略交给宿主 policy。[Issue #118](https://github.com/iOfficeAI/OfficeCLI/issues/118) 修复标准 Skill installer 后，`gh`、Gen、Socket、Snyk 仍给出高风险警告。安装脚本在 checksum 文件不可取时会 fail-open 继续安装；checksum 与 binary 也来自同一 release trust root。

受控环境应采用固定 release + 固定 SHA256 + 内部制品镜像，禁用 Agent 自行远程安装和默认 auto-update。先审阅 Skill，再显式安装到目标 agent。

## 生态位置与同步风险

常见文档 Skill 主要编排 `python-docx`、`openpyxl`、`pptxgenjs`、LibreOffice、Pandoc 和 Poppler。OfficeCLI 的区别在于三种 Office 格式共用一个 path/JSON contract 和一个 render/validate loop。它换来了更统一的 Agent 心智模型，也让 runtime 成为单一故障点。

OfficeCLI 的 MCP 也选择单一 `officecli` command string，而非几十个强类型 tools。这能减少 schema token 和 CLI/MCP drift，却牺牲参数级发现、校验和授权粒度。这个取舍适合强模型和 help-first 工作流，不适合需要细粒度 policy 的宿主。

AionUi/AionCore 的集成值得警惕。AionUi [PR #2750](https://github.com/iOfficeAI/AionUi/pull/2750) 把 10 个 Skill 人工复制进产品；后来 AionCore 仍用版本内嵌 corpus 和人工同步 commit，而不是 package/submodule/parity gate。当前 AionCore 镜像已经保留旧 MCP structured args，并缺少最新 flush 和能力说明，和 OfficeCLI `main` 产生实质 drift。任何下游镜像都应携带 machine-readable upstream commit/hash，并由 CI 做 parity 检查。

搜索时还要排除两个污染源：第三方目录 [Claude Marketplaces](https://claudemarketplaces.com/skills/iofficeai/officecli/officecli) 错称 iOfficeAI OfficeCLI “Works through LibreOffice under the hood”；另一个 [`officecli/officecli`](https://github.com/officecli/officecli) 是同名但不同的 hosted 产品，使用 `officecli new`、REPORT/IMG 和 credits，不能混入本仓库结论。

## 对 context-infrastructure 的建议

可以直接吸收四条规则：

1. 常驻层只保留短 trigger，详细规则和资产按需加载。
2. 变化快的命令/schema 由 runtime 生成或查询，Skill 只保存任务合同、决策和质量门禁。
3. Scene 依赖必须可执行：构建时物化或 loader 显式组合，不能依靠“继承”一句话。
4. 镜像 Skill 必须记录 upstream commit/hash，并由 CI 校验 drift；用户定制与上游生成文件分目录管理。

如果要评估是否实际采用 OfficeCLI，下一阶段应固定 `v1.0.136` 或更新版本，选一组同输入 benchmark：普通 DOCX 报告、10 页 PPTX、带公式和 chart 的 XLSX。分别测完成时间、命令重试、token、文件 diff、真实 Office/WPS 打开结果和视觉缺陷，再和当前 documents/presentations/spreadsheets runtime 对比。没有这轮实测前，不建议替换现有能力。
