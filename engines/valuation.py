
import numpy as np
def valuation(i,p):
    eps=i.get("trailingEps");book=i.get("bookValue");pe=i.get("trailingPE");pb=i.get("priceToBook")
    peval=eps*min(max(pe or 18,8),35) if eps and eps>0 else None
    pbval=book*min(max(pb or 2.5,.8),8) if book and book>0 else None
    vals=[x for x in (peval,pbval) if x and x>0]; fair=float(np.median(vals)) if vals else None
    up=(fair/p-1)*100 if fair else None
    return {"P/E Fair Value":peval,"P/B Fair Value":pbval,"fair_value":fair,"upside_pct":up,
            "classification":"Undervalued" if up is not None and up>=15 else "Fairly valued" if up is not None and up>-10 else "Overvalued" if up is not None else "Insufficient data"}
