# 移动 App 一键托管生产流程调研 Scratchpad

日期：2026-07-17

## 问题定义

这里把“一键托管生产流程”定义为：代码仓库接入后，平台托管 iOS/Android 的构建环境、签名凭据、测试、制品、内测分发、商店上传、审核提交、分阶段发布与 OTA 更新。后端运行时、数据库、推送、监控属于相邻但独立的生产面。

## Claim Extraction

| Claim | 来源层级 | 验证通道 | 当前状态 |
|---|---|---|---|
| Expo EAS 可以从 Git push 自动完成双端构建，并把成功制品上传商店 | Tier 1: Expo 文档 | Expo GitHub issues、Reddit 生产经验、商店官方限制 | 部分验证；上传可自动，首次配置和审核门禁仍存在 |
| EAS Workflows 能按 native fingerprint 在 binary build 与 OTA update 之间自动选择 | Tier 1: Expo 文档 | runtime version、OTA 失败与回滚文档 | 已验证能力；原生代码变化仍需新 binary |
| Codemagic/Bitrise/Appcircle 可以跨 Flutter、React Native、原生 iOS/Android 托管 build-sign-submit | Tier 1: 各厂商文档 | 独立迁移与生产问题 | 待交叉验证 |
| 市场已经有等同 Vercel 的首次接入后一键生产发布 | Tier 1-2 营销表述 | Apple/Google 官方门禁、首发要求、开发者实际发布记录 | 未成立 |
| Apple/Google 的开发者身份、协议、商店资料、测试和审核可被第三方平台完全代理 | Tier 1-2 营销表述 | Apple/Google 官方帮助中心与 API 权限 | 已反驳 |
| Google AI Studio 已经提供 prompt 到 Android production 的一键发布 | Tier 1: Google 文档 | Google AI Studio 限制页、Play production 要求 | 已反驳；仅到 internal testing track |

## 初步判断

1. “托管构建与发布流水线”已经成熟；“托管整个移动生产环境”仍然由多个系统拼接。
2. React Native/Expo 新项目中，EAS 最接近低配置的双端方案。
3. Flutter、原生或多技术栈团队更适合 Codemagic；复杂团队治理和 release management 更适合 Bitrise；私有化/企业分发是 Appcircle 的差异点。
4. 任何方案都无法消除商店所有权与人工/政策门禁。Google Play 新个人账号还需要 12 名测试者连续 14 天 closed test；iOS 需要 App Store Connect app record、metadata、privacy、审核与账号角色。
5. OTA 只能替换与现有 native runtime 兼容的 JS/assets，不能把原生功能更新绕过商店审核。

