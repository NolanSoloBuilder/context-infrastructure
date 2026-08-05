# 打字游中国交互原型

独立的全国城市线路打字游戏原型。城市是节点，公路或策划路线是线路；现阶段验证真实地图、授权实景、打字驱动车辆和无点击连续到站的核心体验。

## 运行

```bash
npm run dev
```

## 真实地图与路线

地图由 MapLibre GL JS 渲染，底图使用 OpenFreeMap Liberty 样式及 OpenStreetMap 数据。`public/data/chengdu-yibin-route.geojson` 是 2026-08-04 从 OSRM driving route 响应固化的“成都 → 雅安 → 乐山 → 宜宾”道路几何，避免运行时依赖公共 routing demo：

```text
chengdu-yibin-route.geojson  6c1cbcdcda6d9d2ab6133de461f92f26a98cb71e7f0046fb65437bf4de932699
```

## 实景资产

当前主画面 `public/assets/yaan-bifengxia-road.jpg` 是 Wikimedia Commons 上的真实摄影《碧峰峡路上》：

- 作者：zhanyoun
- 拍摄位置：四川雅安碧峰峡道路
- 许可证：CC BY-SA 3.0
- 原始上传日期：2010-03-12
- 原图与授权：https://commons.wikimedia.org/wiki/File:%E7%A2%A7%E5%B3%B0%E5%B3%A1%E8%B7%AF%E4%B8%8A_-_panoramio.jpg
- 本地 SHA-256：`97a2c152b1fa5569aa116654ee077c696fe0ec4d210d63deba0d209c4b27a31d`

旧的 `sichuan-mountain-road.png` 是未被页面引用的早期 AI 概念资产，不属于当前真实实景体验。后续新增照片仍需记录来源 URL、作者、许可证、拍摄位置、审核时间与适用路线区间。

## 路线轨迹视觉资产

路线轨迹同样由 ImageGen 生成后去除纯色背景并制作浅色、绿色两个状态：

```text
route-trace-light.png  de1198100af3e45149679717f9bf98cb2f722443ad518e0fbb9427204c0802b0
route-trace-green.png  a0c50333659c63417f52f0ab0f39ae40ab8bdbf198ddfea05d17313a620f662d
```
