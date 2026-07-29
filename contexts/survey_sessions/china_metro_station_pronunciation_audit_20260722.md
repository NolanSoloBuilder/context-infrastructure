# 中国地铁站名无声调拼音审计（2026-07-22）

## 结论

对游戏固定数据集中的 41 个城市、283 条线路、6155 条线路站点记录做了全量审计。按“城市 + 完整中文站名”去重后共 5363 项；先用多音字与双拼音库差异做召回，再按城市分区逐项核验地方读音、官方站名拼写和既有纠音。

本轮用户反馈共新增 24 项纠音：宁波 4 项先行修复，全国复核再发现 20 项。纠音表由 61 项增至 85 项。只修改会影响键盘字母序列的差异，声调、轻声、变调和纯分词差异不改。

## 已修改站名

| 城市 | 站名 | 原拼写 | 修正拼写 |
|---|---|---|---|
| 宁波 | 邱隘东 | `qiu ai dong` | `qiu ga dong` |
| 宁波 | 邬隘 | `wu ai` | `wu ga` |
| 宁波 | 柳隘 | `liu ai` | `liu ga` |
| 宁波 | 曹隘 | `cao ai` | `cao ga` |
| 北京 | 广渠门内 | `an qu men nei` | `guang qu men nei` |
| 北京 | 广渠门外 | `an qu men wai` | `guang qu men wai` |
| 大连 | 革镇堡 | `ge zhen bao` | `ge zhen pu` |
| 大连 | 二十里堡 | `er shi li bao` | `er shi li pu` |
| 大连 | 三十里堡 | `san shi li bao` | `san shi li pu` |
| 大连 | 长店堡 | `chang dian bao` | `chang dian pu` |
| 长春 | 兴隆堡 | `xing long bao` | `xing long pu` |
| 长春 | 前十里堡 | `qian shi li bao` | `qian shi li pu` |
| 无锡 | 北栅口 | `bei shan kou` | `bei zha kou` |
| 杭州 | 枸桔弄 | `gou ju nong` | `gou ju long` |
| 武汉 | 谌家矶 | `chen jia ji` | `shen jia ji` |
| 郑州 | 祭城 | `ji cheng` | `zha cheng` |
| 济南 | 七里堡 | `qi li bao` | `qi li pu` |
| 济南 | 八涧堡 | `ba jian bao` | `ba jian pu` |
| 香港 | 东涌 | `dong yong` | `dong chong` |
| 香港 | 鲗鱼涌 | `zei yu yong` | `ze yu chong` |
| 深圳 | 茜坑 | `qian keng` | `xi keng` |
| 深圳 | 沙壆 | `sha xue` | `sha bo` |
| 成都 | 广都 | `guang dou` | `guang du` |
| 成都 | 航都大街 | `hang dou da jie` | `hang du da jie` |

## 原因与实现边界

问题不只是一类“方言读音”。主要来源有三种：地方沿用的地名专读（如宁波“隘”读 `ga`、郑州“祭城”读 `zha cheng`）、同字在不同地名中的约定读法（如“堡”在不同城市分别可为 `pu` 或 `bao`），以及通用拼音库对专名分词或字义判断错误（如“广渠门”被拆错）。因此实现采用“城市 + 完整站名”覆盖，不能全局替换单个汉字。

香港站名仍按游戏既定的普通话汉语拼音目标处理，不用官方粤语罗马字；“东涌、鲗鱼涌”的普通话审音依据采用《新华字典》第十二版相关审音资料。

主要核验来源包括：[北京公共标识资料](https://wjw.beijing.gov.cn/zwgk_20040/tzgg/201912/P020191216686747641123.pdf)、[辽宁日报地名读音资料](https://epaper.lnd.com.cn/lnrbepaper/pc/con/202111/17/content_133217.html)、[武汉地方志答复](https://dfz.wuhan.gov.cn/hdjl/zwzx/202411/t20241126_2489809.shtml)、[郑州市民政局地名资料](https://mzj.zhengzhou.gov.cn/work/9942221.jhtml)、[济南市政府英文地铁资料](https://english.jinan.gov.cn/col68689/art/2021/art_68689_4760966.html)、[深圳市现行地铁站名表](https://www.sz.gov.cn/en_szgov/life/transport/metro/content/post_12583635.html)和[香港地名审音报道](https://www.chinanews.com.cn/cul/2020/08-13/9264334.shtml)。每条落库规则的来源键与 URL 保存在纠音数据文件中。

## 未决项与数据边界

- 无锡“西园弄”：公开资料同时出现 `Xiyuanlong` 和 `Xiyuannong`，尚未找到足以裁决的官方拼音标注。本轮保留 `xi yuan nong`，避免凭非官方聚合站点改错。
- 大连“革镇堡”：旧铁路资料与现行地铁拼写线索存在冲突，本轮选择现行地铁场景采用的 `ge zhen pu`，并在纠音表中按完整站名限定。
- 当前上游地铁数据截止 2023-06；之后新增线路、站名变更与新站不在本次 5363 项范围内。

## 验证

- `pnpm data:china`：重新生成 41 城、283 线、6155 条线路站点记录。
- `pnpm test`：46/46 通过，包含 24 个本轮纠音的显式回归测试和全部落库纠音覆盖校验。
- `pnpm build`：通过。
- `git diff --check`：通过。
