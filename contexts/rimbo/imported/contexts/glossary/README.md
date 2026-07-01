# glossary/

术语表与命名约定。多人协作下的硬刚需——不写下来，每个人嘴里的"用户"、"信源"、"feed"指向不同对象。

## 文件组织

```
glossary/
├── README.md              # 本文件
├── domain_terms.md        # 业务领域术语(用户、信源、feed、内容、tag…)
├── tech_terms.md          # 技术名词(capability、observation、reflector…)
└── naming_conventions.md  # 命名约定(分支命名、文件命名、frontmatter 字段)
```

## 条目格式

```markdown
### <术语>

**定义**: 一句话定义,精确到边界。

**正例**: 哪些情形指这个概念。

**反例 / 易混**: 容易和哪个概念混淆,区别在哪。

**首次出现**: contexts/products/<x>/prd/v1.md (可选,溯源用)
```

## AI 使用

AI 写文档 / 回复消息 / 起 PR 描述时,术语表里出现过的词必须用团队定义,不用通用定义。如果使用了不在术语表中的关键词,在 PR 描述里提议补充。
