## 主要参考文献

- ①：_A Systematic Review of Key RAG Systems: Progress, Gaps, and Future Directions_（arXiv:2507.18910，2025年7月，田纳西大学 & 橡树岭国家实验室）

- ②：_Graph-Based Approaches and Functionalities in RAG: A Comprehensive Survey_（ACM Computing Surveys，Vol.58，2026年4月，南洋理工大学）

- ③：_Enhancing the Precision and Interpretability of RAG in Legal Technology: A Survey_（IEEE Access，Vol.13，2025年3月，阿联酋大学）

---

## 流程全景图

```plaintext
原始文档
   │
   ▼
【Step 1】文档解析          ← 必做｜将原始内容转换为可处理的文本
   │
   ▼
【Step 2】分块（Chunking）   ← 必做｜切分为适合检索的片段
   │
   ▼
【Step 3】嵌入（Embedding）  ← 必做｜将文本映射为向量
   │
   ▼
【Step 4】索引构建           ← 必做｜建立高效检索结构
   │
   ▼（离线构建完成，以下为在线推理）
   │
用户查询
   │
   ▼
【Step 5】查询处理           ← 可选｜对查询进行改写/扩展/分解
   │
   ▼
【Step 6】检索               ← 必做｜从索引中获取候选内容
   │
   ▼
【Step 7】重排序（Reranking）← 可选｜精排，提升相关性
   │
   ▼
【Step 8】上下文构建         ← 必做｜组装送入LLM的输入
   │
   ▼
【Step 9】生成               ← 必做｜LLM生成最终答案
   │
   ▼
【Step 10】后处理与验证      ← 可选｜引用校验、安全过滤、格式化

```

---

## Step 1：文档解析（Document Parsing）

### 必要性

**必做。** RAG 系统的数据质量上限由解析质量决定。文档格式复杂多样（PDF、HTML、Word、扫描件），解析失败或质量低下会直接污染下游所有环节，产生"垃圾进，垃圾出"的问题。

### 技术选项对比

| 技术 | 原理 | 优势 | 劣势 | 适用场景 |
| --- | --- | --- | --- | --- |
| **规则/结构化解析** | 按 XML/HTML/JSON 格式提取 | 速度快、精确、无幻觉 | 仅适用于规范格式文档 | EU 法规（论文③ Chat-EUR-Lex）、API 响应 |
| **基于规则的 PDF 解析**（PyMuPDF、pdfplumber） | 提取文字层及位置信息 | 轻量，处理数字原生 PDF 效果好 | 对扫描件、多栏布局失效 | 标准 PDF 文档 |
| **OCR 引擎**（Tesseract、PaddleOCR） | 图像识别转文字 | 处理扫描件 | 识别错误率较高，无语义理解 | 纸质文档数字化 |
| **VLM 增强解析**（GPT-4V、DeepDoc） | 视觉语言模型理解文档版面 | 处理复杂版式、表格、图文混排 | 成本高、速度慢 | 复杂报告、含图表的文档（论文①提及 DeepDoc） |
| **OpenIE 三元组抽取** | 从文本中抽取 <split/> (e_h, r, e_t) <split/> 三元组 | 自动构建知识图谱，支持多跳推理 | 精度不稳定，噪声多 | 图 RAG 构建（论文② HippoRAG、GraphRAG） |
| **指令调优 LLM 解析** | 用 LLM 做实体与关系抽取 | 语义理解强，抽取质量高 | 成本极高，速度慢 | 高质量 KG 构建、法律实体识别（论文③ MedGraphRAG） |

### 选型建议

```plaintext
文档格式规范（XML/HTML/数字PDF） → 规则/结构化解析
扫描件或复杂版式                 → VLM 增强解析
需要构建知识图谱                 → OpenIE + 指令调优LLM
通用场景优先                     → 规则解析 + OCR 兜底
```

---

## Step 2：分块（Chunking）

### 必要性

**必做。** LLM 的上下文窗口有限，且检索的基本单位是"块"。分块粒度直接影响检索精度与上下文完整性，是 RAG 效果最敏感的超参数之一。

### 技术选项对比

| 技术 | 原理 | 优势 | 劣势 | 适用场景 |
| --- | --- | --- | --- | --- |
| **固定大小分块** | 按固定 Token 数切割，可设重叠 | 实现简单、速度快 | 割裂语义，边界不自然 | 快速原型、通用文本 |
| **句子级分块** | 按句号/语义句子边界切割 | 边界自然、语义完整 | 块大小不均，短句问题 | 法律 QA（论文③ HyPA-RAG 验证最优） |
| **段落/章节级分块** | 按文档结构（标题、段落）切割 | 保留文档逻辑结构 | 粒度较粗，影响召回精度 | 结构清晰的文档 |
| **模式分块（Pattern-based）** | 设计领域专用分隔符（如法条编号）切割 | 最贴合领域语义，精度最高 | 需领域知识，泛化性差 | 法律/医学等强结构化领域（论文③ 综合最优） |
| **语义分块** | 按语义相似度聚合相关句子 | 语义连贯性强 | 计算成本高，调优复杂，论文③指出未经大量调优不如简单方法 | 语义理解要求极高场景 |
| **递归字符分割（RCTS）** | 按优先级依次尝试多种分隔符 | 适应性强，工程实用 | 仍非语义感知 | 通用工程场景（LegalBench-RAG 使用） |
| **图社区分块** | GraphRAG 对文档实体做社区检测，社区为检索单元 | 支持全局查询，摘要前置 | 构建开销极大 | 需全局理解的大规模分析（论文② GraphRAG） |
| **层次化分块（父子块）** | 小块用于检索，大块用于生成 | 兼顾召回精度与上下文完整性 | 存储翻倍，管理复杂 | 复杂文档的生产级系统 |

