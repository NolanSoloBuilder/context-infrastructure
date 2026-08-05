# Chrome Bookmark Cleanup

这组脚本会读取 Chrome 的书签和 History。书签 URL、访问记录、OAuth fragment、预签名下载地址及内部域名都属于私密数据，不能进入 Git。

## 私密数据边界

源码保留在本目录。运行数据默认写到：

```text
~/Library/Application Support/context-infrastructure/chrome-bookmark-cleanup/
├── backups/
├── history_snapshot/
└── output/
```

可用 `CONTEXT_INFRA_PRIVATE_DATA_DIR` 覆盖根目录。三个 Node 脚本都会设置 `umask 077`，新建文件仅允许当前用户读取。

## 使用顺序

```bash
node audit_chrome_bookmarks.js
node organize_chrome_bookmarks.js
node apply_organized_bookmarks.js
```

`organize_chrome_bookmarks.js` 同时生成 `output/bookmark_plan.json`。若使用 `chrome_extension/`，在扩展页面中手动选择这个本地文件；扩展包内不保存个人书签计划。

不要提交以下内容：Chrome History 数据库、书签备份、审计 CSV/Markdown、整理后的书签 JSON、扩展执行计划，以及包含完整页面源码的第三方站点快照。
