# 小红书 RAG 原文归档

归档日期：2026-09-09。范围：指定 RAG 根目录及前一轮完整遍历的全部后代，共 22 个节点（根目录 + 21 个后代）。15 份有正文材料、7 个空正文节点（含根目录）。

## 保存内容

- `documents/<shortcut_id>/original.md`：接口返回的原文文本，不加摘要、不改写。
- `documents/<shortcut_id>/readable.md`：便于阅读的版本；本次与文本原文内容一致。
- `documents/<shortcut_id>/raw.json`：完整 webFetch 返回数据。
- `documents/<shortcut_id>/metadata.json`：标题、来源、获取时间、源 hash、图片数、SHA-256。
- `review_text_snapshot/`：前一轮调研实际读取的 21 个子节点文本，原样保留。
- `manifest.json`、`directory_tree.json`：归档清单和目录关系。

## 完整性与边界

22 个节点均读取成功，原始返回 SHA-256 已回读校验。本次接口返回图片块数量为 0，未生成图片文件；原文已有链接保持原样。归档属于 REDoc 接口图文内容快照，不包含页面 UI、评论、历史版本，也不扩展抓取文中引用的其他文档。

与前一轮已保存的正文逐字节比对：0 份发生变化。

## 原文目录

- [RAG](documents/58ab2642ea430526353832680db4fcc0/readable.md) · [来源](https://docs.xiaohongshu.com/doc/58ab2642ea430526353832680db4fcc0)
  - [Agentic RAG 架构设计文档](documents/8aff625d7aee65bfe5dae223a26c7ac6/readable.md) · [来源](https://docs.xiaohongshu.com/doc/8aff625d7aee65bfe5dae223a26c7ac6)
  - [法律领域 RAG - 常规 RAG对比](documents/2c6cbb3a673b5d7201c6c0af591b594a/readable.md) · [来源](https://docs.xiaohongshu.com/doc/2c6cbb3a673b5d7201c6c0af591b594a)
  - [RAG调研报告](documents/9732a926592ad7c14feddea5bdce71c4/readable.md) · [来源](https://docs.xiaohongshu.com/doc/9732a926592ad7c14feddea5bdce71c4)
  - [RAG技术选型](documents/6ef4df778fd1cc9b32cfa754fe2e0229/readable.md) · [来源](https://docs.xiaohongshu.com/doc/6ef4df778fd1cc9b32cfa754fe2e0229)
  - [RAG 评测指标](documents/11d967cd2743c384e370444ce31261af/readable.md) · [来源](https://docs.xiaohongshu.com/doc/11d967cd2743c384e370444ce31261af)
  - [合规/法规/新闻多源知识图谱设计与实施方案](documents/2e815bb94df53f2cf02ed10be62f9bbf/readable.md) · [来源](https://docs.xiaohongshu.com/doc/2e815bb94df53f2cf02ed10be62f9bbf)
  - [RAG问答](documents/6831cbdf8e2d8fed7bca347bc8e343a1/readable.md) · [来源](https://docs.xiaohongshu.com/doc/6831cbdf8e2d8fed7bca347bc8e343a1)
    - [画像知识库](documents/d0dd3de848c87e3269c30edc26f3bcf6/readable.md) · [来源](https://docs.xiaohongshu.com/doc/d0dd3de848c87e3269c30edc26f3bcf6)
      - [广告类型与数据利用程度](documents/38f00dc361ca8b338673efca29d74f0b/readable.md) · [来源](https://docs.xiaohongshu.com/doc/38f00dc361ca8b338673efca29d74f0b)
      - [rednote用户数据分类字典（DT）](documents/7a59e41d183d8f72a1248de54ae68cf5/readable.md) · [来源](https://docs.xiaohongshu.com/doc/7a59e41d183d8f72a1248de54ae68cf5)
    - [回答](documents/06ded8b13411bc80764f71ef59ab46bf/readable.md) · [来源](https://docs.xiaohongshu.com/doc/06ded8b13411bc80764f71ef59ab46bf)
      - [0615](documents/55e7c9ff2761e83bc2ff4a47cce843e0/readable.md) · [来源](https://docs.xiaohongshu.com/doc/55e7c9ff2761e83bc2ff4a47cce843e0)
        - [各国删除权法规梳理与客户端功能映射](documents/0a36cc1b6374b4d866a0b237ca7618cf/readable.md) · [来源](https://docs.xiaohongshu.com/doc/0a36cc1b6374b4d866a0b237ca7618cf)
        - [TikTok 云上传约定与 GDPR 数据最小化合规分析](documents/d85c46a0c9c89e8127da2e2ba81493b9/readable.md) · [来源](https://docs.xiaohongshu.com/doc/d85c46a0c9c89e8127da2e2ba81493b9)
        - [小红书画像知识库 — 画像用到的数据盘点 | 2026-06-15](documents/e201d5f8a852e8f8f9f20698cfcf86fc/readable.md) · [来源](https://docs.xiaohongshu.com/doc/e201d5f8a852e8f8f9f20698cfcf86fc)
        - [欧盟和美国隐私合规法律对麦克风/摄像头前端功能的设计要求](documents/bdb6ce28acfd560735f0c981051b50c6/readable.md) · [来源](https://docs.xiaohongshu.com/doc/bdb6ce28acfd560735f0c981051b50c6)
      - [0625](documents/43a403ee87c6094315c450f6f3c3cb50/readable.md) · [来源](https://docs.xiaohongshu.com/doc/43a403ee87c6094315c450f6f3c3cb50)
        - [欧盟与美国隐私合规法律中麦克风/摄像头前端功能设计要求](documents/a774b74c9fde9ae993c19e43fc1313c4/readable.md) · [来源](https://docs.xiaohongshu.com/doc/a774b74c9fde9ae993c19e43fc1313c4)
        - [欧盟与美国个性化广告及个性化推荐合规要求系统整理](documents/6184834c3ee40413d6348efca305e3d1/readable.md) · [来源](https://docs.xiaohongshu.com/doc/6184834c3ee40413d6348efca305e3d1)
      - [0630](documents/93c3fb9c45469e53363423a6ccc06e78/readable.md) · [来源](https://docs.xiaohongshu.com/doc/93c3fb9c45469e53363423a6ccc06e78)
    - [问题](documents/ba0ed4a6875f55c69f81f4a142adee3d/readable.md) · [来源](https://docs.xiaohongshu.com/doc/ba0ed4a6875f55c69f81f4a142adee3d)

## 配套分析

[RAG 目录评审与学习指南](../../survey_sessions/2026_09_09_rag_directory_review_and_learning_guide.md)
