# Cited Alpha 完整报告功能生产接线与验收（2026-09-14）

## 目标与当前验收边界

用户要求“完成完整功能”。验收必须由正式 API admission、Cloud Tasks、Backend Runner、Pi/ML Runner、回调审阅、持久化产物和来源读取组成；不能用之前隔离数据库中的 Tesla 报告替代。本次优先接口和数据验证，不进行 UI 截图。

**完整研究报告主链路已在生产验收成功**。最终结果见文末：正常API恢复任务成功入库，四类来源可读，PDF原字节与页面影像哈希核对通过。下文保留故障和修复过程，不把首次失败任务改记为成功。

## 接线

- ML 同镜像新增私有 research-control，仅 health/review/read-verified/read-page-image。独立 SA、独立数字 Secret，无 Cloud SQL/DocAI/执行路由；read 与 review 各一独立非排队槽，取消请求不提前释放实际工作容量。
- Backend API 接 research callback；独立 callback OIDC 仅 ML runner，原 run-task 保持 dispatch-only。审阅和文档读取固定走 control，freeze 和长执行保持 ML runner。
- research-enabled 与认证 owner 白名单联合控制新研究入口，owner 已校验为 Xuhao。新建工作区不再逐个手工加 workspace 白名单，其他账户默认保持旧行为。请求正文不能指定 owner 或内部服务地址。
- 原生 PDF 改由现有 MySQL 文件库登记私有 GCS 原件；上传不依赖旧 S3/Postgres/Celery。以 nativepdf_ 文件身份、doc_ 文档身份、owner、SHA、大小和固定 object key 绑定。研究启动时才执行 DocAI freeze，保留原字节和结构快照。上限 20,000,000 字节；研究 freeze 现有限额 100 页。
- Web 精确当前 owner API 路径携带 JWT 取 Blob，禁止重定向/任意目标携带 token，关闭/切换时取消并释放 Blob URL；兼容既有签名链接。

## 运行配置与 IAM

项目 cited-alpha-20260701，us-central1，所有 CLI 指定项目。

- ML Secret 新数字版本 3：配置 research-runtime callback 为 Backend API run.app，Vertex project 为本项目；agent_deep_research 与 workspace_report_semantic_verifier 通过模型策略选择 gemini-3.8-flash。
- control 独立 Secret cited-alpha-research-control-secrets-yaml 数字版本 1，仅 Vertex、review scenario、read-enabled、snapshot bucket 配置，不复制生产 DB 或外部平台凭据。
- Backend Secret 新版本 9：research-enabled=true，research-workspace-allowlist=[]，research-user-allowlist 仅已核实本人。Backend 模板历史上仍挂 latest，记录此限制，不能声称已实现其配置可复现回滚。
- control SA：Vertex User、Service Usage Consumer、其独立 Secret accessor、冻结 document snapshot 前缀 viewer；deployer 仅 control SA actAs 和独立 Secret 元数据 viewer。
- Backend API 增加 checkpoint 前缀和 user-files/ 前缀 create-only；保留既有 snapshot viewer。
- ML runner 增加平台文章快照前缀及 user-files/ 前缀 viewer；保留既有 DocAI 与 batch bucket 权限。
- Cloud Tasks 队列 maxConcurrentDispatches 从 2 调为 1，用于有界真实验收，防止两个长研究争用唯一 ML runner。
- DocAI processor ba7872f1c0ed02be/us 已通过只读 API 核实 ENABLED，OCR_PROCESSOR；没有用配置存在冒充解析成功。
- 本机模拟 ML runner 身份的只读尝试因未授予操作者 TokenCreator 被拒绝，没有为此扩权；实际服务身份权限以正常生产链路验证。

## 代码发布与离线验证

三个代码仓均继续绑定 feat_codex/financial-report-agent-plan-writer-20260717。旧未提交改动未纳入本次提交。

