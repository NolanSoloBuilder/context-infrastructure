"""Render reviewed watchlist facts and dated risk metrics using the daily report style."""
from __future__ import annotations
import argparse
import base64
import hashlib
import html
import json
import math
from pathlib import Path


def esc(value):
    return html.escape(str(value), quote=True)


def link(url, label):
    if not isinstance(url, str) or not url.startswith('https://'):
        return esc(label)
    return f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(label)}</a>'


def number(value, suffix='', signed=False, digits=2):
    if value is None or not math.isfinite(float(value)):
        return '—'
    return f'{float(value):+,.{digits}f}{suffix}' if signed else f'{float(value):,.{digits}f}{suffix}'


def stat(label, value, kind=''):
    return f'<div class="stat {kind}"><dt>{esc(label)}</dt><dd>{esc(value)}</dd></div>'


def sparkline(risk, symbol):
    points = risk.get('sparkline', [])
    valid = []
    for p in points:
        value = p.get('value') if isinstance(p, dict) else None
        if value is not None and math.isfinite(float(value)):
            valid.append((p.get('date',''), float(value)))
    if len(valid) < 2:
        return '<p class="data-note">趋势曲线缺少可核验序列。</p>'
    values = [x[1] for x in valid]
    lo, hi = min(values), max(values)
    span = hi - lo or max(abs(hi) * .01, 1)
    coords = [(i/(len(values)-1)*440+4, 63-(v-lo)/span*55) for i,v in enumerate(values)]
    path = ' '.join(f'{x:.2f},{y:.2f}' for x,y in coords)
    color = '#176f65' if values[-1] >= values[0] else '#b33e3e'
    basis = '复权' if risk.get('sparkline_basis') == '分红/拆股复权' else '价格'
    return f'<figure class="spark"><svg viewBox="0 0 448 70" role="img" aria-label="{esc(symbol)}最近{len(values)}个交易日{basis}收盘走势，各图单独缩放"><line x1="4" y1="66" x2="444" y2="66" stroke="#e6eceb"/><polyline fill="none" stroke="{color}" stroke-width="2" points="{path}"/><circle cx="{coords[-1][0]:.2f}" cy="{coords[-1][1]:.2f}" r="2.6" fill="{color}"/></svg><figcaption><span>{esc(valid[0][0])} → {esc(valid[-1][0])}</span><span>{len(values)}交易日 · {basis} · 各自缩放</span></figcaption></figure>'


