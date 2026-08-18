
import requests, pandas as pd
from datetime import datetime

NSE="https://www.nseindia.com"
HEADERS={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/151 Safari/537.36",
         "Accept":"application/json,text/plain,*/*","Referer":"https://www.nseindia.com/"}

def _session():
    s=requests.Session(); s.headers.update(HEADERS)
    try: s.get(NSE,timeout=8)
    except Exception: pass
    return s

def nse_option_chain(symbol, price):
    s=_session()
    try:
        r=s.get(f"{NSE}/api/option-chain-equities",params={"symbol":symbol.replace(".NS","").upper()},timeout=12)
        if r.status_code!=200: return None
        data=r.json().get("records",{})
        rows=data.get("data",[])
        if not rows: return None
        expiries=data.get("expiryDates",[])
        expiry=expiries[0] if expiries else None
        selected=[x for x in rows if not expiry or x.get("expiryDate")==expiry]
        strikes=[]
        for x in selected:
            sp=x.get("strikePrice")
            if sp is None: continue
            ce=x.get("CE") or {}; pe=x.get("PE") or {}
            strikes.append({"Strike":sp,"Call OI":ce.get("openInterest",0),"Call ΔOI":ce.get("changeinOpenInterest",0),
                            "Call Volume":ce.get("totalTradedVolume",0),"Put OI":pe.get("openInterest",0),
                            "Put ΔOI":pe.get("changeinOpenInterest",0),"Put Volume":pe.get("totalTradedVolume",0)})
        df=pd.DataFrame(strikes)
        if df.empty: return None
        for c in df.columns[1:]: df[c]=pd.to_numeric(df[c],errors="coerce").fillna(0)
        pcr=float(df["Put OI"].sum()/df["Call OI"].sum()) if df["Call OI"].sum() else None
        # Max pain.
        pain=[]
        for k in df["Strike"]:
            call=((k-df["Strike"]).clip(lower=0)*df["Call OI"]).sum()
            put=((df["Strike"]-k).clip(lower=0)*df["Put OI"]).sum()
            pain.append((k,call+put))
        max_pain=min(pain,key=lambda x:x[1])[0] if pain else None
        atm=float(df.iloc[(df["Strike"]-price).abs().argsort()[:1]]["Strike"].iloc[0])
        near=df[(df["Strike"]>=atm-price*.06)&(df["Strike"]<=atm+price*.06)].copy()
        call_wall=float(df.loc[df["Call OI"].idxmax(),"Strike"]) if not df.empty else None
        put_wall=float(df.loc[df["Put OI"].idxmax(),"Strike"]) if not df.empty else None
        signal="Bullish OI bias" if pcr and pcr>1.15 else "Bearish OI bias" if pcr and pcr<0.75 else "Neutral OI bias"
        return {"available":True,"source":"NSE option-chain endpoint","expiry":expiry,"pcr":pcr,"max_pain":max_pain,
                "call_wall":call_wall,"put_wall":put_wall,"signal":signal,"levels":near,"message":"Live NSE option-chain response."}
    except Exception as e:
        return None

def fii_dii_flow():
    s=_session()
    endpoints=["/api/fiidiiTradeReact","/api/fiidiiTrade"]
    for ep in endpoints:
        try:
            r=s.get(NSE+ep,timeout=10)
            if r.status_code!=200: continue
            data=r.json()
            if isinstance(data,dict):
                data=data.get("data") or data.get("records") or []
            if isinstance(data,list) and data:
                return {"available":True,"data":pd.DataFrame(data),"source":"NSE FII/DII market-flow endpoint"}
        except Exception: pass
    return {"available":False,"data":pd.DataFrame(),"source":"NSE FII/DII endpoint unavailable from this deployment"}

def market_ownership_note():
    return "FII/DII flow is market-level. Stock-level FII/DII ownership is shown separately from the quarterly shareholding filing."
