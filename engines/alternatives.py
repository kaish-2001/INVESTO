
import yfinance as yf
from engines.peer_map import peers_for
def alternatives(symbol,sector,industry):
    rows=[]
    for s in peers_for(symbol,sector,industry):
        try:
            i=yf.Ticker(s+".NS").info; p=i.get("currentPrice") or i.get("regularMarketPrice")
            if not p: continue
            pe=i.get("trailingPE"); pb=i.get("priceToBook"); rg=(i.get("revenueGrowth") or 0)*100; eg=(i.get("earningsGrowth") or 0)*100
            score=max(0,min(100,55-(pe or 40)*.3-(pb or 3)*1.5+rg*.25+eg*.25+(i.get("returnOnEquity") or 0)*40))
            rows.append({"Stock":s,"Company":i.get("longName") or s,"Industry":i.get("industry") or "N/A","P/E":pe,"P/B":pb,
                         "Revenue Growth %":rg,"ROE %":(i.get("returnOnEquity") or 0)*100,"Score":round(score,1)})
        except Exception: pass
    return sorted(rows,key=lambda x:x["Score"],reverse=True)[:5]