- ML PR33：b0ff214，control 隔离与部署接线，389 Python +16 Pi +21部署测试；合并 a995c721，Actions 34799261667。
- ML PR34：3383598，原生 PDF 原件/MySQL 适配，412 Python +16 Pi。
- BE PR38：f735de7 起，callback/control/owner admission，379 Python（1个既有 sibling-only deselect）+24部署；原生 PDF 补充仍在该 PR 更新。
- Web PR30：e113e28，私有 PDF 预览，60 tests、完整 build、35 SEO 路由检查。

## 验收输入

正式本人工作区 workspace-6646e106-1e05-4a16-bbfb-ddcd795dbb2e，由正常 POST /workspaces 创建。

计划报告：Tesla 2024 财年分析，2023 对比、关键指标表、盈利和现金流、平台后续文章观点。检索截止 2026-09-14，后续文章不得反写成 2024 已知事实。

PDF 为已归档 Tesla 官方 Q4 and FY 2024 Update，36 页、11,267,189 字节，SHA256 05dfde334f800ec5f0ee140c0dd78409f24ad775e11a0c68f8a6b534b04cafdc；与 10-K 是不同文件但同一发行人，不算独立第三方。

本轮运维/验收文件位于 /tmp/cited-alpha-complete-20260914，token 权限 600，不在本文或仓库保存凭据。验收脚本只核对当前 runId 的 sourceRunId、bundle hash、document checksum、citation/source anchor，不把旧报告算入。

## 生产验收进行中的回读

ML PR34 已合并 d115a3ca，Actions 34799794638 success，ML runner 00026-cdw 100%/Secret3；control首发00002-54b已验证匿名HTTP403。
BE PR38追加425a663后合并73e51482，Actions34800239962 success，API00049-hl7 100%。Web PR30追加3043a322，已合并，自动部署进行中。

账户纠正：数据库只读核对发现 Xuhao 的163邮箱账户与 gcloud 当前 Gmail账户为两个记录。正式Google账户是6a4cca322893e6cc23a81efd，Backend Secret10仅把这两个本人ID纳入owner allowlist；之前创建的空163账户工作区保留，没有搬运或覆盖历史数据。

Google账户实际验收工作区：workspace-0cceab24-198e-435d-ae50-2d12eb65f3ba，标题Tesla 2024财报与经营质量研究。正常上传36页官方PDF成功，fileItemId=uf_01f7063faf8145049234208d8200fbf4，documentId=doc_nativepdf_36c8c2e6fbee4c8bb2d8232c4f305760；owner preview-url返回requiresAuthentication=true，原件HTTP回读SHA一致，匿名访问拒绝，正常attachment成功。

正式SSE提交返回workspace-run-1bb2e3c15ca241c68e102073f1ebe917；API状态已确认running且harnessContractVersion=research-v1。本段记录启动，不等同报告成功。当前验收目录为/tmp/cited-alpha-complete-20260914/canary-google。

## 首次真实任务失败与收尾修复

首次run于03:09 UTC失败（modelCalls=30/toolCalls=60），不是上传或召回失败：已冻结PDF version dv-4419893f212697c80b0ee812dbd520515c15d75bc8666f37ad5a89ce061a80a9，登记19证据（11 filing、7 PDF、1平台文章）与6项计算。最后两次submit_report都在Pi schema阶段被拒，未通过语义审阅、未产生正式报告。table row额外type导致anyOf混入paragraph分支提示，下一轮错误修订又丢失table type并损坏heading键，随后预算耗尽。

正常retry纯函数检查已验证保留19证据、6计算、未审阅草稿和completed PDF；重新核对附件授权后复用版本，无需重做DocAI。重试是新run与新deadline，预算上限沿父run冻结配置，不把旧run改成成功。

