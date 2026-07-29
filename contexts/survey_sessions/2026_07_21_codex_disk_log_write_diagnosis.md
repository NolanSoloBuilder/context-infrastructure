# Codex 硬盘占用与日志写入诊断（2026-07-21）

## 结论

本机当前没有复现 Codex 的 GB 级日志暴写，也没有被旧进程占用的已删除 WAL 文件。核心原因是 `~/.codex/logs_2.sqlite` 已安装 `codex_block_logs_insert` trigger，诊断日志插入会被 SQLite 忽略。这个 workaround 有效控制磁盘写入，同时会让 SQLite trace 失去诊断数据。

磁盘仍有约 110 GiB 可用，Data 卷使用率约 75%。`~/.codex` 总计约 3.6 GiB，主要是 sessions 约 1.8 GiB、`.tmp` 约 845 MiB、plugins 约 545 MiB；这些属于会话和插件资产，并非本轮公开 bug 所指的日志文件。

## 公开问题

- [`logs_2.sqlite-wal` 流式响应期间持续写入 TRACE 日志](https://github.com/openai/codex/issues/17320)：2026-04-10 提交，截至检查时仍为 Open。报告写入速度约 5 MiB/s，峰值约 16 MiB/s，且 SQLite sink 不遵循 `RUST_LOG=warn`。
- [`codex-tui.log` 未轮转并持续增长](https://github.com/openai/codex/issues/16886)：2026-04-06 提交，截至检查时仍为 Open；多人报告文件增长到数 GB 乃至数百 GB。
- [Codex Desktop 正常使用时快速扩大 `logs_2.sqlite` / WAL](https://github.com/openai/codex/issues/24275)：2026-05-23 提交，截至检查时仍为 Open，说明问题也涉及 Desktop。
- [删除 WAL 后旧进程仍持有 inode](https://github.com/openai/codex/issues/22444)：该 issue 已关闭，但报告展示了 `du` 看不到、`df` 仍占用的情形；需要用 `lsof +L1` 单独检查。

## 本机证据

检查时间：2026-07-21 15:32–15:40，Asia/Shanghai。

| 项目 | 结果 | 判断 |
| --- | ---: | --- |
| Data 卷 | 324 GiB / 460 GiB，约 110 GiB 可用 | 无磁盘紧急状态 |
| `~/.codex` | 约 3.6 GiB | 总量可控 |
| `~/.codex/logs_2.sqlite` | 40 KiB，0 行 | 无日志库膨胀 |
| `~/.codex/logs_2.sqlite-wal` | 4,152 bytes | 10 秒观察无尺寸增长；后续 mtime 更新但尺寸不变 |
| `~/.codex/log/codex-tui.log` | 277,348 bytes | 2026-03-20 后未再写入 |
| Desktop 文本日志 | 合计约 8.5 MiB，21 个文件 | 按日期分目录；最大单文件约 3.4 MiB |
| 已删除但仍打开的 Codex 文件 | 0 | 无幽灵占用 |
| SQLite 完整性 | `state_5.sqlite` 和 `logs_2.sqlite` 均为 `ok` | 数据库当前健康 |
| 运行进程 | 一个 Desktop `app-server`；无旧 TUI 进程 | 无 stale/suspended writer |

当前 SQLite schema 中存在：

```sql
CREATE TRIGGER codex_block_logs_insert
BEFORE INSERT ON logs
BEGIN
  SELECT RAISE(IGNORE);
END;
```

因此，当前 `logs_2.sqlite` 零增长只能证明 workaround 生效，不能证明上游版本已经修复。目录中存在 2026-06-23 创建的 `pre_insert_block` 备份伴随文件，说明保护至少从该日期起存在。

当前 Desktop 版本为 `26.715.61943`（build `5628`），其内置 Codex CLI 为 `0.145.0-alpha.27`。全局 npm Codex CLI 为 `0.130.0`；检查时 GitHub release 页面列出的最新稳定版本为 `0.144.4`。全局 CLI 版本落后，但升级本身不能作为日志 bug 已修复的证据，因为相关 issue 仍为 Open。

`storage-analyzer` 的整机只读扫描在 `~/Library/Containers/app.pastenow.PasteNow` 上长时间执行，约 10 分钟后主动停止，未产出完整整机报告。上表的 Codex 专项数据来自独立的 `df`、`du`、`stat`、SQLite 和 `lsof` 检查，不依赖该未完成扫描。

## 后续监控

只读检查当前尺寸：

```bash
stat -f '%z %Sm %N' -t '%Y-%m-%d %H:%M:%S' \
  ~/.codex/logs_2.sqlite \
  ~/.codex/logs_2.sqlite-wal \
  ~/.codex/log/codex-tui.log
```

检查已删除但仍被进程占用的文件：

```bash
lsof +L1 2>/dev/null | rg -i 'codex|logs_2|codex-tui'
```

检查保护 trigger 是否仍在：

```bash
sqlite3 ~/.codex/logs_2.sqlite \
  "SELECT name, sql FROM sqlite_master WHERE type='trigger';"
```

如需验证新版是否真正修复，应先完全退出 Desktop 和所有 CLI/TUI 进程，备份日志库，然后临时移除 trigger，在受控的短任务中记录 WAL 每秒增长量。该操作会改变本机保护状态，本轮未执行。