---

## Step 3：嵌入（Embedding）

### 必要性

**必做（向量检索路径）。** 嵌入质量决定语义召回的上限。若使用纯 BM25 则可跳过此步，但实践中几乎所有生产系统都会包含向量检索。

### 技术选项对比

#### 3.1 稀疏嵌入（关键词检索）

| 技术 | 优势 | 劣势 |
| --- | --- | --- |
| **BM25** | 极轻量、关键词精确匹配、可解释 | 无语义理解、词汇不匹配 |
| **TF-IDF** | 更简单，冷启动友好 | 效果弱于 BM25 |

#### 3.2 密集嵌入（语义检索）

| 技术 | 来源论文 | 优势 | 劣势 | 适用场景 |
| --- | --- | --- | --- | --- |
| **DPR 双编码器** | 论文① | 端到端可训练，语义强 | 需要标注数据，泛化弱 | 有监督领域检索 |
| **Contriever** | 论文① | 无监督训练，泛化性强，超越 BM25 和 DPR | 精度略低于有监督方法 | 无标注数据的新领域 |
| **OpenAI text-embedding-3-large** | 论文③ | 开箱即用、多语言、效果优秀 | API 成本高、数据隐私风险 | 商业快速部署 |
| **Legal-BERT / ft-LegalBERT-DPR** | 论文③ | 法律语义理解强 | 领域限制，训练成本高 | 法律专业检索（CLERC） |
| **distilBERT（法律微调）** | 论文③ HyPA-RAG | 轻量、快速 | 效果弱于全量 BERT | 资源受限的法律系统 |
| **bge-m3 / embed-multilingual-v3.0** | 论文③ | 多语言支持 | 中文/多语言专用 | 多语言法律文档（MVRAG） |
| **AnglEBERT** | 论文③ CBR-RAG | 对比学习增强，语义鲁棒性强 | 较新，社区支持少 | 法律案例相似度检索 |

#### 3.3 图结构嵌入

| 技术 | 来源论文 | 优势 | 劣势 | 适用场景 |
| --- | --- | --- | --- | --- |
| **GAT（图注意力网络）** | 论文② | 动态权重聚合，捕捉长程依赖 | 显存开销大，需训练 | 多跳 KGQA（KG-FiD、ATLANTIC） |
| **GCN（图卷积网络）** | 论文② | 局部拓扑高效聚合 | 全局信息建模弱 | 节点分类、链接预测 |
| **Hyperbolic 嵌入** | 论文② HamQA | 天然建模层次关系 | 数学复杂，实现难度高 | 层次化知识图谱推理 |

### 选型建议

```plaintext
通用语义检索，快速部署           → OpenAI text-embedding-3-large
成本敏感/私有化部署             → bge-m3 / Contriever
法律专业领域                   → ft-LegalBERT-DPR 或 Legal-BERT
多语言场景                     → bge-m3 / embed-multilingual-v3.0
图 RAG / 多跳推理              → GAT + 文本嵌入联合方案
```

---

## Step 4：索引构建（Indexing）

### 必要性

**必做。** 没有高效索引，大规模向量检索无法在毫秒级完成。索引结构决定检索速度与精度的权衡。

### 技术选项对比

#### 4.1 向量索引

| 技术 | 原理 | 查询速度 | 精度 | 内存占用 | 适用规模 |
| --- | --- | --- | --- | --- | --- |
| **HNSW**（分层可导航小世界） | 分层图结构 ANN | 极快（毫秒） | 高 | 较高 | 百万级，生产推荐 |
| **IVF-PQ**（倒排文件+乘积量化） | 聚类+量化压缩 | 快 | 中（量化损失） | 极低 | 十亿级，存储敏感 |
| **Flat（暴力精确搜索）** | 全量计算内积 | 慢（线性） | 100% 精确 | 低 | 百万以下，精度优先 |
| **ScaNN**（Google） | 各向异性量化 | 极快 | 高 | 中 | 超大规模 |

#### 4.2 稀疏索引

| 技术 | 原理 | 优势 | 适用场景 |
| --- | --- | --- | --- |
| **倒排索引（Inverted Index）** | 词 → 文档列表映射 | 极快的关键词精确查找 | BM25 基础，所有系统标配 |

#### 4.3 图索引

| 技术 | 来源论文 | 原理 | 优势 | 劣势 |
| --- | --- | --- | --- | --- |
| **知识图谱图索引** | 论文② | 实体+关系图结构存储 | 支持多跳遍历、关系推理 | 构建维护成本高 |
| **Neo4j Vector + 图混合索引** | 论文② | 向量检索 + 图遍历融合 | 兼顾语义与关系 | 需要专业图数据库运维 |
| **社区摘要索引** | 论文② GraphRAG | 预生成社区摘要作为检索单元 | 支持全局查询 | 构建时间长，存储大 |

