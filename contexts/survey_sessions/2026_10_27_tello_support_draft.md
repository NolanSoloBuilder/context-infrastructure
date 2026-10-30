# Tello 短信故障客服记录（已提交在线聊天）

截至 2026-10-27，时间均为 Asia/Shanghai / UTC+8。当前目标是修复原生 Wi-Fi Calling 的下行 SMS，非购买通话或漫游。

## 可发送的英文内容

Hello, please investigate inbound SMS delivery on the Tello line selected in my signed-in account. I am in mainland China using native Wi-Fi Calling on an OPPO PFFM10 with Android 15. The new replacement eSIM profile has been installed and enabled; its ICCID ends in 90067.

The account Text messages setting is ON and an E911 address is configured. The monthly plan includes unlimited texts and 2 GB data, with no voice minutes and $0 PAYG balance.

Evidence from October 27, 2026 (UTC+8):
- At 15:55, texting BALANCE to 800 produced a balance reply. Later replies and OTP messages stopped arriving.
- A replacement eSIM was installed. At 17:04:27, a BALANCE SMS was sent and IMS returned success at 17:04:28, but there was no reply.
- I fully rebooted the phone. Android then recognized the new SIM as subscription ID 5, replacing old subscription ID 4.
- At 17:13:35, I sent one BALANCE SMS to 800 using the new subscription. At 17:13:36, Android IMS reported send success, status=1, reason=0. No reply arrived during the observation period.
- The phone registers on IWLAN with IMS SMS capability available. The Android inbound SMS handler is idle and shows no new downlink SMS event after reboot. This is not just a missing notification.
- The problem also occurred after moving the same card to an iPhone. The OPPO has been tested in airplane mode with Wi-Fi enabled and without an active phone VPN.

Could you please:
1. Verify the replacement ICCID is correctly mapped and fully provisioned for this line, including inbound and outbound SMS over IMS/Wi-Fi Calling.
2. Check for all-SMS, incoming-SMS, commercial/A2P, and short-code blocks or service restrictions, beyond the visible Text messages toggle.
3. Trace the 800 requests at the timestamps above: did 800 receive each request, was a response generated, and what delivery result/reject code did it receive?
4. Refresh or reprovision the line's SMS/IMS services if your investigation shows a provisioning inconsistency.
5. Clarify whether any first-use/activation restriction applies specifically to this line's Wi-Fi Calling SMS. Please distinguish this from international cellular roaming and voice minutes, as I am troubleshooting SMS only.

Please do not change my plan, add paid credit, enable paid roaming, cancel my number, or issue another eSIM without asking me first.

## 隐私边界

客服通过当前已登录账户识别线路。若工具必须明确传入号码，仅提供当前这条 Tello 号码及新 ICCID 尾号；不发送激活码、E911 地址全文、密码、安全 PIN、验证码、eUICC EID、公司 Wi-Fi 名称或网络地址。IMEI 如客服另行索取，应先确认必要性再向用户说明。

## 17:19 官网提交

用户明确回复「允许」后，通过当前已登录 Tello 官网聊天发送问题摘要，选择 Yes, start live chat，随后发送含设备、当前新卡尾号、UTC+8 测试时间、IMS 回调和所需后台检查的完整摘要。页面已显示发送内容；此时尚未出现人工姓名、工单号或后台调查结论。没有发送密码、PIN、验证码、激活码或完整设备标识。

## 17:24 客服确认账户无限期停用

人工客服 Nicole 表示，账户未通过系统自动安全与验证检查，已被 indefinitely suspended；最近订单已取消，9.15 美元已退回原付款方式。上述是客服陈述，未独立核验退款到账。已追问：停用生效时间、对下行 SMS/800 回复的直接影响、可披露的具体原因或原因类别、人工安全复核/申诉路径和工单号。用户随后明确要求继续询问原因，已追加区分支付/账单、身份信息、境外使用、VPN/网络位置等可能类别；这些仅为问题，尚不是已确认原因。没有批准取消号码或付费操作。
