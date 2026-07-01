# repos/

Mindspace-ai GitHub 组织下各代码仓库的速览，给 AI 在 session 里快速回答"X 在哪个仓库"、"Y 是什么栈"用。

> **不是源代码镜像**。每个仓库一份 markdown 卡片，记录角色、技术栈、入口、owner、与其他仓库的关系。详细情况以仓库 README / 实际代码为准。

## 目录结构

```
contexts/repos/
├── INDEX.md           # 一屏速查表（全部 7+1 个仓库一行一条）
├── <repo-name>.md     # 单仓库卡片
└── README.md          # 本文件
```

## frontmatter 约定

每张卡片顶部：

```yaml
---
repo: mindspace_xxx
url: https://github.com/Mindspace-ai/mindspace_xxx
role: <一句话定位>
status: active | archived | unknown
language: python | typescript | mixed
owner: <handle>          # 推断值用 ?<handle>，未知用 unknown
last_reviewed: 2026-MM-DD
---
```

## AI 加载策略

session 启动时不主动加载。当用户问"X 在哪个仓库"、"Y 仓库是干嘛的"、"我们后端用什么框架"时，AI 第一步读 `INDEX.md`，定位到对应 `<repo>.md`。

需要看实际源码 → 走 `external_repos/<repo>/` 本地镜像，**只 fetch 不 merge**，读 `origin/main`。完整协议见 `docs/EXTERNAL_REPOS.md`。

## 维护

- 信息源：仓库 README + 根目录构建文件（package.json / pyproject.toml）+ commit 作者
- `last_reviewed` 超过 90 天 → 重新扫一次
- owner 字段以 `?` 开头表示是按 commit 作者推断的，待对应 owner 自己确认
- 仓库归档 / 重命名 / 拆分时同步更新本目录
