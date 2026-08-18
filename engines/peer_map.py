
# Curated Indian comparable-company map. Exact company mappings take priority.
PEERS = {
    "AFCONS": ["KEC", "KPIL", "NCC", "IRCON", "GRINFRA", "TECHNOE", "POWERMECH"],
    "AFCONS INFRASTRUCTURE": ["KEC", "KPIL", "NCC", "IRCON", "GRINFRA", "TECHNOE", "POWERMECH"],
    "Engineering & Construction": ["KEC", "KPIL", "NCC", "IRCON", "GRINFRA", "POWERMECH"],
    "Construction": ["NCC", "KEC", "KPIL", "IRCON", "GRINFRA", "POWERMECH"],
    "Financial Services": ["HDFCBANK","ICICIBANK","SBIN","AXISBANK","KOTAKBANK","BAJFINANCE"],
    "Technology": ["TCS","INFY","HCLTECH","WIPRO","TECHM"],
    "Healthcare": ["SUNPHARMA","CIPLA","DRREDDY","DIVISLAB","TORNTPHARM"],
    "Automobiles": ["MARUTI","M&M","TATAMOTORS","EICHERMOT","HEROMOTOCO"],
    "Consumer Defensive": ["ITC","HINDUNILVR","NESTLEIND","BRITANNIA","DABUR"],
    "Industrials": ["LT","BEL","HAL","SIEMENS","ABB"],
    "Basic Materials": ["TATASTEEL","HINDALCO","JSWSTEEL","JINDALSTEL"],
    "Utilities": ["NTPC","POWERGRID","ADANIPOWER","TATAPOWER"],
}
def peers_for(symbol, sector="", industry=""):
    s=(symbol or "").upper().replace(".NS","")
    if s in PEERS: return PEERS[s]
    ind=(industry or "").lower()
    sec=(sector or "").lower()
    # Business-model mappings before broad sectors.
    if any(k in ind for k in ["engineering","construction","infrastructure"]):
        return PEERS["Engineering & Construction"]
    for k,v in PEERS.items():
        if k.lower()==sec or k.lower() in ind:
            return v
    return PEERS.get(sector, ["LT","NCC","KEC","KPIL","IRCON"])
