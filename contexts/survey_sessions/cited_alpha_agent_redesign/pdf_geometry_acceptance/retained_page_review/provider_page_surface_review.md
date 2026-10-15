# 解析页面作为独立字段核验视图

2026-09-11，只读审查。建议采用：**原PDF + 保留解析页面双视图**。解析页面可有独立 `surface=retained_provider_page` 的field高亮；原PDF仍明确page定位。它解决“用户在完整视觉上下文中核对具体字段”的需求，不需要冒充已经证明provider→PDF坐标变换。但它是新增核验视图，不能取代原PDF、原版本、原件下载或原有字段证据身份。

## 官方语义与本次实际验证

Google官方Document定义将page.image描述为经过旋转/倾斜/失真预处理的页面图，transforms描述原文档图像到page.image的变换；Layout.boundingPoly对应该布局单元。通用Vertex/NormalizedVertex说明则使用“original image”措辞，因此不能仅凭同一page对象就对所有处理器、输出类型推断frame。[Google Document REST参考](https://docs.cloud.google.com/document-ai/docs/reference/rest/v1/Document#Page)

本次直接取不可变恢复shard里的image bytes，不调用provider；将同page原始line.boundingPoly.normalizedVertices乘该image实际解码尺寸叠图，没有native文本匹配，也没有逆用transforms：

- p4 image2666×1500：25,707与两处2,064均准确覆盖相应字段。图片见 `/tmp/cited-alpha-batch-geometry-review/page4-pair.png` 下半。
- p31 image2666×1500：现金流标签与两处(37)各覆盖正确位置。图片见同目录page31-pair.png下半。
- p26 image1500×2666，原PDF为横向且Rotate0；provider已有近90度+微小deskew transform。**直接用原polygon覆盖保留image仍正确**，Operating Cash Flow ($B)和Free Cash Flow ($B)框落在两条竖向图例文字，见同目录page26-pair.png，已实际查看。这里无需反算到PDFframe，避免了上一个方案最难的变换问题。

p26也说明“解析页面”不一定更易读：provider为识别图表而改变方向，图例相对于默认屏幕竖向。用户旋转时必须让**图像与overlay整体同步旋转**，不能只转图，也不能再单独按PDF/Rotate或layout.orientation转polygon。

上述是当前OCR batch归档三页八个字段的真实局部同frame证据，不是任意DocumentAI模型的通用保证。固定adapter/支持的schema必须有真实fixture测试；缺image/坐标或不一致时不给field。尚未做Chrome产品验收，也未改当前已部署能力。

## 最小可信合同

在现有PDF source响应上增加独立、明确版本化surface或独立端点，不能复用`kind=pdf, locationPrecision=field`暗示原PDF有框。建议独立响应：

- surface=retained_provider_page；precision=field；pageNumber表示原PDF页映射，providerPageNumber/归档page身份单列。
- sourceRawSha256、documentVersionId、providerReceipt.sha256、imageSha256、imageMimeType、解码width/height、fieldId/locator与原quote保持绑定。
- polygonNormalized直接来源该版本该page该field的原boundingPoly，polygonFrame明确retained_provider_page。不能接受客户端上传polygon、image URL、owner或任意page编号绕过报告引用。
- 图片请求必须同样通过owner→artifact version→citation→evidence→source run→当前附件授权链；服务从已验证providerReceipt提取指定page.image，校验bytes实际尺寸/mime/hash，再输出只允许PNG/JPEG的受限二进制内容。不把整个provider JSON或GCS可任意访问地址给浏览器。
- 原PDF source-file与原PDF page-view继续现有receipt/SHA检查；两视图都能看到文件名、原页码、原quote、期间/单位/上下文，切换不丢当前evidence。
- 只在真实字段验证后输出surface；OCR框位置正确不等于OCR数值正确或报告结论得到支持。保留独立事实/引用验证与用户查看原件能力。

页映射不能仅取JSON数组下标：保留shard/chunk页偏移、pageNumber、文档版本实际page映射和完整shard清单。当前4shards页1–36已恢复；通用多chunk/重复page/缺page必须拒绝不猜。图片receipt可作为provider receipt下的内容寻址派生对象/缓存；缓存不绕授权、不改旧ReportVersion/DocumentVersion。图片裁剪只做UI放大，完整page始终可看，避免财务条件被裁掉。

## 产品形态与04能力

引用侧栏可提供两个清楚标签：“解析页面·字段高亮”和“原始PDF·第N页”，另有下载原件。默认字段高亮定位到视觉上下文，允许缩放/平移/同步旋转；展示完整行、列标题、相邻行、脚注，不能只给OCR文本小卡。用户能对照原件确认OCR读错数字、负号或括号，这满足可追溯核验的核心目的。

如果04验收逐字要求“在原PDF上字段框选”，这个方案不能把该条勾为完成，应明确拆成“解析页面字段核验已支持”和“原PDF字段几何仍page”。作为可用产品的追加能力是合理的；作为降低标准的替代声明不合理。未核对04原文具体条款时不得声称已通过其验收。

## 局限和安全边界

- 栅格1500高/2666宽有清晰度上限，缩放无法恢复PDF矢量字；细脚注、小数点、负号可能模糊。JPEG还有压缩；应允许原PDF对照而非宣称完全无损。
- page.image是处理后的衍生图，不保证保留原PDF全部颜色/边缘内容/互动链接/字体/层。不能叫“原件截图”或代替原始下载。
- 图像坏格式、超大像素/解压炸弹、未知mime、hash不符、坐标越界/退化/非有限、同field映射多page都拒绝。限制bytes和像素数；不要渲染provider SVG/HTML/data URI，采用受鉴权二进制端点与nosniff/private cache策略。
- 页图通常包含未引用的同页文字，现有文件级授权允许读该原文时合理；如果将来有字段级脱敏权限，不能据引用一格就返回整页，须单独设计。
- 向用户报告这张图片的source lineage和解析版本，但不要暴露私有GCS路径/token或运行内部配置。

## 建议实施顺序与验收

1. 先确定新的surface响应与鉴权图片端点，保留旧PDF接口兼容；无需新模型或DocAI。
2. 离线真实三页golden：p4重复2,064、p31重复(37)、p26旋转图例；断言绑定的是原line ID和原polygon，不按quote找位置；校验image解码尺寸、hash及页映射。
3. 浏览器实际双视图验证：缩放/旋转同步、完整表头脚注、PDF下载hash一致、image取消/重载与对象URL清理、用户切换/撤附件后拒绝访问、旧报告仍能按旧PDF接口打开。
4. 未知page image/frame缺失明确回退原PDF页定位；不因为新增surface放宽原geometry规则。保持当前Run不热加载，下一次正式产物验收另行使用。

这比native文字猜框更直接，也比通用反算所有batch transforms更小：保留provider自己的视觉证据表面，诚实说明其是原文的解析衍生页面。长期原PDF字段框仍可以继续补，但不必阻塞这个独立、可审计的核验能力。
