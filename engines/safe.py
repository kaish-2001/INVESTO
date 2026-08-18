
import math
import pandas as pd
import numpy as np

def scalar(x):
    if x is None: return None
    try:
        if pd.isna(x): return None
    except Exception: pass
    if isinstance(x, (np.generic,)): x=x.item()
    if isinstance(x, (int,float)) and not math.isfinite(float(x)): return None
    return x

def display_df(df):
    """Convert every cell to a plain string so Streamlit/Arrow never sees mixed object types."""
    if df is None:
        return pd.DataFrame()
    if not isinstance(df,pd.DataFrame):
        df=pd.DataFrame(df)
    x=df.copy()
    x.columns=[str(c) for c in x.columns]
    for c in x.columns:
        x[c]=x[c].map(lambda v: "" if scalar(v) is None else str(v))
    return x

def kv_df(items, a="Metric", b="Value"):
    return display_df(pd.DataFrame(items,columns=[a,b]))
