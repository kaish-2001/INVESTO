
def score(i,t,v):
    up=v.get("upside_pct") or 0
    valuation=max(0,min(100,50+up*1.4))
    growth=max(0,min(100,50+(i.get("revenueGrowth") or 0)*100+(i.get("earningsGrowth") or 0)*60))
    quality=max(0,min(100,50+(i.get("returnOnEquity") or 0)*80+(i.get("profitMargins") or 0)*50))
    technical=75 if t.get("MA Alignment")=="Bullish" else 30 if t.get("MA Alignment")=="Bearish" else 50
    risk=max(20,min(95,90-float(i.get("debtToEquity") or 100)/5))
    return {"overall":round(.25*valuation+.25*growth+.2*quality+.2*technical+.1*risk),"valuation":round(valuation),"growth":round(growth),"quality":round(quality),"technical":round(technical),"risk":round(risk)}
