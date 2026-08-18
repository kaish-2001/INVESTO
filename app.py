
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timezone

from engines.technical import tech
from engines.valuation import valuation
from engines.sector import framework
from engines.scoring import score
from engines.alternatives import alternatives
from engines.entry_exit import build_trade_plan
from engines.oi import get_oi_snapshot

st.set_page_config(page_title="Buddyy", page_icon="📈", layout="wide")

st.markdown("""
<style>
.block-container{max-width:1450px;padding-top:1.5rem}
.brand{font-size:42px;font-weight:900;letter-spacing:-2px}.brand span{color:#4da3ff}
.muted{color:#8fa3bb}
.signal{padding:18px;border:1px solid #26384f;border-radius:14px;background:#101c2d}
.small{font-size:.78rem;color:#8fa3bb}
</style>
""", unsafe_allow_html=True)

def money(x):
    return "N/A" if x is None or pd.isna(x) else f"₹{x:,.2f}"

def pct(x):
    return "N/A" if x is None or pd.isna(x) else f"{x:.2f}%"

def ticker(q):
    q=q.strip().upper().replace(" ","")
    return q if q.endswith(".NS") else q+".NS"

@st.cache_data(ttl=180, show_spinner=False)
def analyze(q):
    sym=ticker(q)
    t=yf.Ticker(sym)
    info=t.info
    if not info:
        raise ValueError("No data found. Try an NSE ticker such as RELIANCE, TCS or ICICIBANK.")
    hist=t.history(period="2y", auto_adjust=False)
    if hist.empty:
        raise ValueError("No historical price data returned.")
    price=float(info.get("currentPrice") or info.get("regularMarketPrice") or hist.Close.iloc[-1])
    sector=info.get("sector") or "Unknown"
    industry=info.get("industry") or "Unknown"
    technical=tech(hist)
    val=valuation(info, price)
    framework_data=framework(sector)
    oi=get_oi_snapshot(sym, price)
    plan=build_trade_plan(price, hist, technical, oi, val)
    scoring=score(info, technical, val)
    return dict(sym=sym,name=info.get("longName") or info.get("shortName") or q,
                info=info,hist=hist,price=price,sector=sector,industry=industry,
                technical=technical,valuation=val,framework=framework_data,
                oi=oi,plan=plan,scoring=scoring)

st.markdown('<div class="brand">buddyy<span>.</span></div><p class="muted">Your Intelligent Stock Research Buddy</p>', unsafe_allow_html=True)
q=st.text_input("Company / NSE ticker", "RELIANCE", placeholder="RELIANCE, TCS, ICICIBANK")
go=st.button("🔎 ANALYZE", type="primary")

