from pathlib import Path
import json
from datetime import datetime, timezone

out = Path(__file__).parent
metrics = {row["symbol"]: row for row in json.loads((out / "metrics.json").read_text())}
reviewed = datetime.now(timezone.utc).isoformat()
models = {}

def add(symbol, base, stress, method, next_check, urls):
    close = metrics[symbol]["close"]
    threshold = .8 * base
    judgment = "基准情景达到八折筛选线，仍需压力测试" if close <= threshold else "当前价格未达基准情景的八折筛选线"
    if close > base:
        judgment = "当前价格高于基准情景估值"
    models[symbol] = dict(
        judgment=judgment,
        basis=f"11/12 Yahoo常规收盘 {close:.2f} 美元。{method} 基准 {base:.2f} 美元，压力 {stress:.2f} 美元，基准八折 {threshold:.2f} 美元。倍数和折扣均为研究假设。",
        next=next_check, reviewed_at=reviewed, market_session="2026-11-12",
        base_value=round(base, 2), stress_value=round(stress, 2),
        discount_price=round(threshold, 2),
        sources=[{"title": title, "url": url} for title, url in urls],
    )

add("INTC", (66*.17-.5)*.8/5.307*22, (60*.08-.5)*.8/5.307*16,
    "Q3收入165.13亿美元、经营利润25.22亿美元；代工部门亏损18.53亿美元。情景年收入660/600亿美元、营业率17%/8%，各扣5亿美元净利息假设、税率20%，除以53.07亿稀释股，分别乘22/16倍。剔除非经营收益，不以季度GAAP净利润直接年化。",
    "核代工非经常合同、18A良率、净资本支出和股数变化。", [
      ("Intel Q3 10-Q","https://www.intc.com/filings-reports/all-sec-filings/content/0000050863-26-000191/intc-20260926.htm")])
add("SNDK", 52.6*4*.55*10, 52.6*4*.30*8,
    "FY27Q1 GAAP稀释EPS 52.60美元。以季度年化为峰值参照，基准按55%保留、10倍，压力按30%保留、8倍，测试NAND价格和利润回落。均为拆股前每股口径，8比1拆股生效后价位须同步除8。",
    "核NAND售价、库存、合资采购承诺与拆股实际生效日。", [
      ("Sandisk FY27Q1业绩","https://investor.sandisk.com/node/8476/pdf")])
add("SKHY", 110/.7110755/1500/10*14*1000, 65/.7110755/1600/10*10*1000,
    "Q3初步净利39.7756万亿韩元，避免直接年化利润高点。基准/压力假设年净利110/65万亿韩元、14/10倍，暂用招股书披露的2026年7月约7.11亿流通股作为敏感性分母，并以1500/1600韩元兑1美元作假设；每ADS为十分之一普通股。股数和汇率均不冒充11/12现值。",
    "核最新K-IFRS加权股数、实际汇率、HBM合同价格与扩产现金支出。", [
      ("SK hynix Q3初步业绩","https://news.skhynix.com/en/q3-2026-business-results/"),
      ("SEC ADS招股书","https://www.sec.gov/Archives/edgar/data/2120882/000119312526299963/d32785d424b4.htm")])
add("ATS", 1.45*16/1.4181, .85*12/1.4181,
    "FY26调整基本EPS 1.69加元，FY27Q2降至0.27加元且公司不再预计达到原年度增长和扩利润率目标。基准/压力假设1.45/0.85加元与16/12倍；用加拿大央行11/10每美元1.4181加元作换算参照。调整口径可能高估现金兑现。",
    "核订单变收入、经营现金转化及债务，更新同日报价汇率。", [
      ("ATS季度公告","https://www.sec.gov/Archives/edgar/data/1394832/000139483226000028/ats-pressreleasexfy27q2.htm"),
      ("ATS年报","https://s201.q4cdn.com/979379719/files/doc_financials/2026/ar/ATS2026-AR_COMPLETE-BOOK.pdf"),
      ("加拿大央行汇率","https://www.bankofcanada.ca/rates/exchange/daily-exchange-rates-lookup/?dF=2026-11-10&dT=2026-11-12&se=FXUSDCAD")])
add("RRX", 9.85*17, 7.5*13,
    "2026调整EPS指引中值10.75美元，扣退款贡献0.58与SBC加回0.32得9.85；基准乘17倍，压力EPS 7.50乘13倍。仍含其他调整，需以现金回收复核。",
    "核AMS退出、债务与自由现金流，避免用机器人叙事给全公司估值。", [
      ("Regal Rexnord Q3公告","https://www.sec.gov/Archives/edgar/data/82811/000008281126000236/a3q2026earningsannouncement.htm")])
add("SOFI", 7.48*(.16-.04)/(.11-.04), 7.48*(.10-.03)/(.14-.03),
    "9/30每股有形账面价值7.48美元。用稳态P/TBV=(ROTCE−g)/(权益成本−g)：基准16%/4%/11%，压力10%/3%/14%。ROTCE是可持续假设，不能用单季EPS简单年化。",
    "跟踪贷款净核销率、真实资本占用、股权稀释和ROTCE。", [
      ("SoFi Q3 10-Q","https://www.sec.gov/Archives/edgar/data/1818874/000181887426000070/sofi-20260930.htm"),
      ("SoFi Q3业绩","https://www.sec.gov/Archives/edgar/data/1818874/000181887426000065/a2026q3earningsrelease.htm")])
add("GOOGL", 125/12.294*24, 80/12.294*18,
    "Q3经营现金流422.90亿美元、现金资本开支513.55亿美元。使用扣除维持与增长投资、并考虑股权激励经济成本后的长期股东现金流假设1250/800亿美元，除10/21三类合计122.94亿股，分别乘24/18倍。为稳态敏感性，尚未实现，不将Q3负现金流简单年化。",
    "核TPU库存转订单与回款、资本开支兑现及云利润向现金的转化。", [
      ("Alphabet Q3 10-Q","https://www.sec.gov/Archives/edgar/data/1652044/000165204426000084/goog-20260930.htm")])
add("NVDA", (108*.74-9.2)*.83*4/24.285*20, (91.8*.70-9.2)*.83*4/24.285*16,
    "FY27Q3指引年化经营情景：基准季度收入1080亿美元、毛利率74%；压力收入918亿美元、毛利率70%。各扣92亿美元营业费用、税率17%，年化除242.85亿稀释股，乘20/16倍。剔除投资收益，单季年化有周期偏差。",
    "11/17核经营指引、毛利、资本承诺及CEO交接。", [
      ("NVIDIA Q2及Q3指引","https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-second-quarter-fiscal-2027"),
      ("CEO交接8-K","https://www.sec.gov/Archives/edgar/data/1045810/000104581026000082/nvda-20261111.htm")])
models["NVDA"]["judgment"] = "CEO交接已确认；现价未达基准八折，等待11/17经营验证。"
models["SKHY"]["judgment"] = "按7月股数及汇率假设，现价未达基准八折；待更新股数和汇率。"
(out/"valuation_core.json").write_text(json.dumps(models,ensure_ascii=False,indent=2)+"\n")
