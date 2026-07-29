# 全国地铁站名无声调拼音审计 Search Manifest

## 产出文件索引

| 文件 | 路径 | 说明 |
|---|---|---|
| Scratchpad | `tmp/metro_pronunciation_audit_20260722/scratchpad.md` | 审计范围、候选生成与阶段判断 |
| Search Manifest | `tmp/metro_pronunciation_audit_20260722/search_manifest.md` | 子任务、来源和覆盖记录 |
| 最终报告 | `contexts/survey_sessions/china_metro_station_pronunciation_audit_20260722.md` | 完整审计结论、修改项与未决项 |

## Subagent 原始产出

| Agent | 区域 | 状态 |
|---|---|---|
| `audit_north_east` | 北方与华东，兼查全国高风险字 | completed：2542 个唯一站名 |
| `audit_south_west` | 华南与西南，兼查粤语/地方专名边界 | completed：1803 个唯一站名 |
| `audit_central_west` | 中部与西北，并做全数据集自动候选扫描 | completed：1018 个唯一站名 |

## 数据覆盖

- 总城市数：41
- 总线路站点记录：6155
- `城市 + 完整站名` 唯一项：5363
- 审计前人工纠音：65
- 审计后人工纠音：85（本轮新增 20；连同先行修复的宁波 4 站，本次用户反馈共新增 24）
- 双词典未覆盖差异候选：62

## 来源记录

按“官方地铁或政府地名资料 > 官方地图/英文站名 > 权威新闻 > 百科与社区线索”登记。社区资料只能生成候选，不能单独支持修改。落库来源见 `data/china-metro-pronunciations.json` 的 `sources` 字段；结论和未决项见最终报告。