#### 4.4 主流向量数据库对比

| 数据库 | 索引类型 | 托管方式 | 特点 | 适用场景 |
| --- | --- | --- | --- | --- |
| **Milvus** | HNSW/IVF/FLAT | 自托管/云 | 高性能、功能完整、开源 | 大规模生产环境 |
| **Qdrant** | HNSW | 自托管/云 | Rust 实现，内存高效，Payload 过滤强 | 中大规模，过滤场景 |
| **pgvector** | IVF/HNSW | PostgreSQL 插件 | 复用现有 PG 基础设施 | 已有 PG 体系 |
| **Weaviate** | HNSW | 自托管/云 | 内置多租户，图-向量混合 | 多模态、企业级 |
| **Chroma** | HNSW | 嵌入式/自托管 | 极简 API，适合原型 | 开发调试、小规模 |
| **Neo4j（+向量）** | 图 + 向量混合 | 自托管/云 | 图 RAG 首选 | 关系推理场景（论文②） |

### 选型建议

```plaintext
通用生产环境           → Milvus（HNSW） 或 Qdrant
已有 PostgreSQL 栈     → pgvector
图 RAG 场景           → Neo4j + 向量索引
超大规模（十亿+）      → Milvus（IVF-PQ）
快速原型              → Chroma
```

---

## Step 5：查询处理（Query Processing）

### 必要性

**可选，但对复杂查询效果提升显著。** 原始用户查询往往模糊、口语化、或信息不足。查询处理通过改写、扩展、分解等手段提升检索质量。

### 技术选项对比

| 技术 | 原理 | 来源论文 | 提升效果 | 成本 | 适用场景 |
| --- | --- | --- | --- | --- | --- |
| **查询改写（Query Rewriting）** | 用 LLM 将口语化查询改写为检索友好形式 | 论文① | 中等提升 | 低（一次 LLM 调用） | 口语化、模糊查询 |
| **HyDE（假设文档嵌入）** | 先生成假设答案，用答案嵌入做检索 | 论文① | 显著提升（尤其稀疏领域） | 中（需生成假设文档） | 稀疏知识库、专业领域 |
| **查询分解（Query Decomposition）** | 将复杂问题拆解为多个子问题分别检索 | 论文①② | 显著提升（多跳查询） | 高（多次检索） | 复杂多跳推理 |
| **查询扩展（Query Expansion）** | 添加同义词、相关术语扩充查询 | 论文① | 小幅提升召回率 | 低 | 专业术语覆盖不全 |
| **子图查询生成（Cypher/SPARQL）** | LLM 将自然语言转换为图查询语言 | 论文② | 精确图检索 | 中（LLM 调用+调试） | 知识图谱 QA（论文② KG-GPT） |
| **双语/多语言查询转换** | 将查询翻译到文档语言 | 论文③ DRAG-BILQA | 显著提升跨语言检索 | 中 | 多语言法律/政务系统 |
| **Self-Ask 分步提问** | Agent 自主生成子问题，逐步缩小检索范围 | 论文② | 高（多跳场景） | 高（多步 LLM 推理） | 复杂推理链 |

### 选型建议

```plaintext
简单问答，成本敏感        → 跳过（直接检索）
查询模糊或口语化          → 查询改写
专业领域稀疏知识库        → HyDE
复杂多跳问题              → 查询分解 + Self-Ask
图 RAG 场景               → 子图查询生成（Cypher）
多语言系统                → 多语言查询转换
```

---

## Step 6：检索（Retrieval）

### 必要性

**必做，是 RAG 的核心环节。** 检索质量直接决定生成质量的上限。

### 技术选项对比

#### 6.1 单路检索

| 技术 | 原理 | 优势 | 劣势 | 代表实现 |
| --- | --- | --- | --- | --- |
| **BM25（稀疏）** | 词频统计匹配 | 关键词精确、轻量、无需 GPU | 无语义理解，词汇不匹配 | Elasticsearch、Lucene |
| **密集向量检索（ANN）** | 向量内积相似度 | 语义理解，同义词泛化 | 专有名词可能漂移 | Milvus、Qdrant |
| **图遍历检索** | BFS/DFS/PPR 在知识图谱上遍历 | 支持多跳关系推理，可解释 | 大图效率低 | Neo4j、论文② MINERVA |
| **随机游走（PPR）** | 个性化 PageRank 扩散 | 可扩展，容错 | 精度低于精确遍历 | 论文② HippoRAG |

#### 6.2 混合检索（生产环境主流方案）

| 融合方式 | 原理 | 优势 | 来源论文 |
| --- | --- | --- | --- |
| **RRF（倒数排名融合）** | \text&#123;RRF&#125;(d) = \sum \frac&#123;1&#125;&#123;k + \text&#123;rank&#125;_i(d)&#125; ， <split/> k=60 | 无需调权重，鲁棒性强 | 论文① |
| **线性加权融合** | \alpha \cdot \text&#123;dense\_score&#125; + (1-\alpha) \cdot \text&#123;sparse\_score&#125; | 可调权重，灵活 | 论文①③ |
| **图+向量混合** | 图检索扩展候选 + 向量精排 | 兼顾关系推理与语义 | 论文② HybridRAG |

