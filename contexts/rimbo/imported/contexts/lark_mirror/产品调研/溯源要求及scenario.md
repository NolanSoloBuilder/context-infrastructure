<!-- lark-mirror obj_token=Q9eCdzKg4opRAXxO1JWj0FQ3pLP space=产品调研 synced=2026-05-18T07:54:44Z -->

<title>溯源要求及scenario</title>

目标：对齐funda ai，ppl 及 rogo



**三、溯源与定位层（Traceability & Grounding）**

这是 Rogo 区别于通用 RAG 的核心，技术要求如下：

1. **片段级溯源（Chunk-level Provenance）**

每个被检索到的片段必须携带：

plain

复制

```Plain Text
{
  "source_id": "capiq_api://companies/AAPL/financials/2024Q3",
  "source_type": "api|pdf|excel|ppt|db",
  "location": {
    "pdf": {"page": 12, "bbox": [x1,y1,x2,y2]},
    "excel": {"sheet": "DCF", "cell": "E23", "formula": "=E22*(1+D23)"},
    "ppt": {"slide": 5, "shape_id": 3},
    "api": {"endpoint": "/v1/equity/financials", "params": {"ticker":"AAPL"}, "timestamp": "2024-10-15T09:30:00Z"}
  },
  "raw_hash": "sha256:abc123...",  // 原始内容哈希，防篡改
  "retrieval_score": 0.92,         // 向量相似度或 BM25 分数
  "parser_version": "pdf_v2.3"     // 解析器版本，便于回溯 bug
}
```

1. **推理链溯源（Chain-of-Thought Provenance）**

对于 Agent 生成的结论（如"目标价 180 美元"），需记录：

- **引用了哪些原始片段**（片段 ID 列表）
- **中间计算步骤**（Excel 公式执行日志、Python 计算中间态）
- **人工修正记录**（如有分析师手动调整，需保留 diff）

1. **实时溯源验证**

- **原文高亮回显**：用户点击引用时，直接打开原始 PDF/Excel/PPT 并跳转到具体位置
- **API 数据 freshness 标记**：显示数据最后更新时间，过期数据自动标红
- **版本对比**：如果原始文档更新（如公司发布了修正版 10-K），自动提示引用内容可能失效



# 10个投资人日常使用场景（channel里实现的）

---

## 场景 1：被投企业动态监控

- **投资人需求信息**：重大交易、收购、融资、产品发布、合作进展
- **举例**：

  - NVIDIA 投资 World Labs 2 亿美元
  - Binance 45.7% 交易自动触发
  - Spark 2.0 发布
- **信息溯源要求**：

  - **片段级溯源**：每条融资、交易、产品发布或合作信息都需要追溯到公司公告、新闻原文、监管文件或 API 返回片段。
  - **实时溯源验证**：公告更新自动提示，API timestamp 标注最新抓取时间，原文支持高亮回显。
  - **推理链溯源**：引用融资公告 + 估值计算 + 投资方变化 + 分析师手动调整 diff，形成“被投企业影响判断”。

**JSON 模板：**

```JSON
{
  "片段级溯源": {
    "source_id": "company_announcement://WorldLabs/funding/2026Q2",
    "source_type": "pdf",
    "location": {
      "pdf": {
        "page": 3,
        "bbox": [100, 200, 400, 250]
      }
    },
    "raw_hash": "sha256:abc123",
    "retrieval_score": 0.95,
    "parser_version": "pdf_v2.3"
  }
}
```



---

## 场景 2：财报事件分析

- **投资人需求信息**：收入、毛利、增长率、资本支出、盈利预测
- **举例**：

  - 2026Q1 APP 美国市场收入增长 20%
  - CapEx 增加 10 亿美元
