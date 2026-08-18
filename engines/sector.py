
SECTOR_RATIOS={
"Financial Services":["P/E","P/B","ROE","ROA","NIM","GNPA","NNPA","Credit Growth","Deposit Growth","CASA","Capital Adequacy","Cost-to-Income"],
"Technology":["P/E","PEG","EV/EBITDA","ROE","ROCE","Revenue CAGR","EPS CAGR","EBIT Margin","FCF Margin"],
"Healthcare":["P/E","PEG","EV/EBITDA","ROE","ROCE","EBITDA Margin","Revenue CAGR","EPS CAGR","FCF Margin","Debt/Equity"],
"Consumer Defensive":["P/E","PEG","EV/EBITDA","ROE","ROCE","Gross Margin","Operating Margin","Revenue CAGR","EPS CAGR"],
"Consumer Cyclical":["P/E","EV/EBITDA","P/B","ROE","ROCE","Revenue CAGR","Volume Growth","EBITDA Margin","Net Debt/EBITDA"],
"Industrials":["P/E","EV/EBITDA","P/B","ROE","ROCE","Order Book","Order Book/Revenue","Revenue CAGR","EBITDA Margin","Working Capital Days","CFO/PAT"],
"Basic Materials":["EV/EBITDA","P/B","P/E","ROE","ROCE","EBITDA Margin","Production Growth","Debt/Equity","FCF"],
"Utilities":["P/E","EV/EBITDA","P/B","ROE","ROCE","Debt/Equity","Interest Coverage","FCF","Dividend Yield"],
"Real Estate":["P/B","P/E","EV/EBITDA","ROE","ROCE","Net Debt/EBITDA","Pre-sales Growth","Collections","NAV"]}
def framework(sector):
    return SECTOR_RATIOS.get(sector,["P/E","P/B","EV/EBITDA","ROE","ROCE","Revenue Growth","EPS Growth","EBITDA Margin","FCF","Debt/Equity"])
