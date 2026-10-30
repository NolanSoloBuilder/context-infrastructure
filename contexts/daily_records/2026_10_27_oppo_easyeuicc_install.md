# OPPO 安装 EasyEUICC

2026-10-27，通过已授权的 ADB 为 OPPO PFFM10（Android 15 / SDK 35）安装 EasyEUICC。

- 来源：用户指定 https://github.com/estkme-group/openeuicc 。该仓库 README 指向官方上游发布页。
- 官方包：https://gitea.angry.im/PeterCxy/OpenEUICC/releases/download/unpriv-v1.7.2/app-unpriv-release.apk
- `adb install -r` 返回 `Success`；包名 `im.angry.easyeuicc`，versionName `v1.7.2-unpriv`，versionCode `802`。
- 已启动应用，界面显示「此 eSIM 上还没有配置文件」。未下载、启用、删除任何运营商配置。
- 系统 features 未声明内置 eSIM 支持；不能仅凭这一点确定硬件是否具有 eUICC，也不能仅凭空列表文案证明后续配置下载和联网可用。

OpenEUICC 需要系统应用权限；普通安装采用同项目的 EasyEUICC。实际 eSIM 配置兼容性及联网尚未验证。

## Tello 配置下载与启用

- 用户指出 Chrome 中的 Tello「我的 SIM」页面及 Apex eSIM 卡飞书用户手册，继续执行配置安装。
- 手册说明该实体 eSIM 可通过 Android LPA 下载、启用配置后移到其他设备使用。
- EasyEUICC 下载向导读取到 SIM 0 可插拔 eUICC，剩余空间约 465.69 KiB。
- 手动输入受到当前中文输入法转换影响，未提交错误地址；改用项目文档定义的 `lpa:` Android Intent 预填，核对服务器正确后提交一次下载。
- 日志确认 Tello 服务器认证、获取配置包返回 HTTP 200；应用列表出现 Tello，随后启用成功，界面状态为「已启用」。系统 SIM 状态为 `LOADED,ABSENT`，SIM 运营商为 `tello`。
- 尚未证实注册移动网络、Wi-Fi Calling 或收发短信可用；未更改漫游、套餐、付款、号码或其他账户配置。Tello 网页向导未操作「完成设置」。
- 不在文档记录激活码、EID、ICCID 或电话号码。

## 验证码未到达的初步排查

用户反馈 Muse 注册验证码未收到，截图中的目标号码与 Tello 线路一致。

- 收件箱截至本轮只查到 13:29、13:45 两条运营商失败通知，内容均为 `Unable to send message - Message Blocking is active`，未发现注册验证码。该提示涉及发送阻断，不能直接用作入站短信被阻断的证据。
- 当前卡槽 0 SIM 已加载，系统显示通过 IWLAN 注册为 HOME/IN_SERVICE；国内蜂窝网络注册为 DENIED。IWLAN 注册本身仍不足以证实 IMS 短信端到端可用。
- Tello 账户设置：Text messages=On；已配置 Wi-Fi Calling E911 地址；International Roaming=Off。未修改这些设置。
- 下一项有判别力的验证：从另一号码发送一条普通短信到 Tello。若普通短信可到，再排查 Muse 的发送或验证通道；若普通短信也不到，再聚焦 Tello/IMS 入站短信链路。
- 未向任何号码发送测试短信，未重复触发验证码，未开启付费漫游。

## 免费测试短信尝试

用户明确授权向自己的 Tello 号码发送免费测试短信。调用 Textbelt 官方 `/text` 接口一次，使用免费 `textbelt` key，返回 `success=false`，原因为 `Sorry, free SMS are disabled for this country due to abuse.`，未产生成功发送记录。

其他入口：Globfone 官方页面要求账户及可能的额外验证；Interpage 需目标号码主动拨打美国测试电话，不适合当前无语音分钟的方案。aFreeSMS 页面在内置浏览器因 DNS 解析失败无法打开；FoxText 导航超时，未提交号码或发送表单。未付费、未注册新账号。免费通道未成功发送，因此不能据此判断 Tello 入站短信是否正常。

## 用户澄清的最终目标

用户明确目标为通过原生 Wi-Fi Calling 收发 Tello 短信。后续应以纯 Wi-Fi 下原生短信的入站、出站成功为验收；My Tello App 登录与第三方免费发送网站均不能替代该验收。原生收发发生在插入并启用 Apex/Tello 卡、且支持运营商 Wi-Fi Calling 的设备上。当前已确认的范围仍是配置已启用、IWLAN 网络注册及账户 Text messages=On，尚未完成双向短信测试。

