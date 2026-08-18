
import numpy as np, pandas as pd, yfinance as yf
from engines.fundamentals import latest
from engines.peer_map import peers_for

def shares(info,price):
    s=info.get("sharesOutstanding")
    if s: return float(s)
    mc=info.get("marketCap")
    return float(mc/price) if mc and price else None

def dcf_valuation(fin,info,price):
    inc,bs,cf=fin["income"],fin["balance"],fin["cashflow"]
    rev=latest(inc,"Revenue"); ebit=latest(inc,"EBIT"); pat=latest(inc,"Net Income")
    da=abs(latest(cf,"D&A") or 0); capex=abs(latest(cf,"Capex") or 0); nwc=latest(cf,"Change NWC") or 0
    debt=latest(bs,"Debt") or info.get("totalDebt") or 0; cash=latest(bs,"Cash") or info.get("totalCash") or 0
    sh=shares(info,price)
    if not rev or not sh:
        return {"fcff_per_share":None,"fcfe_per_share":None,"blended_per_share":None,"forecast":pd.DataFrame(),"metrics":[],"sensitivity":pd.DataFrame()}
    tax_raw=latest(inc,"Tax Provision"); pretax=latest(inc,"Pretax Income")
    tax=tax_raw/pretax if tax_raw is not None and pretax else 0.25
    tax=max(0,min(.35,float(tax)))
    growth=float(info.get("revenueGrowth") or .08); growth=max(-.05,min(.18,growth))
    margin=(ebit/rev) if ebit and rev else float(info.get("operatingMargins") or .08); margin=max(.03,min(.30,margin))
    rf=.065; beta=float(info.get("beta") or 1); mrp=.06; ke=max(.08,min(.18,rf+beta*mrp))
    equity_value=sh*price
    kd=.085; total=equity_value+debt
    wacc=(ke*(equity_value/total)+kd*(1-tax)*(debt/total)) if total else .10
    wacc=max(.075,min(.16,wacc)); tg=.04
    rows=[]; pv_fcff=0; pv_fcfe=0; cur_rev=rev
    for yr in range(1,6):
        g=growth*(1-.06*(yr-1))
        cur_rev*=1+g
        ebit_y=cur_rev*margin
        da_y=cur_rev*(da/rev) if da and rev else cur_rev*.025
        capex_y=cur_rev*(capex/rev) if capex and rev else cur_rev*.035
        nwc_y=(cur_rev/rev)*nwc if nwc and rev else cur_rev*.01
        fcff=ebit_y*(1-tax)+da_y-capex_y-nwc_y
        ni_y=cur_rev*(pat/rev) if pat and rev else ebit_y*(1-tax)
        net_borrowing=debt*.03
        fcfe=ni_y+da_y-capex_y-nwc_y+net_borrowing
        pv_fcff+=fcff/(1+wacc)**yr; pv_fcfe+=fcfe/(1+ke)**yr
        rows.append([yr,g,cur_rev,ebit_y,fcff,fcfe])
    forecast=pd.DataFrame(rows,columns=["Year","Growth","Revenue","EBIT","FCFF","FCFE"])
    tv_ff=forecast.iloc[-1]["FCFF"]*(1+tg)/(wacc-tg)
    tv_fe=forecast.iloc[-1]["FCFE"]*(1+tg)/(ke-tg)
    ev=pv_fcff+tv_ff/(1+wacc)**5
    eq_ff=ev-debt+cash
    eq_fe=pv_fcfe+tv_fe/(1+ke)**5
    # Sensitivity on FCFF value/share.
    sens=[]
    for g2 in [.03,.035,.04,.045,.05]:
        row=[]
        for w2 in [.08,.09,.10,.11,.12]:
            if w2<=g2: row.append(None); continue
            terminal=forecast.iloc[-1]["FCFF"]*(1+g2)/(w2-g2)
            value=(pv_fcff+terminal/(1+w2)**5-debt+cash)/sh
            row.append(value)
        sens.append([g2]+row)
    sensitivity=pd.DataFrame(sens,columns=["Terminal Growth","8% WACC","9% WACC","10% WACC","11% WACC","12% WACC"])
    return {"fcff_per_share":eq_ff/sh,"fcfe_per_share":eq_fe/sh,"blended_per_share":(eq_ff+eq_fe)/(2*sh),
            "forecast":forecast,"metrics":[("WACC",wacc),("Cost of Equity",ke),("Tax Rate",tax),("Terminal Growth",tg),
            ("Enterprise Value (FCFF)",ev),("Equity Value (FCFF)",eq_ff),("Equity Value (FCFE)",eq_fe),("Shares",sh)],
            "sensitivity":sensitivity}

def relative_valuation(symbol,sector,industry,info,price):
    peer_symbols=peers_for(symbol,sector,industry); rows=[]
    for p in peer_symbols:
        try:
            pi=yf.Ticker(p+".NS").info
            pp=pi.get("currentPrice") or pi.get("regularMarketPrice")
            if not pp: continue
            rows.append({"Ticker":p,"Company":pi.get("longName") or p,"P/E":pi.get("trailingPE"),
                         "P/B":pi.get("priceToBook"),"EV/EBITDA":pi.get("enterpriseToEbitda"),
                         "ROE":(pi.get("returnOnEquity") or 0)*100,"Revenue Growth":(pi.get("revenueGrowth") or 0)*100,
                         "Current Price":pp})
        except Exception: pass
    peers=pd.DataFrame(rows)
    fair=[]
    eps=info.get("trailingEps"); book=info.get("bookValue")
    if not peers.empty:
        if eps and peers["P/E"].notna().sum()>=2:
            med=float(peers["P/E"].median()); fair.append(("P/E",eps*med,med))
        if book and peers["P/B"].notna().sum()>=2:
            med=float(peers["P/B"].median()); fair.append(("P/B",book*med,med))
        ev_eb=info.get("enterpriseToEbitda")
        ebitda=info.get("ebitda")
        if ebitda is None:
            ev=info.get("enterpriseValue"); mult=ev_eb
            if ev and mult: ebitda=ev/mult
        if ebitda and peers["EV/EBITDA"].notna().sum()>=2:
            med=float(peers["EV/EBITDA"].median()); ev=ebitda*med
            debt=info.get("totalDebt") or 0; cash=info.get("totalCash") or 0; sh=shares(info,price)
            if sh: fair.append(("EV/EBITDA",(ev-debt+cash)/sh,med))
    fv=pd.DataFrame(fair,columns=["Method","Fair Value","Peer Median"])
    return {"peers":peers,"fair_values":fv}

def valuation_summary(price,dcf,rel):
    vals=[]
    for k in ["blended_per_share","fcff_per_share","fcfe_per_share"]:
        v=dcf.get(k)
        if v and np.isfinite(v) and v>0: vals.append(float(v))
    if not rel["fair_values"].empty:
        vals += [float(x) for x in rel["fair_values"]["Fair Value"] if pd.notna(x) and x>0]
    fair=float(np.median(vals)) if vals else None
    up=(fair/price-1)*100 if fair else None
    return {"fair_value":fair,"upside_pct":up,"classification":"Undervalued" if up is not None and up>=15 else "Fairly valued" if up is not None and up>-10 else "Overvalued" if up is not None else "Insufficient data"}
