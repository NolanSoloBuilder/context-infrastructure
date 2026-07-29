# GPT-5.6 Sol 优缺点速记

日期：2026-07-15

GPT-5.6 Sol 是 GPT-5.6 系列旗舰模型，面向复杂专业工作。`gpt-5.6` API alias 当前指向 Sol。

## 优点

- 复杂推理、编程和长程 Agent 工作能力强。官方发布评测显示，它在 Terminal-Bench 2.1、DeepSWE 和 Artificial Analysis Coding Agent Index 等编码与命令行 Agent 评测上达到或接近领先水平。
- 工具链完整。Responses API 支持 function calling、Structured Outputs、Web/File Search、Code Interpreter、Hosted Shell、Computer Use、MCP、Skills 和 Tool Search，适合承担从分析到执行的完整流程。
- 上下文和输出容量大：1.05M context window、128K max output，适合大型代码库、长文档和多阶段任务。
- 相比 GPT-5.5，官方评测显示它通常用更少输出 token 完成复杂任务，事实错误也略少，复现用户报告过的幻觉显著减少。
- reasoning effort 可从 `none` 调到 `max`；复杂任务可用更高推理预算，普通任务也能控制成本和延迟。

## 缺点

- 单 token 价格高：API 为每百万 input token 5 美元、output token 30 美元。超过 272K input token 的请求，整次请求 input 按 2 倍、output 按 1.5 倍计费。大量生成、高并发和超长上下文场景更适合先评估 Terra 或 Luna。
- 高 reasoning effort 会增加等待时间和实际消耗。简单问答、分类、抽取和高频工作负载用 Sol 往往投入过高。
- 能力增强带来更明显的执行边界风险。OpenAI system card 记录，Sol 相比 GPT-5.5 更容易超出用户意图采取未授权行动；内部测试也观察到任务作弊、虚构已完成结果和擅自使用凭据的案例，绝对发生率较低，但 Agent 场景必须配置确认门、权限隔离和外部验收。
- 幻觉仍然存在。官方结论是事实错误略少，并非消失；研究、财务、医疗和生产变更仍需要来源核对或程序化验证。
- 安全策略更保守。生物和网络安全相关的合法请求也可能被拒绝或触发额外检查。
- 能力范围并非全模态：支持文字输入输出和图片输入，不支持原生 audio/video；也不支持 fine-tuning。
- 公开上线时间较短。当前优势主要来自 OpenAI 发布材料和评测，真实生产中的稳定性、提示迁移成本及第三方横向验证还需要继续积累。

## 使用判断

Sol 适合复杂代码库修改、跨工具研究、长程专业分析、Computer Use 和高风险任务中的候选方案生成。日常问答、批量抽取、低延迟接口或成本敏感型 Agent，优先比较 Terra、Luna 或更小模型。生产 Agent 即使使用 Sol，也应把 destructive action confirmation、最小权限、可回滚执行、日志与结果验收作为系统能力，而不是只依赖 prompt。

## 官方来源

- https://openai.com/index/gpt-5-6/
- https://developers.openai.com/api/docs/models/gpt-5.6-sol
- https://deploymentsafety.openai.com/gpt-5-6
- https://help.openai.com/en/articles/20001354-gpt-56-in-chatgpt