#### 6.3 自适应检索（高级方案）

| 技术 | 原理 | 来源论文 | 适用场景 |
| --- | --- | --- | --- |
| **Self-RAG** | LLM 生成反思 Token（[Retrieve]/[No Retrieve]）按需触发检索 | 论文① | 避免冗余检索，提升效率 |
| **Adaptive-RAG** | 按查询复杂度动态切换无检索/单步/迭代模式 | 论文② | 预算感知的生产系统 |
| **FLARE** | 生成过程中遇低置信度词时触发主动检索 | 论文② | 实时感知生成质量 |
| **SIM-RAG** | 自我怀疑批评者决定何时停止多轮检索 | 论文① | 多轮检索的停止条件 |
| **Self-Routing RAG** | LLM 自主选择用内部知识还是外部检索（减少 29% 检索，提升 5pp 准确率） | 论文① | 效率与质量平衡 |

#### 6.4 迭代检索（复杂推理）

| 技术 | 原理 | 来源论文 | 优势 |
| --- | --- | --- | --- |
| **迭代检索（Iterative RAG）** | 多轮检索+生成，每轮结果作为下一轮查询输入 | 论文① | 解决单次检索信息不足 |
| **CBR-RAG（基于案例推理）** | 检索历史相似案例辅助当前推理 | 论文③ | 提升法律推理可解释性 |
| **RAGRAPH（图上多跳）** | 在知识图谱上进行多跳路径检索 | 论文② | 精确多跳关系推理 |

### 检索方式全面对比

| 检索方式 | 召回率 | 精度 | 多跳能力 | 可解释性 | 延迟 | 构建成本 |
| --- | --- | --- | --- | --- | --- | --- |
| BM25 | 中 | 高（关键词精确） | ❌ | ✅ | 极低 | 极低 |
| 密集检索 | 高 | 中 | ❌ | ❌ | 低 | 中 |
| 混合检索（BM25+密集） | 最高 | 高 | ❌ | 中 | 低 | 中 |
| 图遍历 | 中 | 极高（约束推理） | ✅✅ | ✅✅ | 中 | 高 |
| 图+向量混合 | 高 | 高 | ✅ | ✅ | 中 | 高 |
| Self-RAG（自适应） | 中 | 高 | 中 | 中 | 动态 | 中 |

### 选型建议

```plaintext
通用生产环境                   → 混合检索（BM25 + 密集 + RRF）
成本敏感/简单问答              → BM25 或纯密集检索
需要多跳关系推理               → 图 RAG（图遍历 + 向量混合）
高频系统、需减少检索开销       → Self-Routing RAG / Adaptive-RAG
法律/医疗等需可解释性          → 图检索 + 引用锚定（论文③ CBR-RAG）
```

---

## Step 7：重排序（Reranking）

### 必要性

**强烈推荐，近似必做。** 检索阶段（召回）和生成阶段（精读）的需求不同：召回要宽，精读要准。重排序充当"精读筛选器"，可在不增加检索成本的前提下显著提升 Top-K 质量。

### 技术选项对比

| 技术 | 原理 | 优势 | 劣势 | 延迟开销 |
| --- | --- | --- | --- | --- |
| **Cross-Encoder 交叉编码器** | 将查询与每个候选文档拼接后打分（联合编码） | 精度最高，充分建模交互 | 延迟高（线性于候选数） | 高 |
| **MonoT5** | T5 作为重排器，生成"True/False"判断相关性 | 效果优秀，开源 | 需 GPU，推理较慢 | 中-高 |
| **Cohere Rerank API** | 商业重排 API | 开箱即用，效果优秀 | API 费用，数据外送 | 中 |
| **BGE-Reranker** | BAAI 开源重排模型 | 效果接近商业，中文友好 | 需自部署 | 中 |
| **LLM 打分重排** | 用 LLM 对每个候选文档打相关性分 | 理解深度最强 | 成本极高，速度极慢 | 极高 |
| **RRF（倒数排名融合）** | 多路检索结果排名融合（无模型） | 零额外计算，鲁棒 | 无法学习精细语义 | 极低 |
| **图验证器重排** | CRAG 等用轻量图验证器对候选文档评估质量后重排 | 结合结构信息 | 需构建验证器 | 中 |

### 选型建议

```plaintext
生产环境标准配置         → BGE-Reranker 或 Cohere Rerank
预算充足、精度优先       → Cross-Encoder（如 ms-marco-MiniLM）
多路检索结果融合         → RRF（可与精排叠加使用）
图 RAG 场景             → 图验证器 + Cross-Encoder
极度成本敏感            → 跳过（依赖检索质量）
```

---

## Step 8：上下文构建（Context Assembly）

### 必要性

**必做。** 检索到的内容并不能直接喂给 LLM，需要组织成结构化的 Prompt。上下文质量直接影响生成结果。这也是"上下文工程（Context Engineering）"兴起的核心原因（论文①）。

### 技术选项对比

