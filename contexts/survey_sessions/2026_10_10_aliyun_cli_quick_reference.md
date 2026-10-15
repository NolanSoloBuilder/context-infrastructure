# 阿里云 CLI 对应关系

核验日期：2026-10-10。用户询问阿里云是否有类似 Google CLI 的工具；Google CLI 的具体指代尚未明确。

## 对应关系

- 如果指 Google Cloud 的 `gcloud`，阿里云对应官方 Alibaba Cloud CLI，可执行文件名为 `aliyun`。官方文档列出 ECS、RDS、OSS、SLB、FC 等服务，适合终端操作和脚本自动化。
- 如果指 Gemini CLI 这样的终端 AI 编程工具，通义对应 Qwen Code，官方仓库为 `QwenLM/qwen-code`。
- 阿里云另提供网页版 Cloud Shell，预装阿里云 CLI，并使用当前登录身份配置凭证。

## macOS 入口

官方推荐通过 Homebrew 安装云资源管理 CLI：

```sh
brew install aliyun-cli
aliyun version
aliyun --help
```

管理账户资源前需配置有相应权限的访问凭证。

## 本机安装结果

用户随后授权安装。已通过 Homebrew 全局安装 `aliyun-cli 3.5.1`，命令路径为 `/opt/homebrew/bin/aliyun`。已验证 `aliyun version`、`aliyun configure --help` 及 Homebrew 安装记录。

安装前本机没有 `~/.aliyun/config.json`，也没有相关凭证环境变量。曾启动 `aliyun configure --mode OAuth --profile personal` 并选择中国站，抵达官方应用管理员授权页，未提交授权。

随后「部署」会话通知接手认证；已通过只读读取该会话核实用户要求其在安装完成后负责认证。因此已终止本会话的独立 OAuth 进程并关闭本会话创建的登录标签，避免并发修改配置。认证与目标 ECS 验证由该会话继续，本安装会话未配置 AccessKey、修改云账号权限或操作服务器。

官方推荐本地使用 OAuth。首次使用前需在 RAM 控制台安装 `official-cli` 官方 OAuth 应用，并为使用的 RAM 用户或角色分配允许身份。认证后可用 `aliyun sts GetCallerIdentity` 验证账户身份，再按服务器地域查询实例。

## 官方来源

- [什么是阿里云 CLI](https://help.aliyun.com/zh/cli/what-is-alibaba-cloud-cli)
- [安装与更新阿里云 CLI](https://help.aliyun.com/zh/cli/install-update-alibaba-cloud-cli)
- [使用阿里云云命令行](https://help.aliyun.com/zh/document_detail/2365794.html)
- [Qwen Code 官方仓库](https://github.com/QwenLM/qwen-code)
- [阿里云 CLI OAuth 凭证](https://help.aliyun.com/zh/cli/oauth-credentials)
