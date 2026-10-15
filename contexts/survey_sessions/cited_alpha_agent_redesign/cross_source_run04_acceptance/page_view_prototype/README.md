# 离线页概览原型：完成结果

仅/tmp代码，无应用/工具/提示/Run/模型/云/数据库变更。使用既有真实provider归档离线normalizer重放，不生成新的provider执行状态、授权或Evidence。

运行：

```
/Users/xuhao/Documents/Other/mindspace_ml_backend/.venv/bin/python /tmp/cited-alpha-page-view-prototype/verify.py
/Users/xuhao/Documents/Other/mindspace_ml_backend/.venv/bin/python /tmp/cited-alpha-page-view-prototype/render.py
```

`page_view.py`纯函数接受已验证normalized、version_id、page；公共版本/页信息一份，每字段仅完整text、kind、原始稳定ID、**不降精度的原始bbox**。默认line代表层；kind=span/cell明确可达，availableLayers完整声明，不把line完整覆盖说成所有解析层都已展示。保留原provider顺序，不语义重排、不生成table/表头/期间/数值类型，不按文字去重。图片是离线观察辅助，未发送给模型。

## 实测预算

精确UTF-8紧凑JSON字节，包含响应元数据/coverage；不等于模型token。真实document ID长度已保留，测试version_id为明确offline-material-sha标识。

| 页 | 完整line数 | 完整返回bytes | 32KiB首次返回 | 48KiB单次 |
|---|---:|---:|---:|---|
| p4 | 144 | 36,747 | 127条，需要续页 | 完整 |
| p5 | 144 | 36,714 | 128条，需要续页 | 完整 |
| p7 | 109 | 28,083 | 完整 | 完整 |
| p8 | 109 | 28,055 | 完整 | 完整 |

结论：**保留完整bbox时32KiB不能容纳p4/p5**。不为达标丢尾部现金流/脚注，也不压坐标精度。建议集成选48KiB/300字段硬界，真实四页均单次完整。原型函数仍默认32KiB以留存实验，verify显式使用48KiB。接入真实工具content/results外壳时必须把外壳字节纳入预算或预留明确余量，本实验未计该外层。

## 已通过验证

- 真实p4/p5/p7/p8所有line原文、bbox、稳定ID逐项等于现有生产 `ImmutableDocumentResearchTools._rows` 的相同kind/id记录；精读/cite入口使用同一查找身份，不新造别名。
- 4,000 bytes/7字段分页完整遍历，拼接结果与全页逐字段一致；字段不隐式截断。
- cursor绑定version/page/kind及选择材料hash；跨版本、跨页、跨层拒绝。cursor不是签名授权凭据，正式实现每次仍必须先经过原scope/版本校验；不能将可解码游标当鉴权。
- 重复文字两个ID均保留；超大单字段明确ValueError，不返回部分文字/悬空citation；响应修改不污染原字段；空页明示空且complete。
- span显式按需读取；原型不自动重复其正文到line视图。
- 原型结果非引用，不登记证据。测试没有调用真实authorized load或完整cite `_entry`，因此不能据此宣称线上授权/宿主证据注册已验收；集成后仍须执行真实冻结版本对应cite entry逐字等价及权限负例。

## 原件布局抽检

`render.py`将概览保留的bbox逐字取出，叠加在相应真实provider page.image上（不是原PDF框），导出四页PNG。已实际打开p5及p8图片抽检：年度列头、行名、年度金额、GAAP/non-GAAP两行、现金流/资本支出、交付/储能、底部脚注位置对应，重复值保持各自位置。p4/p7已生成但未逐页人工查看，不宣称四页视觉全验收。

这是retained provider surface的布局保真抽检，不证明模型能仅凭JSON bbox读懂所有表格，更不证明OCR原文数值正确。p8页脚小字及部分数字框贴边，保留原始框而未“优化”。原PDF定位能力没有改变。

## 下一批最小集成建议

1. 新导航view直接从已验证immutable normalized生成，使用48KiB/300字段；保留旧raw_fields与cite语义。
2. 新Run通过**现有toolContractVersion升级**选择新定义与默认模式，不新增平行documentReadViewVersion持久状态；旧checkpoint显式继续旧schema/default。viewVersion仅响应解释元数据，不用于第二套会话版本决策。
3. unknown版本在provider初始化前拒绝；两端先支持新旧读取，再启用新Run；保存了新协议调用的checkpoint不能直接交不识别它的旧runtime。
4. 目前此原型是保真紧凑空间片段清单，尚无自然整行排版。若加按bbox行带排列，只作为derived navigation并保留每片ID/原文，禁止升级成语义表或猜期间。真实table缺失时仍明确spatial_text。
5. 分页目前保证字段完整、cursor绑定和coverage；尚不保证拆页重复标题/单位，因为当前归档没有权威表头关系，不能伪造。48KiB令本次四页不触发此问题；面对更大复杂页需选择真实结构区域分页或如实保留空间片段分页，不可假称整表读完。
6. 后续补真实版本引用等价、300字段边界、畸形坐标/多栏/旋转、单字段超限反馈、预算含外壳、旧checkpoint恢复与权限测试。不要将当前无模型离线通过等同于最终报告质量提升。
