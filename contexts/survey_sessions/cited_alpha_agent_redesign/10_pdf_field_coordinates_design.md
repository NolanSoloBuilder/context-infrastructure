# PDF 字段框选：下一步坐标合同与验证方案

2026-09-10，只读设计；未调用付费解析，未宣称真实 DocAI 字段框选通过。

## 结论

字段验真已经能定位冻结的 line/cell/span，但不能把 provider 的 normalized_vertices 直接乘 Web canvas 宽高。下一步应先把 provider 坐标系与原 PDF 页坐标的关系冻结并验证，再由统一变换生成显示框；不确定时仍返回 locationPrecision=page。框选是 MVP 未完成项，不以“页定位可用”替代。

## 当前代码证据

- ML `mindspace/service/document_ai/layout_parse_utils.py:layout_bbox` 与 `ocr_service.py:_layout_bbox` 只保留 normalized_vertices/vertices。
- ML `layout_parse_builder.py:_add_page` 保存 page_number、width、height，但维度转为整数，metadata 仅 source；未保留 dimension.unit、page.transforms、page.layout.orientation、原图/处理图尺寸及 PDF crop/media box。OCR 输出同样缺这些信息。
- 原始 provider JSON 已由 research document version 的 providerReceipt 保留，因此可从现有归档重建必要几何元数据，不必重新发起付费解析。manifest 的新投影必须带新 parser/geometry 版本，不能静默改变历史 locator。
- Web `ResearchPdfSourceView.tsx` 使用 `getViewport({scale})`，PDF.js 默认应用 page.rotate，并按 page.view/viewBox、userUnit、rotation、Y 翻转构造矩阵。其本地 `node_modules/pdfjs-dist/legacy/build/pdf.mjs:PageViewport` 实现可作为离线金标，不能另写一套未经比较的“旋转宽高互换”。

