---
repo: mindspace_web_frontend
url: https://github.com/Mindspace-ai/mindspace_web_frontend
role: Rimbo 品牌站 + 产品 web app（一体）
status: active
language: typescript
owner: ?bravohenry / ?norahe0304-art
last_reviewed: 2026-05-18
---

# mindspace_web_frontend

## 角色

**品牌站 + 产品 web app 一体**：既是 Rimbo 对外品牌官网（landing + SEO），也是登录后的产品 web 界面。

> 内部 package 名 `rimbo-landing` 是历史命名，不再准确反映其当前角色。

定位语：Rimbo — Personal Intelligence Agent（面向投资人和创作者）。

## 技术栈

- TypeScript + React + Vite
- Tailwind CSS + Framer Motion + Unframer
- Radix Dialog + Zustand + react-router-dom
- posthog-js（埋点）
- pdfjs-dist

## 入口与构建

- `npm run dev` / `npm run build`
- `build:app` / `build:prerender` / `build:seo` —— 多目标构建（产品 app / 预渲染 / SEO）
- 部署：GitHub Actions 蓝绿到自托管 Docker runner（main → 8099, preview → 8100）
- 本地容器化：`scripts/deploy.sh`

## 与其他仓库的关系

- 调用 [`mindspace_backend`](./mindspace_backend.md) HTTP API
- 移动端对应：[`mindspace_app`](./mindspace_app.md)

## 备注

- 仓内 `CMS_GUIDE` / `REFACTORING_SUMMARY` 暗示近期有较大重构
- commit 作者主要为 bravohenry / norahe0304-art —— owner 字段为推断值，需确认

## Open questions

- 「品牌站 + 产品 app 一体」是否长期方向，还是某天会拆成两个仓库 / 子目录
