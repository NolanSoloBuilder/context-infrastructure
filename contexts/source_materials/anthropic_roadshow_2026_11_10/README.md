# Anthropic 路演：最终中英双语视频

当前唯一视频：**anthropic_roadshow_bilingual.mp4**。

- 大小：803,644,640 字节，约 804 MB，低于 1 GB。
- 画面：1920×1080，H.264 AVC High@4.1（avc1），8-bit yuv420p。
- 音频：AAC-LC，原声直接复制，音频流 SHA-256 与原片相同。
- 时长：42 分 43 秒；61,458 个视频帧包。
- 字幕：全部 702 条中英字幕已烧录到画面，不依赖播放器字幕功能；从约 00:30 开始，前面为官方免责声明。
- MP4 播放索引位于视频数据之前（faststart）。

此前的 866 MB 文件虽是 MP4 容器，视频编码为 HEVC/H.265。用户反馈小红书上传提示不支持格式后，现改用 H.264/AAC。编码兼容性是本次修复的判断方向，并非已确认平台报错根因；没有在小红书实际上传或发布，因此不声称上传验收已通过。

本版直接以官方原片重新烧录双语字幕，避免使用上一版有损视频作为输入。仍是有损编码，不宣称像素级无损。成片时长、帧数、声音、像素格式和文件大小已验证，并提取成片代表画面确认双语字幕可见。财务页底部脚注部分可能被字幕覆盖。

按用户清理要求，其他 10 个视频版本及测试片段已移入 macOS 废纸篓，本目录及其子目录仅保留上述最终视频。废纸篓未清空，必要时可恢复。具体路径与大小记录见 `verification/xhs_compatible/cleanup.json`。

## 来源和核验材料

- 官方页面：https://ipo.anthropic.com/us/
- 官方公告：https://www.anthropic.com/news/roadshow-launch
- 官方字幕：https://ipo.anthropic.com/video/us/roadshow/captions.vtt
- 当前编码及封装核验：`verification/xhs_compatible/compatibility.json`
- 当前画面、帧数及抽样质量核验：`verification/xhs_compatible/visible_validation.json`
- 实际成片画面：`verification/xhs_compatible/visible_actual_*.jpg`
- 历次处理记录：`verification/delivery_history.md`（其中旧视频保留状态已被本页替代）
- 当前存在文件的校验和：`SHA256SUMS.txt`

最初原片全片逐帧解码与字幕时间覆盖检查通过，记录仍保存；这不等于人工逐帧观看全部画面。最终版本进行了编码、封装及定向画面验证，未完成真实播放器界面的实播或平台上传验收。
