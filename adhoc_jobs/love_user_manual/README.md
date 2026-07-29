# 关系说明书

一个移动端优先的关系反应自我观察网页。24 个场景分别观察恢复方式、表达节奏、信息偏好与重启方式，生成连续结果、完整说明书和可保存分享卡。

## 本地运行

```bash
npm install
npm run dev
```

默认地址：`http://127.0.0.1:4173`

## 构建与验证

```bash
npm test
npm run build
npm run content
npm run assets
```

生成内容：

- `content/xhs_posts_v02.md`：10 篇完整小红书发布稿。
- `content/questionnaire_v02.md`：24 题可读题库。
- `content/result_library_v02.md`：8 个结果入口完整文案。
- `content/xhs_content_check_v02.md`：10 篇发布前检查。
- `public/covers/`：10 张 1080×1440 封面。
- `public/share_cards/`：8 张 1080×1440 结果卡样张。
- `public/concepts/`：开始、答题和结果三种设计概念。

## 产品边界

- 这是自我观察工具，不是经过信效度验证的心理测验。
- 不输出依恋诊断、人格定性、伴侣匹配或关系去留建议。
- 不收集姓名、手机号、生日或伴侣信息；答题进度只保存在本机浏览器。
- 暴力、威胁、跟踪和强迫控制不适用普通沟通建议。
