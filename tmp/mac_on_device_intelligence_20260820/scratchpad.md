# Mac 端侧智能调研 Scratchpad

日期：2026-08-20

## Claim Extraction

| Claim | 来源层级 | 验证状态 | 边界 |
|---|---|---|---|
| Apple Foundation Models 可在 App 内调用系统端侧模型 | Apple 官方文档 | 已验证 | 依赖 Apple Intelligence 资格、开关、地区与模型下载状态 |
| 系统端侧模型适合摘要、抽取、分类、改写和结构化生成 | Apple 官方文档 | 已验证 | 复杂推理、代码、长上下文不是其强项；macOS 26 系统模型上下文为 4K |
| SpeechAnalyzer / SpeechTranscriber 支持长录音与实时端侧转写 | Apple 官方文档与 WWDC25 | 已验证 | 需要检查设备、语言和模型资产可用性 |
| macOS 有原生 TTS 与个人声音 | Apple 官方文档 | 已验证 | Personal Voice 有设备、语言、用途与授权限制 |
| Vision OCR 在本机处理 | Apple 官方文档 | 已验证 | 中文 OCR 的语言纠错与 custom words 支持有限 |
| Translation 可按需下载语言模型并在 App 中翻译 | Apple 官方文档 | 已验证 | 具体语种对需运行时检查 |
| MLX、Core ML、llama.cpp、whisper.cpp 构成自选模型部署路径 | Apple 与项目官方仓库 | 已验证 | 工程复杂度、内存、模型许可证需自行承担 |
| 端侧 Agent 可通过 tool calling 与 App Intents 执行动作 | Apple 官方文档 | 已验证 | 权限、确认、失败恢复仍需产品侧明确设计 |

## 核心判断

Mac 端侧智能可分为四层：系统现成能力、Apple 原生开发框架、自带或自选模型运行时、跨能力的本地工作流。最有产品价值的通常是第四层，而不是单个模型 Demo。

## 主要来源

- https://developer.apple.com/apple-intelligence/resources/
- https://developer.apple.com/documentation/FoundationModels/generating-content-and-performing-tasks-with-foundation-models
- https://developer.apple.com/documentation/Speech/SpeechAnalyzer
- https://developer.apple.com/videos/play/wwdc2025/277/
- https://developer.apple.com/documentation/AVFAudio/AVSpeechSynthesizer/
- https://developer.apple.com/documentation/Vision/recognizing-text-in-images
- https://developer.apple.com/documentation/Translation
- https://developer.apple.com/documentation/CoreML
- https://developer.apple.com/documentation/FoundationModels/expanding-generation-with-tool-calling
- https://developer.apple.com/documentation/AppIntents
- https://github.com/ml-explore/mlx
- https://github.com/ml-explore/mlx-lm
- https://github.com/ggml-org/whisper.cpp
- https://github.com/ggml-org/llama.cpp
- https://github.com/ollama/ollama

