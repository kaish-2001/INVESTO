
F={"Financial Services":["P/E","P/B","ROE","ROA","NIM","GNPA","NNPA","Credit Growth","Deposit Growth","CASA","Capital Adequacy","Cost-to-Income","Credit Cost"],
"Technology":["P/E","PEG","EV/EBITDA","ROE","ROCE","Revenue CAGR","EPS CAGR","EBIT Margin","FCF Margin","FCF Conversion","Attrition","Utilization"],
"Healthcare":["P/E","PEG","EV/EBITDA","ROE","ROCE","EBITDA Margin","Revenue CAGR","EPS CAGR","FCF Margin","Debt/Equity","R&D/Revenue"],
"Consumer Defensive":["P/E","PEG","EV/EBITDA","ROE","ROCE","Gross Margin","Operating Margin","Revenue CAGR","EPS CAGR","FCF Margin","Dividend Yield"],
"Consumer Cyclical":["P/E","EV/EBITDA","P/B","ROE","ROCE","Revenue CAGR","Volume Growth","EBITDA Margin","Net Debt/EBITDA","FCF"],
"Industrials":["P/E","EV/EBITDA","P/B","ROE","ROCE","Order Book","Order Book/Revenue","Revenue CAGR","EBITDA Margin","Working Capital Days","CFO/PAT","Debt/Equity"],
"Basic Materials":["EV/EBITDA","P/B","P/E","ROE","ROCE","EBITDA Margin","Production/Volume Growth","Debt/Equity","Net Debt/EBITDA","FCF"],
"Utilities":["P/E","EV/EBITDA","P/B","ROE","ROCE","Debt/Equity","Interest Coverage","FCF","Dividend Yield"],
"Real Estate":["P/B","P/E","EV/EBITDA","ROE","ROCE","Net Debt/Equity","Net Debt/EBITDA","Pre-sales Growth","Collections","NAV"]}
D=["P/E","P/B","EV/EBITDA","ROE","ROCE","Revenue Growth","EPS Growth","EBITDA Margin","FCF","Debt/Equity"]
def framework(s): return F.get(s,D)
