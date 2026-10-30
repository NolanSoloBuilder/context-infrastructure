# Wi-Fi Calling 工作原理

核实日期：2026-10-27。

Wi-Fi Calling（VoWiFi）把手机到运营商核心网的接入路径换成 Wi-Fi 和互联网，继续使用运营商的号码、认证和电话服务。

典型的非可信 WLAN 接入链路：手机 → Wi-Fi 路由器 → 互联网 → 运营商 ePDG → 分组核心网 → IMS → 对方电话网络。手机通过 SIM/eSIM 中的身份凭据完成认证，并与 ePDG 建立 IPsec 加密隧道，再向 IMS 注册。呼叫信令用于建立和管理通话，编码后的语音通过数据包双向传输。图示为逻辑路径，省略了中间网元；5G 核心网也有其他接入架构。

接收来电时，运营商通过已注册的 Wi-Fi 接入路径把呼叫送到手机。对方可使用普通手机或固定电话。路由器一般只负责联网，无需理解电话号码或安装电话专用功能。

是否可用取决于运营商开通、终端兼容和网络可达性。Wi-Fi 与蜂窝之间的通话连续性取决于双方支持。计费按运营商套餐及目的号码等规则执行，走 Wi-Fi 不等于免费，境外使用需查具体运营商政策。

来源：
- [GSMA VoWiFi 概述](https://www.gsma.com/solutions-and-impact/technologies/networks/ip_services/vowifi/)
- [华为 VoWiFi 技术分析](https://carrier.huawei.com/en/technical-topics/core-network/huawei-vowifi-technical-white-paper.)（用于传统 ePDG、SIM 认证、IPsec 和 IMS 架构，文中产品部署状态不作为当前结论）
- [T-Mobile Wi-Fi Calling 支持与计费](https://www.t-mobile.com/support/coverage/wi-fi-calling-from-t-mobile)
