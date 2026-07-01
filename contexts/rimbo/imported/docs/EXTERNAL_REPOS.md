# 外部仓库本地镜像协议

为了让 AI 在回答涉及代码的问题时能直接看到 Mindspace org 各仓库的最新代码，我们在本仓库根目录维护一个 **本地工作镜像** `external_repos/`。

> 该目录在 `.gitignore` 里，**不入本仓库 git**。

## 目录布局

```
<repo-root>/
└── external_repos/
    ├── mindspace_backend/
    ├── mindspace_ml_backend/
    ├── mindspace_web_frontend/
    ├── mindspace_app/
    ├── mindspace_user_simulator/
    ├── mindspace_local_sql/
    └── mindspace_info_source/         # 已归档，按需 clone
```

每个子目录是 Mindspace-ai 组织对应仓库的独立 git clone（不是 submodule，避免污染本上下文 git 状态）。

## AI 使用约定

### 何时 clone / 更新

**按需触发**：当用户问题涉及到某仓库的源码、配置、依赖、commit 历史时再处理那个仓。不预先 clone 全部。

判断流程：

1. 仓库在 `external_repos/<repo>/` 下不存在 → `gh repo clone Mindspace-ai/<repo> external_repos/<repo>`
2. 已存在 → **`git -C external_repos/<repo> fetch origin`**（只 fetch，**不 merge / 不 pull / 不 checkout**）
3. 读取最新代码时统一用 `origin/main`（或对应默认分支）作为 ref，例如：
   - `git -C external_repos/<repo> show origin/main:path/to/file.py`
   - `git -C external_repos/<repo> log origin/main --oneline -20`

### 为什么只 fetch 不 merge

如果 owner 在那个仓里有未提交改动 / 本地切到了别的分支，`git pull` 可能会破坏他的工作状态。`fetch + 读 origin/main` 既拿到最新远端，又不动本地工作树。

如果发现本地有未推送 commit / 未提交改动，**告诉用户但不动手处理**。

### 不要做的事

- 不要 `git pull` / `git merge` / `git checkout`
- 不要在 `external_repos/<repo>/` 里写任何文件
- 不要把 clone 出来的内容复制 / 挪到本仓库 `contexts/` 里
- 不要把 `external_repos/` 加入本仓库 git（已在 `.gitignore`）

## 与 `contexts/repos/` 的关系

| 目录 | 角色 | 入 git |
|---|---|---|
| `contexts/repos/<repo>.md` | 元信息卡片（角色、栈、owner、关系） | ✅ 入本仓 git |
| `external_repos/<repo>/` | 本地源码工作镜像 | ❌ 不入本仓 git |

回答用户问题的标准动作：

1. 先读 `contexts/repos/INDEX.md` 定位是哪个仓
2. 读 `contexts/repos/<repo>.md` 拿元信息
3. 需要看具体代码 → 按上面流程同步并读 `external_repos/<repo>/`

## 手动初始化（可选）

新成员第一次想把全部仓库都拉下来：

```bash
mkdir -p external_repos
for repo in mindspace_backend mindspace_ml_backend mindspace_web_frontend \
            mindspace_app mindspace_user_simulator mindspace_local_sql; do
  gh repo clone "Mindspace-ai/$repo" "external_repos/$repo"
done
```

不强制。AI 也会按需 clone。
