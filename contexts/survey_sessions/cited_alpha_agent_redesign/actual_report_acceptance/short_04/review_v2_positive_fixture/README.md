# 人工修订样本的真实检查器正向验收

这是对 short04 原始候选进行人工修订后的 fixture，不能当作 Agent 自主修订或完整财报交付。原 candidate 和旧 accepted 均保留不动。

人工补上摘要及 txt_verification_p1 的 2023 收入和增长计算引用，给 txt_unit_p1 补上金额引用，并将未获支持的记账本位币表述改为金额以美元列报。证据与计算对象未改。fixture-audit.json 保存具体差异与哈希。

独立真实模型 reviewer research-review/v2-anchor-bindings 单次调用：semanticReview/editorialReview 均 passed，无 issues。与 review_v2 对原稿的拒绝组成正反样本。仅证明当前检查器在这两个样本上的表现；没有替代来源检查、真实数据库交付或完整报告验收。
