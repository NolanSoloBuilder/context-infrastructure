# 颈椎节奏岛浏览器视觉能力核对

页面：`https://cowork.xiaohongshu.com/s/neck-rhythm-game-v2/`

## 结论

该页面使用浏览器端的 MediaPipe Face Landmarker 完成人脸关键点与头部姿态识别。摄像头通过 `navigator.mediaDevices.getUserMedia()` 获取，视频帧在 `requestAnimationFrame` 循环中传给 `detectForVideo()`，模型输出面部变换矩阵和 blendshapes。页面随后将变换矩阵换算为 `yaw`、`pitch`、`roll`：

- `yaw`：左右转头
- `pitch`：抬头、低头
- `roll`：左右歪头

模型资源为同站点下的 `./mediapipe/face_landmarker.task` 和 `./mediapipe/wasm`。推理优先使用 GPU，初始化失败时回退 CPU。因此更准确的能力名称是浏览器端实时头部姿态估计，属于 Web 端侧计算机视觉。

## 游戏映射

游戏会比较三种角度与各自阈值，识别 `turnLeft`、`turnRight`、`up`、`down`、`left`、`right` 等方向事件，并结合节拍时间窗计算 `perfect`、`good`、`miss`。角色模型也会跟随 `yaw`、`pitch`、`roll` 转动，眼睛和嘴部动画使用 face blendshapes。

## 本地处理边界

静态代码显示，摄像头视频对象直接传给 MediaPipe 的 `detectForVideo()`，未发现 `MediaRecorder`、WebRTC 或将视频帧编码后上传的业务路径。页面仍然存在常规网络请求，包括加载 JS、WASM、模型、音乐资源，获取用户身份，提交排行榜分数，以及上报由姿态计算得到的调试/统计事件。

所以应区分两件事：

1. 摄像头画面的视觉推理在浏览器本地完成。
2. 整个网页并非天然完全离线，首次加载资源、排行榜和统计功能仍会联网。

本次未授权摄像头并运行完整关卡，因此“没有上传画面”属于静态代码链路核对结果。若要做隐私审计，还需要在允许摄像头后抓取完整 Network 请求，确认运行期 payload。
