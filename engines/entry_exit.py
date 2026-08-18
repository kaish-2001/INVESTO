
import math

def clamp(x, lo, hi):
    return max(lo,min(hi,x))

def build_trade_plan(price,hist,t,oi,val):
    support=t["Support"]; resistance=t["Resistance"]; atr=t.get("_atr") or price*.02
    trend=t.get("_trend","Mixed"); pattern=t.get("_pattern","Range"); candle=t.get("_candlestick","Neutral")
    volume=t.get("_volume_signal","No strong confirmation")
    oi_signal=oi.get("signal","Unavailable")
    bullish=0; bearish=0
    bullish += 2 if trend=="Bullish" else -2 if trend=="Bearish" else 0
    bullish += 2 if pattern=="Bullish breakout setup" else 1 if pattern=="Near support" else 0
    bullish += 1 if candle in ("Bullish engulfing","Hammer") else -1 if candle=="Bearish engulfing" else 0
    bullish += 1 if volume=="Strong buying volume" else -1 if volume=="Strong selling volume" else 0
    bullish += 1 if "Bullish" in oi_signal else -1 if "Bearish" in oi_signal else 0
    # Entry logic: never chase a breakout blindly. Prefer pullback to support/EMA or confirmed breakout.
    if bullish >= 4 and price >= resistance*.99:
        entry=price
        stop=max(support, price-1.5*atr)
        reason="Confirmed/near breakout with multiple bullish confirmations; entry is current price only because price is already at resistance."
    elif bullish >= 2 and price > support:
        entry=min(price, (support+price)/2)
        stop=max(support-0.25*atr, price-1.5*atr)
        reason="Bullish/mixed structure: prefer a pullback toward support rather than chasing."
    elif bullish <= -2:
        entry=support
        stop=support-1.0*atr
        reason="Weak setup: Buddyy prefers waiting near support instead of buying current price."
    else:
        entry=(support+resistance)/2
        stop=support-0.75*atr
        reason="Signals conflict: wait for price confirmation at support or breakout resistance."
    fair=val.get("fair_value")
    t1=resistance if resistance>entry else entry+1.5*atr
    if fair and fair>entry: t1=max(t1,min(fair,entry+3*atr))
    t2=max(t1+1.5*atr, fair if fair and fair>t1 else t1+2*atr)
    risk=max(entry-stop,0.01); rr=(t1-entry)/risk
    if rr<1.5:
        reason += " Risk/reward to the first target is below 1.5x, so the setup should be treated cautiously."
    return {
      "entry":float(entry),"stop":float(stop),"target1":float(t1),"target2":float(t2),
      "risk_reward":f"{rr:.2f}x","reason":reason,
      "trend":trend,"pattern":pattern,"candlestick":candle,"volume_signal":volume,
      "momentum":"Bullish" if bullish>=2 else "Bearish" if bullish<=-2 else "Mixed"
    }
