# Tello 在大陆使用公司 Wi-Fi：余额短信成功但验证码未到

日期：2026-10-27。用户在中国大陆，认为公司 Wi-Fi 出口位于新加坡；该出口位置尚未实测。

## 当前判断

尚无证据证明 OPPO 的基础 Wi-Fi Calling 配置错误。已实测 IMS 注册及 SMS 能力可用、纯 Wi-Fi 下发出 BALANCE 并收到 800 余额回复。但运营商内部服务回复不等于外部 P2P/A2P/OTP 路由正常。此前将其概括为全部短信收发正常过于宽泛，验收应区分内部、外部普通短信、第三方验证码。

## 官方与用户报告

1. Tello 当前首次 eSIM 激活规则：需人在美国并连接美国蜂窝基站。下载配置、eUICC 中启用、IWLAN 注册与完整开通不是同一证据层。用户本轮在大陆下载配置；无法从本机证据确定该线路后端完整开通状态。
   https://tello.com/help_center/activate-port-in/can-i-activate-my-esim-outside-the-us
2. 官方故障指南建议在连接异常时更换 Wi-Fi，必要时尝试美国 IP VPN；也列出 IMS APN，但当前 IMS 已注册，缺少盲目修改 APN/重置网络的依据。VPN 不是美国蜂窝首次激活的替代证据。
   https://tello.com/help_center/service-issues-troubleshooting/wi-fi-calling-is-not-working-what-can-i-do
3. 官方说明支持短码/2FA，但国际号码发来的验证码可能不受支持。尚不知道小红书或 Muse 本次的实际发送号码、短信供应商和投递记录，不能直接归因。
   https://tello.com/help_center/new-to-tello/what-s-included-in-my-tello-plan
4. 2025-08-13 LINUX DO 用户报告 ESTK 可插拔 eSIM、Wi-Fi Calling、800 余额可收，所有验证码不可收；该来源仅为相似现象，未提供已确认根因。
   https://linux.do/t/topic/863496
5. 2026-09-24/25 Reddit 用户报告海外 Wi-Fi Calling 出站或通话正常、入站 SMS/OTP 失败，部分声称客服承认上游问题或提及未在美国使用。此为未经独立证实的用户报告，不能据此判断当前用户被封号。
   https://www.reddit.com/r/Tello/comments/1wotgmg/wifi_calling_stopped_receiving_messages_yesterday/
   https://www.reddit.com/r/Tello/comments/1wq7lir/tello_abruptly_cut_sms2fa_for_me/

## 排查顺序

1. 换个人热点/家庭 Wi-Fi，保留飞行模式，等待 IMS 注册，重新请求同一平台一次验证码。可区分公司网络相关性，但需控制平台限流和请求时间。
2. 从独立号码发送普通 SMS 到 Tello，区分外部整体入站故障与特定 A2P/OTP 路由故障。+86 测试本身依赖国际短信互通，失败不能单独确诊 Tello。
3. 若其他网络同样只有 800 能到，优先找 Tello 支持核查完整开通、短信 barring/provisioning、外部入站及短码/A2P 路由。附设备/线路信息时按需通过官方安全渠道提供，不提交激活码或账户密码。
4. 暂不重置网络、重下 eSIM、购买 PAYG 或开启漫游；这些行动没有现成的修复证据。

## 客服问题草稿（未发送）

I am currently in mainland China using native Wi-Fi Calling on an Android phone. IMS registration and SMS capability are available. In airplane mode with Wi-Fi enabled, texting BALANCE to 800 succeeds and I receive the Tello balance reply. However, a message sent to my own number has not returned, and OTP messages from two independent services have not arrived. Earlier I also received "Message Blocking is active" notifications. Could you verify whether the line is fully activated and provisioned for external inbound/outbound SMS, whether any messaging barring applies, and whether short-code/A2P inbound delivery is restricted? Please also clarify whether initial U.S. cellular activation is required for my line. The eSIM profile was installed while I was abroad.

## 原理澄清与 VPN 证据（用户要求暂停操作，先研究）

本轮仅检索官方资料与整理，不操作手机、不发送短信、不改网络。

### 各层角色

- Apex 是可插拔 eUICC，存储 Tello profile；EasyEUICC/LPA 用于下载、启用、切换 profile，配置完成后短信传输由手机系统与运营商负责。
- 必须区分 profile 下载到卡、卡内启用、Tello 线路后端开通、当前设备 IMS 注册、某一短信投递。任一前层成功都不能替代后层证据。
- Tello 账号要求 E911 地址，手机要求启用原生 Wi-Fi Calling。原生 SMS 经运营商网络收发，My Tello App 登录不在该链路。
- iPhone 的开关 On 表示启用设置；Apple 推荐通过控制中心的运营商 Wi-Fi 状态判断服务可用。绿色 SMS 气泡本身不能证明运营商投递成功。

### VPN 与公司 Wi-Fi

Apple `NEVPNProtocol.excludeCellularServices`（iOS 16.4+）在 `includeAllNetworks=true` 时允许排除 Wi-Fi Calling、MMS、SMS、Visual Voicemail；文档给出的默认值为 true。因此不能把浏览器出口 IP 等同于 IMS/Wi-Fi Calling 出口，也不能笼统说全部 iPhone VPN 都能承载、或都不能承载该流量。必须针对 VPN 客户端和路由配置判断。

T-Mobile 企业网络指南列出 WFC 2.0 的 UDP 500（IKE 认证）和 UDP 4500（IPsec NAT traversal）。公司网络能上网、浏览器有海外 IP，不证明此流量可用。此为底层网络参考，不能把文中地址清单直接当作已经验证的用户这条 Tello 线路实际端点。

