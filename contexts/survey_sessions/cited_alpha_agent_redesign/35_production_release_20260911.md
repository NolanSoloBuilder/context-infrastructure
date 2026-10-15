# 三仓生产代码发布（2026-09-11）

用户授权：发布当前报告与平台文章召回实现。范围为三仓既定 financial-report-agent-plan-writer 分支的通用 Research Agent、报告恢复、来源校验及阅读体验；保留旧固定流程实验、营销页面、本地配置等无关未提交改动。

## 已发布证据

全部通过 feature PR 合入 main，由 GitHub Actions 自动部署，未直接 push main，未执行手工发布 fallback。需求分支均为 `feat_codex/financial-report-agent-plan-writer-20260717`，本地工作目录继续保持该分支。

| 仓库 | Feature HEAD | PR | Merge SHA | 发布 Actions |
|---|---|---|---|---|
| ML | e1c942ac89f1ca5d8b41b10237d4137ea7a047d9 | [32](https://github.com/NolanSoloBuilder/mindspace_ml_backend/pull/32) | e9f66c231cdc4f25f3e9add6a4d691c80611d374 | [34586639091 成功](https://github.com/NolanSoloBuilder/mindspace_ml_backend/actions/runs/34586639091) |
| Backend | ce8c6dc39dfd98535c40dd225390cd291869ef3b | [37](https://github.com/NolanSoloBuilder/mindspace_backend/pull/37) | 391cb66c10794642f5a6407cd7660bab924cb5cc | [34587222188 成功](https://github.com/NolanSoloBuilder/mindspace_backend/actions/runs/34587222188) |
| Web | 6d0dc795480c7308bf4396da5210d23dd86fd882 | [29](https://github.com/NolanSoloBuilder/mindspace_web_frontend/pull/29) | 9a5153e0f5817ae48cea740733beb4273591a900 | [34588261376 成功](https://github.com/NolanSoloBuilder/mindspace_web_frontend/actions/runs/34588261376) |

- ML API revision `cited-alpha-ml-api-00044-t68`；ML Runner `cited-alpha-ml-runner-00024-rv6`，均 100% 流量。
- ML 镜像 `us-central1-docker.pkg.dev/cited-alpha-20260701/cited-alpha-ml-backend/ml-api:release-e9f66c231cdc4f25f3e9add6a4d691c80611d374-34586639091-1`。实际固定 Secret 数字版本 2。
- Backend API revision `cited-alpha-api-00048-wqt`；Runner `cited-alpha-workspace-runner-00024-kn5`，均 100% 流量。
- Backend 镜像 `us-central1-docker.pkg.dev/cited-alpha-20260701/cited-alpha-backend/api:release-391cb66c10794642f5a6407cd7660bab924cb5cc-34587222188`。
- Cloudflare Pages production deployment `758e6284-691d-45ad-9a29-dd6843819cfc`，branch main、source SHA 与 Web merge 相同；GitHub deployment 6391040728 status success。
- 正式 Web [cited-alpha.forgepane.com](https://cited-alpha.forgepane.com/app/login)，部署专属地址 `https://758e6284.cited-alpha-web.pages.dev`。
- 正式 API `/api/v1/auth/health/` 返回 Service echo success；ML实际run.app域名 `/nash-algorithms-docs` 返回200。Actions也完成固定生产URL smoke。
- Backend expand migration execution `cited-alpha-api-schema-migrate-kqrjd` 成功；收尾 `cited-alpha-api-schema-migrate-dp4pt` 完成后 Actions 成功。队列 workspace-runs=RUNNING，scheduler workspace-run-outbox-dispatch=ENABLED。没有回滚。

## 验证与发布修复

- ML 375项便携Python门禁、16项实际Pi镜像内测试通过；部署合同19项。
- Backend 366项便携研究合同通过，排除1项依赖sibling checkout的测试；部署合同23项。迁移相关本地15项通过。
- Web CI 252项/17文件、SEO门禁、完整生产构建通过。
- 本轮补充文章测试到镜像门禁；镜像单仓使用固定golden hash并在sibling存在时额外比对镜像契约。更新新增工具wire断言和16MiB checkpoint边界测试。
- Web历史版本测试在数字强调后使用段落textContent校验，仍检查原始版本内容与baseVersion提交，未改变运行行为。
- Mobile没有消费Workspace research citation接口，本次没有移动端发布。
- 本轮没有付费模型、embedding、ASR或报告生成调用，也没有改写现有报告。

## 不能混淆的生产能力边界

**这次完成的是三仓代码上线，新通用研究入口仍未在生产启用。** Backend prod.yaml 的 research-enabled=false、research-workspace-allowlist=[]；ML生产secret未配置research-runtime。没有为了绕过生产接线问题擅自扩大旧runner的身份权限或并发。

当前缺口仍按27/29号设计记录：生产research callback路由/身份、执行与审阅/文档读取的控制容量隔离、固定服务连接及生产模型/解析配置尚待落地。只打开开关会遇到回调拒绝或长执行占满重入容量，因此本次保持禁用。不能声称正式站已经可以完整生成含平台文章引用的新报告；之前Tesla成功报告属于本地隔离业务数据库，不在本轮迁移到生产。

后续若目标是线上直接生成报告，应按29号ADR落实生产接线与隔离后，再通过真实鉴权、队列、模型、独立核验、报告持久化完成受限canary；浏览器视觉验证仍遵循用户本轮避免截图的偏好。

## 证据落点与保留改动

脱敏日志、运行版本、迁移记录、正式站资源比对在 `/tmp/cited-alpha-release-20260911/`。该目录含三仓精确暂存补丁、文件清单及未纳入发布清单；不含下载的生产secret正文。

未纳入发布的本地文件数：ML 28、Backend 35、Web 67（包含既有删除项）。它们保持原样，未stash/reset/搬运。发布文档保存在context-infrastructure；未将当前工作区绑定切到main。
