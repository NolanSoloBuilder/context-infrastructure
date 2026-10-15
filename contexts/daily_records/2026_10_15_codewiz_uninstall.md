# 独立 Codewiz 卸载

用户要求卸载 Codewiz，明确保留 opencode、codewiz-cc、Codex 客户端与运行中的任务。识别独立包为 @xhs/codewiz，与 @xhs/codewiz-cc 不同。

通过 npm uninstall --global --prefix <prefix> --ignore-scripts 卸载以下 4 份独立安装：

- /Users/xuhao/.local/share/fnm/node-versions/v20.19.4/installation
- /Users/xuhao/.local/share/fnm/node-versions/v18.19.1/installation
- /Users/xuhao/.local/share/fnm/node-versions/v22.22.0/installation
- /Users/xuhao/.local/share/fnm/node-versions/v18.20.1/installation

所有卸载命令退出码 0，目标 package.json 不再存在。对 opencode 入口、codewiz-cc package.json 与客户端内置 Codex 二进制的前后指纹核对一致。未发现独立 Codewiz 运行进程或关联 LaunchAgent；没有结束任何任务进程。保留 ~/.cc-mirror/codewiz-cc、用户配置、项目与历史记录。之前 tar 配置备份属于保留的 codewiz-cc，不能因卸载独立 Codewiz 而认定其机制已移除。