- **信息溯源要求**：

  - **片段级溯源**：财报原文 PDF、10-Q/10-K、业绩新闻稿、earnings transcript 或 Excel 模型 cell 可追溯。
  - **数据级溯源**：收入、毛利、CapEx、增长率等需要标注期间、币种、口径、计算公式。
  - **实时溯源验证**：原文回显 + 修正版财报自动提醒；如果公司更新财报或 filing，引用内容需标记可能失效。
  - **推理链溯源**：同比/环比计算、margin 计算、CapEx 差异计算、Excel 公式日志。

**JSON 模板：**

```JSON
{
  "片段级溯源": {
    "source_id": "sec_filing://APP/10-Q/2026Q1",
    "source_type": "pdf",
    "location": {
      "pdf": {
        "page": 7,
        "bbox": [80, 320, 560, 380]
      }
    },
    "raw_hash": "sha256:def456",
    "retrieval_score": 0.96,
    "parser_version": "pdf_v2.3"
  }
}
```

---

## 场景 3：宏观市场趋势分析

- **投资人需求信息**：GDP、CPI、利率、就业、政策变化
- **举例**：

  - 美国 CPI 4.2%
  - 美联储加息 25bp
- **信息溯源要求**：

  - **片段级溯源**：官方统计表格、央行公告、政策声明、新闻发布会原文可追溯。
  - **数据级溯源**：宏观数据需记录 series ID、发布时间、修订状态、单位、国家/地区、统计口径。
  - **实时溯源验证**：官方数据发布后自动更新；若数据被修订，历史引用需提醒。
  - **推理链溯源**：历史周期对比 + 增长率计算 + 政策路径推演。

**JSON 模板：**

```JSON
{
  "片段级溯源": {
    "source_id": "bls_api://US/CPI/2026-04",
    "source_type": "api",
    "location": {
      "endpoint": "/v1/macro/cpi",
      "params": {
        "country": "US",
        "series": "CPI",
        "period": "2026-04"
      },
      "timestamp": "2026-05-08T12:30:00Z"
    },
    "raw_hash": "sha256:ghi789",
    "retrieval_score": 0.97,
    "parser_version": "macro_api_parser_v1.4"
  }
}
```

---

## 场景 4：行业与竞争格局分析

- **投资人需求信息**：企业市场份额、竞争对手策略、行业趋势
- **举例**：

  - AMD GPU 市场份额 25%
  - NVIDIA Blackwell 架构发布
- **信息溯源要求**：

  - **片段级溯源**：行业报告、公司公告、产品发布稿、第三方研究报告可追溯。
  - **数据级溯源**：市场份额、出货量、客户数量、价格变化等需标注统计口径和时间范围。
  - **实时溯源验证**：最新季度报告或公司公告更新后自动提示。
  - **推理链溯源**：竞争分析 + 市场份额变化趋势 + 产品路线图对比 → 行业趋势判断。

**JSON 模板：**

```JSON
{
  "片段级溯源": {
    "source_id": "industry_report://gpu_market/amd_share/2026",
    "source_type": "pdf",
    "location": {
      "pdf": {
        "page": 12,
        "bbox": [120, 260, 520, 330]
      }
    },
    "raw_hash": "sha256:jkl012",
    "retrieval_score": 0.93,
    "parser_version": "pdf_v2.3"
  }
}
```

---

## 场景 5：投资组合与风险管理

- **投资人需求信息**：投资组合热力图、集中度、回撤、止损规则
- **举例**：

  - NVDA 持仓 20%
  - VaR 95% 1 天
- **信息溯源要求**：

  - **数据级溯源**：持仓比例、交易记录、成本价、价格来源、风险指标都需追溯到交易系统、组合管理系统或交易所数据。
  - **实时溯源验证**：价格变动即时更新；组合暴露、回撤、集中度按最新价格刷新。
  - **推理链溯源**：组合模拟 + 风险情景计算 + VaR 模型参数 + 止损规则触发逻辑。
  - **版本溯源**：若风控模型参数变更，需要保留模型版本和变更记录。

**JSON 模板：**

