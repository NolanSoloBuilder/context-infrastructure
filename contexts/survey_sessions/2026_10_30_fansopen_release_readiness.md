# 粉丝团开通页发布就绪检查（2026-10-30）

结论：feat_codex/fansopen 当前不能直接发布。只执行只读检查、Git 模拟合并与测试；未修改业务代码、未合并、未发布。

## 冻结对象

- 仓库：fe/shopping/aurora
- 分支 / 远端头：feat_codex/fansopen / 16aaabe8ab5a1bb58ff1b3430fb735ce91cfc68c（2026-09-18）
- 当前远端 master：bfb336a0310ef870ac8941853cbbbf007fac0dfb
- 工作树：/Users/xuhao/Documents/Basic/aurora-fansopen-preserved，跟踪文件无改动。
- 分叉后：主干 1144 个提交，功能分支 11 个提交。26 个文件变化。

## 实现范围

新版传统未开通页、默认任务展示、商家入团券开关及推荐金额回填、金额转分与校验、单次开通/建券请求、成功刷新并选中配置页、业务失败重试与传输异常禁止盲重试、新增开通及升级券字段埋点。买手隐藏入团券并直接开通。四组轮播案例与素材已在代码中，推荐值回填也已实现，README 部分待办过时。成长计划 unopenedApply 页面保持原分流。

## 阻塞与缺口

1. git merge-tree --write-tree origin/master HEAD 返回 1。冲突文件 packages/promotion/promotion-story/src/index.ts。合并模拟未修改工作树；尚未解决冲突或验证整合后构建。
2. 分支没有本需求的 changeset，也未进入 master。docs/release.md 要求合入 master 后按根目录 changeset 流程发布，禁止用手动 formula deploy 替代。
3. ShoppingFanOpening.vue:323-333：若响应缺少成功状态，埋点被标记 unknown，但 unknownResult 未置 true，finally 解除 submitting，按钮仍允许重试。与 transport catch 的禁止盲重试处理不一致。此项为静态代码发现，未对真实账号制造异常/重复请求。
4. 最新 REDoc PRD 第五节要求二次确认，代码 confirmOpening 校验后直接 submit。需要确认最终业务口径；不能仅凭文档标完成认定一致。
5. 当前版本首次开团、买手真实开通和推荐数据联调尚缺本轮验收证据。README 仅记录 2026-09-06 商家重复开团及建券回读成功，并明确首次开团及 PGY 尚未实测；该记录不代表最新接口已验收。

## 平台核验

- PingCode 父需求 961020 显示已完成。
- 子任务 1022765「购物粉丝团开通页流程简化 - 开发」仍为测试中。
- 子任务 1022766「购物粉丝团开通页流程简化 - 联调测试」显示已发布，但其完成时间早于分支最终提交，不能作为当前版本验收证据。
- 服务端开发 1022731、服务端联调 1022732 显示已发布。
- delivery 按 feat_codex/fansopen 查询工作项交付和提测单，均无匹配记录。查询未命中不证明从未做过线下验证。
- FE project 1569 / publish app 20970：生产 1.3.118-20261029-161645-master-54706980；共享 STAGING feat.pgy-group-entry.oct-ca895db2，均非目标分支版本。未据共享 STAGING 推断个人环境状态。

## 验证

- promotionark Vitest：99 文件、587 项全部通过；其中本分支新增/修改的开通组件13项、模型12项、开通埋点3项、升级字段埋点2项，共30项通过。
- 测试使用模拟服务和组件；不替代真实网关、资金或首次开团验证。
- git diff --check 通过。
- 未执行完整构建、广泛类型检查或浏览器验收：当前合并冲突和发布合同已明确阻止直接发布；应在完成主干整合后对最终候选制品验证。

## 后续顺序

修复未知响应的重复提交保护；确定二次确认口径；整合最新主干并解决导出冲突；补本需求 changeset；对最终提交运行定向测试及构建，完成商家带券/不带券、买手开通、推荐值与状态回读、现有成长计划分流的预发验收；核对 CR/提测状态后按根目录发布流程推进。

## 来源