| 技术 | 原理 | 优势 | 劣势 | 适用场景 |
| --- | --- | --- | --- | --- |
| **直接拼接（Naive Concatenation）** | 将 Top-K 文档顺序拼接 | 简单 | "中间迷失（Lost in the Middle）"问题，LLM 忽略中间内容 | 简单场景、文档数少（K≤3） |
| **Fusion-in-Decoder（FiD）** | 每个文档独立编码后在解码器融合 | 充分利用多文档，精度高 | 需修改模型架构，不适用黑盒 LLM | 开源模型（论文① 标准方案） |
| **摘要压缩** | 先将检索文档压缩摘要，再拼接 | 节省 Token，减少噪声 | 可能丢失细节 | Token 窗口紧张场景 |
| **层次化上下文（TreeRAG）** | 小块精准检索定位，大块完整喂给 LLM | 兼顾检索精度与上下文完整性 | 实现复杂，需离线构建树状索引 | 论文①（RAGFlow）推荐 |
| **图子图上下文** | 将检索到的实体子图线性化为文本输入 | 保留关系信息，支持多跳推理 | Token 消耗大，格式复杂 | 图 RAG（论文② 拓扑感知提示） |
| **引用锚定构建** | 每个上下文块附带来源标注，嵌入 Prompt | 支持引用验证，提升可信度 | Prompt 变长 | 法律/医疗等需溯源场景（论文③） |
| **多文档排列优化** | 最相关文档放首/尾，避免中间位置 | 缓解"中间迷失"问题 | 需要额外排序逻辑 | 较长上下文场景 |

### 选型建议

```plaintext
通用场景                  → 直接拼接（控制 K≤5，相关文档置首尾）
开源模型/高精度场景       → Fusion-in-Decoder
Token 窗口紧张            → 摘要压缩后拼接
复杂文档理解              → TreeRAG（父子块层次化组装）
图 RAG                    → 子图线性化（文本提示，降低 Token 消耗）
法律/医疗需溯源           → 引用锚定上下文（论文③）

```

---

## Step 9：生成（Generation）

### 必要性

**必做，是最终输出环节。** LLM 的能力决定生成质量的上限，生成策略影响可信度、格式和安全性。

### 技术选项对比

#### 9.1 生成模型选型

略

#### 9.2 生成策略

| 策略 | 原理 | 来源论文 | 优势 | 劣势 |
| --- | --- | --- | --- | --- |
| RAG-Sequence | 固定一个检索文档生成完整答案 | 论文① | 上下文聚焦，生成连贯 | 单文档信息有限 |
| RAG-Token | 每个 Token 可切换不同文档（逐 Token 边际化） | 论文① | 灵活利用多文档 | 实现复杂，训练需特殊处理 |
| Fusion-in-Decoder（FiD） | 多文档独立编码后解码器融合 | 论文① | 多文档融合效果最佳 | 需修改模型架构，不适用黑盒 LLM |
| 约束解码（Constrained Decoding） | 强制生成内容锚定到检索文档，禁止生成未见内容 | 论文③ | 大幅减少幻觉，可信度高 | 灵活性降低，可能影响流畅度 |
| 自我反思生成（Self-RAG） | 生成带反思 Token 的输出（[Retrieve] / [IsRel] / [IsSup] / [IsUse]），自主判断是否需要检索或修正 | 论文① | 质量自控，按需检索，显著超越 ChatGPT | 需要专门训练带反思 Token 的模型 |
| 引用强制生成 | Prompt 中强制要求每句话标注来源引用编号，如 [1][3] | 论文③ | 完全可溯源，法律/医疗场景必要 | Prompt 冗长，输出冗余 |

---

## Step 10：后处理与验证（Post-processing & Verification）

### 必要性

可选，但高风险领域（法律、医疗、金融）近似必做。 生成阶段结束并不意味着系统可以直接将结果返回给用户。后处理是 RAG 流程的最后一道防线，解决三类核心问题：

1. 幻觉与事实错误：生成内容与检索文档不一致

2. 安全风险：对抗攻击、有害内容、隐私泄露

3. 格式与体验：输出结构不符合下游系统要求

---

### 技术选型对比

#### 10.1 事实性验证（Faithfulness Verification）

目标：检测生成内容是否有检索文档的事实支撑，识别幻觉。

| 技术 | 原理 | 来源论文 | 优势 | 劣势 | 适用场景 |
| --- | --- | --- | --- | --- | --- |
| RAGAS 评估框架 | 用 LLM 分别评估 Faithfulness、Answer Relevance、Context Relevance、Context Recall 四个维度 | 论文① | 无需参考答案，自动化评估 | 依赖 LLM 自身能力，存在评估偏差 | 开发阶段质量监控 |
| ARAGOG | 自动化输出评分系统，用于 RAG 管道性能对比 | 论文① | 支持多管道横向对比 | 配置复杂 | 多系统对比评测 |
| NLI 蕴含检测 | 用自然语言推理（NLI）模型判断生成内容是否被检索文档蕴含 | 论文① | 轻量、快速、无需 LLM | 蕴含关系判断粗糙 | 实时在线校验 |
| 引用覆盖率检查（Citation Coverage） | 逐句核查生成内容中引用的条款/文档是否真实存在 | 论文③ | 精确溯源，法律场景必要 | 需结构化引用格式 | 法律/学术系统 |
| CRAG（纠正性 RAG） | 轻量评估器对检索文档打相关性分（低分→网络搜索补充；高分→直接使用；中间→知识精炼） | 论文② | 自动识别知识库覆盖盲区并补救 | 网络搜索引入新的不确定性 | 知识库不完整的场景 |

