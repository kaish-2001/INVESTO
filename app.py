
import streamlit as st, yfinance as yf, pandas as pd, numpy as np
from engines.safe import display_df, kv_df
from engines.technical import tech
from engines.entry_exit import build_trade_plan
from engines.oi import get_oi_snapshot
from engines.fundamentals import financials, ratio_analysis, fmt_financial_table
from engines.valuation_pro import dcf_valuation, relative_valuation, valuation_summary
from engines.market_data import fii_dii_flow, market_ownership_note
from engines.screener import fetch_shareholding
from engines.sector import framework
from engines.scoring import score
from engines.alternatives import alternatives

st.set_page_config(page_title="Buddyy",page_icon="📈",layout="wide")
st.markdown("""<style>.block-container{max-width:1500px;padding-top:1.2rem}.brand{font-size:44px;font-weight:900;letter-spacing:-2px}.brand span{color:#4da3ff}.muted{color:#8fa3bb}</style>""",unsafe_allow_html=True)

def money(x):
    try:
        if x is None or pd.isna(x): return "N/A"
        return f"₹{float(x):,.2f}"
    except:return "N/A"
def pct(x):
    try:
        if x is None or pd.isna(x): return "N/A"
        return f"{float(x):.2f}%"
    except:return "N/A"
def fmt_ratio(name,v):
    if v is None or (isinstance(v,float) and pd.isna(v)): return "N/A"
    if any(k in name for k in ["ROE","ROA","Margin","Growth","CAGR"]): return pct(float(v)*100 if abs(float(v))<2 else float(v))
    return f"{float(v):.2f}"

def symbolize(q):
    q=q.strip().upper().replace(" ","")
    return q if q.endswith(".NS") else q+".NS"

def analyze(q):
    sym=symbolize(q); y=yf.Ticker(sym); info=y.info
    if not info: raise ValueError("No data found. Try an NSE ticker such as AFCONS, RELIANCE, TCS or ICICIBANK.")
    hist=y.history(period="2y",auto_adjust=False)
    if hist.empty: raise ValueError("No historical price data returned.")
    price=float(info.get("currentPrice") or info.get("regularMarketPrice") or hist["Close"].iloc[-1])
    name=info.get("longName") or info.get("shortName") or sym.replace(".NS","")
    sector=info.get("sector") or "Unknown"; industry=info.get("industry") or "Unknown"
    fin=financials(y); ratios=ratio_analysis(fin,info); technical=tech(hist)
    share=fetch_shareholding(sym)
    oi=get_oi_snapshot(sym,price)
    # Initial valuation objects; relative valuation may query peer companies.
    dcf=dcf_valuation(fin,info,price)
    rel=relative_valuation(sym,sector,industry,info,price)
    val=valuation_summary(price,dcf,rel)
    plan=build_trade_plan(price,technical,oi,val); sc=score(info,technical,val)
    flow=fii_dii_flow()
    return locals()

st.markdown('<div class="brand">buddyy<span>.</span></div><div class="muted">Fundamental • Technical • Valuation • Price Action • Ownership</div>',unsafe_allow_html=True)
q=st.text_input("Enter company name or NSE ticker","AFCONS",placeholder="AFCONS, RELIANCE, TCS, ICICIBANK")
if st.button("🔎 ANALYZE / REFRESH",type="primary"):
    st.cache_data.clear()

try:
    d=analyze(q)
except Exception as e:
    st.error(f"Analysis error: {e}"); st.stop()

i=d["info"]; t=d["technical"]; v=d["val"]; p=d["plan"]; oi=d["oi"]; sc=d["sc"]
verdict="STRONG BUY" if sc["overall"]>=85 else "BUY" if sc["overall"]>=75 else "HOLD / WATCH" if sc["overall"]>=60 else "AVOID"
st.subheader(d.get("name") or d["sym"])
st.caption(f'{d["sym"]} • {d["sector"]} → {d["industry"]}')
cols=st.columns(6)
for col,label,val in zip(cols,["Current","Entry","Stop","Target 1","Target 2","Decision"],
                         [money(d["price"]),money(p["entry"]),money(p["stop"]),money(p["target1"]),money(p["target2"]),f'{p["decision"]} • {sc["overall"]}/100']):
    col.metric(label,val)
