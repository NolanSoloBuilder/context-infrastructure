# Codex 全局 Cowork Skills 安装

2026-09-21，按用户提供的 Codewiz 下载链接安装到当前 Codex 全局目录。

- `cowork-publish`：`/Users/xuhao/.codex/skills/cowork-publish`。链接请求版本 `2.0.13`，实际返回的 `SKILL.md` 声明版本 `2.2.3`，保留下载包原始内容。
- `cowork-xhs-sso`：`/Users/xuhao/.codex/skills/cowork-xhs-sso`。链接请求版本 `1.0.1`，包内未声明版本。
- 两个包分别有 145、2 个条目；安装时检查路径越界、符号链接，并逐文件核对归档内容。Python 与 SSO Shell 通过静态语法检查，未执行登录或发布。
- 各安装目录 `.installation-source.json` 记录来源路径、请求版本和归档 SHA-256。
- 本次为全局安装，不向项目 `.agents/skills` 引入公司专用 Skill，不修改项目外部 Skills 注册表。
