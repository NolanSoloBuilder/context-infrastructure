# CodeWiz 通过 Cockpit Tools 多开 Codex

2026-09-21 只读核验：本机 Cockpit Tools 版本为 1.3.57。`/Users/xuhao/Documents/Other/codewiz-proxy` 正在监听 `127.0.0.1:9960`；本次 `/health`、带本地 key 的 `/v1/models` 均返回 200，GPT 模型 ID 为 `gpt-5.6-terra`、`gpt-5.6-luna`。

可行路径：在 Cockpit 的模型供应商中添加 CodeWiz 本地代理，Base URL 为 `http://127.0.0.1:9960/v1`，协议为 OpenAI Responses，API Key 使用 `/Users/xuhao/.config/codewiz-proxy/apikey` 的现有值。新建独立 Codex 多开实例并绑定供应商，避免修改当前默认实例。建议先用 `gpt-5.6-luna`。

依据：Cockpit 官方 README 明确支持 Codex 多实例和独立目录；本地源码 `adhoc_jobs/tmp_cockpit_tools_audit/src-tauri/src/modules/codex_instance.rs` 包含按 Codex home 派生 macOS 用户数据目录的实现，`crates/cockpit-core/src/modules/codex_account.rs` 使用 Responses 协议。官方来源：https://github.com/jlcodes99/cockpit-tools/blob/main/README.md 。

代理项目的 `docs/local-verification-2026-09-20.md` 记录了 luna Responses SSE 文本与完成事件验证通过，该结果为前一天记录。本次仅刷新健康状态和模型列表，没有重新生成文本，也未实际创建、启动第二个 Codex；工具调用、多轮续接和第二实例桌面验收仍待执行。消费走 CodeWiz 上游；多开不会额外产生模型额度。