## 纯 Wi-Fi 短信收发验证成功

用户明确授权通过 ADB 开启飞行模式、恢复 Wi-Fi 并测试短信收发。

- 初始飞行模式关闭、Wi-Fi 开启；执行 `cmd connectivity airplane-mode enable` 和 `cmd wifi set-wifi-enabled enabled`。原保存 Wi-Fi 自动恢复连接。
- 飞行模式保持开启，卡槽 0 注册为 IWLAN HOME，语音和数据均 IN_SERVICE，蜂窝注册 UNKNOWN；IMS SMS 日志确认 `up=true, reg=true, cap=true`。
- 15:54 向本机 Tello 号码发送一次 `WiFi SMS test T27B`，UI 显示已发送；IMS `onSendSmsResult ... status=1 reason=0`。未观察到自发短信回收，故未以此证明入站成功。
- 根据 Tello 官方帮助 https://tello.com/help_center/balance/where-can-i-check-my-service-balances ，15:55 向 `800` 发送一次 `BALANCE`，UI 与 IMS 均显示发送成功；随后收件箱出现 Tello 套餐余额回复，内容为无限短信、2 GB 数据及有效期。
- 由此完成纯 Wi-Fi 下原生 SMS 出站与入站的端到端验证。不能从余额短信成功推断 Muse 等第三方所有验证码必达；仍需用户在目标服务重新请求验证。
- 最终保留用户要求的飞行模式开启 + Wi-Fi 连接状态。未开启漫游或付费增购。

## 小红书验证码仍未到达

用户在 iPhone 小红书使用同一 Tello 号码请求验证码。截图区号与号码匹配。随后 ADB 检查：飞行模式仍开启；IMS SMS 仍 `up=true, reg=true, cap=true`；测试之后收件箱只有 15:55:59 的 Tello 余额回复，没有小红书验证码。当前结果说明基础 Wi-Fi SMS 已通过测试，但第三方验证码未在收件箱出现；不足以区分平台未发送、上游路由失败、运营商过滤或终端过滤。截图按钮显示「获取验证码」，没有可见倒计时，需确认请求是否得到已发送/倒计时反馈，不能仅凭截图认定请求成功。

补充网络与验证码调研见 `contexts/survey_sessions/2026_10_27_tello_wifi_calling_otp_diagnosis.md`。修正验收范围：800 运营商内部短信成功，不代表外部短信/验证码完整可用。查到官方美国蜂窝首次激活规则，应优先区分账户开通状态、外部路由和网络差异，不能仅凭用户报告推断封号。

## 换到 iPhone 后的配置核验

用户将 Apex/Tello 卡移入 iPhone，通过 iPhone 镜像查看设置（只读，未更改开关）：

- 蜂窝网络列表中 Tello 号码对应 Personal 线路，状态 On；国内 Primary 线路也启用。
- Tello 线路的 `Turn On This Line` 为开启。
- `WLAN Calling` 显示 On，进入后 `WLAN Calling on This iPhone` 开关为开启。
- Tello 线路的 `Network Selection` 显示 `Wi-Fi Calling`，说明此时界面已显示通过 Wi-Fi Calling 接入，而不只是开关开启。
- 数据漫游开关关闭。没有因为接码问题改 APN、关闭其他线路或重置网络。

结论：换卡后 iPhone 的线路启用、Wi-Fi Calling 开关及界面所示接入状态均正常；该结果不能替代外部验证码实际投递验证。当前未发现需要修正的本机 Wi-Fi Calling 配置。

## iPhone 原生 SMS 对照测试（尚未收到回复）

用户授权在 iPhone 上向 800 发送 BALANCE。镜像连接恢复后，新信息初始默认 Primary 国内线路；发送前已切为 Personal/Tello，确认唯一收件人为 800、内容 BALANCE。约 16:16 会话出现一条绿色 BALANCE SMS 气泡，没有可见失败标记。等待超过一分钟未观察到余额回复，故不能判定本次收发成功，也不能仅凭绿色气泡确认运营商端送达。

镜像输入存在异步延迟，收件人曾被拆为错误草稿，均在发送前清空并重新核对，没有向错误收件人发送。仅一条正确 800/BALANCE 消息进入会话。

随后 16:17 设置显示飞行模式开启、公司 Wi-Fi 已连、VPN=Not Connected（本 Agent 未操作 VPN；不能断言整个发送时段 VPN 状态保持不变）。Tello 线路启用、WLAN Calling=On、漫游关闭。飞行模式下没有此前的 Network Selection 行，因此该页面只能确认开关，不能替代当前 IMS 实际注册证据。下一步以另一 Wi-Fi/个人热点对照更有判别力。

