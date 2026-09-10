# Matt Pocock Skills 工作流对照

核对日期：2026-08-27  
官方仓库：[mattpocock/skills](https://github.com/mattpocock/skills)  
核对提交：[`6654f6b60cd9d5be8b54c6fafe44346dabeb3b76`](https://github.com/mattpocock/skills/tree/6654f6b60cd9d5be8b54c6fafe44346dabeb3b76)

## 博文直接涉及的 Skills

| 博文步骤 | 官方 Skill | 实际职责 |
| --- | --- | --- |
| setup Matt Skills、选择 issue tracker | [`setup-matt-pocock-skills`](https://github.com/mattpocock/skills/tree/6654f6b60cd9d5be8b54c6fafe44346dabeb3b76/skills/engineering/setup-matt-pocock-skills) | 为当前仓库记录 issue tracker、triage labels 词表和领域文档位置。它负责配置约定，本身不负责把需求批量变成 issues。 |
| 大型、多会话需求对齐 | [`wayfinder`](https://github.com/mattpocock/skills/tree/6654f6b60cd9d5be8b54c6fafe44346dabeb3b76/skills/engineering/wayfinder) | 把尚未明确的大任务组织成 decision-ticket map，逐项消除决策不确定性。它默认只规划，不实现。 |
| 单会话需求对齐 | [`grill-with-docs`](https://github.com/mattpocock/skills/tree/6654f6b60cd9d5be8b54c6fafe44346dabeb3b76/skills/engineering/grill-with-docs) | 追问计划和设计，同时更新领域词汇与 ADR。底层组合 `grilling` 和 `domain-modeling`。 |
| 界面或状态模型原型 | [`prototype`](https://github.com/mattpocock/skills/tree/6654f6b60cd9d5be8b54c6fafe44346dabeb3b76/skills/engineering/prototype) | 用可丢弃代码回答一个设计问题；UI 分支会生成多个可切换方案，logic 分支会生成可交互状态演示。 |
| 形成开发规格 | [`to-spec`](https://github.com/mattpocock/skills/tree/6654f6b60cd9d5be8b54c6fafe44346dabeb3b76/skills/engineering/to-spec) | 把已经对齐的会话与代码库认知综合成 spec，并发布到 issue tracker；它不会重新访谈。 |
| 拆成开发票据、建立依赖 | [`to-tickets`](https://github.com/mattpocock/skills/tree/6654f6b60cd9d5be8b54c6fafe44346dabeb3b76/skills/engineering/to-tickets) | 把 spec 分成可独立验证的 tracer-bullet tickets，标明 blockers，并发布到 tracker。 |
| 实现票据 | [`implement`](https://github.com/mattpocock/skills/tree/6654f6b60cd9d5be8b54c6fafe44346dabeb3b76/skills/engineering/implement) | 按 spec 或 tickets 实现，过程中调用 `tdd`，结束后调用 `code-review`，再提交当前分支。 |
| 测试驱动实现 | [`tdd`](https://github.com/mattpocock/skills/tree/6654f6b60cd9d5be8b54c6fafe44346dabeb3b76/skills/engineering/tdd) | 在预先确认的测试 seam 上执行逐个 vertical slice 的 red-green 循环。 |
| 代码审查 | [`code-review`](https://github.com/mattpocock/skills/tree/6654f6b60cd9d5be8b54c6fafe44346dabeb3b76/skills/engineering/code-review) | 并行检查 Standards 与 Spec 两条轴线，最后并列汇总。 |

## 博文没有点名，但流程内部会调用的 Skills

- [`grilling`](https://github.com/mattpocock/skills/tree/6654f6b60cd9d5be8b54c6fafe44346dabeb3b76/skills/productivity/grilling)：`grill-with-docs` 和 `wayfinder` 使用的追问原语。
- [`domain-modeling`](https://github.com/mattpocock/skills/tree/6654f6b60cd9d5be8b54c6fafe44346dabeb3b76/skills/engineering/domain-modeling)：维护 `CONTEXT.md` 领域词汇与 ADR。
- [`research`](https://github.com/mattpocock/skills/tree/6654f6b60cd9d5be8b54c6fafe44346dabeb3b76/skills/engineering/research)：`wayfinder` 遇到外部事实阻塞决策时，交给后台 agent 调研。

## 正确理解这条链路

常规、单会话可对齐的需求：

```text
grill-with-docs -> prototype（按需） -> to-spec -> to-tickets -> implement
                                                        |-> tdd
                                                        `-> code-review
```

超过一个 agent session 的大型、模糊项目：

```text
wayfinder -> 逐个解决 decision tickets -> to-spec -> to-tickets -> implement
```

`wayfinder` 与 `grill-with-docs` 主要按会话规模选择。前者负责多会话的决策地图，后者负责单会话内的需求对齐。

## 不属于 Matt Skills 的两项

- “新建 goal”是 Codex 的运行管理能力。当前官方 Matt Skills 仓库没有 `goal` Skill。
- “每个 issue 新建一个侧边栏独立任务”是 Codex 的 task/thread 能力。它是一种上下文隔离和并行执行方式，也不是 Matt Skill。

安装入口以官方 README 为准：

```bash
npx skills@latest add mattpocock/skills
```

安装后，每个仓库先运行一次 `/setup-matt-pocock-skills`。
