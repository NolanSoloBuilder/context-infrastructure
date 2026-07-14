# OpenAI GPT-5.6 发布内容摘要

更新时间：2026-07-10（Asia/Shanghai）

## 核心结论

OpenAI 此次发布的重点是 GPT-5.6 模型家族，而非单一模型。新的命名方式把数字作为代际标识，把 Sol、Terra、Luna 作为长期能力档位，用于区分智能水平、速度和成本。

| 模型 | 官方定位 | 适合的工作 |
| --- | --- | --- |
| GPT-5.6 Sol | 旗舰、能力最强 | 高难度 coding、长链路 agent、复杂研究、专业知识工作、科学与安全任务 |
| GPT-5.6 Terra | 日常工作的平衡档、较低成本 | 大多数生产级 agent、代码开发、文档与分析、批量专业任务 |
| GPT-5.6 Luna | 最快、成本最低 | 高频交互、简单工具调用、分类抽取、批处理和延迟敏感场景 |

## 主要更新

- GPT-5.6 重点提升软件工程、computer use、专业知识工作、科学研究和 cybersecurity。
- Sol 新增 `max` reasoning effort，让单模型获得更长的推理时间。
- 新增 `ultra` mode，通过多个 subagent 并行完成复杂任务。它更接近执行模式，而非第四个基础模型。
- 官方称 Sol 在 Terminal-Bench 2.1 上达到新的最佳成绩，并重点展示 biology 与 cybersecurity 的提升。
- 新的 prompt caching 支持显式 cache breakpoint，最低缓存生命周期为 30 分钟。cache write 按未缓存输入价格的 1.25 倍计费，cache read 继续享受 90% 折扣。
- API 标价：Sol 为 $5 input / $30 output，Terra 为 $2.50 / $15，Luna 为 $1 / $6，均按 100 万 token 计算。

## 选型判断

默认生产模型更适合从 Terra 开始。只有任务失败代价较高、复杂度明显超过单次问答，或需要长时间自主执行时，才升级到 Sol。Luna 适合规模化、延迟敏感且结果容易校验的步骤。`ultra` 应留给能并行分工、可交叉验证的复杂任务；简单任务使用它会增加成本和编排开销。

## 可用性说明

截至本次核对，OpenAI 官方发布文章、Help Center 和开发者模型页仍有更新时间差。官方页面可以确认 GPT-5.6 已面向 API 与 Codex 的 selected trusted partners 提供 preview，并计划扩展至 ChatGPT、Codex 和 API；尚不能从官方页面确认 ChatGPT 已对全部用户普遍开放。实际账号是否可用应以产品内 model picker、API organization 和 Codex workspace 的授权状态为准。

## 官方资料

- [Previewing GPT-5.6 Sol: a next-generation model](https://openai.com/index/previewing-gpt-5-6-sol/)
- [A preview of GPT-5.6 Sol, Terra, and Luna](https://help.openai.com/en/articles/20001325-a-preview-of-gpt-5-6-sol-terra-and-luna)
- [GPT-5.6 Preview System Card](https://deploymentsafety.openai.com/gpt-5-6-preview)
- [OpenAI API Models](https://developers.openai.com/api/docs/models)
