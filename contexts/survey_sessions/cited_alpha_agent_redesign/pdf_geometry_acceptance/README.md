# 两页 DocAI 最小验证请求（未执行）

`native_two_page_geometry.pdf` 是本地合成的原生 PDF，不是真实财报、未发起 DocAI 解析。
`expected_fields.json` 记录 raw SHA、PDF 页框/旋转、目标文字和其手工绘制容器矩形。
容器不是期望 OCR glyph bbox；验收应检查 OCR 框位于正确容器并覆盖目标文字，不能要求
它等于容器边界。每页有同值的 Revenue/Costs 干扰项，避免以数值搜索通过验收。

下一轮最小请求：将这一个 2 页原件通过真实授权上传路径接入，明确只执行一次 freeze
（可能产生一次 DocAI batch 费用），保留 raw/provider/manifest 三类 receipt 和原 bytes。
若 provider 返回未知结果，不自动重试，不根据客户端超时断言没有计费。

读取 provider 原始 pages 的 dimension.unit、transforms、orientation、image.width/height
和精确目标 line/cell 的 bbox。与同一 PDF 的 PDF.js 实际 viewport 对比页 1 无旋转、
页 2 Rotate=90/CropBox 非零坐标。只有映射关系得到实际样本支持后，才能资格化对应
processor/frame 规则；其它旋转/裁剪类型仍须额外真实样本，不以数学 fixture 替代。

2026-09-10 只读 `cited-alpha-20260701` 项目指定 bucket 的
`workspace-source-snapshots/documents/sha256/**` 返回 No objects，故当前无已归档
provider/raw 成对样本可完成真实映射验收。

## 已准备的隔离执行入口（尚未执行 provider POST）

API 已由主 Agent 启用，processor 已由主 Agent 创建；不要重复创建。
只读预检确认 `cited-alpha-20260701` / project number `829189946367`，区域 `us`，
processor `ba7872f1c0ed02be`，固定版本 `pretrained-ocr-v2.1-2024-08-07` 为 DEPLOYED。
预检身份为当前 gcloud 用户 `webxuhao00@gmail.com`。没有加载 ML local 的另一项目 ADC。
读取版本权限已验证；process 权限和真实响应只能由下一次实际单次调用验证。

选择 OCR_PROCESSOR 是为了本轮 pages.lines/tables 原始 boundingPoly 验证；现有 Layout
normalizer 支持这些标准字段。此次不使用旧 batch 提交的自动重试，隔离入口采用同项目
固定 processorVersion 的在线 :process，真实 provider JSON 进入既有 freeze/normalizer。
这属于 Document AI 路径，不调用 LLM policy/model_gateway；不能推断新财报模型已验收。

主 Agent 执行命令（工作目录 mindspace_ml_backend，先再核对分支）：

```bash
ENV_MODE=local .venv/bin/python -m mindspace.service.research_agent.document_geometry_canary \
  --pdf /Users/xuhao/Documents/Other/context-infrastructure/contexts/survey_sessions/cited_alpha_agent_redesign/pdf_geometry_acceptance/native_two_page_geometry.pdf \
  --output /Users/xuhao/Documents/Other/context-infrastructure/contexts/survey_sessions/cited_alpha_agent_redesign/pdf_geometry_acceptance/real_canary_20260910 \
  --execute
```

去掉 `--execute` 为只读预检；本轮已运行且输出 execute=false。独占 provider-intent.json
防同目录命令重放；若调用超时不要删除该文件重试。结果 provider-response.json 是原始
HTTP response bytes，附 SHA；objects/ 下保存原件、providerDocuments 与 manifest，
version.json 使用 canary-local receipt，明确不代表生产 GCS/DAO 授权验收。

两页、原件 SHA、项目与 processorVersion 在入口中固定；不存在自动换项目、升级模型、
更换输入或失败后重新提交。下一步从真实响应读取 polygon，并在 Chrome 同一原 PDF
页检查 Revenue 与 Costs 干扰项后再决定 frame 资格；脚本不设置 verified frame。

## 2026-09-10 真实解析与 Chrome 叠框验收（更新上面的待执行状态）

