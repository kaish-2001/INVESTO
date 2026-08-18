
import pandas as pd, numpy as np

def clean_statement(df, wanted):
    if df is None or df.empty: return pd.DataFrame()
    aliases={}
    for key, names in wanted.items():
        for n in names: aliases[n]=key
    rows=[]
    for idx in df.index:
        key=aliases.get(str(idx),None)
        if key:
            row=df.loc[idx].copy()
            row.name=key; rows.append(row)
    if not rows: return pd.DataFrame()
    out=pd.DataFrame(rows)
    out=out.loc[~out.index.duplicated(keep="first")]
    out.columns=[str(c)[:10] for c in out.columns]
    return out

INCOME={"Revenue":["Total Revenue","Operating Revenue"],"EBIT":["EBIT"],"EBITDA":["EBITDA"],
"Net Income":["Net Income","Net Income Common Stockholders"],"Pretax Income":["Pretax Income"],
"Tax Provision":["Tax Provision"],"EPS":["Diluted EPS","Basic EPS"],
"Interest Expense":["Interest Expense Non Operating","Interest Expense"]}

BALANCE={"Assets":["Total Assets"],"Liabilities":["Total Liabilities Net Minority Interest","Total Liabilities"],
"Equity":["Stockholders Equity"],"Cash":["Cash Cash Equivalents And Short Term Investments","Cash Financial"],
"Debt":["Total Debt","Long Term Debt And Capital Lease Obligation","Current Debt"],
"Current Assets":["Current Assets"],"Current Liabilities":["Current Liabilities"],"Inventory":["Inventory"],
"Receivables":["Accounts Receivable"],"Payables":["Accounts Payable"]}

CASH={"CFO":["Operating Cash Flow","Total Cash From Operating Activities"],"FCF":["Free Cash Flow"],
"Capex":["Capital Expenditure"],"D&A":["Depreciation And Amortization"],"Change NWC":["Change In Working Capital"],
"Debt Issued":["Issuance Of Debt"],"Debt Repaid":["Repayment Of Debt"]}

def financials(y):
    def get(attr):
        try:return getattr(y,attr)
        except:return pd.DataFrame()
    return {"income":clean_statement(get("financials"),INCOME),
            "balance":clean_statement(get("balance_sheet"),BALANCE),
            "cashflow":clean_statement(get("cashflow"),CASH)}

def latest(df,row):
    try:
        if df is None or df.empty or row not in df.index:return None
        s=pd.to_numeric(df.loc[row],errors="coerce").dropna()
        return float(s.iloc[0]) if len(s) else None
    except:return None

def ratio_analysis(fin,info):
    inc,bs,cf=fin["income"],fin["balance"],fin["cashflow"]
    rev=latest(inc,"Revenue"); ebit=latest(inc,"EBIT"); ebitda=latest(inc,"EBITDA"); pat=latest(inc,"Net Income")
    assets=latest(bs,"Assets"); eq=latest(bs,"Equity"); debt=latest(bs,"Debt"); ca=latest(bs,"Current Assets"); cl=latest(bs,"Current Liabilities")
    inv=latest(bs,"Inventory"); cash=latest(bs,"Cash"); cfo=latest(cf,"CFO"); fcf=latest(cf,"FCF"); interest=latest(inc,"Interest Expense")
    vals=[
        ("Current Ratio", ca/cl if ca and cl else None,"Liquidity"),
        ("Quick Ratio", (ca-(inv or 0))/cl if ca and cl else None,"Liquidity"),
        ("Debt / Equity", debt/eq if debt is not None and eq else info.get("debtToEquity"),"Leverage"),
        ("Debt / Assets", debt/assets if debt is not None and assets else None,"Leverage"),
        ("ROE", pat/eq if pat is not None and eq else info.get("returnOnEquity"),"Profitability"),
        ("ROA", pat/assets if pat is not None and assets else info.get("returnOnAssets"),"Profitability"),
        ("EBIT Margin", ebit/rev if ebit and rev else None,"Profitability"),
        ("EBITDA Margin", ebitda/rev if ebitda and rev else info.get("ebitdaMargins"),"Profitability"),
        ("Net Profit Margin", pat/rev if pat and rev else info.get("profitMargins"),"Profitability"),
        ("CFO / PAT", cfo/pat if cfo is not None and pat else None,"Cash Quality"),
        ("FCF / PAT", fcf/pat if fcf is not None and pat else None,"Cash Quality"),
        ("Asset Turnover", rev/assets if rev and assets else None,"Efficiency"),
        ("Interest Coverage", ebit/abs(interest) if ebit is not None and interest not in (None,0) else None,"Solvency")
    ]
    return pd.DataFrame(vals,columns=["Ratio","Calculated Value","Category"])

def fmt_financial_table(df):
    if df is None or df.empty:return pd.DataFrame()
    out=df.copy()
    out.index=[str(x) for x in out.index]
    for c in out.columns:
        out[c]=pd.to_numeric(out[c],errors="coerce").map(lambda x: "" if pd.isna(x) else f"{x:,.0f}")
    return out.reset_index().rename(columns={"index":"Line Item"})
