# Batch DocAI 字段坐标资格合同审查

2026-09-11。只读工程审查；没有修改应用、调用provider、重新parse或操作运行中的Run。

## 判断

**当前page fallback不只是“mode字符串不等于online”。** 真实batch存在同一PDF内部的不同坐标frame：34页无变换，2页被近90度旋转并微小deskew。直接把batch加入online资格会出错。不过财务第4/31页的保留polygon已能在原PDF真实离线渲染中对齐字段；可以设计一个独立、严格、版本化的batch资格合同，不必用native文本去猜框，也无须重新付费解析。

本次新验证只覆盖原件两页六个字段的离线PDF.js渲染，尚未覆盖浏览器实际组件/缩放/DPR，也没有实现正式batch规则。当前已部署能力和运行中Run继续page，不应热加载。

## 读取范围与既有能力

- 当前ML `mindspace/service/research_agent/document_geometry.py`：先要求固定 parserVersion 和 exact online PROVIDER_EXECUTION；随后还要求UserUnit1、Rotate0/90、CropBox=visible view、native文本非空、无page.images、provider image/dimension一致、宽高比吻合、允许的 transforms。本PDF财务页含4张图片，即便伪造online执行也仍不满足no-image条件。这个条件是旧online验证范围，不是batch坐标必然不正确的定理。
- 设计 `contexts/survey_sessions/cited_alpha_agent_redesign/10_pdf_field_coordinates_design.md`：provider normalized坐标所指原图和PDF CropBox/Rotate关系必须明确；不能盲逆transforms；原providerReceipt可重建，不需新parse；不修改旧locator。
- 真实 `/tmp/cited-alpha-cross-source-business-02/recovered-provider-readonly/{providerDocuments.json,shard-0000.json,...shard-0003.json}` 与同哈希36页原PDF；读本地归档，未访问云或密钥。
- `/tmp/cited-alpha-batch-geometry-review/render.mjs` 使用现有Web pdfjs-dist + @napi-rs/canvas，原PDF和provider内嵌image分别渲染、叠加**同一真实polygon**。没有通过quote搜索选择位置。输出 page4-pair.png/page31-pair.png，上半原PDF，下半provider image；已实际查看。

## 全36页frame事实及反例

原PDF所有页Rotate0、UserUnit1、MediaBox=CropBox=[0,0,1583.04,890.52]。

- 34页provider dimension/image均2666×1500 pixels，layout.orientation=PAGE_UP，transforms缺失。
- p26/p27 dimension/image均1500×2666 pixels，orientation仍PAGE_UP，但有2×3 float64 transform。
- p26：[−0.00015499597, −0.99999998799, 1500.41320463; 0.99999998799, −0.00015499597, 0.23247393]。
- p27：[−0.00015765914, −0.99999998757, 1500.42029435; 0.99999998757, −0.00015765914, 0.23654705]。

因此 `/Rotate=0` 和 `orientation=PAGE_UP` 都不能单独证明provider没有旋转。p26/27含图表，为了识别可能被provider自动旋转/微调；当前不能只交换宽高或按精确quarter-turn处理，应保持page，直到独立验证normalizedVertices到底属于original raster还是transformed image以及适用逆矩阵。

## 两页六字段真实渲染核对

无transform页宽高比与PDF相差栅格舍入：按PDF宽scale到2666时viewport高度1499.726046，provider1500，相差0.274px（不是deskew证明，只是尺寸符合整页栅格假设）。本次对照canvas2666×1500；这类亚像素差异须在正式矩阵/容差中明确。

第4页：

- 25,707 polygon normalized x=.83008254..86234057，y=.29333332..308；provider pixel x2213..2299、y440..462。红框在原PDF和provider image均覆盖Q4-2024 Total revenues 25,707。
- 两条2,064的不同provider line：一处pixel[1297,658]..[1375,681]，另一处[1295,1270]..[1374,1293]。分别落在Income from operations与Free cash flow对应格，重复数字不会导致定位歧义，因为真实字段ID/record自身已有不同polygon。

第31页：

- Net cash provided by operating activities normalized x=.045011252..20592648，y=.34866667..36399999；pixel[120,523]..[549,546]。原PDF和provider image都落在对应行标签。
- 两处(37) pixel[2488,856]..[2534,879]和[2015,976]..[2062,1001]，分别指非控股现金流与汇率影响的不同单元格；观察中未互换。

图像证据：`/tmp/cited-alpha-batch-geometry-review/page4-pair.png`、`page31-pair.png`。与之前native唯一匹配相比，这条路径能正确区分同页重复值；它的可信前提是field provenance和frame已验证，而不是quote唯一。

## 严格可实施的最小资格合同