主 Agent 已完成一次真实在线 OCR 调用，结果 retained，禁止重跑该 canary。
版本 `dv-f89e51e1de4ef1a4f745a2517b1e1c5c7fa1c9deaf4548abdb256132496ca862`；
原件 SHA `60443b10535d065ff82ca6a97826fbcde559e88bfb2d8eade62af4aa5aad488f`；
provider receipt SHA `0fb5c056fc6335336b22762e0cffc0fd47b2053fc62172731e1853d39fee1580`。
完整 HTTP 响应、内容寻址对象、manifest/version 在 `real_canary_20260910/`。
`real_overlay_candidates.json` 六行的 polygon 来自该响应，bbox 通过几何函数计算，
不是人工框、搜索数字或 expected_fields 的容器矩形。

实际观察：页 1 provider image 为 1732×2309，符合 600×800 未旋转页；页 2 image
1825×2190，符合 500×600 未旋转 CropBox，而原 PDF 的 /Rotate 为 90。
因此本样本坐标转换为：provider normalized (x,y) →
PDF user point `(cropX0+x*cropWidth, cropY1-y*cropHeight)` → PDF.js 实际 viewport。
页 2 Revenue 的显示框为 x=0.27488583,y=0.11232877,w=0.01689497,h=0.22958903。
Costs 位于独立位置，证明本次没有用相同数值进行误定位。

本地隔离预览 `http://localhost:8796`（/tmp/cited-alpha-real-docai-preview，进程 67258）
使用项目已安装的真实 PDF.js 渲染同一原件。子 Agent 在 Chrome 肉眼回读：两页的
Revenue、Costs、标题共六个框覆盖对应文字；页 2 竖排旋转和裁剪正确。主审独立验收待记录。
127.0.0.1 经当前代理路径超时，localhost 可访问；未修改代理配置。

### 可服务用户的资格化规则提案（尚未启用）

资格基于受信调用留存的固定 processorVersion 与明确 PDF 特征，不能用原件 SHA
白名单让测试文件特供。SHA 只用于证明当前框绑定同一 raw/provider 内容。
建议首批只支持该固定 OCR 版本、enableNativePdfParsing=true、原生文本 PDF、
UserUnit=1、Rotate=0 或 90、正常矩形 CropBox 完全包含于 MediaBox；排除扫描图页、
透视/任意角度校正、异常页框、180/270 旋转及未知 provider 变换。
逐页还须核对 provider 图片长宽与未旋转 CropBox 的比例（容纳栅格取整），
并检查实际字段 polygon 有限、界内且非退化。图片比例只能作为一致性检查，不能
单独作为坐标规则的证明。旋转/转换签名还须与已实测帧类别一致，未知时返回 page。

实现前的真实阻断点：当前 manifest.providerProcessorVersion 是
`not_returned_by_current_batch_contract`。需由受信 provider adapter 将实际请求的固定
processorVersion、原生解析选项与调用模式写入同一不可变 manifest，并在 replay 时核验；
不能从模型、请求自报 metadata 或 parserVersion 推测。旧版本没有此受信记录继续 page。
在线 OCR 样本不能自动资格化生产 batch 的不同处理模式。应先把生产 freeze 调用模式
固定到已验证同一版本/选项，或对 batch 另做一次有界验证。当前生产 frame 表仍为空。

### 主审通过及实际接线

Root 已独立 Chrome 回读 tab1044432677：两页六个真实框均覆盖正确文字，
旋转裁剪页的同数字未串行。该结论只证明同一原件/真实 provider 与本地 PDF.js，
不代表完整产品授权 API 已通过。

实现已从空资格表推进到受信参数规则：`document_online_provider.py` 固定在线 OCR
processorVersion/mode/options，实际 parser 将其写入同一 immutable manifest；
`load_verified` 检查执行记录，`read_verified` 将受验 manifest 参数传 geometry。
旧 canary manifest 未被修改或假升级；其真实原始响应作为规则测试输入，测试显式
传已由 canary preflight 确认的执行参数，并明确这不等于旧版本已新增冻结元数据。

在线预算采用 [官方限额](https://docs.cloud.google.com/document-ai/limits) 的 15 页；
本系统仍保留 20MB 原件上限与默认 100 页总上限，16..100 页沿用单次 batch提交，
batch 字段框未资格化时仍 page。在线默认 ADC 必须属于指定项目，不读取另一项目
凭据发起请求。未知响应不自动重试。本轮没有再次调用付费 provider。
