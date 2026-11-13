# 中国长期使用海外真实移动号码：上游调查

日期：2026-11-11。目标为个人开发者向中国用户提供独享海外移动号码，用于本人海外社交与AI账户短信验证。只读调研，未开户、购买、联系供应商或实测短信；不把厂商承诺当作验收。前序报告：`esim_reseller_survey_20261111.md`。

## 结论

未找到已核实同时满足“个人自助批发、低成本、境内激活、永久境外使用、中国Wi-Fi Calling、全平台验证码”的方案。最接近商业需求的是eSIM.net O2 SMS Only GLOBAL；PikaSim明确接受个人经销，但OTP保障和价差较弱。美国零售卡可用于个人验证，不代表授权商业供货。

## 候选与证据

### eSIM.net O2 SMS Only GLOBAL：优先询价

[产品](https://www.esim.net/products/smsonly)：真实英国+44移动号码，无限收短信，£6/30天，当前美元显示$8；订阅续费保号，无出站短信、语音和数据。厂商宣称银行验证码可达，不构成对所有平台的独立验证。

[O2计划说明](https://www.esim.net/helpdesk/knowledge-base/o2-plans-included-calls-texts-data-roaming)：明确英国境外可首次安装激活，订阅有效则境外使用无时长上限。原文短摘录：“no limit on time spent outside the UK”。中国纳入其全球承诺是推断，尚无中国实测和具体网络确认。

该说明还写：境外接听电话可能触发spend cap，导致包括短信在内的服务停至下个自然月。可补发二维码保同号，收费；不能保同号直接升级为其O2全功能套餐。

[Wi-Fi Calling FAQ](https://www.esim.net/helpdesk/knowledge-base/wifi-calling)：仅本国使用，漫游不支持。中国方案须依赖蜂窝漫游，而不是Wi-Fi Calling。

[正式批发合作](https://www.esim.net/wholesale-partner)：有API、白标、月底开票、二线支持，合作方负责一线客服和收款。[API](https://api.esim.net/live/index.html)包括CreateOrder、ExtendOrder、SimSwap等，审核后提供凭据。尚未公开自然人是否可签约、MOQ、SMSOnly SKU批发可用性及采购价。[零售条款](https://www.esim.net/helpdesk/knowledge-base/terms-and-conditions-and-fair-usage-policy)禁止转售，不能用零售购买代替批发授权。

### PikaSim Global：个人可申请经销，但不是OTP保障方案

[经销申请](https://pikasim.com/reseller)明文允许个人、独资经营者，无需注册公司；审核后开放API，无最低订单，所有套餐零售价九折。[经销条款](https://pikasim.com/reseller-terms)要求真实申请信息、遵守上游地域限制、终端个人设备用途，不能保证上游未保证的能力；充值余额原则不可提现。当前中国申请是否获批未知。

[Global产品](https://pikasim.com/global-data-sms-call-plans)：厂商称真实美国+1移动号码，覆盖中国联通/电信；入站短信免费、续费保同号，逾期15天后可能失号。覆盖不等于中国首次激活及短信实测，页面说明语音短信会因地区变化。未找到Wi-Fi Calling承诺。

公开价：7天$25.34；30天$62.28；365天$181.20（20GB、200分钟、200条出站SMS）。按九折推算365天采购$163.08，摊12个月$13.59；保持其零售价仅留$18.12/年商品差价，尚未扣支付、客服、税和获客。续费同价及具体可续套餐仍需核实。

同页明确OTP无法保证，未送达OTP不构成电话套餐退款理由。因此它是可研究的号码分销候选，不能充当“无脑接码”的已验证供货。其USA-only $7起套餐仅美国使用，不可错当中国套餐。[API](https://pikasim.com/reseller/api-docs)写USA/Global可续费保号，但很多其他国家套餐只能单周期，续购换号。

### 美国零售卡：个人测试与商业供货分开

| 服务 | 公开个人成本 | 境外使用及限制 |
|---|---|---|
| Tello | $5/月另税，无数据、300分钟、无限短信 | 首次美国激活；境外原生Wi-Fi Calling/Text；零售套餐住宅非商业用途 |
| Ultra PayGo | $3/30天另税及卡费，100分钟/100短信/100MB | 首次本土激活；Wi-Fi Calling需兼容；条款要求居住及主要使用在美国，限制长期国际使用 |
| US Mobile Light | $10/月或$96/年，含税 | 网络不同Wi-Fi Calling条件不同；条款明确禁止转售及收费代激活，且可因主要境外使用终止 |

Tello：[价格](https://tello.com/buy/custom_plans?plan=NULL-300-Unlimited)、[激活](https://tello.com/help_center/international-calls/can-i-activate-tello-while-i-m-abroad)、[境外功能](https://tello.com/help_center/roaming/how-can-i-use-my-device-overseas)、[条款](https://tello.com/terms)。My Tello App只能打出电话，不能代替原生Wi-Fi Calling接收短信。官方未给出中国各种网络下的稳定性保证。

Ultra：[价格](https://www.ultramobile.com/paygo/)、[条款](https://www.ultramobile.com/mobile-plans-terms-conditions/)，§25把PayGo纳入完整条款，不能忽略长期境外限制。普通Ultra支持eSIM也不能直接推断PayGo支持。

US Mobile：[价格](https://www.usmobile.com/help/docs/our-plans/core-plans/low-data-plans)、[Wi-Fi Calling](https://www.usmobile.com/help/docs/troubleshooting-and-setup/setting-up-device/wifi-calling)、[条款](https://www.usmobile.com/terms)。§23明确包含禁止收费替他人激活。用户愿意境外首次激活，并不能消除转售及长期境外限制。

### 其他候选排除/降级

- giffgaff：[境外不支持Wi-Fi Calling](https://help.giffgaff.com/en/articles/258841-understanding-wifi-calling-and-volte)；[每六个月需主动活动或充值](https://help.giffgaff.com/en/articles/242797-understanding-why-your-number-has-been-deactivated)，仅收SMS不在列；[零售条款](https://www.giffgaff.com/terms)限私人用途。中国激活仅社区线索，未形成商业保证。
- Gigs：[正式移动服务平台](https://gigs.com/devices)有API/白标，但[终端条款](https://gigs.com/legal/end-user-service-agreement)不允许永久漫游；具体中国长期方案、个人合作及采购价未确认。
- 1GLOBAL：[Connect API](https://docs.connect-api.1global.com/)确有号码和订阅能力，但未找到满足本需求的个人公开报价/中国长期Wi-Fi Calling合同，不列作已可接入上游。
- Roamless Numbers：[官方明确是VoIP](https://help.roamless.com/en/articles/14346859-roamless-numbers)，不能满足真实移动号码要求。

## 产品范围与验收

运营商原生Wi-Fi Calling只是传输方式，不会把移动号码变成VoIP虚拟号。但目标服务仍可按号段、历史及自身规则决定是否发码；换机补卡可能重新触发激活要求。

[Claude手机验证规则](https://support.claude.com/en/articles/8287232-verify-your-phone-number)要求支持地区号码和用户实际位于支持地区，不接受VoIP。获得海外手机号不能单独解决服务使用资格，不应售卖“有号即可使用任何AI”。本次未引用生效日期在调研日期之后的新政策作为现行规则。

商业化前优先向eSIM.net确认：SMSOnly是否可批发、接受中国个人/个体经营主体吗、可否面向中国常住客户销售、中国合作网络及短信短码、批发单价与最低量、长期境外例外是否写入合同、暂停续费/补卡/号码迁出流程、能否网络侧禁止来电防止spendcap。

建议付费小样验收（本次未执行）：英国SMSOnly和美国Tello分别用自己的号码/获授权账户，在目标手机及中国不同接入网络上测安装、普通短信、目标社交/AI短信、重启、续费、换机补卡；遵守平台资格与正常验证码频率。用明确支持清单和最近测试日期替代全平台100%承诺。

最小架构：用户自己的手机持有SIM/eSIM并直接收码，你的平台做开卡、续费、到期提醒、故障诊断和替换流程；运营商号码管理API不等于短信正文代收API。不把手机卡池或二维码迁移当成已经获得授权的商业路径。
