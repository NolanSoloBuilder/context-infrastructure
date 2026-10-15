# 2026-10-09 磁盘逐项清理执行结果

用户授权对分析报告每项进行处理，并明确企业微信全部数据弃用、应用已删除。执行按具体路径核验，纯缓存原生清理，持久数据和活跃依赖保留。Mole已在此前升级至1.58.0；本轮进一步清理分析报告中的候选。

本轮同一 Data 卷 `df -k` 执行前可用 **34.81 GB**，最终报告快照可用 **148.93 GB**，增加 **114.12 GB**，约占494.38GB共享容量的 **30.1%**。GB采用十进制。前后增量包含系统自然回收与并发写入；目录分配块可能共享，不能把各项逻辑体量加总当作净释放。先前只读分析快照35.53GB与执行基线的差异来自运行中变化。

## 当次执行账目

| 项目 | 执行结果 | 目录体量/减少量与保留范围 |
| --- | --- | --- |
| 企业微信 | 主容器、辅助XPC/小程序、组容器及偏好共10处全部删除并回读不存在 | 约48.53GB；普通微信独立保留 |
| npx | 561个旧数字目录全部清除，最终剩余数字目录0 | 清理前完整扫描17.00GB；13个原哈希目录和3个运行中MCP保留 |
| npm/npx | Homebrew Node25.2.1随包postinstall恢复npm/npx11.6.2 | 35个其他全局包名称、版本、路径不变，npmrc元信息不变；无安装调用全局Prettier通过 |
| pnpm | 分别使用已装pnpm的原生prune覆盖两个store命名空间 | 减少约9.40GB，保留0.592GB store及global/.tools |
| Bun、uv | 原生cache清理 | 约2.02GB和1.94GB；Bun global/bin、Python解释器与项目虚拟环境保留 |
| NVM | 原生卸载18.20.5、18.20.7 | 约1.07GB；16→14版本，aurora精确18.20.1和独立全局工具所需版本保留 |
| 应用与Codex安装暂存 | 91个缓存/暂存条目处理，含Notion、Figma、Chrome、Lark、WPS、Code/Cursor及闲置安装暂存 | 目录减少约19.62GB；文档/账号/工作区状态和主runtime保留 |
| 公共项目依赖 | craft-agents-oss、LibreChat、Mindspace前端/App及4个地铁旧worktree，共8处node_modules清理 | 目录约6.45GB；源码、Git、manifest、locks回读不变；私有registry与活跃项目依赖保留 |
| CoreSimulator | 原生清dyld共享缓存，核对unavailable/outdated管理入口 | 约7.86GB；2个可用runtime、4个设备及3.799GB设备数据保留 |
| Android | 核对安装版本、AVD及临时下载缓存 | 无可证明可删的重复资源，6.92GB工具链保留 |
| Colima | 临时启动核对，原生image/builder prune、fstrim后恢复Stopped及default context | prune均0B，host占用无净减少；全部5镜像、6容器、10卷保留，数据库健康 |
| Homebrew | 原生cleanup | 删除旧Mole/portable-ruby约47.93MB，当前Mole及运行服务保留 |
| 系统VM | 只读核对，未删除swap/sleepimage，未自动重启 | 中途自然16.11→12.89GB，恢复应用后交换卷约15.03GB，不归因清理；保存工作后正常重启再测 |

Notion仅清普通缓存及Service Worker/CacheStorage，保留IndexedDB、Local Storage与数据库。Chrome清本地AI模型4.27GB和纯缓存，默认profile未删；Chrome和VS Code正常退出后恢复运行。微信原生退出返回用户取消，缓存、聊天和小程序状态均保留。WPS额外核实WpsUpdate/Bundle为156天前zip和解包更新载荷，清2.78GB，账号/备份/文档保持。应用目录未按整根盲删。

Codex `.tmp` 中完整marketplace仓库并不等于废弃暂存：config明确引用openai-bundled目录，其他完整clone服务于已注册源的后续更新，均保留。只清已证实无引用的闲置安装暂存。

## Codex会话的具体审批与执行

当次只读名单142条，约1.005GB rollout候选体量，105条原保留及141个未登记rollout保留。用户明确批准142条后，又指定原清单第138项 **「部署」保留**。冻结原清单不改编号；更正后的授权范围141条，部署ID `01a0fb51-b6f4-7522-afff-ee65c85201ee` 及3个关联子Agent均强制保留。

通过App内Codex0.160.0独立原生app-server stdio验证initialize与thread/list后执行 `thread/delete`，没有手写SQL删行或只删JSONL。有效141条逐一处理：**125条删除并验证，16条保留跳过，0失败**。rollout分配占用减少 **440.92 MB**。

13个父会话会级联删除未获批准的子树，另3个源与未登记保留rollout共用不可变ID，因此按授权边界保留。该行为以[原生request processor](https://github.com/openai/codex/blob/rust-v0.160.0/codex-rs/app-server/src/request_processors/thread_delete.rs)和[thread store实现](https://github.com/openai/codex/blob/rust-v0.160.0/codex-rs/thread-store/src/local/delete_thread.rs)核对，不用数据库改写绕过。

执行后state行与原生list均没有已删ID；原保留105条、部署及3子、全部预存未批准ID、受保护和未索引rollout都仍在，未索引文件大小未变，认证哈希未变，SQLite `quick_check=ok`，MCP工具与当前root/BeamJoin任务正常。

## 交付与边界

- [逐项清理结果报告](../../adhoc_jobs/storage_analysis_20261009/report.html)与[结构化总结果](../../adhoc_jobs/storage_analysis_20261009/cleanup_results.json)。
- [清理前分析快照](../../adhoc_jobs/storage_analysis_20261009/analysis_before.html)。
- [保留原编号的会话执行结果](../../adhoc_jobs/storage_analysis_20261009/codex_cleanup_candidates.html)，原冻结manifest、用户更正scope及native执行ledger均在同目录。
- 各 `cleanup_*.json` 是逐目录before/after、动作、保留原因与验证；不含凭据或聊天正文。
- 本地报告使用原静态server `127.0.0.1:8876`，没有删除API；报告与文档留存不需要该server持续运行。

扫描缺口没有盲删或强行提权。活跃BeamJoin、aurora、当前工具依赖、私有registry项目、工作区研究源码/outputs/.git/.worktrees源码、数据库卷、SDK和用户文档均保留。用户dirty修改未重置。本轮未重启电脑；余下系统交换空间只能在保存工作后正常重启再评估。

本轮重复出现进程参数非UTF8编码，使用字节读取或`errors=replace`进行ASCII路径guard，未打印参数或凭据。旧数字npx目录先按活跃PID保守排除，最终对数值碰撞核实命令路径和句柄后清掉6个零占用旧目录，避免仅凭PID值判断有引用。

清理结束中途曾见151.21GB可用；恢复应用后swap增加约2GiB，最终快照148.93GB。Chrome本地AI模型目录仍不存在，差异不是模型重新下载。
