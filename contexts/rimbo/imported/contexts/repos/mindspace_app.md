---
repo: mindspace_app
url: https://github.com/Mindspace-ai/mindspace_app
role: 移动端 App（iOS & Android）
status: active
language: typescript
owner: unknown
last_reviewed: 2026-05-18
---

# mindspace_app

## 角色

Mindspace 移动端 App，覆盖 iOS / Android。

## 技术栈

- TypeScript + Expo（EAS build / update）
- React Native + React Navigation（bottom-tabs / drawer / native）
- NativeWind / Tailwind
- axios
- 大量 expo 模块：Apple Auth / Auth Session / Camera / Haptics 等

## 入口与构建

- `npm run start` / `ios` / `android`
- EAS 云构建 + `eas update` 热更新（preview / prod 双 channel）
- EAS 项目 ID：`94f8f6eb-...`

## 与其他仓库的关系

- 调用 [`mindspace_backend`](./mindspace_backend.md) HTTP API
- 网页端对应：[`mindspace_web_frontend`](./mindspace_web_frontend.md)

## 当前节奏

最近推送 2026-05-01，停滞约 17 天，明显慢于其他活跃仓库（其他仓库都是近 3 天内推送）。是否仍在主航道待确认。

## ⚠️ 风险点（待核实，与本上下文任务并行处理）

仓库根目录疑似 commit 了：

- `credentials.json`
- `mindspace-477103-807b4cee4dc1.json`（看起来像 GCP service account JSON）

如果属实，是密钥泄露。处理路径不在本卡片职责内，参见独立的安全跟进。

## Open questions

- 节奏偏慢的原因（移动端优先级下调？人员变动？）
- 当前 owner / 主要维护人
- 上述疑似密钥文件是否真的在 git 跟踪中