def full_card(a, risk):
    q, f = a.get('quote', {}), a.get('facts', {})
    symbol = a['symbol'];kind=a['kind']
    full_year = risk.get('complete_year', risk.get('is_full_year', risk.get('period_label') in ['近一年', '近1年', 'one_year', '近一年（含分红复权）']))
    if risk.get('return_period_type') == 'since_inception':full_year=False
    period = risk.get('period_label', '近一年')
    ret_label = '近一年总回报' if full_year else ('成立以来总回报' if '成立' in period or symbol=='DRAM' else period+'回报')
    if str(risk.get('return_adjustment_status','')).startswith('price_only') or (risk.get('return_basis') and ('price_only' in str(risk['return_basis']).lower() or risk.get('return_includes_dividends') is False)):
        ret_label = ret_label.replace('总回报','价格回报')
    ret = risk.get('return_pct')
    primary = stat(ret_label,number(ret,'%',True), 'positive' if ret is not None and ret>=0 else 'negative' if ret is not None else '')
    primary += stat('年化波动率',number(risk.get('annualized_volatility_pct'),'%'))
    primary += stat('区间最大回撤',number(risk.get('max_drawdown_pct'),'%',True),'negative')
    primary += stat('距52周盘中高点',number(risk.get('price_drawdown_52w_pct'),'%',True))
    ma = stat('50日均线 · USD',number(risk.get('ma50')))
    ma += stat('收盘较MA50',number(risk.get('vs_ma50_pct'),'%',True))
    ma += stat('200日均线 · USD',number(risk.get('ma200')))
    ma += stat('收盘较MA200',number(risk.get('vs_ma200_pct'),'%',True))
    quality_warning = ''
    if risk.get('quality_status') == 'outlier_pending_verification':
        primary = ''.join(stat(label, '待核') for label in [ret_label, '年化波动率', '区间最大回撤', '距52周盘中高点'])
        ma = ''.join(stat(label, '待核') for label in ['50日均线 · USD', '收盘较MA50', '200日均线 · USD', '收盘较MA200'])
        quality_warning = '<p class="lag">历史序列存在尚未完成交叉核验的大幅跳变；指标暂不作为有效比较依据，原始计算保留在下载数据中。</p>'
    elif risk.get('quality_note'):
        quality_warning = '<p class="lag">'+esc(risk['quality_note'])+'</p>'
    elif risk.get('extreme_daily_moves'):
        move = risk['extreme_daily_moves'][0]
        quality_warning = '<p class="lag">'+esc(f"{move['date']}单日变化{move['return_pct']:+.2f}%，已与第二行情网页核对，事件原因仍需原始披露核验。这次跳变显著影响历史回报与年化波动，不能作为预期收益。")+'</p>'
    if symbol == 'SGOV':
        quality_warning += '<p class="data-note">区间最大回撤若显示0.00%，只表示本区间复权日收盘的观察结果，不代表风险或未来亏损为零。</p>'
    close = '$'+number(q.get('close'))
    change = number(q.get('day_pct'),'%',True)
    quote_cls='positive' if q.get('day_pct',0)>=0 else 'negative'
    cost = f'年费率 {f["expense_pct"]:.2f}%' if f.get('expense_pct') is not None else '公司普通股'
    quote_date=q.get('session','缺失');metric_date=risk.get('asof_session','缺失')
    lag = f'<p class="lag">指标截至{esc(metric_date)}，收盘报价截至{esc(quote_date)}；日期不同，请分别阅读。</p>' if risk and metric_date!=quote_date else ''
    holdings=[]
    for h in f.get('holdings',[]):
        holdings.append(f'<li><span>{esc(h.get("name",h.get("symbol","")))} <small>{esc(h.get("symbol",""))}</small></span><b>{number(h.get("weight_pct"),"%")}</b></li>')
    holding_body = (f'<p class="data-note">持仓日 {esc(f.get("holdings_date","日期缺失"))} · 主要项目，非完整组合</p><ol class="holding-list">'+''.join(holdings)+'</ol>') if holdings else '<p>'+esc(f.get('business','尚未取得日期和权重明确的官方持仓，不填估计值。'))+'</p>'
    if f.get('holdings_basis'):holding_body+='<p class="data-note">'+esc(f['holdings_basis'])+'</p>'
    facts = ''.join('<p>'+esc(x)+'</p>' for x in f.get('fact_lines',[]))
    notes = ''.join('<li>'+esc(x)+'</li>' for x in f.get('notes',[]))
    sources = ''.join('<li>'+link(s.get('url'),s.get('title','来源'))+'<small> · '+esc(s.get('asof',''))+'</small></li>' for s in f.get('sources',[]))
    sources += ''.join('<li>'+link(s.get('url'),s.get('title','异常价格交叉核验'))+'<small> · '+esc(s.get('scope',''))+'</small></li>' for s in risk.get('quality_sources',[]))
    sources += '<li>'+link(q.get('source_url'),'常规报价来源')+((' · '+link(q['crosscheck_url'],'第二来源')) if q.get('crosscheck_url') else '')+'</li>'
    if risk.get('source_url'):sources+='<li>'+link(risk['source_url'],'历史行情与复权数据')+'</li>'
    gaps=list(dict.fromkeys(f.get('gaps',[])+risk.get('gaps',[])))
    gap_html='<p class="data-note">缺口：'+esc('；'.join(gaps))+'</p>' if gaps else ''
    quote_note='<p class="data-note">'+esc(q.get('crosscheck_status','当日已核验常规收盘快照；价格序列不计现金分红再投资。'))+'</p>'
    extended=a.get('extended',{})
    reference_lines=[]
    for key,label in [('latest_regular','最新常规时段参考'),('pre','盘前参考'),('post','盘后参考')]:
        item=extended.get(key,{})
        if item.get('price_usd') is None or (key!='latest_regular' and item.get('status')!='available'):
            continue
        time=item.get('time_beijing') or item.get('bar_start_beijing') or '时间缺失'
        pct=item.get('change_vs_reference_pct')
        change_text='（'+number(pct,'%',True)+'）' if pct is not None else ''
        note=' · 零量/缺量分钟参考，未确认新成交' if key!='latest_regular' and not item.get('bar_has_positive_volume') else ''
        reference_lines.append('<p>'+esc(label+'：$'+number(item['price_usd'])+change_text+' · '+str(time)+' 北京时间'+note)+'</p>')
    extended_html='<div class="extended-reference"><h4>最新时段参考</h4>'+''.join(reference_lines)+'<p class="data-note">单一提供方参考，报价各自日期与时刻如上；盘前盘后不进入年度指标。'+link(extended.get('source_url'),'分钟行情来源')+'</p></div>' if reference_lines else ''
    if a.get('last_refresh_error'):
        quality_warning+='<p class="lag">本次刷新未取得新数据：'+esc(a['last_refresh_error'])+'；保留上次有效日期。</p>'
    search=' '.join([symbol,a['name'],a.get('original_group',''),a.get('industry',''),f.get('name',''),f.get('strategy','')]).lower()
    heading='基金持仓与特点' if kind=='fund' else '经营数据与研究说明'
    category=a.get('original_group',a.get('role',''))
    return f'''<article class="asset-card" data-symbol="{esc(symbol)}" data-search="{esc(search)}">
+<div class="asset-head"><div><div class="asset-kind">{esc(category)} · {esc(a.get('kind_label',''))}</div><h3>{esc(symbol.replace('BRK-B','BRK.B'))}</h3><p class="asset-name">{esc(f.get('name',a['name']))}</p></div><div class="asset-price"><strong>{close}</strong><span class="change {quote_cls}">{change}</span><small>{esc(quote_date)} 常规收盘</small></div></div>
+<p class="asset-strategy">{esc(f.get('strategy',a['name']))}</p><div class="asset-cost">{esc(cost)}<span>{esc(a.get('role','研究观察'))}</span></div>
+<dl class="risk-grid">{primary}</dl>{quality_warning}{sparkline(risk,symbol) if risk.get('quality_status') != 'outlier_pending_verification' else ''}<dl class="ma-grid">{ma}</dl>
+<p class="data-note">指标截至 {esc(metric_date)} · 区间 {esc(risk.get('period_start','缺失'))} 至 {esc(risk.get('period_end','缺失'))} · {esc(period)}</p>{lag}{extended_html}
+<p class="personal-note">{esc(a['personal_note'])}</p>
+<details class="asset-detail"><summary>{heading}</summary><div>{holding_body}{facts}<ul>{notes}</ul><p><b>风险：</b>{esc('；'.join(f.get('risks',[])))}</p><p><b>下一项核查：</b>{esc(a.get('next','核验经营、估值与重叠风险'))}</p></div></details>
+<details class="asset-detail sources-detail"><summary>来源与数据缺口</summary><div>{quote_note}{gap_html}<ul>{sources}</ul></div></details></article>'''.replace('\n+','\n')


