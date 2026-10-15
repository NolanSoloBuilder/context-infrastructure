# 留存解析页与原始PDF双视图

2026-09-11。新增字段核验能力设计；不放宽原PDF几何资格，不覆盖04验收合同。原始PDF仍可完整查看，解析页明确为从原件处理得到的衍生页面。正式报告的事实、来源版本与引用身份均不改变。

## 证据与用户行为

已有真实batch原图与polygon离线验证：p4、p31、p26共8处字段可在各自留存page.image上对齐，包括重复数字及provider旋转页。原PDF坐标逆变换尚未普遍证明。新视图直接使用留存解析页的实际像素与该字段原polygon；完整页保留表头和脚注。用户可切换解析页字段高亮与原始PDF页级查看，缩放/旋转将图像与高亮一起变换。

此功能必须单独记录定位表面。解析页可字段定位不代表原PDF可框选；不能仅凭新增视图将原PDF字段验收标为通过。真实报告中至少一处引用的两个视图、原件hash及字段口径均需验收。

## 共享合同

新增可选`pageRendition`元数据，位于ML read-verified和Backend kind=pdf source响应。旧客户端可忽略；缺少支持时原PDF行为不变。字段：

```json
{
  "schemaVersion": "research-page-rendition/v1",
  "surface": "retained_provider_page",
  "documentVersionId": "dv-...",
  "rawSha256": "64 lowercase hex",
  "providerSha256": "64 lowercase hex",
  "fieldKind": "line",
  "fieldId": "exact frozen field id",
  "pageNumber": 4,
  "mimeType": "image/png",
  "byteSize": 123,
  "sha256": "64 lowercase hex",
  "width": 2666,
  "height": 1500,
  "locationPrecision": "field",
  "bboxNormalized": {"x": 0.1, "y": 0.2, "width": 0.1, "height": 0.02}
}
```

`fieldKind`可line/cell/span；mime只PNG/JPEG；最大4,000,000字节、40,000,000像素，严格解码并核对声明尺寸/mime。坐标只来自已重放核验的同字段record及唯一provider page，数值有限、范围内、非退化。已支持的固定normalizer输出才适配；未知格式/image缺失不生成元数据，保留原PDF页定位。禁止模型或浏览器指定坐标、URL或provider对象。

ML新增私有POST `/agent/v1/research/documents/read-page-image`，请求复用DocumentReadRequest，身份、scope、version、locator校验与read-verified相同。响应data保留同read-verified字段，并附`pageRendition`和`imageBase64`。调用应只做一次原件/provider/manifest读取与normalizer回放。没有解析/模型调用。无可用image拒绝明确请求，不生成假图。原read-verified只附元数据，不包含图片字节；旧geometry及context保持逐值一致。

Backend新增认证GET于既有引用证据路径 `/source-page`；每次经过owner→workspace→artifact version→citation→evidence→source run→当前附件授权及精确字段回读。ML客户端新增read_page_image并校验receipt/scope/field、严格metadata/base64/bytes/hash，不能让知道imageHash代替授权。新endpoint二进制输出Content-Type为PNG/JPEG，nosniff和private,no-store；响应元数据来自同版source。普通source JSON只返回安全白名单pageRendition，不含imageBase64/对象URI。通过既有WorkspaceService文档client注入，复用生产默认client，便于真实本地验收。

Web扩ResearchPdfEvidenceSource可选元数据，校验字段类型、hash/page/field/version关联及bbox。新增getResearchEvidencePageImage使用同认证path，限定bytes/mime并验证sha256，再创建object URL。未加载/错误/晚到响应不可显示高亮。页面切换时abort并revokeURL；不允许provider SVG/data URI/任意外链。旧PDF分页、原PDFgeometry及原件获取不变；新视图只影响阅读组件，不修改研究工具/模型提示/checkpoint。

## 实施与验收

ML负责材料到衍生图的纯函数及只读路由；Backend负责完整引用授权、客户端和二进制端点；Web负责双视图与交互。三仓源阅读模块可独立实现，当前真实研究worker不重启；新代码只在任务终态后启动的只读服务中验证。记录当前Run加载HEAD，避免把新代码说成本次研究执行版本。

测试需覆盖真实3页golden及重复值身份、旋转整图、缺图/坏格式/超限/尺寸不符/NaN/bbox越界、hash和字段篡改、跨用户/撤销附件、旧source兼容、请求迟到和URL清理。浏览器真实来源验证缩放/旋转、表头脚注、切回原PDF同页，且原PDF继续标明真实精度。离线fixture与真实业务报告分别记录，不用构造报告代替最终交付。

## 2026-09-11 实现与独立复验

Web `e5c25e7`、Backend `9c26ef5`、ML `247d52d` 已分别提交。Web相关153项测试通过，最终请求取消改动再跑27项通过；全局tsc仍有既有错误，新运行文件未命中诊断。Backend完整portable gate 323 passed/1预期排除，ML 327 passed/0 skipped。远端CI及浏览器真实双视图另行验收。

provider dimension必须为pixels且与实际图像一致；EXIF只允许缺失或1，避免浏览器旋转改变字段坐标。独立复验捕获PNG在verify前读取EXIF会提前load的问题，已调整验证顺序。最终真实8字段及10项拒绝测试通过，包含两仓独立拒绝Orientation 3、ML拒绝尺寸冲突。具体证据见[独立复验结果](pdf_geometry_acceptance/retained_page_review/final-review-result.json)。这些结果属于真实材料离线函数验证，尚无报告HTTP/浏览器验收。

远端回读：Backend9c26ef5的CI34565406287成功；ML247d52d的CI34565407024成功。Web e5c25e7的CI34565261979在既有页面观察测试中失败（getWorkspace期望1实际2），235项通过；正在定位并修复等待后的卸载请求问题，不能将Web当前门禁标为通过。