ML PR35修复范围：SEC非法cell坐标返回当前已读行的可用索引；Pi诊断选择匹配discriminator的分支但权威schema不放宽；retained草稿提供精确错误键；最后6个模型调用预留submit/calculate，早期仍可补证；仅host已独立接受submit后以本地零usage stop结束，不额外调用模型。419 Python、19 Pi、15部署检查通过；feature 0c1eebd1a1c93ca8b3f5a164260a0456afc20c75，PR CI34802462580 success，merge05ac1bea243dee7af9456b93c6a721b7a9eae572，发布34802653858进行中。

Web PR30部署已成功：merge528a777dbb7d19d1da918e9c9e46da686ec507bc、Actions34800947040、Pages a1e943ca；正式域名/app/login HTTP200且静态资源引用与该deployment完全一致。Backend Runner实际00025-vnr/100%，镜像绑定73e51482d4129cbde1ba27f7f6ac1094d9bd11fa。


## 最终生产验收：成功

ML发布34802653858 success，merge05ac1bea；ML API00047-fcz、Runner00027-5dv、control00004-42v均为最新ready/100%，镜像绑定该merge。

正常POST retry创建workspace-run-9ca05266a24b4c8ca0b8aeef70b8ebc3，03:38:42 UTC以succeeded结束。恢复复用19证据、6计算和已冻结PDF，最后仅1次模型调用、2次工具调用。新审阅明确拒绝两处无本地证据/计算的同比单元格，以及将1.67 billion误写成1.67亿美元；修正为16.7亿美元后通过。不存在跳过审阅或人工伪造成功报告。

持久化artifact=workspace-artifact-b2b53fa0060b4c30bfdf4a4aee9b7a00，version=2，versionId=research-version-29597e48-f011-5dc3-9087-dc5476e8557f。sourceRunId与本次成功run一致，bundle hash、documentJson及documentChecksum匹配。22个引用均通过正常认证API解析，最终选用18条证据、6计算；包含SEC表格、SEC段落、PDF字段、平台文章，四类原文读取均验证。

PDF验收：原件11,267,189bytes/SHA与官方归档相同；第5页留存provider page为395,719bytes，实际响应与签名元数据SHA一致，17.9%字段框x=0.83420855/y=0.35066667/width=0.02775693/height=0.014。默认页面影像提供字段高亮；原始PDF的几何精度仍是page，不把未经验证的OCR坐标强行覆盖原始PDF。Web默认rendition页签、允许切换original。匿名原件请求403，owner读取成功。原PDF是同一份字节，不是重新生成的报告附件。