if go or q:
    try:
        with st.spinner("Buddyy is reading price action, structure and derivatives data..."):
            d=analyze(q)
    except Exception as e:
        st.error(str(e)); st.stop()

    i=d["info"]; t=d["technical"]; v=d["valuation"]; p=d["plan"]; oi=d["oi"]; sc=d["scoring"]
    verdict="STRONG BUY" if sc["overall"]>=85 else "BUY" if sc["overall"]>=75 else "HOLD / WATCH" if sc["overall"]>=60 else "AVOID"

    st.subheader(d["name"])
    st.caption(f'{d["sym"]} • {d["sector"]} → {d["industry"]}')

    a,b,c,e=st.columns(4)
    a.metric("Current price",money(d["price"]))
    b.metric("Technical entry",money(p["entry"]))
    c.metric("Target 1",money(p["target1"]))
    e.metric("Signal",f'{verdict} • {sc["overall"]}/100')

    st.markdown("### Current-price trade plan")
    c1,c2,c3,c4,c5=st.columns(5)
    c1.metric("Entry",money(p["entry"]))
    c2.metric("Stop / invalidation",money(p["stop"]))
    c3.metric("Target 1",money(p["target1"]))
    c4.metric("Target 2",money(p["target2"]))
    c5.metric("Risk / Reward",p["risk_reward"])
    st.info(p["reason"])

    tabs=st.tabs(["Overview","Entry/Exit Engine","Technical","Price Action","Open Interest","Fundamental","Sector Ratios","Valuation","5 Alternatives"])

    with tabs[0]:
        st.subheader("Price & volume")
        st.line_chart(d["hist"].Close.tail(252))
        st.dataframe(pd.DataFrame({
            "Metric":["Market Cap","P/E","P/B","ROE","Revenue Growth","Debt/Equity"],
            "Value":[money(i.get("marketCap")/1e7)+" Cr" if i.get("marketCap") else "N/A",
                     i.get("trailingPE"),i.get("priceToBook"),
                     pct((i.get("returnOnEquity") or 0)*100),
                     pct((i.get("revenueGrowth") or 0)*100),i.get("debtToEquity")]
        }), hide_index=True, use_container_width=True)

    with tabs[1]:
        st.subheader("Entry / Exit Decision Engine")
        st.write("Buddyy derives levels from the current price plus market structure. It does not use a fixed percentage target.")
        st.dataframe(pd.DataFrame({
            "Component":["Current price","Support","Resistance","Pattern","Candlestick","Price-volume","Open Interest","Momentum","Final entry","Stop","Target 1","Target 2"],
            "Value":[money(d["price"]),money(t["support"]),money(t["resistance"]),p["pattern"],p["candlestick"],
                     p["volume_signal"],oi["signal"],p["momentum"],money(p["entry"]),money(p["stop"]),money(p["target1"]),money(p["target2"])]
        }), hide_index=True, use_container_width=True)
        st.caption("A level is valid only when multiple independent signals agree. If evidence conflicts, Buddyy can return WAIT rather than force an entry.")

    with tabs[2]:
        st.subheader("Technical indicators")
        st.dataframe(pd.DataFrame(list(t.items()), columns=["Indicator","Value"]), hide_index=True, use_container_width=True)

    with tabs[3]:
        st.subheader("Price-action engine")
        st.dataframe(pd.DataFrame({
            "Signal":["Trend","Pattern","Candlestick","Volume confirmation","Support","Resistance","Breakout watch"],
            "Reading":[p["trend"],p["pattern"],p["candlestick"],p["volume_signal"],money(t["support"]),money(t["resistance"]),t["breakout"]]
        }), hide_index=True, use_container_width=True)

    with tabs[4]:
        st.subheader("Open Interest")
        if oi["available"]:
            x,y,z=st.columns(3)
            x.metric("Put/Call OI", "N/A" if oi["pcr"] is None else f'{oi["pcr"]:.2f}')
            y.metric("Max pain", money(oi["max_pain"]))
            z.metric("OI signal", oi["signal"])
            st.dataframe(pd.DataFrame(oi["levels"]), use_container_width=True, hide_index=True)
        else:
            st.warning(oi["message"])
        st.caption("OI is relevant only when derivatives data is available for the security. The production version should use a licensed exchange-grade OI feed.")

    with tabs[5]:
        names=["Revenue Growth","Earnings Growth","P/E","Forward P/E","P/B","EV/EBITDA","ROE","ROA","Profit Margin","Operating Margin","Debt/Equity","EPS","FCF","Beta"]
        vals=[pct((i.get("revenueGrowth") or 0)*100),pct((i.get("earningsGrowth") or 0)*100),i.get("trailingPE"),i.get("forwardPE"),i.get("priceToBook"),i.get("enterpriseToEbitda"),
              pct((i.get("returnOnEquity") or 0)*100),pct((i.get("returnOnAssets") or 0)*100),pct((i.get("profitMargins") or 0)*100),
              pct((i.get("operatingMargins") or 0)*100),i.get("debtToEquity"),i.get("trailingEps"),i.get("freeCashflow"),i.get("beta")]
        st.dataframe(pd.DataFrame({"Metric":names,"Value":vals}),hide_index=True,use_container_width=True)

    with tabs[6]:
        st.subheader(f"Relevant ratios: {d['sector']}")
        st.write(d["framework"])

    with tabs[7]:
        st.subheader("Valuation")
        st.warning("Current package uses a transparent prototype P/E + P/B anchor. The next valuation upgrade should add normalized peer, historical and sector-specific DCF/FCFE methods.")
        st.dataframe(pd.DataFrame(list(v.items()),columns=["Metric","Value"]),hide_index=True,use_container_width=True)

    with tabs[8]:
        if st.button("Find 5 alternatives"):
            with st.spinner("Comparing candidates..."):
                st.dataframe(pd.DataFrame(alternatives(d["sym"],d["sector"])),hide_index=True,use_container_width=True)
        else:
            st.info("Click to rank five potentially stronger alternatives.")

    st.caption("Buddyy is investment research/decision support. Data may be delayed or incomplete. Entry/exit levels are model outputs, not guarantees.")
