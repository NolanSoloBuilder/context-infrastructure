# OfficeCLI Skills 调研 Search Manifest

## 产出文件索引

| 文件 | 路径 | 说明 |
|---|---|---|
| Scratchpad | `tmp/officecli_skills_survey_20260715/scratchpad.md` | claim、快照与中间判断 |
| Search Manifest | `tmp/officecli_skills_survey_20260715/search_manifest.md` | 本文件 |
| 官方仓库快照 | `tmp/officecli_skills_survey_20260715/repo/` | shallow clone，commit `4ba79f0b` |
| 最终报告 | `contexts/survey_sessions/officecli_skills_survey_20260715.md` | 最终决策备忘录 |

## Subagent 原始产出

| Agent | 定位 | 状态 |
|---|---|---|
| `/root/official_architecture` | 官方架构、Skill 内容、加载和维护机制 | completed |
| `/root/issues_boundaries` | issues、PR、CI、失败边界 | completed |
| `/root/ecosystem_comparison` | 分发、AionUi、同类能力与第三方误述 | completed |

## 数据覆盖

- 官方仓库源码、README、根与 specialized SKILL、installer、updater、CI workflow、commit/release history。
- GitHub issues / PR：重点覆盖 skill 发现、context 成本、安装安全、schema drift、真实 Word 回归、性能与集成故障。
- Agent Skills 官方 specification，用于检查 progressive disclosure、目录结构和建议的上下文边界。
- 第三方页面只用于发现线索和识别误述，不作为核心 claim 的验证依据。

## 主要来源

- https://github.com/iOfficeAI/OfficeCLI
- https://github.com/iOfficeAI/OfficeCLI/tree/main/skills
- https://github.com/iOfficeAI/OfficeCLI/blob/main/src/officecli/Core/SkillInstaller.cs
- https://github.com/iOfficeAI/OfficeCLI/blob/main/src/officecli/Core/UpdateChecker.cs
- https://github.com/iOfficeAI/OfficeCLI/blob/main/.github/workflows/build.yml
- https://github.com/iOfficeAI/OfficeCLI/issues/69
- https://github.com/iOfficeAI/OfficeCLI/issues/87
- https://github.com/iOfficeAI/OfficeCLI/issues/118
- https://github.com/iOfficeAI/OfficeCLI/issues/158
- https://github.com/iOfficeAI/OfficeCLI/issues/186
- https://github.com/iOfficeAI/OfficeCLI/issues/191
- https://github.com/iOfficeAI/OfficeCLI/issues/192
- https://github.com/agentskills/agentskills