- https://pingcode2.devops.xiaohongshu.com/work-item-detail/961020
- https://pingcode2.devops.xiaohongshu.com/work-item-detail/1022765
- https://docs.xiaohongshu.com/doc/1e6af01a6564e1f6726df7afbe159dd4
- 本地代码、Git 远端引用、FE 平台与 ee-cli 实时只读返回。


## 后续执行：两个配套分支完成本地主干 rebase

用户授权 rebase 并核对 Ark / 蒲公英发布包。

- Aurora：feat_codex/fansopen 从 16aaabe8ab rebase 到 master 4ca7738a6bd，结果 a716e0e838；11 个提交保留。仅手动解决 promotion-story/src/index.ts 导出冲突，同时保留主干 cashback 与新开通页导出。range-diff 确认另外的 FAQ 自动合并保留主干新增换行/图标样式。
- Mono Live：发现同需求同名分支，原 6eb22d42 含两个配套提交；rebase 到 master 61a4fb096 后结果 f537d4a9e，无冲突、patch 等价。
- 两仓工作树干净，主干均为当前分支祖先；原始提交保留在各仓 refs/backup/fansopen-before-rebase-20261030。
- 未推送重写后的分支、未合并 master、未执行发布；未修复上文列出的未知响应重试问题，也未变更二次确认口径。

### 发布范围（按当前依赖和 Changesets 实际预览）

| 仓库 | 包 | 类型 | 当前版本 | 预览 patch 版本 |
| --- | --- | --- | --- | --- |
| Aurora | promotionark | 本需求直接发版，包含 Ark 页面与 PGY 使用的 MF remote | 1.3.120 | 1.3.121 |
| Aurora | @xhs/promotion-story | 本需求直接变更公共 UI | 0.0.22 | 0.0.23 |
| Mono Live | redlive-pgy | 本需求直接变更宿主接口注入与共享埋点实例 | 2.5.21 | 2.5.22 |
| Aurora | systemark | Changesets 自动依赖联动，无本需求源码改动 | 0.2.49 | 0.2.50 |
| Aurora | activityark | Changesets 自动依赖联动，无本需求源码改动 | 1.6.44 | 1.6.45 |

- ark-app-root 和 redlive-ark 无本需求改动，不在当前发布预览中。
- @xhs/shopping-fan-signup 出现在计划中但 type=none，版本不变，不是升级包。
- Aurora 主干另有 note-version-tracking changeset（datacenterark 5.6.15 → 5.6.16），直接根发布会带上。这是其他需求的待发布项，不计入本需求包。
- 预览通过临时 changeset 执行 changeset status，已清理临时文件；未创建持久 changeset 或修改版本。

### rebase 后验证

- Aurora 开通组件/模型/埋点：4 文件、30 项通过。
- PGY 接口测试：8 项通过。
- PGY 埋点/MF 合同：指定本次 Aurora provider 源码后，4 项通过，无 skip。
- 两仓 git diff --check 通过；未跑完整构建或浏览器验收。


## 后续执行：changeset 已提交并推送两个分支

用户明确授权补 changeset 并推送两个分支，准备发布。

- Aurora changeset：.changeset/fans-group-opening-simplification.md，promotionark patch + @xhs/promotion-story patch；提交 4212126baee。
- Mono Live changeset：.changeset/fans-group-opening-simplification.md，redlive-pgy patch；提交 09bdc887922。
- 两仓 changeset status 均成功输出发布计划，范围与前节相同。Aurora 的既有依赖版本不一致警告仍存在，未改动无关依赖。
- 两仓通过显式旧远端 SHA 的 --force-with-lease 推送 feat_codex/fansopen 成功，随后 ls-remote 核对与本地 HEAD 一致；工作区干净。
- 未合并 master、未创建发布 tag、未触发生产发布。之前的异常处理、需求口径及真实联调缺口仍未处理，不将推送完成等同于验收通过。


## 后续执行：已创建两个目标为 master 的 CR

