# Anthropic 路演字幕与核验资料

本地已删除 `anthropic_roadshow_bilingual.mp4` 和 `anthropic_roadshow_bilingual_trimmed.mp4`。本目录可以查阅字幕、官方来源、成片截图及历史处理记录。

## 字幕与官方来源

- [中英双语 SRT](anthropic_roadshow.zh_en.srt)和[双语 ASS](anthropic_roadshow.bilingual.ass)
- [官方路演页面](https://ipo.anthropic.com/us/)、[官方公告](https://www.anthropic.com/news/roadshow-launch)和[官方英文字幕](https://ipo.anthropic.com/video/us/roadshow/captions.vtt)

## 历史成片与核验

最后一次交付的成片约 804 MB，时长 42 分 43 秒，使用 1920×1080 H.264 和 AAC-LC，烧录了 702 条中英字幕。此前 HEVC 版本在小红书被提示格式不支持，随后重新编码为 H.264。H.264 版完成了编码、封装及画面抽样核验，实际上传仍未验证。

- [编码与封装核验](verification/xhs_compatible/compatibility.json)
- [画面、帧数及抽样质量核验](verification/xhs_compatible/visible_validation.json)和[成片截图示例](verification/xhs_compatible/visible_actual_1840.jpg)
- [历次处理记录](verification/delivery_history.md)和[早期版本清理记录](verification/xhs_compatible/cleanup.json)
- [历史校验和](SHA256SUMS.txt)保留生成时的校验记录，其中的 MP4 条目用于核对历史交付版本。
