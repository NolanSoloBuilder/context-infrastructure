# 2026-10-09 追加清理 Android、模拟器和弃用应用数据

用户在第一阶段结果报告基础上进一步明确授权：Android SDK 在不影响 adb 的前提下删除；两个 iOS runtime、四个模拟器设备与约 3.799GB 设备数据删除；Notion、普通微信聊天与小程序本地数据弃用；LibreChat Colima 环境与 Chrome 本地 AI 也弃用。本记录是追加阶段，不改写第一阶段当时的保留决策。

追加执行基线为 2026-10-09 17:18:28，同一 Data 卷可用 **150.335762432 GB**，采用十进制。第一阶段最终快照为148.93GB，之后运行中的系统自然回收使本阶段起点发生变化。最终净增加以本阶段前后 `df -k` 为准，不能把目录分配块相加替代磁盘净增加。

## 已验证的追加动作

| 范围 | 动作和验证 | 目录占用减少 |
| --- | --- | --- |
| Android SDK | 删除 platforms、build-tools、ndk、emulator、system-images、sources、cmake 七类包；保留整个 platform-tools、`.android` 密钥和连接配置、原ADB进程与SDK路径 | 6.887124992GB，SDK由6.921GB缩为34.06MB |
| iOS模拟设备 | 原设备均已Shutdown，按四个冻结ID逐一 `simctl delete`，设备目录剩8KB | 3.798552576GB |
| LibreChat Colima | `colima delete --profile librechat --data --force`；列表已无profile，VM路径不存在，容器磁盘目录为空 | 10.593546240GB |
| Notion | 删除明确归属的Application Support、Safari扩展容器、cache、HTTPStorage、plist等本地状态；应用保持关闭，回读全部不存在 | 19.931136MB追加数据；第一阶段另已清7.39GB缓存 |
| 普通微信 | 删除聊天/小程序主容器、分享和FileProvider扩展、组容器、缓存和明确归属状态；应用保持关闭，回读全部不存在 | 6.830501888GB |
| Chrome本地AI | 正常退出后，仅修改原生本地生成式AI和历史AI搜索设置，精确删除遗留分类模型及PASSAGE_EMBEDDER target43；恢复默认Chrome后读回 | 163.614720MB追加模型；第一阶段另已清4.27GB基础模型 |

