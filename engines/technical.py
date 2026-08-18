
import pandas as pd

def last(s):
    s=s.dropna()
    return float(s.iloc[-1]) if len(s) else None

def tech(df):
    c,h,l,v=df["Close"].astype(float),df["High"].astype(float),df["Low"].astype(float),df["Volume"].astype(float)
    e9,e20,e50,e200=[c.ewm(span=n,adjust=False).mean() for n in (9,20,50,200)]
    sma20,sma50,sma200=[c.rolling(n).mean() for n in (20,50,200)]
    d=c.diff(); gain=d.clip(lower=0).ewm(alpha=1/14,adjust=False).mean(); loss=(-d.clip(upper=0)).ewm(alpha=1/14,adjust=False).mean()
    rsi=100-100/(1+gain/loss.replace(0,pd.NA))
    macd=c.ewm(span=12,adjust=False).mean()-c.ewm(span=26,adjust=False).mean(); ms=macd.ewm(span=9,adjust=False).mean()
    mid=c.rolling(20).mean(); sd=c.rolling(20).std()
    tr=pd.concat([h-l,(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1); atr=tr.rolling(14).mean()
    vr=v/v.rolling(20).mean().replace(0,pd.NA)
    recent=c.tail(60); p=float(c.iloc[-1])
    o=df["Open"].astype(float); body=(c-o).abs(); rng=(h-l).replace(0,pd.NA)
    upper=h-pd.concat([o,c],axis=1).max(axis=1); lower=pd.concat([o,c],axis=1).min(axis=1)-l
    hammer=(lower>body*2)&(upper<body)&(body/rng<.45)
    bull=(c>o)&(c.shift(1)<o.shift(1))&(o<c.shift(1))&(c>o.shift(1))
    bear=(c<o)&(c.shift(1)>o.shift(1))&(o>c.shift(1))&(c<c.shift(1))
    pattern="Bullish breakout setup" if p>=float(recent.max())*.99 else "Near support" if p<=float(recent.min())*1.02 else "Range"
    candle="Bullish engulfing" if bool(bull.iloc[-1]) else "Bearish engulfing" if bool(bear.iloc[-1]) else "Hammer" if bool(hammer.iloc[-1]) else "Neutral"
    volume_signal="Strong buying volume" if (last(vr) or 0)>=1.5 and c.iloc[-1]>o.iloc[-1] else "Strong selling volume" if (last(vr) or 0)>=1.5 and c.iloc[-1]<o.iloc[-1] else "No strong confirmation"
    trend="Bullish" if last(e20)>last(e50)>last(e200) else "Bearish" if last(e20)<last(e50)<last(e200) else "Mixed"
    return {"RSI 14":last(rsi),"MACD":last(macd),"MACD Signal":last(ms),"EMA 9":last(e9),"EMA 20":last(e20),"EMA 50":last(e50),"EMA 200":last(e200),
            "SMA 20":last(sma20),"SMA 50":last(sma50),"SMA 200":last(sma200),"MA Alignment":trend,
            "Bollinger Upper":last(mid+2*sd),"Bollinger Lower":last(mid-2*sd),"ATR 14":last(atr),"Volume Ratio":last(vr),
            "Support":float(recent.min()),"Resistance":float(recent.max()),
            "52W Low":float(c.tail(min(252,len(c))).min()),"52W High":float(c.tail(min(252,len(c))).max()),
            "Breakout":"YES" if p>=float(recent.max())*.99 and (last(vr) or 0)>=1.2 else "No",
            "_trend":trend,"_pattern":pattern,"_candlestick":candle,"_volume_signal":volume_signal,"_atr":last(atr)}
