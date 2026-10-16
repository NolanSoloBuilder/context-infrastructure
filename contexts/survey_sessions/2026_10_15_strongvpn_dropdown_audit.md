# StrongVPN 下载页下拉框与请求核对

2026-10-15，按用户要求重新核对两个下载页的真实下拉框和浏览器请求。未填写账号密码、未点击下载/二维码生成、未发送配置生成 POST，未变更现有配置或 VPS。

## 结论

| 页面 | 可选服务器 option | 国家/地区 optgroup | 与现有目录解析的 ID 集合 |
| --- | --- | --- | --- |
| [tools.strongvpn.asia](https://tools.strongvpn.asia/share/strong-wg/strong-wg.html) | 53 | 34 | 完全一致，无额外 ID |
| [tools.strongtech.org](https://tools.strongtech.org/share/strong-wg/strong-wg.html) | 53 | 34 | 完全一致，无额外 ID |

两个页面的下拉框均为 `select#serverSelect`，另有一个禁用的“Select a server”占位项，不计入 53。两个镜像当前选项 ID 与顺序一致，页面及节点模块的内容哈希也一致。日本组有两个选项：`str-nrt301`、`str-nrt302`。

上次的 **47 是生成成功数量，不是网页可选数量**。原导出报告为 53 个目标、47 成功、6 失败；53 个原目标目前都能在实际下拉框找到，没有发现由映射表额外加入的目标。

下拉框是公开的可选服务器目录，不是账户已经保存或当前仍有效的配置列表。它在未填写凭据时已完整渲染；不能把 53 个目录选项、47 次成功生成或后续 12 份连接通过混为一个数量。生成全部目录与复用既有配置的影响不同。

## 实际抓到的请求与页面构造

浏览器分别打开两个真实 HTTPS 页面，并观察加载请求：

```text
GET /share/strong-wg/strong-wg.html
GET /share/strong-wg/servers.js
```

主镜像的页面、节点模块均观察到 HTTP 200；备用镜像同样观察到节点模块请求及其下拉框渲染。其余请求为 logo、第三方静态依赖等，不参与账户节点授权。

页面的 module 脚本实际引用 `import { servers, serverMapping } from './servers.js'`。`renderServers()` 遍历 `servers` 的国家键和每个国家的条目，创建 optgroup 与 option；`serverMapping` 为已列出的 ID 提供 IP，不能把仅存在于映射表的 ID 当作可选节点。本次渲染代码未按账号筛选目录。

下载按钮的生成逻辑从 `serverSelect.value` 取一个选中 ID，然后构造 `POST /wg-generate`，JSON 字段是 `aiouser`、`aiopass`、`server`、`publickey`。此 POST 结构来自当前页面源码核对，**本次没有实际发出生成请求**，避免注册新公钥。

## 后续执行合同

1. 页面下拉框的真实可选项为候选集合；排除占位项、disabled/hidden 项和禁用组。
2. CLI 从当前页面实际 module import 定位目录，不假设永远叫 `servers.js`，不执行远程代码。读取一个镜像的完整页面及目录，不能把两个镜像合并扩大集合。
3. 页面或脚本结构改变、目录与下拉框不一致，或计划遍历全目录时，先取得真实 DOM option 列表逐项核对；未核对清楚不调用生成接口。
4. **可选集合不等于本次下载目标**。目标还必须符合用户明确指定的节点/地区；普通订阅维护继承当前统一订阅选定的集合，不默认遍历全部 53 个选项。仅用户明确要求全量时才处理所有可选项，并说明新生成可能影响旧配置。
5. 报告分别记录可选数、目标数、尝试数、生成成功数、失败数、最终连接通过数，不能只写“下载了多少节点”。
6. 当前统一订阅仍保留原来 12 份配置，本次核查没有重新下载或调整它们。

核查还发现当前解析器只剥除整行 `//` 注释，对块注释和行尾注释存在误计旧项的通用风险。该风险有离线复现，但本次真实目录与 DOM 一致，**不能把它写成本次 47 的原因**；对应修复和回归用于防止后续页面变更引入误计。

已完成代码修正：读取网页实际 module import，并验证来源同源 HTTPS；不再直接猜测 `servers.js`。注释扫描保留字符串中的内容，剥离行尾/块注释并拒绝未闭合注释；缺少下拉框、引用歧义等未知格式停止读取。CLI JSON 增加 `pageUrl` 和 `catalogUrl` 便于下次审计。36 项定向 Node 测试通过，真实只读 CLI 仍得到 53 节点/34 国家，两镜像公开快照与 DOM 均逐项一致。

## 证据位置

公开页面和脱敏网络元数据保存在 [`output/strongvpn_catalog_audit/`](../../output/strongvpn_catalog_audit/)：

- `strongvpn-page.html`、`strongtech-page.html`：当次公开页面源码。
- `strongvpn-servers.js`、`strongtech-servers.js`：页面实际使用的公开目录模块。
- `strongvpn-dropdown.json`、`strongtech-dropdown.json`：真实 DOM 中的可选 ID、标签、国家。
- `strongvpn-network.json`、`strongtech-network.json`：请求方法/URL 和响应状态；不包含请求头、Cookie 或凭据。
- `summary.json`：抓取时间、哈希、数量、镜像与历史目标集合核对结果。

目录模块 SHA-256：`4cb50c9cd01e10fbb8a8e498adc661311c949a9660d22b1d6b82f9ecf30454a5`。这是当次证据，不是未来目录的固定哈希。