### 官方条件与实际根因

Tello 当前官方要求新 eSIM 首次连接美国蜂窝基站。更早海外激活经验与当前官方要求应分开陈述；目前无法确定本用户后端完整开通/限制状态。美国 VPN IP 不等同于连接美国蜂窝基站。即便是政策条件，也不能单凭它确诊本例 OTP 故障。

### 新增一手来源

- Tello 原生 Wi-Fi Calling 设置（E911、开关、公司网络限制）：https://tello.com/help_center/service-issues-troubleshooting/how-can-i-use-wi-fi-calling
- Apple iPhone Wi-Fi Calling 接入判断：https://support.apple.com/zh-cn/108066
- Apple VPN 排除蜂窝服务（已通过官方 Markdown 获取正文，默认 true）：https://developer.apple.com/documentation/networkextension/nevpnprotocol/excludecellularservices
- Apple 路由机制：https://developer.apple.com/documentation/networkextension/routing-your-vpn-network-traffic
- T-Mobile 企业网络 WFC 端口：https://www.t-mobile.com/support/coverage/wi-fi-calling-on-a-corporate-network

下一轮排查需明确三个独立目标：当前设备 IMS 是否注册、独立普通 SMS 是否互通、指定 A2P/OTP 是否送达。换设备、换网络、换 VPN 不应同时进行，否则不能归因。iPhone 测试与此前 OPPO 测试不是同一运行状态，不能互相代替。

## iPhone 当前接入与具体 VPN 客户端核验（约 16:25）

- 镜像重连后只读查看：飞行模式已关闭（非本轮 Agent 修改），公司 Wi-Fi 连接，系统 VPN=Not Connected。
- Tello/Personal 线路 `Network Selection=Wi-Fi Calling`，`WLAN Calling=On`，说明当前系统界面报告已通过 Wi-Fi Calling 接入。该证据仍不等于特定外部短信成功。
- 尝试 macOS 27 镜像 Command-4，系统提示 iPhone 需 iOS 27+ 才能镜像控制中心；未升级系统。以线路实际 Network Selection 状态作为当前已有证据。
- VPN 列表当前选中 Clash Mi（未连接）；另有 WireGuard 名为 us 的配置及公司内网配置。不读取密钥、不切换、不修改任何 VPN 设置。
- Clash Mi 官方 FAQ 确认核心设置→TUN 提供 includeAllNetworks 与 excludeCellularServices 等开关。若专门做 VoWiFi 代理实验，应针对 includeAllNetworks=true、excludeCellularServices=false，并验证节点/规则支持 UDP。不能把官方针对 APNs 推送的整组参数不加区分地全部应用到短信，也没有必要为了该测试关闭 excludeLocalNetworks / excludeAPNs。
  https://clashmi.app/guide/faq
- 用户澄清“接收短信不需要激活”指无需先连接美国基站便可用 Wi-Fi Calling。实际 OPPO 在大陆已收到 800 回复，支持这一有限运行事实。应尊重这项实证，同时如实说明 Tello 现行官方新 eSIM 首次激活规则仍要求美国蜂窝接入；规则不能直接当作本例故障根因，也不能用内部余额短信推断外部验证码不受任何后端限制。
- 较早官方 how-to-activate-tello-from-abroad 链接当前重定向新闻首页，无法将旧教程当作现行支持承诺。
  https://blog.tello.com/news/how-to-activate-tello-from-abroad/

## 重置后进一步白盒排查（约 17:14）

- 新配置启用后首次 17:04 的短信仍记录在旧 sub_id=4。完整重启后，active/default subscription 变为 5，旧 4 的 simSlotIndex=-1，新 5 的 simSlotIndex=1。说明重启刷新了实际订阅映射；不能以卡内显示已启用代替 Android 订阅层确认。
- 重启后旧 #1 禁用、新 #2 启用；IWLAN HOME，IMS SMS 恢复 up/reg/cap=true。
- 17:13:35 一次 BALANCE 发送记录明确 sub_id=5，17:13:36 IMS 回调 status=1 reason=0。随后仍未收到本次新增入站。
- 重启后的 GsmInboundSmsHandler[1] 只有启动接受短信与释放唤醒锁记录，无下行事件；状态正常 Idle。默认短信 App 为 com.android.mms。没有证据支持“短信到了但通知被隐藏”；系统日志也不能排除基带/IMS实现或网络路径未上报，不能直接确诊运营商后台。
- 账户网页 Text messages=On，E911 地址存在，Web Guard=Off。可见开关不能替代后端 block/provisioning 核验。
- blockednumber provider 不存在、SIMINFO provider 受权限保护，因此未读取完整系统黑名单或完整 ICCID，不把权限查询失败写成“无阻断”。
- T-Mobile 官方文档说明商业/验证码短信可单独阻断，服务通知等可例外；仅作为运营商端需要核验的机制，不据此推断 Tello 当前已封锁。
  https://www.t-mobile.com/support/plans-features/message-blocking
- 调试已达到需要独立下行输入或运营商投递追踪的边界。准备客服草稿：2026_10_27_tello_support_draft.md，未发送，不默认获得外部消息授权。

## 17:24 运营商客服的新证据

用户授权联系官网客服后，Nicole 明确称账户因未通过自动安全与验证检查而被无限期停用，并称最近订单取消、9.15 美元退回原付款方式。故当前排查重点从终端/VPN转为账户服务限制；具体触发项、停用时间、SMS受限范围和复核可能性仍在追问，不将“境外/VPN触发”写成事实。完整联系记录见同目录 `2026_10_27_tello_support_draft.md`。