正式入口：[Tesla 2024 财报与经营质量研究](https://cited-alpha.forgepane.com/app/workspaces/workspace-0cceab24-198e-435d-ae50-2d12eb65f3ba)，使用已核实的Google本人账户登录。初始空primary占位由Web现有逻辑隐藏，成功报告作为supporting artifact可见。

持久验收数据位于[artifacts/20260914-production-report](artifacts/20260914-production-report/)，仅保存报告版本、运行结果、引用统计与PDF哈希/定位证明，不保存token。无UI截图测试。

### 已知范围与报告编辑质量

本次完成的是研究工作区的完整主链路。原生PDF上传限制20,000,000bytes，freeze上限100页；普通Chat与其它格式仍使用既有索引链路，不宣称已完成通用格式迁移。研究入口当前仅对两个核实本人账户开放。Backend Secret仍挂latest，需要后续单独收敛为数字版本。

当前正文约2518字符含指标表，五项指标及期间/金额单位齐全，平台2026-07-05文章独立注明后续观点，不能倒写成2024事实。剩余编辑优化：同比列标题包含%但一行使用bp；应更清晰解释展示毛利率四舍五入与-39bp差异；“唯一拉动因素”“市场普遍关切”措辞偏强；正文未单独呈现检索截止日；摘要与正文仍有部分重复。功能验收成功不等于这些编辑细节完美。

## 正式浏览器验收（同日追加）

用户明确要求在正式网页验证一个报告。本次使用Codex Computer Use控制本地Chrome，正常已登录会话打开上述Tesla工作区，实际看到v2正文、核心结论、目录和五项指标表；没有通过注入token或直接API读取替代网页操作，也没有重新付费生成报告。

- PDF引用11：右侧来源面板显示-39 bp、第5页第55行。点击原文位置后默认解析页成功加载，截图确认目标字段黄色高亮。
- 原始PDF：切换后显示第5/36页，真实页面成功渲染；下一页到第6页，返回引用页回到第5页，均通过。
- SEC引用3：显示2023营收96,773及年度、百万美元口径；上下文表格高亮2023总收入单元格。切换完整原文成功加载带research-evidence-target锚点的留存全文，原网站链接可见。
- 平台文章引用22：显示对应第8段；上下文和完整留存正文均可加载，正文明确提示可能为RSS摘录，原网站链接可见。这里不声称已访问付费发布方完整文章。
- 计算引用5：可查看两个年度输入、各自原文入口和公式(97,690,000,000 / 96,773,000,000 - 1) * 100 = 0.95%，精度2位。

结论：本报告阅读、右侧引用、原文预览、PDF字段高亮/原件翻页、计算解释的正式网页流程通过。浏览器标签已保留。下载、公开分享、本轮从网页新建生成流程不在此次已验证范围；既有报告编辑质量限制仍保留。

## 证据集合到完整原文（同日发布 PR31）

用户确认保留中间证据集合：报告引用 → 证据集合（摘录、来源、计算）→ 查看来源 → 完整留存原文高亮锚定。HTML 默认完整原文，上下文为可选视图；PDF 仅在原件具备可信字段坐标时优先原件，否则使用解析页字段高亮，保留原始 PDF 页级导航。无需重新生成既有报告。

Web 需求分支 feat_codex/financial-report-agent-plan-writer-20260717，任务提交 aa75b3c980c11e1ad7b517b756438569fe30d203；PR31 合并 f4f936235e6d72639f5fb09fb3bd6dfa242b46cc。50 项相关测试、完整构建通过。生产工作流 34814961515 成功，Pages 部署 794a5ef3；正式域名与部署域名资产列表一致（主包 index-Ci5u6i2D.js）。

正式 Chrome 刷新后，点击引用3先展示“来源与计算”集合及96,773摘录、2023期间/单位，再点击“查看来源”，无需切换标签，默认“完整原文”选中。截图确认完整 SEC 留存原文已自动定位并黄色高亮96,773单元格，右侧原文面板可见，验收通过。本轮没有重新生成报告。

## 原件版式验收纠正（2026-09-14）

用户指出上述PR31验收不满足原件高亮要求：解析页图像和经过统一CSS重排的HTML虽然保留了证据内容，却不能替代PDF原始页面与网页原始版式。前述通过仅代表证据集合到派生内容的导航通过，不代表原件高亮需求完成。

最终验收路径仍为报告引用→证据集合→查看来源。PDF默认直接渲染留存原始PDF bytes，在经原件文字层或已核验坐标系确定的字段位置覆盖高亮；原始文件哈希不变。HTML保留原始DOM、CSS布局与可用来源资源，在原DOM字段增加高亮锚点，脚本和活动内容隔离。仅有RSS正文的来源必须明确显示原始网页未留存，不能将正文重排冒充原网页；原站跳转定位与留存摘录分别标明。外站不支持嵌入或文字片段定位时不得宣称站内原件高亮完成。

### 原件修复实现与离线结果

- Web提交b1b1cbfda5871b5ba5de719380acc0236aff53b2（PR32）：PDF始终默认原件；解析页明确辅助；保留证据集合。HTML按留存原布局打开，纯平台摘录默认提示原网页缺失，原站文字片段定位链接与手动摘录分开。94项测试及完整构建通过。
- BE提交22dc9858d09dc3aef4a79676a080c431b1b2f3ca（PR39）：保留原HTML DOM/CSS/尺寸，同站HTTPS资源受CSP限制，脚本/活动内容关闭。支持新增text_match坐标并核对原件hash/页码/证据文字/唯一候选和方法；52项测试通过。
- ML提交dd0a15d（PR36）：从冻结原始PDF文字层取得原件坐标，唯一整行精确匹配；重复数字使用真实原件与provider内的同行文字关系消歧，禁止将provider坐标直接套用原件。新增text_match与原有field/page分开，不提升事实证据等级；428项portable测试通过。

真实Tesla原件7个PDF引用全部得到text_match，27%通过Capital expenditures同行锚唯一定位到下方CapEx行；结果见artifacts/20260914-production-report/native-text-geometry-results.json，约1.1秒，无新OCR/模型调用。text_match只声明文字位置匹配，不能证明任意PDF中不存在隐藏/遮挡文本；正式field仍沿用既有provider资格门禁。当前native匹配首版对旋转、非零crop等不支持页面保留页级定位。

本轮先BE兼容部署，再并行ML和Web（完整验收等待二者成功）：新ML增加text_match枚举，旧BE会拒绝，故不能沿用新ML先行顺序。所有旧page/field合同继续可用，无数据库变更。

BE正式发布完成：merge f3dfaa24c23f7ef1de9e1fed66e318f3b7722501，GHA34816515932 success；API cited-alpha-api-00050-79g与runner cited-alpha-workspace-runner-00026-vzk同镜像100%，正式health、迁移和队列恢复全部回读成功。云端Job启动曾等待数分钟，未重复触发，旧服务保持可用。

### 最终生产与原件验收

Web merge 01b7cc18ecff58cef00b5e714bbc2de419c8a59a，GHA34817728869 success；Pages c11c13ec-b069-401a-bc6e-7d2f0b10aae5。正式域与固定部署均为index-DPmvD_eq.js且SHA一致，证据web-original-source-asset-proof.json。

ML merge b1509319c09f45bb4941c55fea069d1fbf3fb5ff，GHA34817688364 success；API cited-alpha-ml-api-00048-x9z、runner cited-alpha-ml-runner-00028-gdl、control cited-alpha-research-control-00005-g9q，均100%/Ready且同immutable镜像，无候选tag残留。公开docs和私有OIDC health均200。

正式Chrome最终验证（同一既有Tesla v2，无重新生成报告）：
- SEC引用3→证据集合→查看来源：完整留存HTML直接加载并定位，截图确认原文件蓝白交替行、Times字体、原始财务表格排版保留，96,773在原单元格高亮。
- 平台文章引用22：先证据集合，查看来源后明确“此来源仅保存了文章摘录，原始网页请到发布网站查看”，显示同原站text fragment链接及手动“查看辅助摘录”，未伪造原件。本轮未验证发布方付费页中的文字片段命中。
- PDF引用11：先显示-39 bp证据，查看来源默认选中“原始PDF”；第5/36页，截图确认Tesla原版Financial Summary整页渲染、-39 bp直接原件黄色高亮；辅助解析页未自动打开。页面说明“按原件文字定位，请结合上下文核对”，未冒称provider字段坐标资格。

浏览器曾发生单个标签Debugger unattached，按文档建立新标签后恢复，没有改用其他浏览器工具或注入凭据。最终原PDF高亮页保留为用户交付页。此次仅两张必要版式/原件高亮截图，其余使用数据与AX核对。无新OCR、模型或报告生成费用。所有三仓无关本地改动保留。

### 既有网页 iframe 定位能力核查

用户提醒曾实现iframe原网页高亮。代码核查确认：Web app-shell/DocumentReferenceViewer.tsx 的 HtmlSourceFrameView 已通过source-html解析HTML，再以srcDoc+受控高亮脚本进行定位和多匹配导航；app-shell README明确URL-only网页也走此代理链路。新报告的research_report/article_source_view.py则只调用ArticleSnapshotReader读取留存平台正文并生成摘录HTML，未调用既有source-html原站抓取链路。因此当前RSS引用缺原网页预览属于新旧阅读器未接通，不能概括为产品无此能力。后续应复用既有抓取/预览能力并适配版本化evidence授权：抓到原HTML且匹配引用时展示原网页，正文快照命中和仅RSS摘录仍分别标注；当前网页不能冒充旧报告冻结来源版本。本次仅核查，尚未接通。

### RSS 当前原网页接入（本地验证，未发布）

本轮沿用三仓用户确认的 `feat_codex/financial-report-agent-plan-writer-20260717`，保留已有未提交改动。业务后端在 ArticleSnapshotReader 完成 owner/workspace/immutable snapshot 验证后，复用旧 URL SourceMaterial resolver 抓取和匹配；独立 `publisherPreview` 携带当前原网页 HTML、抓取时间与 anchored 状态，原始留存 html/targetHtml/hash/locator 不变。抓取限定同源 HTTPS、公网 DNS 固定连接、跳转逐次检查、5 MB 上限与 12 秒总时限；失败或引用不唯一时不提供原网页预览。

Web 默认展示成功匹配的当前原网页，复用 ResearchHtmlSourceFrame 的 Blob、空权限 sandbox 和原 DOM 高亮锚点；辅助摘录作为报告时点证据保留。无预览仍默认展开摘录。完整外链隐藏为图标和短文案。网页当前版本和报告证据版本明确区分。

验证：Web 来源视图 12 + PDF 3 项通过；修改涉及的 Web 文件无 TypeScript 错误，全仓仍有 43 项其它诊断。Chrome 使用后端真实 resolver 与 mock HTTP transport 生成的预览数据，验证原 DOM/Georgia 文本、黄色高亮、默认原网页、辅助摘录切换及失败回退。预览地址 `http://127.0.0.1:8099/output/source-preview/index.html`，明确标注后端处理样例，不访问生产 API；这不是生产实报验收，也不是原网站网络抓取成功的证明。当前未 commit、push 或部署。

实际引用 SeekingAlpha URL 单次网络实测：0.87 秒返回 fallback，不能宣称该文章原网页已可内嵌。记录 `/tmp/cited-alpha-publisher-preview-live.json`，未进一步推断付费墙或反爬原因，也未尝试绕过。

补充公网成功路径：example.com 完整引用经真实 HTTP、旧 resolver 和新 adapter 返回 anchored，耗时 0.43 秒，记录 `/tmp/cited-alpha-publisher-preview-example-live.json`。本地预览已替换为这一真实抓取结果，Chrome 确认原站布局和引用段落黄色高亮。后端最终 46 项测试通过（publisher preview/article sources/source view），加前端 15 项共 61 项。该公网测试仅验证预览能力，不代表所有发布网站均可抓取。

### 真实报告本地页面验收

通过唯一入口 `npm run dev:stack:cloudsql` 启动本地 Web 8099 / Backend 8079 / ML 9090 与 Cloud SQL Proxy 3307；三项 health 成功。Chrome 本地旧账号对目标 workspace 返回 workspace not found，通过正常退出和 Google 登录切到报告所属账号后，成功读取现有 Tesla 2024 报告 v2，未注入认证凭证、未修改报告或重跑模型。

真实产品路径：`http://127.0.0.1:8099/app/workspaces/workspace-0cceab24-198e-435d-ae50-2d12eb65f3ba`。第 22 条引用经过真实 citation/source API，返回 platform_article 与完整 targetHtml，publisherPreview 缺省；默认展开辅助摘录，链接只显示打开原网页。第 3 条来源 API 返回 retained_original_html、originalHtmlRetained=true 与原始 DOM 高亮锚点；Chrome 显示官方 10-K 表格原版式，在总营收2023列直接高亮 96,773，右侧原文抽屉正常。页面没有mock或fixture替换。此次是本地代码读取真实数据的验收，未发布。