```JSON
{
  "片段级溯源": {
    "source_id": "portfolio_db://fund_alpha/positions/NVDA/2026-05-08",
    "source_type": "db",
    "location": {
      "db": {
        "table": "portfolio_positions",
        "primary_key": "fund_alpha|NVDA|2026-05-08"
      }
    },
    "raw_hash": "sha256:mno345",
    "retrieval_score": 0.98,
    "parser_version": "portfolio_db_parser_v1.1"
  }
}
```

---

## 场景 6：投资机会识别（赛道/新兴技术）

- **投资人需求信息**：高增长赛道、资本流入、创新项目
- **举例**：

  - World Labs Spark 2.0 融资 10 亿美元
  - 全球 AI 支出 2.52 万亿美元
- **信息溯源要求**：

  - **片段级溯源**：融资公告、公司博客、行业报告、投资机构披露、新闻稿可追溯。
  - **数据级溯源**：融资金额、投资方、估值、赛道分类、报告年份和币种需明确。
  - **实时溯源验证**：公告或行业报告修订后自动提示，新增融资事件触发更新。
  - **推理链溯源**：资本流入趋势 + 技术发布节奏 + 投资方结构 → 赛道机会判断。

**JSON 模板：**

```JSON
{
  "片段级溯源": {
    "source_id": "company_announcement://WorldLabs/Spark2.0/funding/2026",
    "source_type": "web",
    "location": {
      "url": "https://www.worldlabs.ai/blog/spark-2-0-funding-2026"
    },
    "raw_hash": "sha256:pqr678",
    "retrieval_score": 0.94,
    "parser_version": "web_parser_v1.2"
  }
}
```

---

## ~~场景 7：交易/价格监控~~

- **投资人需求信息**：股票价格、期权价格、交易量、波动率
- **举例**：

  - NVDA 当日价格 \$215.20
  - 52 周区间 \$97.28–\$212.19
- **信息溯源要求**：

  - **实时溯源验证**：交易所 API 拉取秒级或分钟级更新，显示最后更新时间，过期数据自动标红。
  - **数据级溯源**：价格、成交量、波动率、52 周区间需标注交易所、ticker、时间戳、币种。
  - **推理链溯源**：价格变化 → 市值计算；波动率变化 → 风险信号；成交量异常 → 流动性判断。
  - **原文/API 回显**：支持展示 API response 或行情源原始字段。

**JSON 模板：**

```JSON
{
  "片段级溯源": {
    "source_id": "exchange_api://NVDA/price/2026-05-08",
    "source_type": "api",
    "location": {
      "endpoint": "/v1/equity/price",
      "params": {
        "ticker": "NVDA",
        "fields": ["last_price", "volume", "volatility", "week_52_range"]
      },
      "timestamp": "2026-05-08T09:30:00Z"
    },
    "raw_hash": "sha256:stu901",
    "retrieval_score": 0.99,
    "parser_version": "market_price_api_parser_v1.5"
  }
}
```

---

## 场景 8：市场情绪监控

- **投资人需求信息**：投资者观点、社区分歧、情绪指数
- **举例**：

  - 社区对 AI 投资 Bullish/Bearish 分布
  - 分析师评级 33 看涨 / 1 中性
- **信息溯源要求**：

  - **片段级溯源**：原帖、评论、分析师报告、评级摘要都需要可追溯。
  - **聚合规则溯源**：情绪百分比需记录样本窗口、来源权重、分类规则、情绪模型版本。
  - **实时溯源验证**：帖子删除、评级更新、来源失效时需要提示。
  - **推理链溯源**：原始观点 → 情绪分类 → 权重计算 → Bullish/Bearish 分布。

**JSON 模板：**