def card(a, risk):
    q=a.get('quote',{});f=a.get('facts',{});symbol=a['symbol']
    period_label='一年回报' if risk.get('complete_year') else '成立以来' if risk.get('period_label')=='成立以来' else '区间回报'
    if str(risk.get('return_adjustment_status','')).startswith('price_only'):period_label=period_label.replace('回报','价格回报')
    ret=risk.get('return_pct');pending=risk.get('quality_status')=='outlier_pending_verification'
    ret_text='待核' if pending else number(ret,'%',True)
    vol='待核' if pending else number(risk.get('annualized_volatility_pct'),'%')
    mdd='待核' if pending else number(risk.get('max_drawdown_pct'),'%',True)
    search=' '.join([symbol,a['name'],a.get('original_group',''),a.get('industry',''),f.get('name',''),f.get('strategy','')]).lower()
    flags=[]
    if pending:flags.append('历史指标待核')
    elif risk.get('extreme_daily_moves'):flags.append('含极端跳变')
    if not risk.get('complete_year'):flags.append('不足一年')
    flag='<span class="summary-flag">'+esc(' · '.join(flags))+'</span>' if flags else ''
    change=q.get('day_pct');change_cls='positive' if change is not None and change>=0 else 'negative'
    return_cls='positive' if ret is not None and ret>=0 else 'negative'
    ma50=number(risk.get('vs_ma50_pct'),'%',True);ma200=number(risk.get('vs_ma200_pct'),'%',True)
    curve=sparkline(risk,symbol) if not pending else ''
    name=a['name'];fee=f' · {f["expense_pct"]:.2f}%' if f.get('expense_pct') is not None else ''
    info=full_card(a,risk)
    return f'''<article class="asset-card asset-summary-card" tabindex="0" role="button" aria-haspopup="dialog" aria-label="查看{esc(symbol)}详情" data-symbol="{esc(symbol)}" data-search="{esc(search)}">
<div class="summary-head"><div><h3>{esc(symbol.replace('BRK-B','BRK.B'))}</h3><p title="{esc(name)}">{esc(name)}{esc(fee)}</p></div><div class="summary-price"><strong>${number(q.get('close'))}</strong><span class="change {change_cls}">{number(change,'%',True)}</span></div></div>
<dl class="summary-metrics">{stat(period_label,ret_text,return_cls)}{stat('年化波动',vol)}{stat('最大回撤',mdd,'negative')}</dl>
<div class="summary-trend">{curve}</div><div class="summary-ma"><span>MA50 {ma50}</span><span>MA200 {ma200}</span></div>
<div class="summary-foot"><span>{esc(str(risk.get('asof_session') or q.get('session','缺失'))[5:])} · 常规收盘</span>{flag}<span class="detail-hint">悬停 / 点击详情</span></div>
<template class="asset-detail-template">{info}</template></article>'''