ADB清理前后为同一路径 `/Users/xuhao/Library/Android/sdk/platform-tools/adb`，版本36.0.0保持，动态依赖只有macOS系统库，platform-tools inode、adb密钥元信息和原server PID均保持。此执行shell清理前后 `command -v adb` 原本均无结果，未擅自修改PATH，未重置或重新连接实体设备。以后Android编译、NDK或模拟器测试需要重装相应包；这些包不属于ADB运行依赖。[Android官方Platform Tools说明](https://developer.android.com/tools/releases/platform-tools)。

LibreChat源码与`.git`、全局Colima/Docker CLI保留，Docker的default与desktop-linux context不变；本轮删除的是已明确弃用的虚拟机及容器持久卷，未额外创建备份。

## Chrome设置与实际边界

已按本机152.0.7977.152官方源码确认，并修改两个真实原生用户设置：

- `optimization_guide.on_device_foundational_model_user_settings=false`：关闭基础本地生成式AI，重开后仍为false。
- `optimization_guide.history_search_setting_state=2`：关闭历史AI搜索，重开后仍为2。

编辑期间完整JSON语义diff仅含对应请求设置变化，Chrome默认profile保留，书签、密码、历史和其它模型文件未删除。生成式AI模型目录、遗留分类模型目录与target43模型目录在最终检查时不存在。Notion和微信没有重新启动或生成数据。

反钓鱼、安全与浏览器预测模型保留。历史语义模型37.58MB是共享target，即使关闭历史AI搜索，Chrome的其它预测功能仍可能重新注册下载；未找到稳定用户设置能阻止全部共享下载，因此没有写内部flags，也没有关闭浏览器安全保护。不能把上述结果表述为“所有Chrome本地机器学习永不下载”。同版本官方源码与逐项验证保存在 `cleanup_extra_apps.json`。

## iOS系统资产处理

两个原runtime已通过原生 `simctl runtime delete` 执行删除，Xcode27、CommandLineTools、iPhoneOS27编译SDK和实体iPhone支持路径保留。原生命令返回0后，仍发现iOS18.4/Build22E238对应的MobileAsset父镜像9.116GB；此残留在物理文件消失前不计为回收。

Xcode Settings→Components实际显示Other Installed Platforms为No Items，无删除入口；随后退出本次临时打开的Xcode。系统设置→通用→储存空间→开发者中选中“模拟器支持”后，删除按钮仍disabled，只提供在Xcode中管理。系统设置已恢复原通用页面。

原生scan-and-mount无法清理父资产。MobileAsset精确加载返回 `5 (MAQueryNotEntitled)`，系统日志明确普通进程缺少该资产类型entitlement；未对无匹配对象调用purge，也没有关闭SIP或修改资产索引。

重新导入现有父dmg尝试未下载新文件，导入中只读内部镜像导致失败。此尝试在17:33产生 `Images/Inbox/5F5EAB22-FAD8-40B2-B42A-6A56A8ADB253.cxbd`，逻辑8,825,558,354B、分配8,825,561,088B。初次QA只检查登记列表与clone，漏查Inbox，导致错误估计runtime目录只剩4KB。root完整du发现并纠正，此次新增暂存不能当作清理前垃圾或额外回收收益。

这个精确暂存已核实inode、size、创建时间、SHA-256、非symlink与无占用句柄。普通管理员授权后的精确unlink实际返回 `Operation not permitted`；原生扫描和逐UUID删除无法匹配，原生 `add --move` 遇到已存在父资产的Duplicate而失败，未移除源文件。只对闲置simdiskimaged进行原生服务刷新，启动GC仍未回收该文件。后续新增登记、Unusable、ghost与挂载已原生删除/verify刷新清空，未再扩大尝试。

最终18:03完整du核实：CoreSimulator唯一大文件是本次cxbd，Cryptex/cache均0，设备与runtime登记为空，无模拟器挂载，无Inbox占用句柄。原系统父资产9.116GB和本次暂存8.826GB均真实留存，不能报告模拟器物理资产全部清完。父资产在服务启动时可能重新被发现并登记，本次刷新也发生过并已再次删除登记。

因此Android、设备与runtime目录的实际净减少应为 **10.253623296GB**，旧 **19.079GB** 已撤回；后者忽略了本次8.825561088GB暂存。当前没有已验证可用的精确回收入口，需要Apple/Xcode系统管理器识别或修复。最终处理状态与证据见 `cleanup_extra_runtime.json` 和 `cleanup_extra_runtime-inbox-final-qa.json`。

## 证据与结果

用户随后明确授权“Cursor没用了，删掉并且全部清理”。Cursor未运行，无需强退；主程序3.8.16、`~/.cursor`扩展/会话、cursor-agent runtime及用户CLI、缓存、HTTPStorage、偏好、最近文档与Cursor Safe Storage专属钥匙串均已清理。钥匙串只按精确服务名删除并回读不存在，没有读取秘密值。没有Cursor Homebrew cask或专属LaunchAgent，VSCode、Codex、Apple CursorUIViewService和共享全局Node包保持。

当前Cursor目录实际减少 **5.396639744GB**，仍有两个精确权限残留：`/usr/local/bin/cursor`（指向已删Cursor.app的root软链）与 `~/Library/Application Support/Cursor` 内root-owned backups及空外层目录 **1,273,856B**。Cua实际返回Mac已锁定且自动解锁失败，正常管理员入口无法继续；用户解锁请求已发出，未把这两项算作全清完成。

Cursor的两份wakanda真实源码不是缓存，原样同卷迁出至 `/Users/xuhao/Documents/Other/cursor-retained-worktrees-20261009/wakanda-monorepo`，共29,319,168B，不计释放。所有inode/size/mtime不变，1,920个非凭据源文件内容双读SHA256一致；`.env`/`.npmrc`只保留元信息，不读内容。原`.git`指针在清理前就指向不存在的主仓库worktrees元数据，原生Git操作失败；未篡改源码或虚构Git修复，也未遍历删除仓库内Cursor格式规则。

当前报告同卷快照可用 **178.167930880GB**，相对追加起点增加 **27.832168448GB**。这是真实当前可用变化，包含本阶段未能回收的iOS暂存及系统并发分配；不是把成功清理目录之和当作磁盘回收。累计相对最初34.809315328GB执行基线增加 **143.358615552GB**。Cursor最后两项与iOS两项均在报告中单独标未完成。

- [当前逐项报告](../../adhoc_jobs/storage_analysis_20261009/report.html)、[总账](../../adhoc_jobs/storage_analysis_20261009/cleanup_results.json)。
- [第一阶段冻结结果](../../adhoc_jobs/storage_analysis_20261009/cleanup_results_phase1.json)保持当时的保留范围与数字。
- `cleanup_extra_baseline.json`、`cleanup_extra_apps.json`、`cleanup_extra_colima.json`、`cleanup_extra_runtime.json`、`cleanup_extra_cursor.json`记录本阶段动作与验证。
- Codex「部署」及三个子会话保持；没有继续删除会话。认证文件、Mole whitelist、ADB密钥与LibreChat Git目录保持。本轮未自动重启电脑，也未手删swap。

可复用检查：原生runtime删除返回0或列表为空，不能证明关联系统父镜像已经释放；需同时检查准确父资产路径、整个持久Images/Inbox、异步Deleting状态是否结束，以及最终同卷可用空间。原生导入失败也可能留下受系统保护的物理暂存，不能以登记/clone消失代替物理副产物回收；不要在普通清理流程中循环重新导入受保护资产。