#### 10.2 安全过滤（Safety Filtering）

目标：防止系统输出有害内容，抵御对抗攻击。

论文①的 SafeRAG 基准对 14 个主流 RAG 系统测试后发现：所有系统均存在安全漏洞，揭示了四类主要攻击向量及对应防御策略：

| 攻击类型 | 攻击描述 | 危害 | 防御手段 |
| --- | --- | --- | --- |
| 银噪声（Silver Noise） | 注入貌似相关但事实错误的文档，污染检索结果 | 生成内容被误导，输出错误信息 | 多源交叉验证；置信度阈值过滤；来源可信度评分 |
| 上下文冲突（Context Conflict） | 注入与其他检索文档相互矛盾的内容 | LLM 被混淆，输出不一致答案 | 冲突检测模块；强制要求生成时标注文档间矛盾 |
| 软广告注入（Soft Ad Injection） | 在正常回答中植入商业宣传或偏向性内容 | 系统被用于商业操纵 | 内容审核模型；来源白名单机制 |
| 拒绝服务（DoS） | 构造特殊查询使系统检索超时或崩溃 | 服务不可用 | 查询限速；异常查询检测；超时熔断 |

#### 领域专用安全过滤（论文③）

法律/医疗等高风险领域还需额外的内容安全层：

| 过滤类型 | 原理 | 代表实现 |
| --- | --- | --- |
| 有害法律建议过滤 | 识别并屏蔽可能误导用户的不当法律建议 | ChatLaw 内置安全层（论文③） |
| 免责声明强制插入 | 在所有 AI 生成法律/医疗内容前附加免责声明 | 论文③ 多个系统标配 |
| 权威来源白名单 | 仅允许使用经认证的官方文档作为知识源 | 论文③ TaxTajweez、Chat-EUR-Lex |
| 隐私信息脱敏 | 检测并遮蔽输入/输出中的个人隐私信息 | 论文③ 数据保护场景 |

---

#### 10.3 引用溯源与可解释性（Citation & Explainability）

目标：使生成结果可审查、可追溯，满足高可信场景的合规要求。

| 技术 | 原理 | 来源论文 | 实现方式 |
| --- | --- | --- | --- |
| 引用锚定输出 | Prompt 中强制要求每个关键声明附带 [来源编号] | 论文③ | System Prompt 约束 + 后处理解析 |
| 图路径溯源 | 图 RAG 中将检索所用的子图路径随答案一并输出 | 论文② | 图遍历记录路径，输出人类可读推理链 |
| 置信度标注 | 在输出中为每个声明附加不确定性分数 | 论文③ | NLI 模型打分或 LLM 自评 |
| 反思 Token 可视化 | Self-RAG 的 [IsSup]/[IsRel] 等 Token 暴露给用户 | 论文① | Self-RAG 模型原生支持 |
| 来源文档高亮 | 在 UI 层将生成内容与原始检索文档段落对齐标注 | 通用工程实践 | 前端染色 + 后端偏移量记录 |

---

#### 10.4 输出格式化与结构化（Output Formatting）

目标：将生成内容转换为下游系统可消费的格式。

| 技术 | 适用场景 | 实现方式 |
| --- | --- | --- |
| JSON 结构化输出 | API 接口、前端渲染 | Function Calling / Structured Output |
| Markdown 格式化 | 文档生成、富文本展示 | Prompt 约束 + 后处理解析 |
| 法律文书格式 | 法律助手输出判决摘要 | 模板化 Prompt（论文③） |
| 流式输出（Streaming） | 实时聊天界面 | Server-Sent Events / WebSocket |
| 多语言翻译后处理 | 多语言系统 | 生成后自动翻译（DRAG-BILQA，论文③） |

---

#### 10.5 人工审核节点（Human-in-the-Loop）

适用场景：法律判决、医疗诊断、金融合规等不可逆高风险决策。

论文③明确指出，当前 RAG 技术在以下情况下必须保留人工审核：

| 场景 | 原因 | 推荐机制 |
| --- | --- | --- |
| 生成置信度低于阈值 | AI 不确定，需人工确认 | 自动路由至人工队列 |
| 涉及重大法律后果 | AI 建议影响当事人权益 | 律师强制复核 |
| 检测到文档冲突 | 多来源矛盾，AI 无法裁定 | 人工裁决后反馈入库 |
| 新颖查询（无历史案例） | 超出知识库覆盖范围 | 人工解答 + 补充入库 |

### 选型建议

