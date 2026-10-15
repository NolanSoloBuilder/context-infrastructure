# 2026-10-09 清理后的磁盘占用与下一步

本轮按用户要求只读分析，没有进一步清理、修改工具链、重启或关闭用户应用。重点路径通过 `du -x -k` 和 CLI/目录元信息核验；Mole 整机 JSON 返回 `partial`，因此没有将其约20GB扫描结果当作整机总占用。

最终 APFS 快照：内置容器总容量 **494.38 GB**，已用 **458.86 GB**，可用 **35.53 GB**，剩余约 **7.2%**。上轮刚清理后约32.5GB可用，本轮观测在34.9–36.1GB附近变化；并发运行和系统回收会继续改变数字。本文GB为十进制，目录统计是分配块画像，硬链接/APFS共享及根子目录包含关系使其不能直接相加，也不等于删除后一定能释放的字节。

## 已核实的大项

| 项目 | 占用 | 性质与处理边界 |
| --- | ---: | --- |
| 企业微信 Data | 48.42 GB | 账号、聊天附件和本地文档；安装目录/Spotlight未找到应用，仅能判断疑似残留。需要先确认资料保留、导出与使用状态 |
| 系统 Developer | 18.29 GB | 含iOS26.3镜像8.39GB、dyld共享缓存7.86GB和CLT；`du -x`排除挂载卷重复统计 |
| 系统旧iOS runtime backing | 9.12 GB | 在AssetsV2，与上述Developer独立；不用的版本应通过Xcode/simctl runtime管理入口卸载 |
| npx总目录 | 18.15 GB | 561个旧数字目录17.00GB，13个现代哈希目录1.15GB，其中三个在运行 |
| 系统VM交换卷 | 16.11 GB | 真实swap位于`/System/Volumes/VM`；保存工作、正常重启后复测，可释放量未知 |
| 16个NVM Node版本 | 12.57 GB | 包含各版本全局CLI，应先核对项目`.nvmrc`及全局工具，筛选不用的版本 |
| Colima | 10.59 GB | LibreChat profile已停止，持久虚拟盘；数据库/上传内容/卷占比未验证 |
| pnpm共享store | 9.99 GB | 原生prune只清未引用包，实际收益未知；根目录还含global与.tools |
| Codex根目录 | 9.80 GB | archived_sessions4.66GB、thread_history_1.sqlite1.58GB、sessions0.77GB；保留会话与索引一致性 |
| Notion | 7.41 GB | 普通Cache/Code Cache约0.90GB，Service Worker离线状态6.49GB；应用安装查询无结果，整目录仍需判断 |
| Android SDK | 6.92 GB | 只核实到一个NDK和一个Android36系统镜像，没有重复版本证据 |
| Chrome本地AI模型 | 4.27 GB | 可再下载模型，Chrome当前仍运行；清理后应用再次请求内置AI可能重下 |
| Figma明确普通缓存 | 1.14 GB | 只包括v42的Cache和Code Cache，保留Service Worker及用户档案 |
| Bun下载缓存 | 2.02 GB | 与install/global和bin分开，停止相关任务后用原生命令处理 |

企业微信`Data`与其随后单测的`Documents/Profiles`来自不同遍历，不能相加修正父目录总量。企业微信Profiles单测约39.38GB，属于账号关联数据，不能整体当缓存删除。

## 下一步顺序

1. **先处理全局工具链与旧npx安装。** 本机默认`node`为25.2.1，但`npm`/`npx`为6.14.18，均已复核软链与实际版本。现装`libnpx/index.js:146-151`按PID建立`_npx`目录，在进程退出时注册清理；大量残留与退出清理未完成相符，具体退出/中断原因尚未验证。先统一默认全局Node/npm/npx来源，固定常用MCP/CLI的全局版本并验证入口。再在维护窗口按进程与具体路径列清单，定向清旧数字目录；现代哈希和运行中根保留。候选上限17.00GB。
2. **应用及下载缓存专项。** 退出相关应用后，清Notion/Figma明确普通缓存2.03GB；确认不需要Chrome内置AI模型后再处理4.27GB；Bun缓存约2.02GB。与旧npx合计约25.3GB候选上限，不包括pnpm额外收益。这里不触碰浏览器用户档案、Notion离线分区、聊天数据或项目源码。
3. **pnpm原生prune，再按实际收益评估。** 先核对当前pnpm版本、store dir、全局CLI并完成安装任务；使用`pnpm store prune`，保留global/.tools。store的9.99GB体量不能预先承诺全部释放。
4. **保存工作后正常重启再读盘。** 当前VM卷约16.1GB，其中swap可能部分回收，也可能随重启后的内存压力增长。`/private/var/vm`只有2.15GB的sleepimage，不代表当前swap；不手删swap或sleepimage。
5. **如果还需更多空间，再选择数据和环境。** 企业微信48.4GB若已弃用且资料导出完成，收益最大；继续使用则在应用内按大附件审查。接着选择不再需要的Node版本、iOS runtime、Colima环境和不活跃项目依赖。常用应用、本机数据库、Maven及当前项目默认保留。

项目示例：armor的node_modules3.33GB、craft-agents-oss2.22GB、LibreChat2.04GB、mono-live1.75GB。是否清理取决于近期使用，重装还依赖网络和私有registry。当前工作区4.18GB中含adhoc_jobs1.96GB、worktrees0.87GB、tmp0.61GB，不能仅凭临时目录名删除任务成果或活跃worktree。

Codex会话如需清理，按仓库规则保留`【长期】`前缀、正在运行会话和automation，先列当次dry-run清单，再取得确认，通过App能力一致处理会话和索引；不手删SQLite或只删rollout文件。

## 扫描缺口与交付物

Documents根、aurora根与其node_modules超时，大部分其他项目已单独补测；`private/var`总量超时。Containers根未完整完成，企业微信/微信/WPS重点Data已补测。FileProvider一个目录deadlock、PasteNow超时，以及受隐私/管理员保护的系统目录仍有缺口。普通应用本体按单App测到约29.71GB，SMPrinterClient一处权限不足使总量为下限。未发现Time Machine本地快照；仅有不可清除的系统启动快照，未列入候选。

- [只读交互报告](../../adhoc_jobs/storage_analysis_20261009/report.html)
- [分析JSON](../../adhoc_jobs/storage_analysis_20261009/analysis.json)
- 同目录的`*_evidence.json`保存各重点范围的只读扫描元信息，不含凭据或聊天正文。
- [Chrome官方模型管理说明](https://developer.chrome.com/docs/ai/understand-built-in-model-management)：模型由Chrome管理，未来应用调用内置AI可能重新下载。

报告没有删除接口。本轮没有执行报告中展示的任何清理命令。