def render(data, risk_data):
    assets=[{**a,'original_group':g['label']} for g in data['groups'] for a in g['assets']]
    by_symbol={a['symbol']:a for a in assets}
    order=['VOO','QQQM','SPMO','MAGS','VGT','SOXX','SMH','DRAM','SGOV']
    funds=[by_symbol[s] for s in order if s in by_symbol]
    funds += [a for a in assets if a['kind']=='fund' and a['symbol'] not in order]
    industry_order=['internet_ai','semiconductors','automation','fintech','biotech','conglomerate']
    stocks=sorted([a for a in assets if a['kind']=='stock'],key=lambda a: industry_order.index(a.get('industry_id')) if a.get('industry_id') in industry_order else len(industry_order))
    risk_by_symbol=risk_data.get('symbols',{})
    sections=[f'<section id="etfs" class="report-section asset-group" data-kind="fund"><div class="section-title"><h2>ETF基金</h2><span>{len(funds)}项</span></div><p class="section-description">宽基、动量、七巨头、科技、半导体、存储与超短美债集中展示。</p><div class="asset-grid">'+''.join(card(a,risk_by_symbol.get(a['symbol'],{})) for a in funds)+'</div></section>']
    industries={}
    for a in stocks:
        industry_id=a.get('industry_id', 'other')
        bucket=industries.setdefault(industry_id, {'label':a.get('industry','其他行业'),'assets':[]})
        bucket['assets'].append(a)
    industry_sections=[]
    for key,bucket in industries.items():
        items=bucket['assets']
        industry_sections.append(f'<section id="industry-{esc(key)}" class="asset-group stock-industry {"industry-wide" if len(items)>1 else ""}" data-kind="stock"><div class="industry-title"><h3>{esc(bucket["label"])}</h3><span>{len(items)}项</span></div><div class="asset-grid">'+''.join(card(a,risk_by_symbol.get(a['symbol'],{})) for a in items)+'</div></section>')
    sections.append(f'<section id="stocks" class="report-section" data-stock-section><div class="section-title"><h2>个股 · 按行业</h2><span>{len(stocks)}项</span></div><p class="section-description">按主要业务划分研究行业；多元经营公司单列。</p>'+'<div class="industry-layout">'+''.join(industry_sections)+'</div></section>')
    css=Path(__file__).with_name('report.css').read_text()+'\n'+Path(__file__).with_name('catalog.css').read_text()
    script=Path(__file__).with_name('catalog_interactions.js').read_text()
    payload=base64.b64encode(json.dumps({'catalog':data,'risk_metrics':risk_data},ensure_ascii=False,indent=2).encode()).decode()
    date=data['report_date'];count=len(assets)
    live=bool(data.get('live_mode'))
    runtime=json.dumps({'live':live,'version':data.get('live_version'),'status':data.get('live_status',{})},ensure_ascii=False).replace('<','\\u003c')
    refresh_control='<button id="refresh-data" class="refresh-button" type="button">刷新行情</button>' if live else '<a class="local-live-link" href="http://127.0.0.1:8789/" target="_blank" rel="noopener">打开可刷新版</a>'

    auto_control='<label class="auto-refresh-toggle"><input id="auto-refresh" type="checkbox" checked>自动刷新</label><select id="auto-refresh-interval" aria-label="自动刷新间隔"><option value="60">1分钟</option><option value="300" selected>5分钟</option><option value="900">15分钟</option></select><span id="auto-refresh-countdown" class="auto-countdown"></span>' if live else ''
    periods=sorted({risk_by_symbol.get(a['symbol'],{}).get('asof_session','缺失') for a in assets})
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><meta name="referrer" content="no-referrer"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src data:; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'; base-uri 'none'; form-action 'none'"><title>ETF与个股观察 · {date}</title><style>{css}</style></head><body id="top"><a class="skip-link" href="#main">跳转到正文</a><div class="page"><header class="masthead"><div><p class="eyebrow">投资研究 · 收益与风险</p><h1>ETF与个股观察</h1></div><div class="edition"><time>{date.replace('-','.')}</time><span>北京时间</span></div></header><nav class="navigation" aria-label="页面目录"><a href="#etfs">ETF基金 · {len(funds)}</a><a href="#stocks">个股 · {len(stocks)}</a><a href="#method">指标口径</a><button id="print-report" type="button">打印 / 保存PDF</button></nav><main id="main"><section class="introduction"><p id="catalog-data-times">常规报价采用美股{esc(data.get('regular_session','日期缺失'))}；历史指标截至{' / '.join(esc(x) for x in periods)}，各卡片分别注明。</p><p class="compact-guide">悬停展开详情，点击固定查看。回报含分红复权；DRAM显示成立以来，历史指标采用已完成常规交易日。基金持仓与财报保留各自披露日期。</p></section><div class="catalog-toolbar"><label class="search-label"><span class="visually-hidden">搜索标的</span><input id="search" type="search" placeholder="搜索代码、名称或类别"></label><div class="type-tabs" role="group" aria-label="标的类型"><button class="active" data-kind="all" aria-pressed="true">全部</button><button data-kind="fund" aria-pressed="false">ETF</button><button data-kind="stock" aria-pressed="false">个股</button></div><span id="result-count" aria-live="polite">{count}项观察</span>{refresh_control}{auto_control}</div><p id="refresh-status" class="refresh-status" role="status" aria-live="polite">{'刷新可更新行情与指标；经营研究另按披露日期。' if live else '离线快照 · 可打开本地可刷新版使用固定地址。'}</p><div id="catalog-assets">{''.join(sections)}</div><p id="empty-state" class="empty-state" hidden>没有匹配标的。可清空搜索或切换类别。</p><section id="method" class="report-section"><h2>收益与风险指标口径</h2><details><summary>如何读这些数字</summary><div class="method-grid"><div><h3>收益、波动与最大回撤</h3><p>近一年总回报使用提供方含分红再投资及拆股调整的复权收盘价。起点取一年前当日或此前最近交易日；不足一年从最早有效交易日开始，回报不强行年化。</p><p>年化波动率为区间日收益率样本标准差 × √252。最大回撤为同一区间复权收盘序列相对截至当日历史峰值的最深跌幅，不包含盘中路径。</p></div><div><h3>均线与当前回撤</h3><p>50/200日均线使用最近50/200个交易日拆股调整、未做分红再投资的收盘价。偏离 = 对应指标日收盘 ÷ 均线 − 1。</p><p>距52周盘中高点以同一截至日收盘相对过去364个日历日最高价计算。它与区间最大回撤含义不同；成立不足52周时留空。数据不足200日时留空，不填估计。</p></div></div></details><details><summary>来源、时点与持仓边界</summary><p>历史指标来源为Yahoo日线及复权序列，保留原始响应和逐日数据。各项完整日线日期见页首和卡片。以后若最新日线不完整，指标停在实际可验证日期并标注，不用独立报价快照补造日线。部分复权异常或缺失会在卡片中降级为价格回报或标缺失。</p><p>基金持仓为发行人各自披露日数据，股票与互换敞口口径另注。MAGS/DRAM现金担保品不作为低风险配置比例。成立以来年化波动仅用于描述已发生区间，不能代表长期风险。</p><p>Google实际持股为GOOG C类；本研究清单的GOOGL A类仍作公司研究对照，两者价格和成本分别计算。本页不复制私人的持仓股数和成本。</p><p>预算30,000美元、期限3–5年及约20%暂时亏损容忍继续作为研究背景；新增观察不增加风险预算或改变QQQM、VOO、BRK.B三项15%/25%提醒。</p></details><p class="download-row"><a id="catalog-export" download="watchlist_metrics.json" href="data:application/json;base64,{payload}">下载指标、持仓披露与来源数据</a></p></section></main><footer><span>ETF与个股观察 · {date} · 已保存研究</span><a href="#top">回到顶部 ↑</a></footer></div><aside id="asset-hover-panel" class="asset-hover-panel" role="dialog" aria-modal="false" aria-label="标的详情" hidden></aside><dialog id="asset-dialog" aria-label="标的详情"><div class="detail-toolbar"><span id="dialog-label">标的详情</span><button type="button" id="close-detail">关闭</button></div><div id="dialog-body" class="detail-body"></div></dialog><script id="catalog-runtime" type="application/json">{runtime}</script><script>{script}</script></body></html>'''


def main():
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--metrics',type=Path)
    args=p.parse_args();data=json.loads(args.data.read_text());mp=args.metrics or args.data.with_name('risk_metrics.json')
    if not mp.exists():raise ValueError('Verified historical metrics are required; run catalog_metrics.py first')
    risks=json.loads(mp.read_text());doc=render(data,risks);args.out.write_text(doc)
    args.out.with_name('catalog_manifest.json').write_text(json.dumps({'input':str(args.data),'metrics':str(mp),'output':str(args.out),'assets':sum(len(g['assets']) for g in data['groups']),'layout':'all ETFs together, stocks separate; daily report shared style','sha256':hashlib.sha256(doc.encode()).hexdigest(),'external_runtime_requests':False},ensure_ascii=False,indent=2))
    print(args.out)

if __name__=='__main__':main()
