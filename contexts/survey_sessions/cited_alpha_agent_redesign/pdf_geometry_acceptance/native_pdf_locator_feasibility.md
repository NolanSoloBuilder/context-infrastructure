# Native PDF 文本定位：有界离线可行性审查

2026-09-11。结论：**可以实现一个独立的原生文本定位候选路径，但“同页文本唯一”本身还不够证明可见字段框正确。** 候选召回率不错；渲染可见性、文字 run 几何和混合图片歧义仍须验证。当前服务继续 page fallback，不应热加载规则，也不能把以下比例当作已上线 field 覆盖率。

## 当前真实边界

ML `mindspace/service/research_agent/document_geometry.py` 仅对固定 online OCR/native frame 的 providerExecution 组合做 field qualification。本次 batch/processOptions=None、manifest 未标该 online 执行，不符合资格。不能补一个假的 providerExecution 来借用 online 坐标假设。

新路径应从已按 receipt/SHA 验证的原始 PDF 自身重建文字坐标，而不是重新解释不合格的 DocAI bbox。仍由原授权、版本、原件哈希、quote 原文校验先行，模型不提供或修改定位条件。本次不调用 provider、不修改应用、不触碰实际 Run。

## 材料和工具

- 原件 `/Users/xuhao/Documents/Other/context-infrastructure/contexts/source_materials/cited_alpha_cross_source_tesla_2024/05dfde334f800ec5f0ee140c0dd78409f24ad775e11a0c68f8a6b534b04cafdc.pdf`，36 页。
- 已恢复结果 `/tmp/cited-alpha-cross-source-business-02/recovered-provider-readonly/providerDocuments.json`，4 个 shard，页1–10/11–20/21–30/31–36。每个 shard 的 textAnchor 索引为该 shard text 内索引，本次按这一实际结构提取，未把 textOffset 重复相加。
- 现有 Web `node_modules/pdfjs-dist/legacy/build/pdf.mjs`：提取全36页4634个text items、样式与viewport；现有ML pypdf读取页面box/rotation/image数。未安装库。PDF.js报两条 `TT: undefined function: 21`，提取成功；这是字体渲染进一步验收的理由，不应忽略。
- 本次只有离线文本/结构检查，没有浏览器像素验收。原始材料系已有归档；此统计没有重新验证云端receipt或operation，不扩大原恢复流程的证据等级。
- 可复查脚本/数据 `/tmp/cited-alpha-native-pdf-locator-review/{extract.mjs,analyze.py,native-text.json,matches.json,stats.json}`。这些是独立调查文件。

## 匹配准则和结果

只折叠空白为一个空格并去首尾空白；保留大小写、数字、标点、负号、括号、连字符、Unicode。对**完整 OCR quote**在同页 native text 中做完整 token 边界匹配。拒绝无匹配、多匹配；进一步只计开始/结束落在完整 PDF.js item 边界的唯一匹配，避免按字符数估算字体内部宽度。没有相似度/编辑距离/数值归一化，也不跨页选第一个数值。

| 样本全集 | 总数 | 唯一完整item边界候选 | 多次匹配 | 无匹配 |
|---|---:|---:|---:|---:|
| DocAI lines | 2198 | 1607（73.1%） | 306 | 282 |
| DocAI paragraphs | 1996 | 1402（70.2%） | 289 | 302 |

两行是相互重叠的不同单元集合，不能相加。另各有3条唯一字符串匹配但未落在完整item边界，保守不接受。按同类型OCR记录再次检查同页quote唯一，以上候选数不变。恢复输出没有 tables 数组，因此这里不是财务table-cell评测；不少line只是数值、页码或标签，**比例不是实际研究证据/报告点击覆盖率**。

| 页 / 类型 | line总数 | 唯一完整item候选 | 多匹配 | 无匹配 |
|---|---:|---:|---:|---:|
| 4 财务季度汇总 | 144 | 135 | 7 | 2 |
| 29 利润表 | 209 | 176 | 31 | 2 |
| 30 资产负债表 | 201 | 175 | 24 | 2 |
| 31 现金流量表 | 142 | 127 | 12 | 3 |
| 6 经营解释文本 | 20 | 11 | 4 | 5 |
| 35 说明/定义长文本 | 36 | 24 | 0 | 12 |
| 18 产品比较/混合图像 | 63 | 3 | 4 | 54 |
| 26 图表 | 71 | 17 | 52 | 2 |
| 36 图像末页 | 2 | 0 | 0 | 2 |

真实反例：