## Clash Mi TUN 与美国节点测试进行中

用户明确授权调整 Clash Mi TUN、使用支持 UDP 的美国节点并向 800 发 BALANCE。

- 初始：VPN 未连，规则模式，TUN 覆写与启用均开启，网络栈 gvisor，MTU 1280，默认路由/DNS 劫持开启；includeAllNetworks=false，excludeLocalNetworks=false，excludeCellularServices=false，excludeAPNs=false，excludeDeviceCommunication=false，enforceRoutes=false。
- 仅将 includeAllNetworks 改为 true，其余保持原值。前后 TUN 截图保存在 /tmp/clashmi-tun-before.png 与 /tmp/clashmi-tun-after.png。
- 读取现有私人 YAML 的节点名/协议/UDP 开关（不输出密钥），洛杉矶 str-lax311 与达拉斯 str-dal301 均 WireGuard、udp:true。
- 启动手机 Clash Mi 后界面显示已连接，实际选中 StrongVPN → United States · Los Angeles · str-lax311，有持续实际流量。没有新建身份、修改源订阅、操作公司 REDpass 或更改 Mac VPN。
- 随后 iPhone 镜像断开，重连超时。本轮尚未发送 BALANCE，不能声称短信测试完成，也尚未证明运营商流量经代理。
- 推测 includeAllNetworks 生效且 excludeLocalNetworks=false 与镜像本地通信冲突；时序相关，需断开手机 VPN 对照确认。Apple 明确指出 VPN 不应阻止本地联网，否则影响 Continuity。先由用户在手机断开 Clash Mi，恢复镜像后考虑开启 excludeLocalNetworks 以保留本地通信，同时保持 excludeCellularServices=false。
  https://support.apple.com/en-ca/guide/iphone/iph505911a40/27/ios/27

## 换回 OPPO 后 800 未回复（约 16:47）

用户反馈 iPhone 曾手动发送 BALANCE 并收到套餐回复，随后 VPN 重连后再次无回复；之后把卡换回 OPPO，800 同样未回复。本轮 ADB 只读排查，不重发短信、不切网络。

- Tello 目前位于 OPPO SIM 槽 1（系统索引），状态 LOADED；另一槽 ABSENT。与最初槽 0 不同，当前查询匹配实际槽位。
- 飞行模式开启，卡槽 1 IWLAN HOME，语音/数据 IN_SERVICE。IMS SMS `up=true, reg=true, cap=true`。
- 16:46:48 最近发往 800 的正文确认为 BALANCE，数据库 type=2。16:46:49 IMS 回调 `status=1 reason=0 networkReasonCode=-1`，说明本机发送操作获得成功结果；不等于接收方已处理或回复已送达。
- 当前连接表没有 VPN 网络，不能将本次未回复直接归因于手机 VPN 开着。
- 尚无证据区分 800 自动回复处理、运营商下行路由、换机后会话状态或外部验证码投递。不要把 800 的重复测试当成独立外部入站验收；避免继续重复请求形成干扰。下一步有价值的证据为独立号码普通 SMS 入站及 Tello 运营商投递追踪。

## 用户重置 Tello eSIM 后重新添加（约 17:04）

用户已自行在 Tello 重置 eSIM，明确要求重新添加配置。本轮读取用户指定 My SIM 页的新安装信息，未再次申请更换，也未删除任何 profile。

- 新网页 ICCID 尾号 90067，与卡内新下载 #2 配置核对匹配；激活码不写入文档。
- OPPO SIM 1 中保留旧 #1 配置（已禁用），新 #2 配置下载写入成功并启用。使用官方 lpa Intent 预填提交一次。
- 网页点击 Finalize Setup，进入第 3 步 Turn on your eSIM & verify service。该向导进度不等于运营商已验收完整服务。
- OPPO 飞行模式维持开启；新配置启用后 IWLAN HOME，语音与数据 IN_SERVICE，IMS SMS up/reg/cap 全为 true。
- 17:04:27 向 800 发一次 BALANCE，17:04:28 IMS 返回 status=1 reason=0；等待约一分钟仍没有本次新增入站回复。旧 15:55 余额短信仍留在会话，未将其误判为新回复。
- 未变更付费套餐、充值、漫游、VPN；新 eSIM 的外部验证码接收能力仍未证实。
- 截图：/tmp/tello-new-esim-enabled.png（新旧配置状态）、/tmp/tello-new-esim-sms-test.png（短信会话）、/tmp/tello-new-esim-setup.png（网页安装向导第 3 步）。
