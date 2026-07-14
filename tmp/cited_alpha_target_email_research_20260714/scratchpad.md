# Cited Alpha 目标用户工作邮箱获取研究 Scratchpad

日期：2026-07-14

## 研究问题

在已经识别目标账户和目标角色之后，如何获得可解释、可验证、可用于合规一对一外联的工作邮箱，并为 Cited Alpha 设计从低规模人工验证到可扩展 enrichment 的流程。

## 边界

- 只研究工作邮箱、公司通用业务邮箱、官网联系表单和用户主动提交的邮箱。
- 不研究私人邮箱、手机号、猜测个人账号、绕登录抓取、LinkedIn/X profile scraping 或自动私信。
- “邮箱技术上可投递”不等于“允许营销”；来源、地区、合法基础、透明告知和退出状态必须单独记录。

## Claim Extraction

| Claim | 来源 | 验证通道 | 状态 |
|---|---|---|---|
| 首轮 30–100 条线索应先查目标用户自己控制的官网、Newsletter About/Contact、公司 Team/Press/Partnership 页 | 产品推断 | 现有 16 个 seed leads 中 7 个有明确公开商务邮箱，全部有官方触达路径 | 已验证 |
| 已知姓名与公司域名后，可用 Domain Search / Email Finder 推断工作邮箱，再用 Verifier 检查可投递性 | Hunter 等厂商文档 | 多供应商功能、RFC 与 verifier 状态模型交叉验证 | 已验证；不代表营销授权 |
| 单一 B2B 数据库覆盖率和新鲜度不稳定，waterfall 能提升覆盖，但会增加成本、数据来源与删除链路复杂度 | Clay/Apollo 厂商叙事 | 独立同名单测试与工具迁移证据 | 方向成立；需在自有 ICP 上实测 |
| 对独立作者、小型研究机构，Apollo/ZoomInfo 这类企业数据库可能弱于官网和 newsletter 联系页 | 产品推断 | 当前 seed 覆盖抽样、各工具输入边界 | 方向成立；未做付费数据库同名单 live test |
| 邮箱验证只能降低明显退信，catch-all、role-based、未知状态仍需保守处理 | 验证工具文档 | RFC、多工具官方文档、用户行为证据 | 已验证 |
| Opt-in 表单、Newsletter、样稿申请和 Lead Gen Form 是最干净的规模化邮箱来源 | 平台/法规推断 | LinkedIn、FTC、ICO、GDPR/ePrivacy 官方材料 | 已验证 |
