# 铝构平台 Web 组件库候选（2026-09-24）

## 当前工程与选型范围

独立仓库 `agent-native-aluminum-platform/apps/web` 当前使用 React 19、Vite、R3F/Three.js，未接入通用 UI 组件库。产品界面包括 3D 画布、构件树、参数属性、BOM、规则问题和 Agent 提案预览。这里选的是 Web 工作台基础组件；3D 场景、几何操作、领域校验仍由平台自身实现。

## 候选

| 候选 | 适用面 | 本项目判断 |
| --- | --- | --- |
| [Ant Design 6](https://ant.design/) | 表单、树、表格、抽屉、分隔面板、提示与状态；[React 19 兼容](https://ant.design/docs/react/migration-v6/) | 默认首选。覆盖工作台普通控件。用主题 token 调整密度和色彩，避免直接套后台模板。 |
| [Semi Design](https://semi.design/en-US/start/introduction) | 现代中后台视觉与常规组件 | 备选。React 19 要用 [`@douyinfe/semi-ui-19`](https://semi.design/en-US/start/getting-started)；试点核对主题能力、画布中的弹层和键盘事件。 |
| [Arco Design](https://github.com/arco-design/arco-design) | 中后台常规组件、较简洁的视觉 | 备选。发布仍活跃；React 19 项目需真实试装和交互验收，不能只看 peer dependency。 |
| [Blueprint](https://blueprintjs.com/docs/) | 高信息密度的桌面工具界面，含独立 Table 包 | 如果最终定位更接近 CAD/IDE，可做视觉原型。组件广度和中文业务表单生态需与 Ant Design 对比。 |
| [AG Grid](https://www.ag-grid.com/react-data-grid/key-features/) | 大规模 BOM、分组、筛选、编辑、粘贴等表格 | 作为专用数据网格按需引入。Community 可免费用于生产；Enterprise 生产使用需要许可。先用真实 BOM 样例确定高级功能是否必要。 |
| [MUI X Data Grid](https://mui.com/x/react-data-grid/) | 复杂表格的另一个专用候选 | Community 为 MIT；Pro/Premium 功能需要商业许可。若主库选 Ant Design，需验证跨设计系统的样式一致性。 |
| [Ant Design X](https://x.ant.design/) | Agent 对话输入、消息、过程展示等 | 若主库选 Ant Design，可复用 AI 交互基础组件。但提案的修订号、命令、画布高亮、BOM 差异和审批动作仍须自定义并接平台真实 API。 |

## 建议的落地次序

1. 选 Ant Design 6 为唯一基础视觉系统，用 `Tree`、`Form`、`InputNumber`、`Splitter`、`Drawer`、`Alert` 搭出一条完整编辑任务。数值输入 UI 与领域内核的 0.01 mm 整数模型通过显式转换衔接；库本身不承担尺寸正确性。
2. 用真实的 3D 画布 + 右栏属性 + BOM + Agent 提案，检查弹层层级、键盘快捷键冲突、窄面板布局、深浅主题和错误定位。
3. BOM 出现明显超出普通 Table 的需求时，试 AG Grid Community；需要 Enterprise 分组、透视或其他专有能力再核算许可。Agent 面板出现真实流式消息需求时再加 Ant Design X。

选型是当前建议，尚未试装、跑页面或验证实际 BOM 数据规模；不能将此文当成已采用记录。

## 2026-09-24 补充：优先定设计风格

用户明确希望先找更现代的设计风格，组件库不是先决条件。当前 `apps/web/src/style.css` 使用深绿顶栏、大量浅绿底色与 10–12px 小字号；这是源码观察，尚未做页面视觉验收。

建议方向是**浅色精密工作台**：参考 [Linear 2026 界面更新](https://linear.app/now/behind-the-latest-design-refresh) 的层级处理、[Geist 色彩系统](https://vercel.com/geist/colors)的少量中性色层级，以及 [Fusion 工作区](https://help.autodesk.com/cloudhelp/ENU/Fusion-GetStarted/files/GS-THE-FUSION-INTERFACE.htm)以画布为中心的工具布局。借鉴其原则，不复刻品牌外观。

- 画布占视觉中心，侧栏与工具条安静退后；中性灰白底、细分隔线，减少大片彩色背景和装饰卡片。
- 一种品牌强调色只用于当前选中、焦点和主操作；红/橙/绿仅表达规则错误、待复核、通过等业务状态。Agent 过程用信息层级与变化标注呈现，不靠发光球或渐变代表智能。
- 工具栏、构件树和属性面板保持高密度，但字段正文至少 13–14px，尺寸数值可用等宽数字；尺寸和单位在视觉上成组，修订号、规则来源可被直接查到。
- Agent 提案优先展示作用范围、画布差异、尺寸/BOM 变化、规则问题和应用按钮。聊天记录是过程入口，工程变更预览是决策主体。
- 建议先做一张固定场景的设计稿：`850×450×900 mm` 桌架、下层净空 300 mm、Agent 修改宽度、2 条 BOM 差异与 1 条待复核问题；同时看空白和复杂项目两种密度。

此方向仍是方案，尚未改页面代码或验证渲染效果。基础组件可以混合使用现成库与自定义控件，最终以同一套视觉 token 和真实交互验收为准。

## 2026-09-24 视觉反馈与修订

首轮静态预览被用户判断为“太 AI”，缺少现代、科技与专业感。问题主要是通用 SaaS 卡片、装饰性状态、悬浮 Agent 卡、玩具化模型让工程任务退居次位。已在独立仓库 `design_previews/` 重做三套方向：Precision OS（浅色工程工作台）、Graphite CAD（深色专业工作台）、Digital Twin（混合工业工作台）。共同基线为命令工具栏、装配树、工程尺寸线、属性检查器、固定变更审阅；AI 仅作为可追溯变更来源。三套 `design.md` 与 HTML 属视觉方案，不连接真实项目 API。用户对修订版的接受度仍待确认。

随后用户确认前两套风格适合作为同一产品的暗色与亮色模式（原话“两色模式”，按语境理解为“亮色模式”）。已补充共享[主题合同](https://github.com/NolanSoloBuilder/agent-native-aluminum-platform/blob/main/DESIGN.md)，并在预览顶栏加入即时主题切换。用户随后要求直接丢弃第三套 Digital Twin，相关预览、截图、文档与代码均已移除；项目只保留亮暗两套。
