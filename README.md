
# Buddyy — Intelligent Equity Research

## Entry/Exit Engine

Buddyy now derives entry, stop and target levels from the **current price** using a multi-factor price-action model:

- support/resistance
- trend and EMA structure
- breakout/breakdown state
- recent candlestick patterns
- price-volume confirmation
- ATR-based risk distance
- open-interest confirmation when an options chain is available
- fair value as a secondary target anchor

It intentionally avoids a fixed rule such as "buy 5% below current price".

### Important OI note

The prototype attempts an options-chain OI snapshot through yfinance. For Indian production use, replace this with an appropriately licensed NSE/authorized data feed. NSE publishes equity-derivatives price/volume/OI reports and market tools, but automated redistribution should follow the applicable data licensing terms.

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## GitHub + Streamlit

Upload the contents of this folder to GitHub and deploy `app.py` using Streamlit Community Cloud.

## Current-price decision philosophy

1. Determine market structure.
2. Mark support and resistance.
3. Detect breakout/pullback context.
4. Confirm with candles and volume.
5. Use OI as confirmation where available.
6. Calculate entry.
7. Place invalidation below structural support / volatility allowance.
8. Set Target 1 at the next meaningful resistance or fair-value area.
9. Set Target 2 from the next resistance/volatility/valuation zone.
10. Calculate risk/reward.
11. Return WAIT when evidence conflicts instead of forcing a trade.

This is a research prototype, not a guaranteed trading signal.
