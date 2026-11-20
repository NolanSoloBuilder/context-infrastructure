# 清言字舍

基于 2026-11-17 的 [原站 H5](https://h5.qingzhuzishe.com/) 前端快照。保留原有主要页面与操作流程，起名、测评、工具、历史、收藏、资料包和报告使用独立后端，所有自助功能免费开放。

## 运行

需要 Node.js 22.13 或更新版本。安装三个全局依赖后，从本目录启动服务。

```sh
npm install -g lunar-javascript@1.7.7 pinyin-pro@3.28.0 pdfkit@0.17.2
node server.mjs
```

打开 [本地首页](http://127.0.0.1:4175/) 或 [起小名](http://127.0.0.1:4175/nickname/form)。浏览器首次打开会创建本地设备会话。历史、收藏及旧订单记录保存在 `.local/bazi.sqlite` 和 `.local/site.sqlite`。可用 `QINGZHU_BAZI_DB`、`QINGZHU_LOCAL_DB` 指定文件。PDF 按本机可用的中文字体生成，系统没有适用字体时可用 `QINGZHU_PDF_FONT` 指定文件，字体集合可额外设 `QINGZHU_PDF_FONT_FAMILY`。

## 功能和数据

- 八字起名沿用本地排盘、喜用字和完整姓名流程。128 组原站样本覆盖基础计算和强弱评分，结果记录见 [验收记录](VERIFICATION.md)。
- 诗词起名使用本地古籍候选和原站公开用字。AI 起名使用 Vercel AI Gateway 的 `openai/gpt-6.2-sol`，保留原页面的逐批进度、结果与详情。后端先用本地规则筛选合法用字和可核对出处，再让大模型选择姓名、排序并撰写推荐理由和使用提醒。诗词语料使用固定版本的 [chinese-poetry](https://github.com/chinese-poetry/chinese-poetry/tree/b8594f81a89752241442f2ce267d6f66f96704ee)，许可随数据一起保存。
- 起小名可按 29 类风格推荐、换一批和看详情。英文名支持风格、性别、拼音首字母匹配、搜索和详情。美国流行度取自 [SSA 2020–2025 数据](https://www.ssa.gov/oact/babynames/decades/names2020s.html)，词源词义来自本地精选数据。外文用户中文名支持选择姓氏、意象和发音难度。
- 姓名测评、常用字和古籍字典、百家姓、黄历、生肖星座、五格、精品名库和父母姓氏起名在本机运行。工具使用公开快照以及有许可的字典，部分传统评分和解释采用本地规则。
- 本地账号可查看历史、收藏、资料及报告，资料和中文 PDF 可下载。使用本地设备会话。旧会员、优惠和结算入口已停用。付费原站姓名库和会员数据由原站持有，本地数据的规模、分数和排名会不同。

已有兼容服务时仍可用源地址启动联调模式，例如 `PORT=4176 QINGZHU_API_ORIGIN=http://127.0.0.1:8000 node server.mjs`。该模式使用指定后端的数据及账号接口。

## 验证

```sh
node --test test/*.test.mjs
# 启动服务后，使用全局 Playwright 和系统 Chrome
CHROME_CHANNEL=chrome node test/browser-smoke.cjs
CHROME_CHANNEL=chrome node test/site-smoke.cjs
```

`PLAYWRIGHT_MODULE` 可指定 Playwright 模块的绝对路径，`BASE_URL` 可指定测试服务端口。刷新数据有独立导入脚本，日常运行和测试使用已保存的数据。旧版本的 UI 入线补丁保留在 `patch-snapshot.cjs`、`scripts/wire-local-bazi.py`、`scripts/wire-local-site.py`。

## 生产环境

[清言字舍](https://qingyan.forgepane.com/) 的前端和 API 运行在香港 VPS，通过独立 Cloudflare Tunnel 提供 HTTPS。Docker Compose 配置在 `deploy/vps/compose.yaml`。VPS 上的当前发布位于 `/opt/qingyan/current`，只在 `127.0.0.1:14175` 监听。SQLite 数据独立持久化在 `/var/lib/qingyan`，生产环境从空数据库开始。服务端环境变量和 Tunnel 配置保存在 VPS 的 `/etc/qingyan`。

```sh
cd /opt/qingyan/current
docker compose -f deploy/vps/compose.yaml ps
curl -fsS http://127.0.0.1:14175/healthz
curl -fsS https://qingyan.forgepane.com/healthz
```

所有自助工具免费。公网 AI 起名按 UTC 自然日计算，当前额度为每 IP 每天 50 次、全站每天 100 次，同时最多执行 2 个生成请求。每日额度通过 VPS 服务端环境变量配置。

## AI Gateway

服务端通过 `AI_GATEWAY_API_KEY` 或 `VERCEL_OIDC_TOKEN` 鉴权。用已有凭据管理器把变量注入 `node server.mjs` 后即可生成。密钥由服务端读取，避免放进前端资源、命令参数或提交文件。模型固定为用户确认的 `openai/gpt-6.2-sol`。2026-11-18 的实时模型目录尚未列出 GPT 6.5 Sol。

生成请求会把本次输入的姓氏、性别、出生信息（有填写时）、固定字、偏好和合法候选发往 Vercel Gateway。模型返回逐行 JSON 后，后端核验姓名是否属于候选池、是否重复、评分是否降序、推荐理由是否完整，按 5 个姓名一批写回原页面。未知生日不会补造生日。出处由字库保留。模型的推断、理由和分数用于选名参考，姓名列表按模型原始顺序展示。

网络失败、余额不足、截断和非法候选会显示错误。已验证的部分结果按会话保存，记录 `generation.status` 和实际模型。原有规则生成的历史仍可打开。缺少 Gateway 凭据时 AI 生成会明确报告配置问题。

`scripts/compare-ai-naming.mjs` 可将实测保存的流事件与本机已有的匿名原站样本对照，输出位于 `.local/ai-model-comparison.json`。原站完整出生信息与全部偏好没有保存，样本只支持有限比较。

`node scripts/replay-ai-naming.mjs <样本 JSON> <报告 JSON>` 可批量复放 AI 起名请求。样本文件为数组，每条包含 `id`、生成请求 `input`、`inputStatus` 和 `original.names`（原站两字名，按原顺序排列）。输入字段有缺失时用 `inputStatus: "partial"` 和 `missing` 记录。脚本使用内存数据库，依次读取流式候选及详情。
