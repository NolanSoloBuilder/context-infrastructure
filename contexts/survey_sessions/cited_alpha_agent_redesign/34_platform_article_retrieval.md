# 平台文章信源库接入（2026-09-11）

## 产品行为

平台 `source_items` 文章库接入现有通用 Pi Research Agent，与 SEC、上传文件并列。新任务获得 `search_articles → read_article → cite_article` 三个工具，模型按研究问题决定搜索和引用；不是强制每个结论凑一篇文章，也没有恢复旧的固定维度流水线。

搜索是现有 MySQL 全文 + LIKE 召回，不宣称已实现向量检索、BM25、Hybrid 或 Rerank。查询只读 READY/ANALYZED 全局平台文章；发布日期截止条件在 SQL LIMIT 前执行，截止时点未知的文章排除。此库不是用户私人频道内容。

阅读阶段精确读取 sourceId/itemId 对应正文，留存完整平台捕获内容到私有 GCS 内容寻址路径；搜索摘要不能直接作为证据。引用只接受已经读到的段落编号，不接受模型自填 URL、正文、owner 或数值。Evidence 保留正文哈希、parser version、文章身份、发布日期、前后段落、段落索引和对象回执。

业务后端独立回读 GCS 并重新生成证据；篡改引用、定位、标题、归属或正文即拒绝。文章论述不能冒充带类型的财务计算输入。右侧原文面板沿用鉴权的 artifact/version/citation/evidence 接口，完整留存正文支持唯一锚点和高亮，原网页有 URL 时给出外链。页面明确说明平台留存内容可能是 RSS 摘录，不承诺为出版网站全文。

## 运行与恢复

ML checkpoint 增加 articleLibraryEnabled/articleDiscoveryState；新任务启用，已经执行的旧任务不会恢复时悄然增加工具。后端禁止执行途中切换能力；显式重试保留文章原始证据及能力，按回执重建已读段落。最终仍必须独立核验，不能沿用旧审批。

仓储只负责 SQL；ML article_tools/article_store 负责研究工具和留存；Backend article_reader/source_integrity/article_source_view 负责独立核验与展示。article_contract 在两仓完全镜像并有一致性测试。各就近 README 已更新。Workspace Web 范围不扩展 Mobile。

## 实际验收

- Google Cloud SQL 实际只读查询 source_items：120 条记录。
- 真实 `search_articles(query=Tesla, limit=5)`：5 篇候选；选取一篇真实 Electrek 平台文章，`read_article` 留存 60 段，`cite_article` 注册第 0 段。
- 后端独立 GCS metadata/字节/SHA256/身份/段落核验通过；完整原文生成且目标锚点唯一。
- 真实 Pi 子进程的离线组合测试完成 search/read/cite/submit/checkpoint；模型、仓储与对象为测试替身，不冒充付费报告验收。
- ML 30 项、Backend 50 项、Web 43 项针对性测试通过；三仓 git diff --check 通过。Web Vite 构建通过（保留已有大 chunk 警告）。
- 本次未调用付费模型，没有伪造或改写已有 Tesla 财报。现有报告版本 2 仍只有 SEC 与 PDF 引用，不能说已经使用文章库。
- 本轮为分支实现和真实数据链路验收；没有云端发布。临时本机只读报告服务不是完整生产 Research Runtime。

真实验收材料：`/tmp/cited-alpha-article-live/` 中 search.json、state.json、catalog.json、body.json、source-view.json、verification.json。日志：`/tmp/cited-alpha-article-{ml-tests,be-tests,web-tests,web-build}.log`。正文保存在私有 GCS，receipt 与 hash 在 catalog.json。未改写平台 SQL 数据，未把数据库凭据写入文档。

实施沿用三个既定仓库和 `feat_codex/financial-report-agent-plan-writer-20260717`，保留全部既有未提交改动；未提交或推送。