- 第4页 `2,064`、`-71%`、`Adjusted EBITDA` 各出现2次，必须page。不能按数字相同选任意一格。
- 第31页 `Other`、`(37)` 重复，必须page；`Net cash flows from noncontrolling interests - Solar` 无精确匹配，不可用模糊匹配强行定位。
- 第6页若干 `+ ...` 解释在不同业务段重复；OCR的 `Al` 与native `AI` 等差异不能悄悄更正为同一quote。
- `FINANCIAL SUMMARY` 与native字间排版 `F I N A N C I A L ...` 不相同，保留page，而不是删除所有空格来碰撞。
- 第18页产品比较多项在图片里，native缺失；第36页无native文字，不能用图形或OCR bbox补成field。

## 最小可实现定位器

独立版本例如 `native-pdf-text-locator/v1`；不修改/冒充provider frame资格。输入只能是验证后的PDF bytes、冻结pageNumber、原始quote；输出包括实际matcherVersion、rawSha256、page与候选item范围。provider record继续负责原始证据身份，native matcher只提供显示位置，绝不能从匹配推出指标/期间/单位正确。

保守步骤：

1. 验证原始receipt/SHA/页码；读 native text 与 PDF.js 文字 item/字体样式。禁止跟随外部字体/URL；限制页/item/时间/内存，使用现有固定依赖版本。
2. 建立空白规范化前后字符↔完整text item映射，按全文匹配计数；native和同类provider quote都唯一才继续。OCR差异、重复、数字子串、图片scan一律page。
3. 首版仅支持LTR、非vertical、非倾斜、无异常变换、完整item边界、单行连续几何。多item之间不能存在大跨度跳栏；多行长quote先page，避免一个巨大bbox遮住无关区域。统计中的1607仅文字候选上限，施加该几何条件后只会下降；本次未测最终qualified率。
4. 从 native item 的实际变换和字体 ascent/descent 得文字行框，交 PDF.js viewport 转换到显示坐标；不复用DocAI normalized_vertices。坐标非有限、零宽、越CropBox或不支持旋转/字体则page。
5. **可见性资格单独验证**：PDF能有隐藏/透明/遮挡文本以及图片内同样文字。唯一textContent只证明文本层唯一，不能证明屏幕上唯一。样本第4/6/29/31等每页都有4张image，故“page.images非空就拒绝”会把这些好候选全部拒绝；不能以“有native文字”等价“不是扫描/OCR层”。需要有界检查被匹配文字渲染模式/alpha/clip/覆盖关系，或把native结果作为明确的候选高亮，不提升正式field。若首版无法可靠证明，应继续page，而不是为覆盖率忽略这一点。
6. formal geometry返回field的能力声明必须以原始PDF样本与浏览器像素验收为依据；不把native结果混入旧online qualification。若暂时只做客户端“查找原文”辅助，标签须区分文本搜索结果与已验证字段位置，不写回证据可信几何。

性能上不应为每个citation重复解析36页：按授权后原始SHA+matcherVersion缓存只读native索引（有限大小/LRU），仍每次校验当前report/version/source权限；缓存命中不能绕过授权。不要为了这个定位器引入新解析付费任务或 embedding。

## 坐标与 PDF.js 可复现验收

第4页 `25,707` 是同页唯一完整item：transform=[18,0,0,18,1315.7021,617.7906]，width=50.0706，height=18，ascent=.75/descent=-.25。页面view=[0,0,1583.04,890.52]、rotation0，scale1 viewport=[1,0,0,-1,0,890.52]。按字体行框候选：left1315.7021、top259.2294、width50.0706、height18。这是**行框候选，不是已观察像素墨迹精确边界**。

第31页 `Net cash provided by operating activities`：transform=[15,0,0,15,72.4534,569.0781]，width254.148，ascent=.75/descent=-.25；候选left72.4534、top310.1919、width254.148、height15。quote不补数字，其框仅覆盖这段行标签。

后续零provider浏览器实验：直接加载同一个哈希PDF，使用现有PDF.js canvas+text layer，同scale/rotation的viewport和text transform；核对上述两个候选及第35页长句，逐个截图确认文字、bbox、比例。对50%/100%/200%缩放及0/90/180/270旋转重复映射，不允许把截图缩放系数当原PDF坐标。CropBox非零/UserUnit特殊的本地合成fixture另外覆盖，和真实文件证据分开。对重复2,064、OCR差异、图表刻度、图片页，应明确显示page，不产生“看起来合理”的矩形。

至少增加负例：隐藏OCR文本、透明文字、遮挡、同值图片、断词、不同列相邻text item、旋转字、空page、font无ascent。实际只有有限简单native能力被证实，就只登记那一小类资格。当前跨来源Run不加载此实验；等真实报告可读后，可在独立页面用其真实引用做定点比对，不能篡改正式geometry以制造验收截图。
