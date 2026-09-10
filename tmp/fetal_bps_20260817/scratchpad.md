# 胎儿肺隔离症自然史调研 Scratchpad

日期：2026-08-17

## 问题定义

- 用户报告：孕 22 周，四维超声提示肺隔离症，指标写作 `cvd 0.3`。
- 工作假设：该指标更可能是 `CVR 0.3`（congenital pulmonary airway malformation volume ratio），需要以原始超声报告确认。
- 核心终点必须分开：
  1. 孕期体积下降；
  2. 孕晚期超声不再可见；
  3. 出生后 CTA/CT/MRI 证实病灶真正消失；
  4. 胎儿水肿、胸腔积液、出生呼吸支持等临床结局。

## Claim Extraction

| Claim | 来源 | 验证通道 | 当前判断 |
|---|---|---|---|
| BPS 常在 26–28 周后缩小 | 单中心 BPS 队列、胎儿中心资料 | BPS 原始队列 | 已验证；不等于解剖学消失 |
| “约 75% 自行消失” | 综述/患者资料常见表达 | 同一患者出生后横断面影像 | 表述过强；多数数据测的是缩小或超声等回声 |
| CVR 0.3 属低风险 | CPAM 阈值与 BPS 队列 | BPS 专属预后队列 | 支持，但要看后续峰值和积液/水肿等伴随征象 |
| 产前超声消失后无需随访 | 非专业化理解 | 出生后 CT/CTA 队列及指南 | 不支持；超声消失不能排除残留 |

## 关键原始数据

### BPS 103 例队列（2008–2015）

来源：[Prenatal Growth Characteristics and Pre/Postnatal Management of Bronchopulmonary Sequestrations](https://pmc.ncbi.nlm.nih.gov/articles/PMC5828905/)

- 103 例孤立性 BPS：59 例 extralobar，44 例 intralobar。
- 未接受相关产前治疗且有连续测量的 80 例中，64 例（80%）从首次到末次评估表现为 CVR 下降或病灶变成等回声。
- intralobar 94%，extralobar 71%。
- 平均 CVR 约 26 周达到峰值，随后下降；模型峰值约 28.4 周。
- `CVR < 0.75` 对不发生胸腔积液/水肿的阴性预测值 98%，对出生时无呼吸症状的阴性预测值 96%。
- 局限：回顾性、单中心；`CVR 0.3` 是当前值还是峰值会影响可比性；阴性预测值不是个体保证。

### BPS 68 例队列

来源：[Retrospective study of prenatal diagnosed pulmonary sequestration](https://pmc.ncbi.nlm.nih.gov/articles/PMC5814128/)

- 继续妊娠并存活的 66 例中，18 例（27.3%）后续产前超声显示病灶“消失”。
- 其中 14 例接受出生后 CT，14 例均证实病灶仍存在；4 例未做 CT，不能判定真正消失。
- 56 例 `CVR ≤ 1.6` 均无胎儿水肿和出生后呼吸症状；`CVR > 1.6` 的 12 例中 7 例有水肿。
- 作者解释，晚孕期异常组织与正常肺组织等回声，可造成超声上“消失”。
- 局限：回顾性，阈值 1.6 最初来自 CPAM；队列并未单独给出 `CVR 0.3` 的风险。

### BPS 41 例双中心队列（2002–2011）

来源：[Bronchopulmonary sequestration with massive pleural effusion](https://pubmed.ncbi.nlm.nih.gov/24407869/)

- 无胸腔积液或水肿、保守观察的 29 例中，19 例（65.5%）孕期部分或完全回缩。
- 29 例全部活产；16 例（55.2%）出生后仍做了 sequestrectomy。
- 说明“部分或完全回缩”与病灶真正消失、无需出生后处理不是同一终点。

### 早期 UCSF 14 例队列

来源：[Fetal pulmonary sequestration: a favorable congenital lung lesion](https://pubmed.ncbi.nlm.nih.gov/10511360/)

- 14 个胎儿、16 个胸内 PS；4 例在出生前被描述为 large lesions regressed completely。
- 摘要未交代这 4 例是否均用出生后 CT/CTA 证实无残留；不能把 4/14 当作真正解剖学消失率。

### 41 例肺叶外型 BPS 队列

来源：[Fetal lung lesions: management and outcome](https://pubmed.ncbi.nlm.nih.gov/9790364/)

- 41 例均为 extralobar PS；28 个病灶在连续产前超声上明显回缩。
- 这 28 例出生后均无症状、无需切除，但仍只能通过出生后影像检出。
- 该研究进一步支持“明显回缩”不等于解剖学消失；由于终点不是严格的“产前完全不见”，不与 14/14 或 5/5 简单合并计算。

### 出生后 extralobar PS 自然缩小

来源：[Extralobar pulmonary sequestration in neonates: The natural course](https://pubmed.ncbi.nlm.nih.gov/27659701/)

- 51 名出生后 1 个月内 CT 确诊且未治疗、接受复查 CT 的新生儿。
- 到 4 年时，累计 93.0% 病灶体积减少超过 50%，73.3% 供血动脉直径减少超过 50%。
- 该结果是出生后的显著缩小，不代表完全消失，也只适用于 extralobar PS。

## 初步结论

1. 对 `CVR 0.3`、目前若无胸腔积液、水肿、明显纵隔移位或心脏受压，现有队列整体支持低风险和良好围产结局。
2. 孕期“变小/不再显影”的概率约为三分之二到五分之四；不同研究定义不一致，不能合并成精确个体概率。
3. 产前超声完全不再可见的可引用队列数字约 27%；但出生后 CT 核对显示，超声消失常是等回声遮蔽，而非病灶真正消失。
4. 真正解剖学自愈缺乏可靠总体概率。直接核对最强的一组数据为 0/14，但样本小且不能据此断言总体概率为 0；更合理的表述是“可能发生但明显少见，无法用现有证据给出可信百分比”。
5. 22 周还处在可能继续长大的阶段，单次 `CVR 0.3` 不能代替 24–28 周连续趋势。
