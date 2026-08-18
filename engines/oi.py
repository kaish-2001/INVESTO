
from engines.market_data import nse_option_chain
import yfinance as yf

def get_oi_snapshot(symbol,price):
    x=nse_option_chain(symbol,price)
    if x: return x
    # Yahoo fallback; if unavailable, do not fabricate PCR.
    try:
        t=yf.Ticker(symbol); exps=t.options
        if not exps: raise ValueError("No options chain")
        ch=t.option_chain(exps[0]); c=ch.calls.copy(); p=ch.puts.copy()
        coi=c["openInterest"].fillna(0).sum(); poi=p["openInterest"].fillna(0).sum()
        pcr=float(poi/coi) if coi else None
        signal="Bullish OI bias" if pcr and pcr>1.15 else "Bearish OI bias" if pcr and pcr<.75 else "Neutral OI bias"
        return {"available":True,"source":"Yahoo/yfinance fallback","expiry":exps[0],"pcr":pcr,"max_pain":None,"call_wall":None,"put_wall":None,"signal":signal,
                "levels":c[["strike","openInterest"]].head(0),"message":"Fallback options-chain data."}
    except Exception as e:
        return {"available":False,"source":"Unavailable","pcr":None,"max_pain":None,"call_wall":None,"put_wall":None,"signal":"Unavailable",
                "levels":None,"message":"No options-chain data was returned. Buddyy will not invent PCR/OI."}