| 场景 | 事实验证 | 安全过滤 | 引用溯源 | 人工审核 |
| --- | --- | --- | --- | --- |
| 通用企业问答 | RAGAS（开发期）+ NLI（线上） | 基础内容审核 | 来源文档高亮 | 不需要 |
| 法律文书助手 | 引用覆盖率检查 + RAGAS | 有害建议过滤 + 权威白名单 | 引用锚定 + 图路径溯源 | 必须（关键决策） |
| 医疗问答系统 | NLI 蕴含检测 + CRAG | 隐私脱敏 + 来源白名单 | 置信度标注 | 必须（诊断建议） |
| 公开对抗环境 | RAGAS + 多源交叉验证 | SafeRAG 全套防御 | 溯源链路记录 | 异常触发 |
| 知识库不完整 | CRAG 三级处置 | 基础过滤 | 标注"来源：网络搜索" | 不需要 |
| 实时客服 | NLI 轻量检测 | 基础有害词过滤 | 来源链接 | 不需要 |

# RAG框架调研

| 框架 | Stars | Forks | License | 语言 | 创建时间 | 描述 |
| --- | --- | --- | --- | --- | --- | --- |
| **Dify** | 140K | 22K | 自定义 | TypeScript | 2023-04 | Production-ready platform for agentic workflow development |
| **LangChain** | 136K | 22.5K | MIT | Python | 2022-10 | The agent engineering platform |
| **RAGFlow** | 80K | 9.1K | Apache-2.0 | Python | 2023-12 | Leading open-source RAG engine with Agent capabilities |
| **mem0** | 55K | 6.3K | Apache-2.0 | Python | - | Universal memory layer for AI Agents |
| **LlamaIndex** | 49K | 7.4K | MIT | Python | 2022-11 | Leading document agent and OCR platform |
| **Milvus** | 44K | 4.0K | Apache-2.0 | Go | - | High-performance cloud-native vector database |
| **LightRAG** | 35K | 5.0K | MIT | Python | - | [EMNLP2025] Simple and Fast RAG |
| **DSPy** | 34K | 2.9K | MIT | Python | - | Programming—not prompting—language models |
| **Microsoft GraphRAG** | 33K | - | MIT | Python | - | Modular graph-based RAG system |
| **LangGraph** | 32K | - | MIT | Python | - | Build resilient language agents as graphs |
| **Qdrant** | 31K | 2.2K | Apache-2.0 | Rust | - | High-performance massive-scale vector database |
| **Chroma** | 28K | 2.2K | Apache-2.0 | Rust | - | Search infrastructure for AI |
| **RAG_Techniques** | 27K | 3.3K | 自定义 | Jupyter | - | 100+ advanced RAG technique tutorials |
| **Haystack** | 25K | 2.8K | Apache-2.0 | MDX | - | Open-source AI orchestration framework |
| **Weaviate** | 16K | 1.3K | BSD-3 | Go | - | Vector database with structured filtering |
| **LLMWare** | 15K | 2.9K | Apache-2.0 | Python | - | Enterprise RAG with small specialized models |
| **txtai** | 12K | 809 | Apache-2.0 | Python | - | All-in-one AI framework for semantic search |
| **CocoIndex** | 9.2K | 687 | Apache-2.0 | Python | - | Incremental engine for long horizon agents |
| **Arize Phoenix** | 9.6K | 855 | 自定义 | Python | - | AI Observability & Evaluation |
| **R2R** | 7.8K | 629 | MIT | Python | - | SoTA production-ready AI retrieval system |

_(数据来源：GitHub API，2026-05-09)_

```plaintext
RAG 框架生态
│
├── 【全栈平台型】开箱即用，Web UI + API
│   ├── Dify            — 可视化工作流，Agent 编排，零代码
│   ├── RAGFlow         — 深度文档解析，GraphRAG，知识库管理
│   └── R2R             — RESTful API 优先，Agentic RAG
│
├── 【开发框架型】代码优先，灵活组合
│   ├── LangChain       — 最全生态，Agent/Chain/工具调用
│   ├── LlamaIndex      — 文档索引专家，300+ 数据连接器
│   ├── Haystack        — 企业级管道，组件化架构
│   └── DSPy            — 声明式编程，自动优化 Prompt
│
├── 【专项能力型】聚焦单一环节极致
│   ├── LightRAG        — 轻量极速，图+向量混合
│   ├── Microsoft GraphRAG — 社区检测，全局摘要，多跳推理
│   ├── RAG_Techniques  — 100+ 高级 RAG 技术教程集
│   └── LLMWare         — 小型专用模型，CPU 友好
│
├── 【记忆与状态型】持久化上下文
│   ├── mem0            — 通用记忆层，用户/会话/Agent 三层
│   └── CocoIndex       — 增量数据处理，长时 Agent 引擎
│
├── 【基础设施型】向量/图存储底座
│   ├── Milvus          — 云原生向量数据库，十亿级
│   ├── Qdrant          — Rust 实现，高性能过滤
│   ├── Chroma          — 轻量嵌入式，开发友好
│   └── Weaviate        — 向量+对象混合存储
│
└── 【评估监控型】质量保障
    ├── RAGAS           — RAG 专用评估框架
    ├── Arize Phoenix   — AI 可观测性平台
    └── LangSmith       — LangChain 官方调试工具

```

# 法务知识库相关

## 框架总览

数据隐私合规知识库核查框架 v2.2 由 **7大职能域（Domain）、5层文档结构（Layer）** 构成，并配套**入库状态追踪体系**。

### 框架结构图

