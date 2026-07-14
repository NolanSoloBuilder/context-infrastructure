# GitHub API 直连故障修复

## 症状

Codex 一度提示 GitHub CLI 不可用。WireGuard 开启时 GitHub 网页和 CLI 正常；关闭 WireGuard 后，GitHub 主站可访问，但 `api.github.com:443` 超时，导致 GitHub 页面部分能力和 `gh` API 不可用。

## 原因

关闭 WireGuard 后，系统 DNS 将 `api.github.com` 解析到 `20.205.243.168`。该地址在当前网络不可达；同一网络下 `140.82.121.6` 可以正常建立 TLS 并返回 HTTP 200。WireGuard 开启时默认路由和 DNS 均由隧道接管，因此掩盖了直连节点故障。

## 处理

在 `/etc/hosts` 增加以下映射，并刷新 macOS DNS 缓存：

```text
140.82.121.6 api.github.com
```

## 验证

保持 WireGuard 关闭，依次验证：

- `dscacheutil` 将 `api.github.com` 解析到 `140.82.121.6`。
- `curl https://api.github.com` 返回 HTTP 200。
- `gh auth status`、`gh api rate_limit` 和 `gh repo view` 正常。
- Chrome 可完整打开 GitHub 仓库页，控制台无加载错误。

## 后续规则

`/etc/hosts` 固定的是时点可用 IP，不是长期稳定的 GitHub 服务发现机制。如果该地址将来失效，应先重新测试多个 GitHub API 节点，再更新映射；不要把 CLI、登录态或浏览器缓存误判为根因。
