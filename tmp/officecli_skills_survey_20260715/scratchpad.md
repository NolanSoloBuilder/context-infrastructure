# OfficeCLI Skills 调研 Scratchpad

调研快照：2026-07-15，官方仓库 `main` commit `4ba79f0b984e141f57f58d4398ba2df29e8187e8`，release `v1.0.136`。

## Claim Extraction

| Claim | 来源层级 | 验证通道 | 当前状态 |
|---|---|---|---|
| 单二进制、无需 Office/LibreOffice | 官方 README（Tier 1） | build matrix、release assets、独立安装记录 | 基本验证；第三方目录存在错误的 LibreOffice 说法 |
| Skill 可在多个 agent 中自动发现和安装 | README / `SkillInstaller.cs`（Tier 1/4） | issue #118、安装器实现、AionUi 集成问题 | 部分验证；标准目录问题已修，跨宿主注入仍可能失败 |
| Specialized skills 可按需加载并降低常驻 context | 根 `SKILL.md` / `SkillInstaller.cs`（Tier 1/4） | 文件体积、`load_skill` 实现、issue #69 | 机制成立；单个 specialized skill 仍偏大 |
| Scene skill 已包含基础规则，因此每个产物只加载一个 skill | 根 `SKILL.md`（Tier 1） | 逐个检查 scene skill | 反证：多个 scene skill 明确要求先读 base skill，且称 base 规则未重述 |
| Help-first 能避免 skill 与 CLI schema 漂移 | Specialized skills / help 实现（Tier 1/4） | commit history、issue #97/#100、近期 skill 修复 | 设计合理；历史上确实发生过 drift，运行时 help 是必要补救 |
| Render → look → fix 与 Delivery Gate 能显著提高质量 | README / skills（Tier 1） | issue、独立用户反馈、CI smoke | 有行为证据支持，但未见公开 benchmark 或系统化 skill E2E |
| 安装与自动更新安全、可复现 | install script / updater（Tier 4） | checksum、签名、版本 URL、issue #87/#118 | 有 SHA256 和 macOS 签名；默认自动更新及 skill 覆盖仍带来供应链与可复现性取舍 |

## 事实快照

- 仓库创建于 2026-03-15；2026-07-15 API 快照约 17,066 stars、1,134 forks、40 个 open issues。
- `skills/` 有 11 个一级目录，其中 `skills/officecli/SKILL.md` 是指向根 `SKILL.md` 的 symlink；可被 `load_skill` 发现的 specialized skill 共 10 个。
- `skills/` 共 121 个 blob、约 1.65 MB；65 个 Markdown 合计约 590 KB；27 个二进制资产约 483 KB。
- 10 个 specialized `SKILL.md` 合计约 61,886 words。8/10 超过 Agent Skills 文档建议的 500 行上限；最大 `officecli-pitch-deck` 为 809 行、66.7 KB。
- `morph-ppt` 额外附带 helper、decision rules、设计参考和 51 套 style 目录；Skill 正文仍写 52，已产生小幅 drift。它是该仓库唯一充分利用 progressive references/assets 的 skill。
- `SkillInstaller` 把 `load_skill` 设计为纯读取，把 `skills install` 设计为显式写入；通过 MCP/CLI 动态加载时会剥离已无意义的 `Setup` 安装段，并追加 reference manifest。
- 二进制默认每天后台检查更新；版本变化后会刷新已经安装的 skill 文件。这样保持 CLI/skill 同步，也会覆盖用户对已安装 skill 的本地修改。

## 已确认的合同不一致

1. 根 `SKILL.md` 说 scene 已含基础规则，要求每个 artifact “load one skill, never stack”。但 `academic-paper`、`pitch-deck`、`financial-model`、`data-dashboard`、`morph-ppt` 都说基础规则 “inherited, not re-taught”，并要求先读 base skill。
2. `SkillInstaller.SkillMap`、MCP trigger summary 和 CLI help 都有 `word-form`，根 `SKILL.md` 的 Specialized Skills 路由表却没有它。只安装 umbrella skill、没有 MCP trigger 时，fillable form 不容易被发现。

## 重要行为证据

- issue #69 直接提出根 Skill 常驻约 4k tokens 的成本，后来形成“短 trigger 常驻、完整 Skill 按需 pull”的实现。
- issue #87 讨论了 agent 自行执行 `curl | bash` 的供应链策略；上游选择保留自动 bootstrap，把限制交给宿主 policy。
- issue #118 促成标准 `skills/<name>/SKILL.md` 目录；修复后用户验证 `gh skill install` 与 `npx skills add` 可用，同时两者仍给出高风险/安全警告。
- issue #191/#192 证明 skill 指令本身能生成 schema-valid 但真实 Word 错误的结果；维护者在真实 Word 复现后修正 page break 和 TOC 规则。
- issue #186 报告高能力模型一次生成仍需约 10 分钟；维护者建议把重复场景沉淀为直接运行的 workflow/code。
- issue #158 展示 skill 注入层、模型工具能力和 CLI binary 三层之间的故障归因容易混淆。

## 初步判断

OfficeCLI Skills 应当理解为 OfficeCLI 垂直运行时的 agent control plane，而不是可脱离 CLI 复用的通用 Office 知识库。值得借鉴的是动态 schema、渐进加载、交付门禁和 reference manifest；不适合原样复制的是超长 SKILL、隐式继承、自动安装/自动覆盖，以及把运行时 bug workaround 长期堆进指令正文。
