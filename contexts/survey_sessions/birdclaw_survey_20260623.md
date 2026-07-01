# birdclaw 项目调研备忘录

日期：2026-06-23

调研对象：[birdclaw.sh](https://birdclaw.sh/) / [steipete/birdclaw](https://github.com/steipete/birdclaw)

## 结论

birdclaw 是一个 local-first Twitter/X 个人数据工作台。它不是单纯的 archive search CLI，而是把 X archive import、live sync、本地 SQLite/FTS5、Web UI、CLI、AI inbox/digest、reply/moderation、Git-friendly backup 做到同一个本地应用里。对“把个人社交数据变成 agent 可查询、可操作的本地 memory”这个方向，它很贴近需求。

我的判断是：可以试，但应该按个人工具 / early adopter 工具对待。它已经不是空壳，release、CI、测试、第三方 PR 都说明项目可用性在快速提升；同时它也明确处在 WIP 状态，仍有 schema churn、transport gaps 和个人化 prompt 这类边界。短期适合作为本地 archive/search/agent tooling 试验，不适合作为需要长期稳定 API 的基础设施直接依赖。

## 它解决什么问题

X 自带 archive 很难检索，也很难被 agent 使用。birdclaw 的核心做法是先把个人 X 数据落到本地 SQLite，再在上面提供三层能力：

第一层是数据归档。它能导入 Twitter/X archive，并把 tweets、DMs、likes、bookmarks、mentions、followers/following、blocks/mutes 等放进一个本地数据库。官网首页描述的是一个 “local-first Twitter workspace”，并列出 SQLite、FTS5、多账号、archive-first、live-aware 等能力：[birdclaw.sh](https://birdclaw.sh/)。

第二层是操作界面。它同时提供 CLI 和本地 Web app。CLI spec 里有 `search`, `sync`, `mentions`, `dms`, `inbox`, `compose`, `blocks`, `graph`, `backup`, `serve` 等命令树，并强调 `--json` 输出、stderr diagnostics 和 TTY prompts 分离：[CLI Spec](https://birdclaw.sh/cli.html)。

第三层是 agent/AI workflow。它能给 inbox 做 OpenAI scoring，也能生成 “what happened” digest。这个能力有价值，但目前源码里还保留作者个人场景，比如 inbox scoring 的 system prompt 直接写了 Peter Steinberger，digest prompt 也会判断 Peter 是否已参与 conversation。因此它的 AI 层还不是完全通用产品。

## 当前成熟度

项目活跃度高。GitHub API 在 2026-06-23 检索到 repo 约 1.1k stars、100 forks、442 commits、open issues 1。npm latest 是 `birdclaw@0.8.5`，发布时间是 2026-06-21；从 `0.1.0` 到 `0.8.5` 只有约两个月，说明项目推进很快。

最新 release [Birdclaw 0.8.5](https://github.com/steipete/birdclaw/releases/tag/v0.8.5) 不是只发 tag：release notes 里给了 npm package、tarball integrity、CI run，并声明 141 个 test files、1,173 个 tests、90.83% line coverage、12 个 Playwright E2E。对应 [CI run 27920819997](https://github.com/steipete/birdclaw/actions/runs/27920819997) 是 success，耗时约 2m29s。

源码静态检查也支持这个判断：`src` 下有 355 个文件，测试文件 141 个；CI workflow 跑 `pnpm check`、coverage、build 和 Playwright。`package.json` 当前发布 compiled CLI/server/client artifact，说明 0.8.4 以后已经在改善安装包形态。

不过它自己也承认还没稳定。README/官网写明 “real and usable, not finished”，并提示 schema churn、transport gaps 和 rough edges。这个表述和代码状态一致。

## 架构形态

运行时是 TypeScript / Node / React / TanStack Start / Effect / SQLite。项目要求 Node `>=25.8.1 <27`，安装文档也写了 Node 25.8.1 或 Node 26.x：[Install](https://birdclaw.sh/install.html)。这会带来试用门槛，因为不少机器还在 Node 22/24/25.2 这类版本。

数据默认放在 `~/.birdclaw`，主库是 `~/.birdclaw/birdclaw.sqlite`，media/avatar cache 也在这个目录下。`src/lib/db.ts` 里能看到一套比较完整的 SQLite schema，覆盖 account、profile、tweet、tweet collection/edge、DM conversation/message、blocks、mutes、AI scores、sync cache、URL expansion 等表。docs 的 [Data And Architecture](https://birdclaw.sh/data-architecture.html) 也说明核心 I/O 正在迁到 Effect，CLI/React/route 边界保留 Promise wrapper。

live 数据不由 birdclaw 自己直接登录 X。它委托两个外部 CLI：[xurl](https://github.com/xdevplatform/xurl) 走官方 X API，[bird](https://github.com/steipete/bird) 走浏览器 cookie-backed web API。官方 [Sign in](https://birdclaw.sh/auth.html) 文档强调：新数据库先导入 X archive，用 archive 建立 account identity；`auth status` 只验证 transport，不会把数据库绑定到认证账号。

## 主要能力

最值得看的能力不是单点，而是组合：

archive import 能从 X archive 建立本地基线。Quickstart 里要求先 `birdclaw init`，再 `birdclaw archive find` / `birdclaw import archive`，之后再做 live sync：[Quickstart](https://birdclaw.sh/quickstart.html)。

sync 能拉 authored tweets、likes、bookmarks、timeline、mentions、mention threads、followers/following、DMs，并把结果写回同一个 canonical store。[Sync docs](https://birdclaw.sh/sync.html) 里明确了缓存、cursor、rate-limit、partial exit code 等设计。

search 是本地 FTS5 路线。它覆盖 tweets/DMs，并支持 liked/bookmarked/quality filters。对 agent 来说，关键是它能稳定输出 JSON。

inbox 把 mentions 和 DMs 做统一 triage。默认 heuristic 排序；加 `--score` 后调用 OpenAI 做 actionability scoring。文档也保留了边界提醒：OpenAI scoring 是 overlay，不是最终判断：[Inbox](https://birdclaw.sh/inbox.html)。

backup 把 SQLite 的长期记录导出为 deterministic JSONL shards，可以 Git diff/merge/sync。这个设计对跨机器和 agent memory 很有价值，但也意味着 DMs、likes、profiles、follow graph 等会以明文 JSONL 形式进入 backup repo：[Backup](https://birdclaw.sh/backup.html)。

moderation / compose 让它从只读 archive 工具变成 operator console。可以 reply、post、block/mute，并有 `BIRDCLAW_DISABLE_LIVE_WRITES=1` 用于开发/干跑。

## 风险和边界

第一是 X transport 的不确定性。birdclaw 的 live 能力依赖 `xurl` 和 `bird`。`xurl` 依赖 X developer app / OAuth2；`bird` 读取浏览器 cookie。X API、GraphQL、rate limit、cookie 访问策略都可能变。这里不是 birdclaw 独有问题，而是整个 Twitter/X tooling 的现实约束。

第二是个人工具痕迹。源码里有硬编码 Peter 的 AI prompt；默认 demo/test data 也大量围绕 `@steipete`。如果只做 archive import/search，影响较小；如果依赖 AI inbox/digest，排序和摘要语义会偏作者本人。

第三是版本和 schema churn。release 很密集，且 0.8.x 仍在改 SQLite writer、schema migration、backup codec、compiled package、query plan。对个人工具是好事，对外部依赖是风险。现在更适合用 CLI/JSON 做薄集成，少直接依赖内部 DB schema。

第四是隐私。它是 local-first，但 local-first 不等于自动安全。`bird` 会读取 X browser cookies；backup sync 会把私人数据写成 Git repo；local web 默认无 app-level auth，但生产 server 默认只信 loopback，远程需要 `BIRDCLAW_ALLOW_REMOTE_WEB=1` 或 `BIRDCLAW_WEB_TOKEN`。实际使用时 backup repo 必须私有，且不要把 `~/.birdclaw`、backup JSONL 或 cookies 暴露给普通同步工具。

第五是环境门槛。当前 npm package 需要 Node `>=25.8.1 <27`。我没有在本机运行 birdclaw，因为当前 Node 是 `v25.2.1`，低于要求。

## 同类项目位置

和 [dogsheep/twitter-to-sqlite](https://github.com/dogsheep/twitter-to-sqlite) 比，birdclaw 更现代也更产品化。`twitter-to-sqlite` 是经典 SQLite 导入工具，但 README 仍说明它使用 Twitter API v1，且 [issue #54](https://github.com/dogsheep/twitter-to-sqlite/issues/54) 记录过新 archive export 结构导致导入失效。

和 [DocNow/twarc](https://github.com/DocNow/twarc) 比，birdclaw 不是学术/公共数据归档工具。twarc README 明确说 Twitter API quota 变化后已不再 active supported；birdclaw 的方向是个人本地 workspace。

和 [xf](https://github.com/Dicklesworthstone/xf) 比，birdclaw 更重。xf 聚焦 ultra-fast archive search，Rust/Tantivy/SQLite，支持 keyword/semantic/hybrid search；birdclaw 则把 search、sync、web UI、reply、moderation、AI digest 都装进来。

和 [tweetxvault](https://github.com/lhl/tweetxvault) 比，二者最接近。tweetxvault 支持 official archive import、browser cookie extraction、crash-safe resume、FTS/semantic search；birdclaw 的差异是本地 Web workspace、compose/moderation、OpenAI inbox/digest 和 Git-friendly backup 更成体系。

## 对你的适用建议

如果你的目标是给 agent 一个本地 Twitter/X memory substrate，birdclaw 值得试。它的设计很贴近“个人数据进 SQLite，CLI 提供稳定 JSON，agent 按需查询和操作”的路径。尤其是 archive import + local search + backup，这三件事对长期个人知识工作很有价值。

试用路径建议保守一点：

1. 先只做 archive-only，不接 `bird` / `xurl` / OpenAI。
2. 用一个新的 `BIRDCLAW_HOME`，避免污染默认 `~/.birdclaw`。
3. 导入 X archive，验证 `db stats`、`search tweets`、`search dms`。
4. 再考虑 `backup export` 到本地私有目录，不先 `backup sync --remote`。
5. 最后再接 live sync，且先跑小 limit / dry-run 路径。

目前我会把它归类为“值得跟踪和轻量试用”的项目，而不是马上深度依赖的基础组件。它的方向对，但仍需要看两件事：X live transport 是否能长期维持，AI prompt/config 是否会从作者个人场景抽象成可配置的通用层。

## 可复现实验建议

如果下一步要真正评估可用性，我建议做一个 30 分钟 smoke：

```bash
export BIRDCLAW_HOME="$HOME/.birdclaw-smoke"
birdclaw init
birdclaw import archive ~/Downloads/twitter-archive.zip --select tweets,likes,bookmarks,directMessages --json
birdclaw db stats --json
birdclaw search tweets "local-first" --json
birdclaw search dms "meeting" --json
birdclaw backup export --repo ~/Projects/birdclaw-smoke-backup --json
birdclaw serve
```

验收标准是：archive import 能完成；DB stats 数量符合预期；search 能返回可读 tweet/DM；backup validate 通过；Web UI 能在本地打开 Home/Likes/Bookmarks/DMs；整个过程不需要 live X credential。

这个 smoke 需要先把 Node 升到项目要求的 `>=25.8.1 <27`，或者用 `fnm`/`nvm` 单独切一个 Node 26 环境。