```JSON
{
  "片段级溯源": {
    "source_id": "social_api://AI_investing/sentiment/2026-05-08",
    "source_type": "api",
    "location": {
      "endpoint": "/v1/social/sentiment",
      "params": {
        "topic": "AI investing",
        "window": "24h",
        "sources": ["x", "reddit", "analyst_reports"]
      },
      "timestamp": "2026-05-08T10:15:00Z"
    },
    "raw_hash": "sha256:vwx234",
    "retrieval_score": 0.91,
    "parser_version": "sentiment_parser_v2.0"
  }
}
```

---

## ~~场景 9：预测与概率分析~~

- **投资人需求信息**：市场概率预测、盈亏机会、潜在事件影响
- **举例**：

  - Kalshi 市场预测 \$196 / 51%，\$212 / 44%
  - 盈利超预期概率 30%
- **信息溯源要求**：

  - **数据级溯源**：预测平台原始数据、market id、盘口价格、成交量、样本量、数据截止时间必须保留。
  - **实时溯源验证**：预测概率随交易变化更新；过期 market 或低流动性 market 自动标注。
  - **推理链溯源**：预测价格 → implied probability → 事件情景 → 盈亏影响。
  - **来源类型标注**：明确该数据来自预测市场，不等同于公司指引或分析师预测。

**JSON 模板：**

```JSON
{
  "片段级溯源": {
    "source_id": "kalshi_api://markets/NVDA_PRICE_RANGE/2026-05-08",
    "source_type": "api",
    "location": {
      "endpoint": "/v1/prediction_market/odds",
      "params": {
        "platform": "Kalshi",
        "market_id": "NVDA_PRICE_RANGE_2026_05_08",
        "outcomes": ["196", "212"]
      },
      "timestamp": "2026-05-08T11:00:00Z"
    },
    "raw_hash": "sha256:yz5678",
    "retrieval_score": 0.92,
    "parser_version": "prediction_market_parser_v1.0"
  }
}
```

---

## 场景 10：投资决策晨会/汇总

- **投资人需求信息**：汇总重要财报、市场动态、趋势信号
- **举例**：

  - 昨日交易总览
  - 企业关键公告
  - 市场情绪摘要
- **信息溯源要求**：

  - **片段级溯源**：晨会摘要中的每条结论都必须对应原始报告、新闻、公告、行情或数据库记录。
  - **实时溯源验证**：股价、事件、公告、评级更新可即时追溯；过期数据标红。
  - **推理链溯源**：多源信息汇总 → 信号排序 → 结论生成 → 人工修改记录。
  - **版本溯源**：晨会稿生成时间、使用的数据快照、修改人、修改 diff 需要保存。

**JSON 模板：**

```JSON
{
  "片段级溯源": {
    "source_id": "briefing_pipeline://daily_morning/2026-05-08/NVDA",
    "source_type": "db",
    "location": {
      "db": {
        "table": "morning_brief_fragments",
        "primary_key": "2026-05-08|NVDA|market_summary"
      }
    },
    "raw_hash": "sha256:briefing890",
    "retrieval_score": 0.94,
    "parser_version": "briefing_parser_v1.0"
  }
}
```

### News

#### ① 英伟达 2026 年 AI 股权投资承诺突破 400 亿美元

英伟达在 2026 年前五个月显著加快投资节奏，总额已超 400 亿美元。其中最核心的动作包括： 向 **OpenAI 注入 300 亿美元，**与数据中心运营商 **IREN 达成 21 亿美元战略投资协议，**向光学组件商 **Corning 投资 32 亿美元 一个引用按钮查看引用：`eweek.com` `letsdatascience.com` `Web`：公司公开披露 / 媒体报道汇总**

#### ② 英伟达股价创下 217.80 美元历史新高

受与 IREN 达成大规模数据中心合作及强劲财报指引驱动，英伟达股价在 5 月 8 日触及历史高点，市值突破 5.2 万亿美元，创下自去年 10 月以来最大单周涨幅。







<sheet sheet-id="CyMR4F" token="VqAyshokph3pCXtphOaji4PFpue"></sheet>