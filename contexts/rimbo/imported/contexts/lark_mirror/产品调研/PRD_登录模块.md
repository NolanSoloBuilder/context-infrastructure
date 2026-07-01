<!-- lark-mirror obj_token=M9FfdOAdXoEKoxxRJKajiDjIpyj space=产品调研 synced=2026-05-18T07:54:44Z -->

<title>PRD_登录模块</title>

# 一、 版本日志

| **时间** | **版本号** | **负责人** | **更新内容** |
|-|-|-|-|
| Oct/26/2025 | V1.0 | Clarice | MVP登录版本 |

# 二、 功能详细说明

## 登录及账号生命周期功能模块

<whiteboard token="B5QQw9NiNhKDBkbe6M4j23q1pDb"></whiteboard>

## 交互原型图

https://www.figma.com/design/ZgZ4CtocU02wqrG4IohIZ8/Podnote?node-id=831-23775&t=OWNwCrFS6KN3Wxi1-1

## 功能链路

### 3.1 邮箱密码

#### 3.1.1 登录流程

<whiteboard token="QZERwkFIBhZTsebTfBojudyrpfg"></whiteboard>

#### 3.1.2 邮箱密码各阶段报错文案

<table><colgroup><col/><col/><col/><col/></colgroup><thead><tr><th>阶段</th><th>错误类型</th><th>检测</th><th>报错文案/处理</th></tr></thead><tbody><tr><td rowspan="4">注册</td><td>邮箱格式错误</td><td>是否有@符号</td><td>Email is not valid.</td></tr><tr><td>邮箱格式错误</td><td>@符号后面是否有文字输入</td><td>Email is not valid.</td></tr><tr><td>邮箱为空</td><td>是否为空</td><td>Email cannot be empty.</td></tr><tr><td>密码强度不够</td><td>密码长度是否大于等于12位数</td><td>Your password must contain: At least 12 characters </td></tr><tr><td></td><td>验证码输入错误</td><td>验证码是否等于6位数</td><td>The verification code should be exactly 6 characters long </td></tr><tr><td></td><td>验证码输入错误</td><td>验证码是否正确</td><td>The verification code is incorrect</td></tr><tr><td rowspan="4">登录</td><td>邮箱格式错误</td><td>是否有@符号</td><td>Email is not valid.</td></tr><tr><td>邮箱格式错误</td><td>@符号后面是否有文字输入</td><td>Email is not valid.</td></tr><tr><td>密码为空</td><td>密码为空</td><td>Password cannot be empty.</td></tr><tr><td>邮箱或密码错误</td><td>匹配错误</td><td>Incorrect email or password. Please try again.</td></tr><tr><td rowspan="4">密码重置流程</td><td>新密码强度不够</td><td>密码长度是否大于等于12位数</td><td>Your password must contain: At least 12 characters </td></tr><tr><td>两次输入的新密码不一致</td><td>两次输入密码是否一致</td><td>Passwords don’t match. Please confirm.</td></tr><tr><td>验证码输入错误</td><td>验证码是否等于6位数</td><td>The verification code should be exactly 6 characters long </td></tr><tr><td>验证码输入错误</td><td>验证码是否正确</td><td>The verification code is incorrect</td></tr></tbody></table>

#### 3.1.3 发送的邮件

<table><colgroup><col/><col/><col/></colgroup><thead><tr><th></th><th>验证邮箱</th><th>重新设置密码</th></tr></thead><tbody><tr><td>参考</td><td><img name="Screenshot 2025-10-26 at 5.55.34 PM.png" href="https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=YmIxODk0YTIwZjdmOGIwNTk1MzY0MjNhMmVlMTA2YmZfMDQwY2E4YjNkMDc2OTliMDgzYzM3YTY0NWVmNjViZTBfSUQ6NzU2NTY5ODg3NTA1OTYyMTM5Nl8xNzc5MDkwODk5OjE3NzkwOTQ0OTlfVjM" mime="image/png" scale="1.000000" src="HqHUb0oLloImcmxGyH8juLeyp0b"/></td><td><img name="Screenshot 2025-10-26 at 5.55.54 PM.png" href="https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=NjVhNDI2MmNjNTA5OWIyODQzNDg1NzllODEyZTEyMDZfYTVkYmI1YWQ3NDRlNGUwYzIyOTY0ODJjZTIzOGY4ZTlfSUQ6NzU2NTY5ODk2MjYzMjY1ODQ1MV8xNzc5MDkwODk5OjE3NzkwOTQ0OTlfVjM" mime="image/png" scale="1.000000" src="HJyLbVvb2oZ7p6xLObhjTVqLpMe"/></td></tr><tr><td>文案</td><td><h1>MindSpace</h1><br/>Enter this temporary verification code to continue:<h1>292635</h1><br/>Please ignore this email if this wasn’t you trying to create a Mindspace account.<br/><br/>Best,<br/>The  Mindspace team<br/>Subject title:  Your MindSpace code is 292635</td><td><h1>MindSpace</h1><br/>Enter this temporary verification code to continue:<h1>659077</h1><br/>Please ignore this email if this wasn’t you trying to reset your password.<br/><br/>Best,<br/>The  Mindspace team<br/><br/>Subject title: Your MindSpace password reset code is 659077</td></tr></tbody></table>