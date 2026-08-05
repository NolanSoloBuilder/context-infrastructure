# GitHub Secret Scanning remediation（2026-08-05）

仓库：`NolanSoloBuilder/context-infrastructure`

## 事件范围

GitHub 在公开仓库中报告 16 条 open alerts：AWS 相关 5 条、Google 相关 3 条、Tencent Cloud 4 条、Tencent WeChat App ID 4 条。15 条位于误提交的 Chrome `History.sqlite`，1 条位于第三方参考站的完整 HTML 快照。

Chrome History 中的命中来源包括 OAuth fragment、微信登录 query、Google API query、S3/COS 预签名下载 URL 和已删除页面残留。GitHub 的 `validity` 均为 `unknown`，因此仓库侧无法证明它们已经失效。相同任务目录下的书签备份、审计输出和扩展计划还包含临时授权参数与内部域名，虽然没有全部触发 provider pattern，也必须按同一事件处理。

独立 `gitleaks` 扫描还发现 `contexts/rimbo/imported/contexts/lark_mirror/研发部门/APPLE登录.md` 含有一段可被 OpenSSL 成功解析的 private key。该 key 只命中这一份文件，但其风险高于 pattern-only 候选，必须从当前树和历史中移除，并在 Apple Developer 侧定位对应 Sign in with Apple key 后立即吊销。原文仅迁入本机私密归档，不能再次进入 Git。

## 仓库侧修复合同

当前树与 Git 历史需同时移除：

- `adhoc_jobs/chrome_bookmark_cleanup/backups/`
- `adhoc_jobs/chrome_bookmark_cleanup/history_snapshot/`
- `adhoc_jobs/chrome_bookmark_cleanup/output/`
- `adhoc_jobs/chrome_bookmark_cleanup/chrome_extension/plan.json`
- `tmp/yencheng_site_source/`
- `contexts/rimbo/imported/contexts/lark_mirror/研发部门/APPLE登录.md`

Chrome 清理工具的源码继续保留。私密运行数据迁移到 `~/Library/Application Support/context-infrastructure/chrome-bookmark-cleanup/`，第三方完整页面快照迁移到 `~/Library/Application Support/context-infrastructure/reference_snapshots/`。扩展运行计划改为本地文件选择，不再打包进扩展目录。

历史清理必须先在隔离 mirror clone 中 dry-run，并验证：目标路径在所有 refs 中不可达；当前源码与非目标文件保留；commit mapping 可审计；远端仅有 `main`、无 tag、无 open PR、无 branch protection 时，才进入 force push。force push 后重新读取 GitHub alerts，确认 location 不再被默认分支历史引用，再按实际来源填写 resolution。

## Provider 侧动作

仓库历史清理不能替代吊销与轮换。对本人或团队拥有的 AWS、Google、Tencent 凭据，应在对应控制台按告警类型逐条核对 usage/audit log，并遵循“先创建替代凭据并迁移消费者，再禁用旧凭据，最后删除旧凭据”的顺序。第三方页面或预签名下载 URL 中的凭据无法由本仓库所有者轮换，应在 GitHub 中按证据标记为 revoked、used in tests 或 false positive，不能把 `unknown` 直接解释为安全。

任何核对记录只保存 alert number、provider、owner、rotation time、验证结果和审计链接，不保存 secret、token、Cookie、完整 URL 或 credential fragment。