- Aurora !5722：https://yunxiao.devops.xiaohongshu.com/cr/details?mrId=5722&projectId=38974&tab=general
- Mono Live !618：https://yunxiao.devops.xiaohongshu.com/cr/details?mrId=618&projectId=46587&tab=general
- 创建前核对远端 SHA 和本地 HEAD 一致、工作树干净，查询本人 opened CR 无同源分支命中。描述包含当前最终功能、验证边界、changeset 范围和未解决项，两个 CR 已互相引用。
- 两个 CR 均已正式关联已有前端子任务 1022765，归属父需求 961020，列表回读验证成功。平台只允许关联 subtask/bug，父 task 无法直接绑定。
- 创建后状态：两个 CR 均 opened、无代码冲突、canMerge=false；流水线尚未启动，评审尚未通过、结构化描述模板未填，PGY 额外有提测卡点。PingCode 关联项在状态查询之后已补齐。
- ee-cli cr update 仅支持标题/描述，不支持结构化模板。未伪造 checklist 已验收、未代审批、未自动合并或发布。
- Codex 附件工具不支持这两个内网 CR URL，调用返回 unsupported/invalid URL，未成功生成聊天附件；云效 CR 本身已创建并可通过上述链接查看。


## 后续执行：用户要求 Aurora 切 master 并 npm run publish

- 原 Aurora 主工作树仍 detached HEAD 5470698045，promotion-ark/CHANGELOG.md 有未合并冲突。Git 拒绝其他 worktree checkout master（主工作树的未完成操作保留 master 使用权）。未重置、清理或解决该现场。
- 在 /Users/xuhao/Documents/Basic/aurora-fansopen-release-20261030 创建独立共享对象 clone，使用独立 Git 引用；切换 master 并拉取至 41a9f17743263ce971b85d6688f61ea7076b7ef9，工作区干净。没有新增或改写公司的 MCP 本机配置。
- 期间远端 master 被沐秋（muqiu）于 2026-10-30 14:58:54 推送 release 提交，已消费 fans-group-opening-simplification 等全部待发布 changeset；本次没有重复执行 npm run publish，没有制造空提交或重复 tag。
- 远端 annotated tag promotionark@1.3.121、@xhs/promotion-story@0.0.23、systemark@0.2.50、activityark@1.6.45 均 peeled 至 41a9f17743263ce971b85d6688f61ea7076b7ef9，版本提交包含本需求最终实现。
- 发布提交另外包含 vendor-ark@3.0.43、fulfillmentserviceark@6.0.16 等其他已合并需求包。不要把它们记为本会话单独发版。
- 同提交云效 CI：pipeline 21663 / history 16152387，首次查询 running；https://yunxiao.devops.xiaohongshu.com/ci/project/38974/pipeline/21663/16152387。版本/tag 推送不等于生产页面已更新。


## 后续执行：Mono Live publish 被 master 保护规则拒绝，版本提交已送 CR

用户确认 Mono Live CR 已合并并要求 publish。

- 在原 mono-live 干净工作区切 master，pull --ff-only 至 29ca8459bd2f6986a323b2f5d7126a76920fbd2b（!618 已合并）。
- 按 .nvmrc 使用已有全局 Node 18.19.1 执行 npm run publish（根脚本 pnpm mono-publish）。消费唯一 changeset，生成 redlive-pgy@2.5.22 和发布提交 99b9531bec535ca4ace6de38b9f9ecfa1ddc142b，只改 package.json、CHANGELOG、changeset 三个文件。未新增业务源码。
- script 推 master 返回 remote rejected / pre-receive hook declined：You are not allowed to push code to protected branches on this project。CLI 顶层捕获错误，进程退出码虽为 0，发布仍未完成；不可据 exit 0 宣称成功。
- 保留版本提交，已推送 feat_codex/fansopen-release-2.5.22，并创建版本 CR !619：https://yunxiao.devops.xiaohongshu.com/cr/details?mrId=619&projectId=46587&tab=general，关联前端子任务 1022765 成功。
- 远端回读 release branch 为 99b9531bec535ca4ace6de38b9f9ecfa1ddc142b；master 仍为 29ca8459bd2f6986a323b2f5d7126a76920fbd2b，没有 redlive-pgy@2.5.22 tag。需先按正常门禁合并版本 CR，再为最终版本提交补推 tag 并核对 FE 构建发布。
- 本地仍在 master，HEAD 为生成的版本提交，工作区干净；未 reset 用户分支、未绕过保护规则、未部署。


