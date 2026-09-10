# 打字游中国交互原型

独立的全国城市线路打字游戏原型。城市是节点，公路或策划路线是线路；现阶段验证真实卫星地图、授权实景、打字驱动车辆、路线关卡和分岔奇遇。

## 运行

```bash
npm run dev
```

## 真实地图与路线

地图由 MapLibre GL JS 渲染。主体影像使用 EOX 的 `s2cloudless-2025`（经处理的 Copernicus Sentinel 2025 数据），道路与地名来自 OpenFreeMap/OpenStreetMap，地形使用 Mapterhorn Raster DEM。默认以倾斜视角渲染卫星影像、山地起伏和道路信息。路线、已完成路段、城市节点、事件点和车辆分别作为独立图层；车辆位置由打字进度插值，始终沿真实道路几何前进。

地图页内保留可点击的数据署名。卫星影像服务不需要项目密钥；若影像服务暂时不可达，OpenFreeMap 的真实地形底图仍作为可用回退，不影响打字、路线与关卡状态。

`public/data/chengdu-yibin-route.geojson` 是 2026-08-04 从 OSRM driving route 响应固化的“成都 → 雅安 → 乐山 → 宜宾”道路几何，避免运行时依赖公共 routing demo：

```text
chengdu-yibin-route.geojson  6c1cbcdcda6d9d2ab6133de461f92f26a98cb71e7f0046fb65437bf4de932699
```

## 关卡与分岔玩法

- `第一关 川南城市线` 可游玩；`河西走廊`、`东南海岸` 作为后续关卡保持锁定并给出明确解锁提示。
- 输入目标城市拼音会同步推动车辆、路线进度和关卡进度，不使用骰子。
- 第一段连续输入两个正确字母后触发“熊猫古镇”岔路：国道偏探索，高速偏连击，选择会改变旅费、体力和幸运值。
- 累计 12 个正确字母后点亮隐藏路线标记；条件在触发前可见，结果可验证。
- 实景按钮随当前目的地切换图片与作者、许可证和来源链接。

## 实景资产

当前三段目的地实景均来自 Wikimedia Commons。抵达下一城后，背景图片、替代文本、拍摄信息和授权链接一起切换；下一张图片会提前加载。

### 雅安 · 碧峰峡路上

- 作者：zhanyoun
- 拍摄位置：四川雅安碧峰峡道路
- 许可证：CC BY-SA 3.0
- 原始上传日期：2010-03-12
- 原图与授权：https://commons.wikimedia.org/wiki/File:%E7%A2%A7%E5%B3%B0%E5%B3%A1%E8%B7%AF%E4%B8%8A_-_panoramio.jpg
- 本地 SHA-256：`97a2c152b1fa5569aa116654ee077c696fe0ec4d210d63deba0d209c4b27a31d`

### 乐山 · 市井街巷

- 文件：`public/assets/leshan-sideroad.jpg`
- 作者：Kounosu
- 拍摄位置：四川乐山城区
- 许可证：CC BY-SA 3.0
- 拍摄日期：2009-07-22
- 原图与授权：https://commons.wikimedia.org/wiki/File:Leshan-sideroad_China.jpg
- 本地 SHA-256：`7fed3288e59523a25d5be905ab5970162cc7b6ebeeb41576ef995f3a0337e855`

### 宜宾 · 翠屏山城市眺望

- 文件：`public/assets/yibin-birdview.jpg`
- 作者：Terence85
- 拍摄位置：四川宜宾翠屏山
- 许可证：CC BY-SA 3.0
- 拍摄日期：2009-12-27
- 原图与授权：https://commons.wikimedia.org/wiki/File:Yibin_birdview.jpg
- 本地 SHA-256：`4eca96fe66856a5eb6779995ea10175a2776fdde17d446da50465777ed04f1ad`

旧的 `sichuan-mountain-road.png` 是未被页面引用的早期 AI 概念资产，不属于当前真实实景体验。后续新增照片仍需记录来源 URL、作者、许可证、拍摄位置、审核时间与适用路线区间。

## 路线轨迹视觉资产

路线轨迹同样由 ImageGen 生成后去除纯色背景并制作浅色、绿色两个状态：

```text
route-trace-light.png  de1198100af3e45149679717f9bf98cb2f722443ad518e0fbb9427204c0802b0
route-trace-green.png  a0c50333659c63417f52f0ab0f39ae40ab8bdbf198ddfea05d17313a620f662d
```
