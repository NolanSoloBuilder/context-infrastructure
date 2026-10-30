# 在线美股观察台

固定地址：https://nolan-market-watch.choice-calf-0415.chatgpt.site

用户2026-10-30最终明确要求无需鉴权、知道链接即可访问，已从owner-private改public。不操作用户OpenAI登录或账号设置。

独立Sites源码位于adhoc_jobs/us_market_site，自有Git仓库；.openai/hosting.json持久保存project_id，后续必须复用此ID，不能重新创建。最新发布/commit/访问策略见deployment.json。只发布行情与通用研究，不发布portfolio_private/的账号、数量或成本，不发布个人预算/持仓标签。

默认每5分钟仅在页面可见时自动刷新，可选1/5/15分钟或关闭；支持手动。后台页暂停，回到页面检查过期。刷新云端真实获取17项数据、重新计算指标并R2持久化；基金持仓和财报研究仍保留披露日期。云端不依赖本机8789。

发布用Sites技能与原项目ID。public站点应save_site_version后deploy_site_version，不使用owner-private快捷部署操作，也不改变用户已确认的public访问方式。源码推送、打包、版本和部署必须对应同一commit，不提交凭据。

验收：匿名页面/API200，公开数据无私账信息；完整云端刷新17/17成功并持久化，新版本在完成提示前写入；真实浏览器免登录页面、筛选、详情弹层和自动刷新倒计时已验证。截图public_preview.jpg。手机实际视口未单独验收。

### 2026-10-30 曲线区间发布

原站点已增加一年／两年／三年全局切换，卡片与弹层同步，浏览器记忆区间，自动刷新后保留。17标的从新取5年Yahoo日线生成实际周年窗口；DRAM只显示2026-04-02以来并注明不足对应年限。年度指标不随曲线切换。线上31项定向测试通过，浏览器实际切换、弹层、DRAM提示与自动刷新保留3年通过；刷新17/17完成。精确source commit e2b99a580436d258edba2794f93f5a4d49887eb5，public deployment appgdep_6ae4093c76e881919ae4e849c3ea7214 succeeded。源数据、计算核验和线上回读见chart_ranges_2026-10-30/，真实截图three_year_preview.jpg。

### 2026-10-30 区间指标与价格交互

用户进一步要求统计随一年／两年／三年切换，取代上一条“年度指标固定”。已部署 source 5b42714897a3ace40177cc0effc7ef6c711af24c，version appgprj_6ae3fe7f4f9c8191be98b84d10171139~appgver_9db71542a1f88191915ef8a23039eff8，deployment appgdep_6ae40f278e1481919913fd07286c51a0 succeeded。收益为区间累计总回报，波动为区间日收益年化，MDD为完整区间内峰谷；均线50/200日固定。所有指标显示实际起止日，短历史单独注明。曲线为USD拆股调整日收盘，支持均线／收盘极值开关与日期／价格提示，鼠标、点按及键盘左右可查看。37项定向测试通过，线上17×3区间又用Python独立重算收益／波动／MDD并核对收盘极值。浏览器实际切换及VOO日期提示、次交易日移动通过。证据见chart_ranges_2026-10-30/interactive_live_verification.json，截图interactive_chart_preview.jpg。
