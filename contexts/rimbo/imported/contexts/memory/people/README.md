# memory/people/

每个团队成员的私域记忆。**单作者**——`<handle>/` 目录只能由 `<handle>` 本人的 AI 写入。

## 结构

```
people/
├── README.md
└── <handle>/
    ├── observations.md     # 每日观察(由 observer.py 追加)
    ├── preferences.md      # 反复浮现的偏好(由 reflector 蒸馏)
    └── current_focus.md    # 最近在做的事(可被本人 / AI 主动更新)
```

## AI 加载策略

AI 在和 `<handle>` 对话时只加载 `<handle>/`，不加载别人的，避免上下文污染。`observations.md` 不全文加载，按主题检索。

## 写入

- `observer.py` 每日 cron 追加到 `<handle>/observations.md`
- `reflector.py` 每周提议更新 `<handle>/preferences.md` 和 `<handle>/current_focus.md`
- 用户主动让 AI 记某事 → AI 写入对应文件，可直接 commit（单作者目录）

## 与 OBSERVATIONS.md 的关系

`contexts/memory/OBSERVATIONS.md` 是团队全局观察池，append-only。`reflector.py` 每周从所有 `people/<handle>/` 里蒸馏出有跨人价值的观察，提议追加到全局 OBSERVATIONS.md（走 PR）。