Google 说明 normalized vertex 相对原始图像，page.transforms 是原图到 Page.image 的变换；这并不自动证明该原图等同 PDF 的 CropBox 或已经应用 /Rotate。layout.orientation 也不是可直接照抄的 PDF /Rotate。[Document 官方定义](https://docs.cloud.google.com/document-ai/docs/reference/rest/v1/Document)
PDF.js viewport 同时处理旋转与 PDF 到 canvas 的坐标变换。[官方示例](https://mozilla.github.io/pdf.js/examples/index.html)、[API 源码](https://mozilla.github.io/pdf.js/api/draft/api.js.html)

## 冻结最小几何记录

每个冻结 page 的 manifest 增加 versioned geometry（具体代码字段名在实现前与 ML/Web 再冻结）：

- `geometryVersion: research-pdf-geometry/v1`
- `rawSha256, providerSha256, pageNumber`
- PDF 从原 bytes 读取：`mediaBox[4], cropBox[4], rotate:0|90|180|270, userUnit`
- Provider 原样保存：`dimension{width,height,unit}, image{width,height}, transforms[], orientation`；缺失不能用假 0 替代。
- `providerCoordinateFrame`：明确指向哪个图像/页面、原点方向和是否已旋转。必须来自已经验证的 parser adapter 规则与 fixture，而非依据长宽相等猜测。
- `providerToPdfMatrix[9]` 与 `mappingStatus:verified|unknown`：二维齐次变换把 provider 点映射到 PDF 原始 user space。保存产生此矩阵的 adapterVersion、校验样本/规则身份。

原 locator.record 中的 polygon 不变。geometry 绑定同一原文/解析 manifest；source read 同时验真字段和 page geometry 后才能产生 bbox。任何文档 rotation、crop 或 provider 处理变化均产生新身份，不沿用旧矩阵。

## 转换规则

对原始 polygon 每个顶点执行：

1. normalized_vertices → provider 原坐标；缺失 x/y 的 protobuf 零值可按官方语义补 0，非有限值/越界值拒绝。vertices 必须有可信原图尺寸；不能拿 PDF point 尺寸当 pixel。
2. 用冻结的 providerToPdfMatrix 变到 PDF user space；若是齐次透视变换，必须除以 w，w=0/不可逆/不支持的矩阵拒绝。
3. 用与 Web 相同的 `page.getViewport({scale:1})` 变换到最终可见页（CropBox、Rotate、UserUnit、Y 翻转均在这一步统一处理）。如果 provider 点已经属于原图坐标，不得再盲目逆应用 transforms；只有明确以 Page.image 为起点时才应用其对应逆矩阵。
4. 对变换后的所有顶点求包围矩形，再除以 viewport.width/height，返回现有 `bboxNormalized{x,y,width,height}`、`locationPrecision:field`。四角必须全部校验；不只换 x/y，也不假设两对角点足够。
5. 明显超页/退化/无穷的框拒绝；只有明确浮点误差阈值（例如 1e-6）内可修正边界，并记录。框跨页必须按页拆开，不能强行并成一个 pageNumber。

与现有 Web 合同兼容：bboxNormalized 的定义是最终可见页面左上角原点，x/y/w/h 都在 [0,1]，不包含 DPR。Web overlay 用 CSS viewport 尺寸乘归一化值，canvas 像素可独立乘 DPR。用户缩放只改 viewport scale，不重新解释原坐标。

## 实现位置

1. ML 新纯模块 `research_agent/document_geometry.py`：从已归档 raw PDF/provider JSON 读取 metadata，生成新 manifest geometry、测试变换；不要改原 PDF。
2. ML `document_version` read_verified：连同精确 field 返回受验 geometry，版本/页码必须与 rawReceipt 一致。生产 DocAI frame 规则未确认前 mappingStatus=unknown。
3. Backend `research_report/pdf_source_view.py`：验证 geometry 返回绑定，只有 verified 时给 field bbox；继续从配置桶读取原 PDF，保持 owner/附件/版本校验。
4. Web `ResearchPdfSourceView.tsx`：保留 pdfjs canvas、不开放 PDF JS；以 viewport 渲染框，并对测试中真实 page.rotate/view 核验 Backend 归一化结果。最好由同版本 pdfjs 离线生成几何 golden，避免 Backend 自写矩阵与渲染器漂移。

## 最小验收 fixture

合成 PDF 是变换数学测试，不是 DocAI 行为证明：

- 同一页在 0/90/180/270 度各一个样本；已知 cell rectangle 位于非中心位置，重复数字在另一个位置以证明按字段 ID 框选。
- MediaBox [0,0,600,800]、非零 CropBox [50,100,550,700]；目标包含正常框、边界框、框外拒绝；至少一份 UserUnit=2。
- 跨两行合并 cell 的 polygon；长表底部 cell；两个页相同数字但引用只指 page2。
- 原始 normalized polygon、绝对 pixel polygon 各一份；缺单位、缺 frame、奇异矩阵、越界、NaN 均降级/拒绝，不生成假框。
- 对每个 fixture 用真实本地 pdfjs 渲染 canvas，比较四角投影与已知位置；缩放 0.5/1/2 和 DPR 1/2 下 CSS overlay 应一致。目标中心在框中、另一个同数值 cell 不在框中。

真正 DocAI 验收另列一道门：优先读取已有 providerReceipt+rawReceipt 的实际样本，检查至少未旋转、旋转、裁剪样本中的实际字段 polygon 与原页面。若现有归档没有对应样本，先完成数学测试并保持这些类型为 unknown，待显式允许的付费解析样本补齐。不能将手写 provider fixture 标为“DocAI 已验证”。

## 原生PDF文字定位候选审查（2026-09-11）

真实36页PDF与恢复的batch结果已完成[有界离线审查](pdf_geometry_acceptance/native_pdf_locator_feasibility.md)。2198条OCR line中1607条满足同页完整文本唯一且落在完整PDF.js item边界，只是73.1%的文字候选上限。尚未验证可见性、字体和浏览器坐标，不能作为字段级覆盖率，也不改变当前batch来源的页级回退。

后续设计将原生定位器与provider geometry资格分别版本化。重复数字、OCR差异、图片文本、隐藏文字及不支持的变换均需要明确拒绝或回退。先用实际报告引用检验文字与位置，再决定是否实施；当前真实Run不加载实验规则。
