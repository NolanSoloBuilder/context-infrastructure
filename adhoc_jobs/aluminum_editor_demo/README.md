# 型构 Studio · 铝型材 3D 编辑 Demo

可运行的浏览器 Demo，用 React、Three.js 和 React Three Fiber 独立实现。参考了嘉立创 FA、乐玩 DIY 等产品的编辑流程，没有复制其代码、模型或素材。

## 启动

```bash
cd adhoc_jobs/aluminum_editor_demo
npm install
npm run dev
```

默认地址为 `http://127.0.0.1:5173/`。

## 已实现

- 12 根型材的矩形框架模板；可调整宽、深、高及 2020/3030/4040 规格后重新生成。
- 3D 选中、高亮、镜头旋转与缩放、坐标轴拖拽移动/旋转；右侧精确编辑长度、规格、颜色、位置、角度。
- 添加、复制、删除单根型材；撤销/重做；按规格、长度和颜色汇总材料清单。
- 浏览器本地保存、JSON 导出与导入。

## 边界

这是交互和数据模型 Demo。型材外形是简化的四面槽口表现，不含真实供应商 SKU、连接件、孔加工、承重、报价或可制造性校验。模板尺寸调整会重新生成整个框架，不保留此前对单根构件的修改。保存为当前浏览器的 localStorage；导出 JSON 可跨浏览器转移。

相关调研：[`contexts/survey_sessions/aluminum_3d_canvas_open_source_options_20260923.md`](../../contexts/survey_sessions/aluminum_3d_canvas_open_source_options_20260923.md)。