```plaintext
DPKF v2.2 框架架构

【五层文档结构】
L1 外部法规层    ──  法律法规原文（他律·强制）
        +
L2 监管指引层    ──  监管机构执法口径（他律·引导）
        ↓ 须符合
L3 平台公示层    ──  对外公示的平台制度（自律·对外承诺）
        ↓ 须符合
L4 内部文档层    ──  内部制度 / SOP / 操作清单 / 评估模板（自律·内部执行）
        ↓ 须符合
L5 合同模板层    ──  对外协议 / 通知模板（执行层·对外使用）

【七大控制域】
├── D1. 治理与问责 Governance & Accountability
│   ├── C1.1 隐私组织架构 Privacy Organizational Structure
│   ├── C1.2 政策与制度体系 Policy & Regulatory Framework
│   ├── C1.3 风险管理 Risk Management
│   └── C1.4 合规监督与审计 Compliance Monitoring & Audit
│
├── D2. 数据资产与全生命周期保护 Data Asset & Lifecycle Protection
│   ├── C2.1 数据分类分级 Data Classification & Categorization
│   ├── C2.2 数据采集与最小化 Data Collection & Minimization
│   ├── C2.3 数据存储与安全 Data Storage & Security
│   ├── C2.4 数据使用与处理 Data Use & Processing
│   ├── C2.5 数据共享与跨境 Data Sharing & Cross-Border Transfer
│   └── C2.6 数据留存与销毁 Data Retention & Disposal
│
├── D3. 用户权利保障 Individual Rights Protection
│   ├── C3.1 隐私通知与告知 Privacy Notice & Disclosure
│   ├── C3.2 同意管理 Consent Management
│   ├── C3.3 数据主体权利响应 Data Subject Rights Response
│   └── C3.4 未成年人与弱势群体保护 Minors & Vulnerable Groups Protection
│
├── D4. 技术隐私工程 Privacy Engineering
│   ├── C4.1 隐私设计原则 Privacy by Design
│   ├── C4.2 隐私增强技术 Privacy Enhancing Technologies
│   ├── C4.3 安全技术控制 Security Technical Controls
│   └── C4.4 隐私影响评估与个人数据保护影响评估 Privacy Impact Assessment & Data Protection Impact Assessment
│
├── D5. 广告与用户画像合规 Advertising & User Profiling Compliance
│   ├── C5.1 用户画像的合法性依据 Lawful Basis for User Profiling
│   ├── C5.2 定向广告的数据处理合规 Data Processing Compliance for Targeted Advertising
│   ├── C5.3 敏感数据与未成年人数据的广告限制 Restrictions on Sensitive & Minors' Data in Advertising
│   ├── C5.4 退出机制与用户控制权 Opt-Out Mechanisms & User Control
│   └── C5.5 自动化决策与算法的透明度义务 Transparency Obligations for Automated Decision-Making & Algorithms
│
├── D6. 第三方与供应链管理 Third-Party & Supply Chain Management
│   ├── C6.1 供应商隐私评估 Vendor Privacy Assessment
│   ├── C6.2 合同与数据处理协议 Contracts & Data Processing Agreements
│   └── C6.3 第三方SDK/API管理 Third-Party SDK / API Management
│
└── D7. 事件响应与持续改进 Incident Response & Continuous Improvement
    ├── C7.1 隐私事件管理 Privacy Incident Management
    ├── C7.2 监管报告与配合 Regulatory Reporting & Cooperation
    ├── C7.3 员工培训与意识 Employee Training & Awareness
    └── C7.4 框架迭代与度量 Framework Iteration & Metrics
```

## 五层文档结构说明

| 层级 | 名称 | 内容说明 | 典型文档示例 | 典型文件格式 |
| --- | --- | --- | --- | --- |
| L1 | 外部法规层 | 各法域立法机关颁布的法律法规原文，是合规义务的最终依据；所有下层文件须符合此层要求 | PIPL、GDPR、CCPA、COPPA、DSA | HTML、PDF |
| L2 | 监管指引层 | 监管机构发布的执法指引、解释性文件、口径说明，细化法规适用方式 | EDPB指南、ICO指南、网信办操作指引 | HTML、PDF |
| L3 | 平台公示层 | 对外公示的平台制度文件，具有对用户的法律约束力，须符合L1/L2，同时作为L4-L6的上位依据 | 隐私政策、用户服务协议、Cookie声明、未成年人保护说明、算法透明度说明 | HTML、PDF、REdoc（Markdown）、TXT |
| L4 | 内部文档层 | 公司内部结合业务实际制定的管理制度、治理规程，及面向一线执行的SOP、操作清单、检查表、评估模板等，须与L3平台公示内容保持一致 | 全球隐私治理总纲、DSR管理制度、DPO任命文件、内部处置SOP | HTML、PDF、REdoc（Markdown） |
| L5 | 合同模版层 | 对外使用的协议、声明、通知模板，经法律审查可直接引用 | 法务提供 | Docx、REdoc（Markdown） |

<redoc-highlight fillColor="orange">
**层级约束关系**：L1 → L2 → L3 → L4 → L5，下层文件须符合上层要求；L3平台公示层是对外承诺的**法律**锚点，L4内部文档和L5合同模板均不得与L3产生矛盾。
</redoc-highlight>