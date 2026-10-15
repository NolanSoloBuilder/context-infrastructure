# 铝型材平台的 3D 画布：开源方案与自研边界

日期：2026-09-23。这里的“画布”指浏览器中选型材、搭框架、编辑尺寸、查看装配的交互界面；不等于 CAD 几何内核，也不等于完整的铝型材业务编辑器。以下只依据开源项目官方仓库和文档判断能力，不推测嘉立创、乐玩等平台的内部技术栈。

## 现成能力

| 层 | 开源选择与已确认能力 | 对铝型材产品的适用边界 |
| --- | --- | --- |
| 3D 渲染与交互 | [Three.js](https://github.com/mrdoob/three.js)（MIT）提供场景、相机、模型、[射线拾取](https://threejs.org/docs/pages/Raycaster.html)、[移动/旋转控制](https://threejs.org/docs/pages/TransformControls.html)及[截面拉伸网格](https://threejs.org/docs/pages/ExtrudeGeometry.html)。[Babylon.js](https://github.com/BabylonJS/Babylon.js)（Apache-2.0）是另一套开源引擎，其 [Inspector](https://github.com/BabylonJS/Documentation/blob/master/content/toolsAndResources/inspector.v2.md) 可查看并操作场景。 | 能搭可交互画布，但不知道“3030 型材”“角码”“孔位”代表什么。 |
| React 画布组织 | [React Three Fiber](https://github.com/pmndrs/react-three-fiber)（MIT）是 Three.js 的 React 渲染层，可把场景组织为组件。 | 适合 React 产品界面；它不是 CAD 或装配规则引擎。 |
| 通用开源编辑器 | Three.js 仓库内有[场景编辑器](https://github.com/mrdoob/three.js/blob/dev/editor/index.html)；[JSCAD](https://github.com/jscad/OpenJSCAD.org)（MIT）提供浏览器/CLI 参数化建模与部分格式输出；[FreeCAD](https://github.com/FreeCAD)是开源桌面参数化 CAD。 | 可参考交互、脚本和建模方式，但无法直接替代面向型材 SKU、连接件、工艺和报价的网页编辑器。 |
| 精确 CAD 几何 | [OpenCascade.js](https://github.com/donalffons/opencascade.js)将 Open CASCADE 移植到 JS/WASM；[replicad](https://github.com/sgenoud/replicad/blob/main/packages/replicad-docs/docs/use-as-a-library.md)在其上封装建模 API，并说明可输出 STL/STEP、用 Three.js 展示。 | 适合需要 B-rep、布尔加工或 STEP 的阶段；WASM 较大且计算可能耗时，官方建议在 Web Worker 中运行。引入前需单独核对许可证和部署成本。 |

## 哪些通常要自己实现

图形库只负责把物体画出来、让用户点到和移动它。专用编辑能力仍要基于产品物料和工艺构建：

1. **设计数据模型**：型材规格与长度、位置姿态、连接关系、面板、五金、孔加工、模板参数和版本。3D 网格只是这个模型的一个视图。
2. **约束与编辑命令**：端点/槽口吸附、角度与长度锁定、批量改宽高、相邻构件联动、撤销重做、无效操作反馈。
3. **制造规则**：SKU 兼容、连接件和孔位生成、切割清单、BOM、报价、可加工范围。BOM 必须从结构化设计模型推导，不能从三角网格反推。
4. **AI 修改接口**：把自然语言转成受限的编辑命令，在同一套约束与校验里执行；保留可解释的变更清单和失败原因。AI 不应直接改渲染网格。

因此，较准确的行业表述是**“开源图形/几何底座 + 自建垂直领域编辑器”**。下面对几个产品的公开资源做了进一步核查；没有发现可以开箱即用、同时覆盖铝型材装配、BOM 和 AI 改型的开源网页编辑器。

## 公开网页资源的技术指纹

核查时间：2026-09-23。方法：抓取入口 HTML，跟随 `script src`、`modulepreload` 和 iframe 地址，再在公开 JS 中查框架标识及实际渲染 API。资产 URL 可能随部署变更；下列判断限于本次抓到的版本。公开 bundle 能证明某些库**存在于产物中**，不能证明全部代码的作者、后台技术或某项业务能力的实现方式。

| 产品 | HTML/脚本证据 | 可得结论 | 置信度 |
| --- | --- | --- | --- |
| 嘉立创 FA | [`/free-design`](https://xc.jlcfa.com/free-design) 的 HTML 有 `__NUXT__`，主体嵌入 [`/profile-editor`](https://xc.jlcfa.com/profile-editor?iframeId=freeDesignEditor) iframe。后者加载 [`index-B2ryqjj_.js`](https://xc.jlcfa.com/profile-editor/assets/index-B2ryqjj_.js)，其中出现 `react-dom` 19.2.4、Three.js 的 `WebGLRenderer`/`GLTFLoader`/`TransformControls` 实现。 | 外壳是 Nuxt/Vue；实际 3D 编辑器至少使用 React + Three.js。不能只分析外壳 bundle。 | 高（库指纹）；具体业务代码归属未知 |
| 乐玩 DIY | [编辑器 HTML](https://www.lewandiy.com/editor) 预加载 `three-*.js`、[`three-react-*.js`](https://www.lewandiy.com/assets/three-react-1789545428597.js)、`react-vendor-*.js`。`three-react` bundle 明确包含 `rendererPackageName: "@react-three/fiber"` 和 `TransformControls`；[主 bundle](https://www.lewandiy.com/assets/index-1789545428597.js) 创建 React root。 | React + Three.js + React Three Fiber；吸附、BOM 等产品逻辑在其应用代码中，不能归因于 R3F。 | 高 |
| 80/20 IdeaBuilder | [HTML](https://ideabuilder.io/) 只加载 [`webcad.b04555.min.js`](https://ideabuilder.io/js/webcad.b04555.min.js)。其中有 `react-dom` 16.14.0、`createShader`/`createProgram`、自带场景 `renderScene` 等 WebGL 代码；未在此 bundle 检出 Three.js/Babylon.js 典型标识。 | UI 使用 React；3D 部分至少包含直接调用 WebGL 的 `webcad` 代码。**不能仅凭压缩包断言该引擎由 80/20 从零自研**，也不能排除嵌入了未标名的第三方代码。 | React 高；渲染引擎来源低 |
| Zoo Design Studio | [HTML](https://app.zoo.dev/) 加载 Vite 产物 [`index-j-V5fAUm.js`](https://app.zoo.dev/assets/index-j-V5fAUm.js)。脚本有 `react-dom` 19.2.8、Three.js `WebGLRenderer`，也引用 `kcl_wasm_lib_bg.wasm`。 | 公开前端包含 React + Three.js，另有 KCL WASM；仅凭这些不能描述其完整 CAD 后台。 | 高（库指纹） |
| MISUMI FRAMES | [官网 FAQ](https://us.misumi-ec.com/service/promotion/frames/) 指向 Windows 软件，而非网页编辑器。 | 没有对应网页编辑器资源可按此方法判断。 | 高 |

**回答“是否大家都自己实现”**：嘉立创和乐玩已能从产物确认使用 Three.js，乐玩还使用 R3F。80/20 的公开 bundle 呈现另一种做法：React 界面加直接 WebGL 的 WebCAD 实现，但其代码来源仍无法确定。无论哪一种，3D 引擎之外的型材装配与制造规则都需要产品自己构建或集成；压缩前端资源不能证明具体规则的来源和正确性。

**获取边界**：浏览器需要下载的 HTML、JS、CSS、公开模型和可见的请求协议都可以分析。压缩 JS 中确有选取、吸附、BOM 等前端逻辑的线索，但变量名、模块边界和设计意图会被打包与压缩弱化。本次抽查的嘉立创编辑器、乐玩和 IdeaBuilder 主脚本未发现可用的公开 source map；嘉立创相应 `.js.map` 地址返回的是 HTML 页面，乐玩及 IdeaBuilder 返回 404。服务端的价格、订单、物料主数据及规则不能仅凭浏览器资源完整获得。学习和功能验证可参考公开行为；我们的[独立 Demo](../../adhoc_jobs/aluminum_editor_demo/README.md)不复用它们的私有脚本和素材。

## 对创意平台的首版建议

先用 Three.js（React 团队可加 React Three Fiber）做画布，以独立的参数化装配数据模型作为唯一真源。首版限定少量标准截面、直线型材和典型框架：从 SKU 截面和长度生成展示网格；把拖拽、吸附、改尺寸转换成设计命令；每次命令后重算连接和 BOM。模板保存为结构化设计数据，社区作品可从模板分叉。AI 负责提议和执行这些命令，并返回变更预览。

只有当首版明确要求复杂自由曲面、任意布尔加工、可靠的 STEP 交付时，再做 OpenCascade.js/replicad 的原型验证。STEP 与采购 BOM 的准确性要分别验证；能导出一个 3D 文件不等于能形成可采购方案。

关联：[平台调研](aluminum_creative_platform_survey_20260923.md)、[编辑能力对比](aluminum_editor_capability_comparison_20260923.md)。