st.info(p["reason"])

tabs=st.tabs(["Overview","Entry/Exit","Technical","Price Action","Open Interest","Ownership & FII/DII","Financials","Ratios","Sector Ratios","DCF / FCFF / FCFE","Relative Valuation","5 Alternatives"])

with tabs[0]:
    st.subheader("Price & volume")
    st.line_chart(d["hist"]["Close"].tail(252))
    st.dataframe(kv_df([
        ("Market Cap",money((i.get("marketCap") or 0)/1e7)+" Cr" if i.get("marketCap") else "N/A"),
        ("P/E",money(i.get("trailingPE"))),("P/B",money(i.get("priceToBook"))),
        ("Revenue Growth",pct((i.get("revenueGrowth") or 0)*100)),
        ("ROE",pct((i.get("returnOnEquity") or 0)*100)),("Debt/Equity",money(i.get("debtToEquity")))
    ]),hide_index=True,use_container_width=True)

with tabs[1]:
    st.subheader("Current-price entry / exit engine")
    st.dataframe(kv_df([
        ("Decision",p["decision"]),("Signal score",p["score"]),("Trend",p["trend"]),("Pattern",p["pattern"]),
        ("Candlestick",p["candlestick"]),("Price-volume",p["volume_signal"]),("OI confirmation",oi["signal"]),
        ("Support",money(t["Support"])),("Resistance",money(t["Resistance"])),("Entry",money(p["entry"])),
        ("Stop / invalidation",money(p["stop"])),("Target 1",money(p["target1"])),("Target 2",money(p["target2"])),("Risk/Reward",p["risk_reward"])
    ]),hide_index=True,use_container_width=True)

with tabs[2]:
    st.subheader("Technical indicators")
    display={k:v for k,v in t.items() if not k.startswith("_")}
    st.dataframe(kv_df([(k,fmt_ratio(k,x) if isinstance(x,(int,float,np.number)) else x) for k,x in display.items()]),hide_index=True,use_container_width=True)

with tabs[3]:
    st.subheader("Price-action engine")
    st.dataframe(kv_df([("Trend",p["trend"]),("Chart pattern",p["pattern"]),("Candlestick",p["candlestick"]),
                        ("Volume confirmation",p["volume_signal"]),("Support",money(t["Support"])),("Resistance",money(t["Resistance"])),
                        ("Breakout watch",t.get("Breakout","N/A"))]),hide_index=True,use_container_width=True)

with tabs[4]:
    st.subheader("Open Interest / PCR")
    if oi["available"]:
        a,b,c,e=st.columns(4)
        a.metric("PCR", "N/A" if oi["pcr"] is None else f'{oi["pcr"]:.2f}')
        b.metric("Max Pain",money(oi["max_pain"])); c.metric("Call Wall",money(oi.get("call_wall"))); e.metric("Put Wall",money(oi.get("put_wall")))
        if oi.get("levels") is not None: st.dataframe(display_df(oi["levels"]),hide_index=True,use_container_width=True)
        st.caption(f'Source: {oi["source"]} • Expiry: {oi.get("expiry","N/A")}')
    else: st.warning(oi["message"])
    st.caption("Buddyy does not fabricate PCR/OI when the provider returns no option chain.")

with tabs[5]:
    st.subheader("Stock-level shareholding")
    if d["share"] is not None:
        st.dataframe(display_df(d["share"]["table"]),hide_index=True,use_container_width=True)
        st.info(f'{d["share"]["source"]} • {d["share"]["latest"]}')
    else:
        st.warning("Stock-level promoter/FII/DII shareholding could not be fetched from the public fallback.")
    st.subheader("Market-level FII / DII cash flow")
    flow=d["flow"]
    if flow["available"]:
        st.dataframe(display_df(flow["data"].tail(10)),hide_index=True,use_container_width=True)
    else: st.warning(flow["source"])
    st.caption(market_ownership_note())