## 流程核验与纠正：Mono Live 标准 Release 不是补版本 CR / tag 触发 CI

用户要求先确认正常发布流程，当前仅做只读调查，暂停后续发布及 CR 流转。

权威来源：mono-live README 链接的《使用文档：通用 monorepo》 https://docs.xiaohongshu.com/doc/6592e6a4cb6fed20a19589df6e684cdc，读取 hash 16037a72eb4fb301e9d13ac3423478f4。Release 段第274–310行明确：合并需要的 MR 后本地进入 master，执行 pnpm mono-publish；生成版本和 CHANGELOG，推 master 触发 CI，并推送 tag；CI 在分支上运行，tag 仅供存档。

- 根 npm run publish = pnpm mono-publish，使用仓库自2024年起固定依赖 @xhs/monorepo-presets@2.3.0-canary-no-push，非本轮临时替换。
- 实际发布实现顺序：检查分支/干净工作区；changeset version + pnpm i；release commit；git push origin 当前分支；changeset tag；git push --follow-tags。名字 no-push 不代表默认不推 master；--no-push 参数仅影响最后的 follow-tags，前面的分支 push 仍执行。
- 当前生效 CI34976 配置 acceptPush=true、acceptTag=false；最近 release 2.5.21 的 CI16140200 triggerType=push、ref=master、success，印证手册。
- 之前“补推 tag 触发构建/发布”的判断不准确，应更正为 master 分支推送触发 CI，tag留档。也不能将额外版本 CR619说成正常流程必需步骤，它只是之前权限失败后的替代提议，目前不应继续当作必经流程。
- FE prod 生效版本为 2.5.20-20261028-171514-master-b36d93a5；平台已有 2.5.21-20261030-103519-master-61a4fb09 候选，但并非生产当前版本。因此版本提交/CI成功/候选登记与生产上线必须分别报告。
- SSH只读身份探针 ssh -T 返回 Welcome to GitLab, @xuhao2!，认证身份匹配用户；本次实际失败点仍为该身份不能直接推受保护 master，不是缺少发布通知。未改权限、未发通知、未关闭/合并CR619。


## 保护分支权限只读核验

2026-10-30 GitLab Members UI 实时确认：xuhao2（用户本人）在 fe/live/mono-live 是 Developer；liyingyu 是 Maintainer。CI16140200 的 triggerEmail=liyingyu@xiaohongshu.com，triggerType=push，ref=master，2026-10-30 10:35:11，success，证明今天早些时候其他账号可通过 master push 发布。当前用户访问仓库 settings/repository 返回404且无Settings入口，无法读取精确的 protected master 推送白名单，不能进一步断言所有 Maintainer 当前都可推。结合本次 push 明确拒绝，证据指向用户的 Developer 角色权限不足，而非所有人一律禁止。未修改任何权限，临时只读浏览器标签已关闭。


## 权限补齐后完成 Mono Live publish 剩余步骤

用户明确确认权限已添加并要求继续。重新只读核对：本地 master 干净，HEAD99b9531be；远端 master29ca8459b，无2.5.22 tag，没有其他发布者消费/发布同版本。

未重复执行 version 或生成空提交，而是续做此前 npm run publish 内失败点之后的步骤：git push origin master 成功；按仓库 Node18.19.1 执行 pnpm changeset tag，仅生成 redlive-pgy@2.5.22；显式推送该 tag 成功。

远端 master 和 annotated tag redlive-pgy@2.5.22 peeled commit 都是99b9531bec535ca4ace6de38b9f9ecfa1ddc142b，工作区干净。云效CR619已自动显示merged，未另行代审批或点击合并。

本次master push于2026-10-30 15:21:53触发CI34976/history16153965，状态running：https://yunxiao.devops.xiaohongshu.com/ci/project/46587/pipeline/34976/16153965。发布命令的版本提交/tag交付已完成；不将CI运行中表述为生产已上线。
