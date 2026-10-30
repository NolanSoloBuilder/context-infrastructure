# 美国 VPS 选型：速度、IP 属性与价格

核查日期：2026-10-27。用户主要使用 ChatGPT、Claude、Gemini，希望美国固定独用出口；本次仅查公开目录和条款，不注册、不购买、不联系新商家、不改现有网络。

## 候选比较

| 候选 | 当前官方公开报价/规格 | 路线与 IP 的证据 | 判断 |
| --- | --- | --- | --- |
| DMIT 洛杉矶 Premium TINY，AS3 | 参考 $10.90/月，1 vCore、2GB、20GB、1000GB、1Gbps | 官网 Premium 写明 CN2 GIA/中国优化；AS3 页面特别提示仍在建设优化，可能有较低磁盘性能/SLA。其他硬件平台与实际库存需另核 | 优先线路候选，但不能把其他站点的 AN5 $12.98 报价套用；询价与试用前核对具体产品 |
| 搬瓦工 CN2 GIA ECOMMERCE 20G | $49.99/季，折合 $16.66/月；1GB、20GB、1000GB/月、2.5Gbps、1独立IPv4 | 官方写明洛杉矶 China Telecom IDC/CN2 GIA，支持迁移；属机房服务，独享不证明历史干净 | 重视跨境线路、接受季度付的候选 |
| LisaHost 洛杉矶 9929 一期精简版 | ¥68/月，1核1GB、10GB、50Mbps、1000GB、1IPv4 | 商家宣称双ISP住宅属性、9929线路与48小时退款；该套餐写明机房，与其“真实住宅托管VDS”是不同产品 | 值得短期验证 IP 类型与目标站点，不把宣传当第三方验证 |
| Vultr 洛杉矶 Regular 1GB | 官方公共API返回 vc2-1c-1gb $5/月、$0.007/小时，1核1GB、25GB、1024GB流量，locations含lax | 常规云实例；本次未取得中国优化线路承诺或分配IP历史 | 便宜对照，不优先作为解决国内跨境速度的主选 |
| LisaHost 西雅图 Atlas 家庭宽带VDS | ¥169/月，1核1GB、20GB、100Mbps、3000GB、1IPv4 | 商家宣称真实住宅托管；官网明确非大陆直连优化，退款仅网站余额 | 住宅属性方向的备选，不适合作为当前速度问题的一步解决方案 |

价格为公开标价，不含未确定税费、促销和汇兑；端口速率不是跨境可达吞吐。页面展示可订购不等于付款前保证有货。DMIT 官方也声明价格表可能滞后。没有取得任何候选分配给本用户的IP，因此不能判断实际滥用记录、风险评分或三家AI服务接受情况。

## 来源（只采用供应商与服务官方）

- DMIT 价格：https://www.dmit.io/pages/pricing
- DMIT 网络说明：https://www.dmit.io/pages/cloud-instance
- DMIT 条款：https://www.dmit.io/pages/tos （当前退款章节写新订单3天且不超过30GB，扣支付渠道手续费，并有不适用条件；不能承诺无条件退款。未从当前条款取得可通用引用的IP更换价格，旧转载不使用。）
- 搬瓦工价格：https://bandwagonhost.com/cart.php
- 搬瓦工退款FAQ：https://bandwagonhost.com/kb.php?action=displayarticle&id=4 （30天、受条款约束）
- LisaHost 9929：https://lisahost.com/cart.php?gid=12
- LisaHost 住宅VDS：https://lisahost.com/cart.php?gid=33
- Vultr 官方公共价格API：https://api.vultr.com/v2/plans （通过macOS curl读取，未鉴权、未创建资源；API包含lax适用地区。）
- ChatGPT 支持地区：https://help.openai.com/en/articles/7947663-chatgpt-supported-countries
- Gemini 网页版地区：https://support.google.com/gemini/answer/13575153?hl=en
- Claude 地区与资格：https://support.claude.com/en/articles/8114491-get-started-with-claude

Claude 的 supported-countries URL 当前跳转到标注 2026-11-12 生效的新政策页面，晚于本次核查日期；不把该未来生效文本写成本日已生效政策。各服务资格不单由出口IP决定，不能承诺购买美国VPS就具备访问资格或不触发风控。

## 初步建议与验收标准

先筛 DMIT 洛杉矶 Premium 与 LisaHost 洛杉矶9929；前者侧重公开线路定位，后者侧重商家宣称ISP属性及较低月付成本。搬瓦工作季度付备选；普通Vultr作低成本对照。当前不能按实测速度或“纯净度”给四家排名。

下一步在采购前取得匹配具体套餐的测试IP/Looking Glass与退款/IP更换条件，使用用户真实接入网络，至少覆盖晚高峰，测RTT、丢包及较大文件持续吞吐。公司网、家用网应分开记录，不停止RedPass。拿到正式IP后核查美国定位、ASN、Hosting/ISP分类和公开滥用记录；不同数据库结论可能不一致。目标AI网站在合法可用账户下分别验证登录、正常对话/流式响应与上传（如需要），不以首页200或第三方“解锁脚本”证明全功能可用。

私有自建出口可继续使用现有Clash及固定VPS订阅分发流程，保留小红书、UU和国内DIRECT；这仅是兼容设计，尚未部署。
