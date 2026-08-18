
import math

def get_oi_snapshot(symbol, price):
    """
    Best-effort Yahoo/yfinance options snapshot for the prototype.
    OI interpretation is used as confirmation, not as a standalone signal.
    For Indian production use, replace with an authorized exchange-grade OI feed.
    """
    try:
        import yfinance as yf
        t=yf.Ticker(symbol)
        exps=t.options
        if not exps:
            return {"available":False,"message":"No options chain available from the prototype provider.","pcr":None,"max_pain":None,"signal":"Unavailable","levels":[]}
        exp=exps[0]
        chain=t.option_chain(exp)
        calls=chain.calls.copy(); puts=chain.puts.copy()
        calls["openInterest"]=calls["openInterest"].fillna(0); puts["openInterest"]=puts["openInterest"].fillna(0)
        pcr=float(puts.openInterest.sum()/calls.openInterest.sum()) if calls.openInterest.sum() else None
        strikes=sorted(set(calls.strike.tolist())|set(puts.strike.tolist()))
        # Max pain: total intrinsic payout across call/put OI at each candidate strike.
        pain=[]
        for k in strikes:
            call_pain=((k-calls.strike).clip(lower=0)*calls.openInterest).sum()
            put_pain=((puts.strike-k).clip(lower=0)*puts.openInterest).sum()
            pain.append((k,float(call_pain+put_pain)))
        max_pain=min(pain,key=lambda x:x[1])[0] if pain else None
        atm=min(strikes,key=lambda x:abs(x-price)) if strikes else None
        near=[k for k in strikes if atm is not None and abs(k-atm)<=max(abs(atm*.04),100)]
        levels=[]
        for k in near:
            co=float(calls.loc[calls.strike==k,"openInterest"].sum())
            po=float(puts.loc[puts.strike==k,"openInterest"].sum())
            levels.append({"Strike":k,"Call OI":co,"Put OI":po})
        call_max=max(levels,key=lambda x:x["Call OI"])["Strike"] if levels else None
        put_max=max(levels,key=lambda x:x["Put OI"])["Strike"] if levels else None
        if pcr is not None:
            signal="Bullish OI bias" if pcr>1.15 else "Bearish OI bias" if pcr<0.75 else "Neutral OI bias"
        else: signal="Neutral / unavailable"
        return {"available":True,"expiry":exp,"pcr":pcr,"max_pain":max_pain,"signal":signal,
                "call_wall":call_max,"put_wall":put_max,"levels":levels,
                "message":"Prototype options-chain OI; validate freshness."}
    except Exception as e:
        return {"available":False,"message":f"OI unavailable from provider: {e}","pcr":None,"max_pain":None,"signal":"Unavailable","levels":[]}