建议独立 `batch-untransformed-raster/v1` 能力，不扩展旧online常量。只支持经过校准的无transform整页栅格frame；其余page。

1. **来源身份**：保持当前user/workspace/attachment/source-run/report-version检查；验证原raw/provider/manifest receipt SHA。field record必须与保留provider对应page、line/cell/span身份及polygon逐字一致。缺页、重复page、shard offset错误或不一致必须拒绝，不能按quote找一条代替。
2. **执行身份**：新解析固化真实请求mode、processor实际version、processOptions（区分字段省略/default/显式false）、原文件/chunk页映射、shard清单/哈希及provider/image。此历史batch intent只记createdAt/inputUri/outputUri/maxPaidSubmissions，没有processorVersion/options；不可回填假metadata。若无法由真实操作/已有配置快照证明实际版本，则只能走经过独立校准的artifact-specific派生几何凭据，不能号称已资格化所有该processor batch。
3. **PDF窄边界**：首版Rotate0、UserUnit1、非零/裁剪页面先page；MediaBox=CropBox=可见view，无加密/错误页。可保留图片，因为坐标来源是原件渲染与provider栅格映射，非native text；但须通过下一项校准，不能只删旧no-image门槛。
4. **provider窄边界**：unit=pixels，image有效且尺寸与dimension逐项相同；无transforms；原始orientation及缺字段状态保留。满足整数栅格舍入的比例误差只作必要条件。任意旋转/deskew/透视、page26/27、维度缺失、越界polygon仍page。
5. **frame证据**：两种可选上线范围必须明确。
   - 固定已知processorVersion+options的能力规则：需有覆盖非中心、页角/底部、重复值的真实batch golden并在浏览器验收，才能称该窄组合适配器支持。当前两页证明此artifact可行，却不足以给未知默认processor版本普遍背书。
   - 历史artifact派生校准：对该原raw+provider哈希建立独立geometry receipt，记录page/provider frame→PDF矩阵、校准方法/工具版本及输出hash；校准覆盖每个要field的page，尚未校准页继续page。不得做源码里特定PDF哈希白名单或直接人工写bbox；派生结果独立不可变，不修改旧DocumentVersion/locator。若希望自动化逐页校准，需要真实栅格配准/图像一致性算法与holdout检验，阈值须实测，本次没有实现或声称可靠阈值。
6. **变换**：对已证实normalized coords属于未变换整页raster的page，矩阵为[W,0,x0;0,−H,y1;0,0,1]投PDFuser space，然后使用既有project_polygon经实际PDF.js可见viewport规范化。不能把像素取整数后的坐标再当唯一精度真源；normalized/absolute一致性应在明确pixel容差内检查。两者严重不符page。
7. **输出**：保留research-pdf-geometry既有绑定并显式记录新derivationVersion/资格原因，receipt绑定raw/provider/page/matrix。使用原bbox而非native候选。服务只给已资格页field；前端CSS viewport绘制，不乘DPR。新派生几何如何挂载既有版本需先定读取协议，不篡改历史manifest哈希。

最小工程路线优先是把当前两页作为真实batch goldens，并完成独立浏览器校准；不要在一次修复中同时自动支持deskew、历史缺metadata升级、全页图像配准和native文本定位。长期新的parse artifact应原生保留真实execution/version信息，避免每次研究补operator证明。

## 可复用测试与尚缺验收

可复用：

- `tests/test_research_document_geometry.py::test_projection_matches_installed_pdfjs_actual_viewport`：真实installed PDF.js viewport金标，0/90/180/270及UserUnit1/2、非零crop矩阵数学。
- 同文件invalid/NaN/singular/out-of-view测试与`test_real_pdf_metadata_alone_does_not_qualify_provider_frame`：继续保护未知frame不产假框。
- `test_retained_real_online_polygons_with_explicit_trusted_execution`及`pdf_geometry_acceptance/real_canary_20260910`：只能证明online窄规则和旧manifest不自动升级；不可当作batch样本。
- 当前Backend PDF source/hash/geometry绑定与Web ResearchPdfSourceView规范化overlay逻辑可原样复用；授权/引用审查不改。

应补batch专用：两页真实原件+shard完整hash fixture（可离线读取授权归档；portable CI用明确来源小fixture），重复2,064/(37)身份不能串格；p26/27真实transform降级；缺execution/版本、变更provider尺寸、非零crop/rotate/UserUnit等负例。

浏览器后续用实际PDF.js组件对第4/31页六字段，以50%/100%/200%缩放和DPR1/2核验；Math金标不代替实际overlay。原图及provider图的本次Node离线像素对照支持进一步实现，尚不是Chrome产品验收。没有必要再次调用DocAI获得同两页数据。
