
import requests, pandas as pd, re
from bs4 import BeautifulSoup

HEADERS={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/151 Safari/537.36",
         "Accept":"text/html,application/xhtml+xml,application/json"}

def fetch_shareholding(symbol):
    symbol=symbol.replace(".NS","").upper()
    url=f"https://www.screener.in/company/{symbol}/consolidated/"
    try:
        r=requests.get(url,headers=HEADERS,timeout=12)
        if r.status_code!=200: return None
        soup=BeautifulSoup(r.text,"html.parser")
        target=None
        for table in soup.find_all("table"):
            txt=table.get_text(" ",strip=True)
            if "Promoters" in txt and ("FIIs" in txt or "FIIs +" in txt) and ("DIIs" in txt or "DIIs +" in txt):
                target=table; break
        if target is None: return None
        rows=target.find_all("tr")
        parsed=[]
        headers=[]
        # Screener shareholding tables commonly have period columns in first row.
        for tr in rows:
            cells=[c.get_text(" ",strip=True) for c in tr.find_all(["th","td"])]
            if cells: parsed.append(cells)
        if not parsed: return None
        maxlen=max(len(r) for r in parsed)
        parsed=[r+[""]*(maxlen-len(r)) for r in parsed]
        df=pd.DataFrame(parsed)
        # Find a row containing Promoters and extract last populated numeric-ish column.
        result=[]
        for label in ["Promoters","FIIs","DIIs","Public"]:
            hit=None
            for r in parsed:
                if r and label.lower() in r[0].lower():
                    hit=r; break
            if hit:
                vals=[x for x in hit[1:] if x]
                result.append((label, vals[-1] if vals else "Unavailable"))
        if not result: return None
        latest="Latest reported period"
        # Try to identify latest header/date/quarter from top rows.
        for r in parsed[:3]:
            for x in reversed(r):
                if re.search(r"(Mar|Jun|Sep|Dec|20\d\d|TTM)",x):
                    latest=x; break
            if latest!="Latest reported period": break
        return {"table":pd.DataFrame(result,columns=["Holder","Holding %"]),
                "fii":next((v for n,v in result if n=="FIIs"),"Unavailable"),
                "dii":next((v for n,v in result if n=="DIIs"),"Unavailable"),
                "promoter":next((v for n,v in result if n=="Promoters"),"Unavailable"),
                "public":next((v for n,v in result if n=="Public"),"Unavailable"),
                "latest":latest,"source":"Screener public shareholding table"}
    except Exception:
        return None
