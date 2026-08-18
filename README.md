
# Buddyy V6 — Integrated Equity Research

This version fixes the recurring Streamlit/Arrow mixed-type table error by converting all displayed tables to plain strings before rendering. It also integrates the previously disconnected modules.

Features:
- Live-ish Yahoo/yfinance price and history with refresh
- Technical indicators, support/resistance, candlesticks, volume, entry/stop/targets
- NSE option-chain OI/PCR attempt with Yahoo fallback and no fabrication
- Stock-level promoter/FII/DII/public shareholding via public Screener fallback
- NSE market-level FII/DII cash-flow attempt
- Income statement, balance sheet, cash flow
- Calculated ratios
- Sector-specific ratio framework
- FCFF / FCFE / blended DCF with 5-year forecast and sensitivity
- Relative valuation using curated industry/business-model peers
- Five peer alternatives

Important: NSE's website terms/data-access conditions apply to its market data. For production/commercial redistribution, use an appropriately licensed feed.
