
import yfinance as yf
from engines.technical import tech
from engines.valuation import valuation
from engines.scoring import score
U=["RELIANCE","TCS","INFY","HDFCBANK","ICICIBANK","SBIN","AXISBANK","KOTAKBANK","BAJFINANCE","MARUTI","M&M","SUNPHARMA","CIPLA","DRREDDY","ITC","HINDUNILVR","BHARTIARTL","LT","NTPC","POWERGRID","TATASTEEL","HINDALCO","TITAN","ASIANPAINT","WIPRO","HCLTECH","TECHM","TRENT","BEL","HAL","ULTRACEMCO"]
def alternatives(selected,sector):
    out=[]
    for s in U:
        if s==selected.replace(".NS",""): continue
        try:
            t=yf.Ticker(s+".NS"); i=t.info; h=t.history(period="1y",auto_adjust=False)
            if h.empty: continue
            p=i.get("currentPrice") or i.get("regularMarketPrice") or float(h.Close.iloc[-1])
            v=valuation(i,p); sc=score(i,tech(h),v); same=i.get("sector","Unknown")==sector
            out.append({"Stock":s,"Company":i.get("longName") or s,"Sector":i.get("sector","Unknown"),"Score":sc["overall"],"Upside":v.get("upside_pct"),"Valuation":v.get("classification"),"Why":"Higher score + same sector" if same else "Higher broader-market score","Rank":sc["overall"]+(8 if same else 0)})
        except: pass
    return sorted(out,key=lambda x:x["Rank"],reverse=True)[:5]