with tabs[6]:
    st.subheader("Income statement")
    st.dataframe(display_df(d["fin"]["income"].reset_index().rename(columns={"index":"Line Item"})),hide_index=True,use_container_width=True)
    st.subheader("Balance sheet")
    st.dataframe(display_df(d["fin"]["balance"].reset_index().rename(columns={"index":"Line Item"})),hide_index=True,use_container_width=True)
    st.subheader("Cash flow")
    st.dataframe(display_df(d["fin"]["cashflow"].reset_index().rename(columns={"index":"Line Item"})),hide_index=True,use_container_width=True)

with tabs[7]:
    st.subheader("Calculated financial ratios")
    rr=d["ratios"].copy()
    rr["Calculated Value"]=rr["Calculated Value"].map(lambda x: fmt_ratio("",x) if isinstance(x,(int,float,np.number)) else ("N/A" if x is None else str(x)))
    st.dataframe(display_df(rr),hide_index=True,use_container_width=True)

with tabs[8]:
    st.subheader(f"Relevant ratios for {d['sector']}")
    relevant=framework(d["sector"])
    available={r["Ratio"]:r["Calculated Value"] for _,r in d["ratios"].iterrows()}
    rows=[]
    for name in relevant:
        rows.append((name,fmt_ratio(name,available.get(name))))
    st.dataframe(kv_df(rows,"Relevant Ratio","Calculated / Available"),hide_index=True,use_container_width=True)
    st.caption("Sector-specific ratios are selected first; ratios are calculated only where the financial statements/data support the formula.")

with tabs[9]:
    st.subheader("DCF valuation — FCFF & FCFE")
    dc=d["dcf"]
    st.dataframe(kv_df([("FCFF value / share",money(dc.get("fcff_per_share"))),("FCFE value / share",money(dc.get("fcfe_per_share"))),
                        ("Blended DCF / share",money(dc.get("blended_per_share")))]),hide_index=True,use_container_width=True)
    st.subheader("5-year forecast")
    st.dataframe(display_df(dc["forecast"].assign(Growth=dc["forecast"]["Growth"].map(lambda x:pct(x*100))),),hide_index=True,use_container_width=True)
    st.subheader("DCF assumptions and values")
    st.dataframe(kv_df([(a,money(b) if a not in ["WACC","Cost of Equity","Tax Rate","Terminal Growth"] else pct(b*100)) for a,b in dc["metrics"]]),hide_index=True,use_container_width=True)
    st.subheader("FCFF sensitivity: Fair value / share")
    st.dataframe(display_df(dc["sensitivity"].round(2)),hide_index=True,use_container_width=True)

with tabs[10]:
    st.subheader("Relative valuation")
    rel=d["rel"]
    st.write("Peer set is selected from the company's business/industry mapping, not from a generic market list.")
    st.dataframe(display_df(rel["peers"].round(2)),hide_index=True,use_container_width=True)
    st.subheader("Relative fair values")
    st.dataframe(display_df(rel["fair_values"].round(2)),hide_index=True,use_container_width=True)
    st.dataframe(kv_df([("Blended fair value",money(v["fair_value"])),("Upside / downside",pct(v["upside_pct"])),("Classification",v["classification"])]),hide_index=True,use_container_width=True)

with tabs[11]:
    st.subheader("5 potentially stronger alternatives")
    alt=alternatives(d["sym"],d["sector"],d["industry"])
    st.dataframe(display_df(pd.DataFrame(alt)),hide_index=True,use_container_width=True)
    st.caption("Alternatives are ranked within the mapped peer universe; they are not guaranteed to outperform.")

st.caption("Buddyy is decision-support software. Market data can be delayed, incomplete or unavailable. Valuation outputs depend on assumptions and are not guaranteed returns.")
