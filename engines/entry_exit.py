
def build_trade_plan(price,t,oi,val):
    support=t["Support"]; resistance=t["Resistance"]; atr=t.get("ATR 14") or price*.02
    trend=t.get("_trend","Mixed"); pattern=t.get("_pattern","Range"); candle=t.get("_candlestick","Neutral"); volume=t.get("_volume_signal","No strong confirmation")
    ois=oi.get("signal","Unavailable")
    score=0
    score+=2 if trend=="Bullish" else -2 if trend=="Bearish" else 0
    score+=2 if pattern=="Bullish breakout setup" else 1 if pattern=="Near support" else 0
    score+=1 if candle in ("Bullish engulfing","Hammer") else -1 if candle=="Bearish engulfing" else 0
    score+=1 if volume=="Strong buying volume" else -1 if volume=="Strong selling volume" else 0
    score+=1 if "Bullish" in ois else -1 if "Bearish" in ois else 0
    if score>=4 and price>=resistance*.99:
        entry=price; stop=max(support,price-1.5*atr); reason="Breakout/continuation setup with multiple confirmations."
    elif score>=2 and price>support:
        entry=min(price,(support+price)/2); stop=max(support-.25*atr,price-1.5*atr); reason="Bullish/mixed structure; prefer a pullback instead of chasing."
    elif score<=-2:
        entry=support; stop=support-atr; reason="Weak setup; wait near structural support."
    else:
        entry=(support+resistance)/2; stop=support-.75*atr; reason="Signals conflict; wait for support confirmation or a volume-backed breakout."
    fair=val.get("fair_value")
    target1=resistance if resistance>entry else entry+1.5*atr
    if fair and fair>entry: target1=max(target1,min(fair,entry+3*atr))
    target2=max(target1+1.5*atr,fair if fair and fair>target1 else target1+2*atr)
    rr=(target1-entry)/max(entry-stop,.01)
    decision="BUY" if score>=4 and rr>=1.5 else "WAIT" if score>=-1 else "AVOID"
    if rr<1.5: reason+=" First-target risk/reward is below 1.5x."
    return {"entry":entry,"stop":stop,"target1":target1,"target2":target2,"risk_reward":f"{rr:.2f}x","reason":reason,
            "trend":trend,"pattern":pattern,"candlestick":candle,"volume_signal":volume,"momentum":"Bullish" if score>=2 else "Bearish" if score<=-2 else "Mixed",
            "decision":decision,"score":score}
