"""
RSI + PE Screener — Nifty 50 | HK 50 | US 50
Institutional Grade Dashboard built with Streamlit
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import os, json as _json
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

# ── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RSI + PE Pro Screener",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom Visual Theme ───────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    h1, h2, h3, .mono { font-family: 'Space Mono', monospace; }
    
    .block-container { padding-top: 1.5rem !important; padding-bottom: 2rem !important; }
    
    /* Preset Action Buttons */
    div.stButton > button[kind="secondary"] {
        background: #111e2e;
        color: #8da4b8;
        border: 1px solid #1e3347;
        font-size: 0.8rem;
        font-weight: 500;
        border-radius: 6px;
        transition: all 0.2s ease;
    }
    div.stButton > button[kind="secondary"]:hover {
        background: #1a2d3d;
        color: #00d4aa;
        border-color: #00d4aa;
    }
    
    /* Primary Run Scan Button */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #00d4aa, #0099cc);
        color: #050e18 !important;
        font-weight: 700;
        font-family: 'Space Mono', monospace;
        border: none;
        border-radius: 6px;
    }
    
    /* Footer Styling */
    .disclaimer { 
        color: #4b6375; 
        font-size: 0.75rem; 
        text-align: center; 
        margin-top: 2.5rem; 
        padding-top: 1rem; 
        border-top: 1px solid #1e3347; 
    }
</style>
""", unsafe_allow_html=True)

# ── Stock Universes ───────────────────────────────────────────────────────────

NIFTY50 = [
    'RELIANCE.NS','TCS.NS','HDFCBANK.NS','BHARTIARTL.NS','ICICIBANK.NS',
    'INFY.NS','SBIN.NS','HINDUNILVR.NS','ITC.NS','BAJFINANCE.NS',
    'KOTAKBANK.NS','LT.NS','HCLTECH.NS','AXISBANK.NS','MARUTI.NS',
    'SUNPHARMA.NS','TITAN.NS','NTPC.NS','POWERGRID.NS','ULTRACEMCO.NS',
    'WIPRO.NS','ONGC.NS','TECHM.NS','ADANIENT.NS','BAJAJFINSV.NS',
    'NESTLEIND.NS','COALINDIA.NS','TATAMOTORS.NS','ADANIPORTS.NS','JSWSTEEL.NS',
    'TATASTEEL.NS','HINDALCO.NS','GRASIM.NS','DRREDDY.NS','CIPLA.NS',
    'DIVISLAB.NS','BAJAJ-AUTO.NS','EICHERMOT.NS','HEROMOTOCO.NS','TATACONSUM.NS',
    'APOLLOHOSP.NS','INDUSINDBK.NS','SHRIRAMFIN.NS','BPCL.NS','BRITANNIA.NS',
    'LTIM.NS','HDFCLIFE.NS','SBILIFE.NS','TRENT.NS','BEL.NS'
]

HK50 = [
    '0005.HK','0011.HK','0388.HK','2318.HK','0939.HK','1299.HK','2388.HK',
    '0700.HK','9988.HK','9888.HK','3690.HK','0981.HK','0992.HK','1810.HK',
    '0823.HK','0016.HK','0001.HK','0012.HK','0017.HK','0101.HK',
    '0857.HK','0883.HK','0386.HK','1088.HK','2899.HK',
    '0291.HK','1929.HK','0322.HK','0027.HK','0762.HK',
    '0002.HK','0003.HK','0006.HK','0066.HK','0267.HK',
    '1177.HK','2269.HK','0241.HK',
    '0019.HK','0083.HK','0288.HK','0175.HK','0669.HK',
    '0868.HK','2020.HK','6862.HK','9618.HK','6098.HK',
]

US50 = [
    'AAPL','MSFT','NVDA','GOOGL','META','AMZN','TSLA','AVGO',
    'JPM','BAC','WFC','GS','MS','BRK-B','V','MA',
    'JNJ','UNH','LLY','ABBV','PFE','MRK','TMO','ABT',
    'WMT','KO','PG','PEP','COST','MCD','NKE','HD',
    'XOM','CVX','COP','SLB','CAT','DE','GE','HON',
    'SPY','QQQ','IWM','GLD','SLV','T','VZ','NEE','DUK',
]

# ── Data Processing Core ──────────────────────────────────────────────────────

def calc_rsi(series, period=14):
    """Calculates 14-period Relative Strength Index safely."""
    if len(series) < period + 1:
        return 50.0
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, 1e-10)
    rsi = 100 - (100 / (1 + rs))
    res = rsi.dropna()
    return round(float(res.iloc[-1]), 1) if not res.empty else 50.0

def safe_float(val, default=0.0):
    try:
        f = float(val)
        return default if np.isnan(f) or np.isinf(f) else f
    except:
        return default

def fetch_single_ticker(ticker, currency_symbol):
    """Fetches single ticker historical and fundamental data via yfinance."""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='6mo', auto_adjust=True)
        if hist is None or len(hist) < 20:
            return None
            
        close = hist['Close'].dropna()
        if len(close) < 20:
            return None
            
        price = float(close.iloc[-1])
        if price <= 0:
            return None
            
        rsi = calc_rsi(close)
        change_1d = ((price - float(close.iloc[-2])) / float(close.iloc[-2])) * 100
        
        # Sparkline mini-trend list (last 30 close prices)
        sparkline = close.tail(30).round(2).tolist()

        # Fundamental Info Extraction
        info = stock.info or {}
        if not info and '.NS' in ticker:
            info = yf.Ticker(ticker.replace('.NS', '.BO')).info or {}

        pe = safe_float(info.get('trailingPE'))
        forward_pe = safe_float(info.get('forwardPE'))

        if pe == 0:
            eps = safe_float(info.get('trailingEps', 0))
            pe = round(price / eps, 1) if eps > 0 else 0.0
            
        if forward_pe == 0:
            fwd_eps = safe_float(info.get('forwardEps', 0))
            forward_pe = round(price / fwd_eps, 1) if fwd_eps > 0 else 0.0

        pb = safe_float(info.get('priceToBook'))
        mkt_cap = safe_float(info.get('marketCap'))
        total_debt = safe_float(info.get('totalDebt'))

        name = info.get('shortName') or info.get('longName') or ticker
        sector = info.get('sector') or info.get('industry') or 'N/A'

        # Dividend calculation
        div_yield = 0.0
        div_raw = info.get('dividendYield')
        div_rate = safe_float(info.get('dividendRate'))
        if div_raw is not None:
            dv = safe_float(div_raw)
            div_yield = dv * 100 if 0 < dv < 1 else (dv if 1 <= dv <= 20 else 0.0)
        if div_yield == 0.0 and div_rate > 0 and price > 0:
            div_yield = (div_rate / price) * 100
        div_yield = round(min(div_yield, 20.0), 2)

        # Expected Growth Percentage
        growth_exp = round(((pe - forward_pe) / forward_pe) * 100, 1) if (pe > 0 and forward_pe > 0) else None

        # Debt Unit Adjustments
        if '.HK' in ticker:
            debt_display = round(total_debt / 1e8, 1) if total_debt > 0 else 0.0
        elif '.NS' in ticker:
            debt_display = round(total_debt / 1e7, 1) if total_debt > 0 else 0.0
        else:
            debt_display = round(total_debt / 1e9, 2) if total_debt > 0 else 0.0

        clean_ticker = ticker.replace('.NS','').replace('.HK','').lstrip('0')

        return {
            'ticker': clean_ticker,
            'name': str(name)[:25],
            'sector': str(sector),
            'price': round(price, 2),
            'change_1d': round(change_1d, 2),
            'rsi': rsi,
            'rsi_signal': 'Oversold' if rsi < 35 else ('Overbought' if rsi > 65 else 'Neutral'),
            'pe': round(pe, 1) if pe > 0 else None,
            'forward_pe': round(forward_pe, 1) if forward_pe > 0 else None,
            'growth_exp': growth_exp,
            'pb': round(pb, 2) if pb > 0 else None,
            'div_yield': div_yield if div_yield > 0 else None,
            'debt': debt_display,
            'sparkline': sparkline,
            'currency': currency_symbol
        }
    except Exception:
        return None

@st.cache_data(ttl=900, show_spinner=False)
def parallel_market_scan(tickers, currency_symbol):
    """Executes market scans in parallel threads for 10x performance."""
    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_ticker = {
            executor.submit(fetch_single_ticker, t, currency_symbol): t for t in tickers
        }
        for future in as_completed(future_to_ticker):
            res = future.result()
            if res:
                results.append(res)
    return results

# ── Render Screener Interface ─────────────────────────────────────────────────

def render_screener_tab(tab_key, tickers, currency_symbol, market_title, sector_options):
    st.sidebar.markdown(f"### ⚙️ {market_title} Settings")
    
    # Run Scan Trigger
    scan_clicked = st.button(f"🚀 Run {market_title} Scan", key=f"run_{tab_key}", type="primary", use_container_width=True)
    
    if scan_clicked or f"data_{tab_key}" not in st.session_state:
        with st.spinner(f"Fetching live market metrics for {market_title}..."):
            scan_data = parallel_market_scan(tickers, currency_symbol)
            st.session_state[f"data_{tab_key}"] = scan_data
            st.session_state[f"time_{tab_key}"] = datetime.now().strftime('%b %d, %Y - %I:%M %p')

    data = st.session_state.get(f"data_{tab_key}", [])
    last_time = st.session_state.get(f"time_{tab_key}", "N/A")

    if not data:
        st.warning("No stock data returned. Click 'Run Scan' above to reload.")
        return

    df = pd.DataFrame(data)

    # Top Metrics Bar
    m1, m2, m3, m4, m5 = st.columns(5)
    oversold_cnt = len(df[df['rsi'] < 35])
    overbought_cnt = len(df[df['rsi'] > 65])
    avg_rsi = round(df['rsi'].mean(), 1)
    valid_pe = df[df['pe'].notnull()]['pe']
    median_pe = round(valid_pe.median(), 1) if not valid_pe.empty else 0.0

    m1.metric("Total Tracked", len(df), f"Updated {last_time.split('-')[-1]}")
    m2.metric("🟢 Oversold (<35)", oversold_cnt)
    m3.metric("🔴 Overbought (>65)", overbought_cnt)
    m4.metric("Avg RSI", avg_rsi)
    m5.metric("Median P/E", median_pe)

    st.markdown("---")

    # Filter Section & Preset Shortcuts
    st.markdown("#### 🎛️ Screener Controls & Quick Presets")
    
    p1, p2, p3, p4 = st.columns([1.2, 1.2, 1.2, 2.4])
    
    # Preset triggers using session state
    if p1.button("🎯 Deep Value Oversold", key=f"p1_{tab_key}", use_container_width=True):
        st.session_state[f"preset_{tab_key}"] = "value"
    if p2.button("🚀 GARP Growth", key=f"p2_{tab_key}", use_container_width=True):
        st.session_state[f"preset_{tab_key}"] = "garp"
    if p3.button("💰 High Div Yield", key=f"p3_{tab_key}", use_container_width=True):
        st.session_state[f"preset_{tab_key}"] = "div"
    if p4.button("🔄 Reset Filters", key=f"p4_{tab_key}", use_container_width=True):
        st.session_state[f"preset_{tab_key}"] = "reset"

    preset = st.session_state.get(f"preset_{tab_key}", "reset")

    c1, c2, c3, c4 = st.columns([1.5, 1.5, 1.5, 1.5])
    
    with c1:
        search = st.text_input("🔍 Search Ticker / Name", key=f"s_{tab_key}")
    with c2:
        sec_filter = st.multiselect("🏭 Sector Filter", sector_options, key=f"sec_{tab_key}")
    with c3:
        rsi_range = st.slider("📊 RSI Range", 0, 100, (0, 100), key=f"rsi_{tab_key}")
    with c4:
        pe_max = st.number_input("💵 Max P/E Ratio", min_value=0.0, max_value=200.0, value=0.0, step=5.0, key=f"pe_{tab_key}")

    # Apply Presets if selected
    if preset == "value":
        df = df[(df['rsi'] < 40) & (df['pe'].notnull()) & (df['pe'] < 20)]
    elif preset == "garp":
        df = df[(df['growth_exp'].notnull()) & (df['growth_exp'] > 10) & (df['rsi'] < 60)]
    elif preset == "div":
        df = df[(df['div_yield'].notnull()) & (df['div_yield'] > 2.5)]
    else:
        # Standard manual filter application
        if search:
            df = df[df['ticker'].str.contains(search.upper(), na=False) | df['name'].str.contains(search, case=False, na=False)]
        if sec_filter:
            df = df[df['sector'].isin(sec_filter)]
        df = df[(df['rsi'] >= rsi_range[0]) & (df['rsi'] <= rsi_range[1])]
        if pe_max > 0:
            df = df[(df['pe'].notnull()) & (df['pe'] <= pe_max)]

    st.markdown("<br>", unsafe_allow_html=True)

    # Interactive Native Data Grid Display
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=520,
        column_config={
            "ticker": st.column_config.TextColumn("Ticker", width="small"),
            "name": st.column_config.TextColumn("Company", width="medium"),
            "sector": st.column_config.TextColumn("Sector", width="medium"),
            "price": st.column_config.NumberColumn("Price", format=f"{currency_symbol}%.2f"),
            "change_1d": st.column_config.NumberColumn("24h %", format="%.2f%%"),
            "rsi": st.column_config.ProgressColumn("RSI (14)", format="%.1f", min_value=0, max_value=100),
            "rsi_signal": st.column_config.TextColumn("Signal", width="small"),
            "pe": st.column_config.NumberColumn("P/E", format="%.1f"),
            "forward_pe": st.column_config.NumberColumn("Fwd P/E", format="%.1f"),
            "growth_exp": st.column_config.NumberColumn("Growth Exp %", format="%.1f%%"),
            "pb": st.column_config.NumberColumn("P/B", format="%.2f"),
            "div_yield": st.column_config.NumberColumn("Div Yield %", format="%.2f%%"),
            "debt": st.column_config.NumberColumn("Total Debt", format="%.1f"),
            "sparkline": st.column_config.LineChartColumn("30D Price Trend", width="medium"),
            "currency": None
        }
    )

    # Data Download CSV
    csv_bytes = df.drop(columns=['sparkline'], errors='ignore').to_csv(index=False).encode('utf-8')
    st.download_button(
        f"📥 Export {market_title} Screener Data (CSV)",
        data=csv_bytes,
        file_name=f"{tab_key}_screener_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

# ── Application Layout ────────────────────────────────────────────────────────

st.markdown("""
<div style='display:flex;align-items:center;justify-content:space-between;margin-bottom:1rem;'>
    <div>
        <h2 style='margin:0;color:#00d4aa;'>📊 RSI + PE SCREENER PRO</h2>
        <p style='margin:0;color:#6b8fa8;font-size:0.85rem;'>Wall-Street Style Multi-Market Intelligence Engine</p>
    </div>
</div>
""", unsafe_allow_html=True)

tab_n50, tab_hk50, tab_us50 = st.tabs(["🇮🇳 Nifty 50", "🇭🇰 HK 50", "🇺🇸 US 50"])

with tab_n50:
    render_screener_tab('n50', NIFTY50, '₹', 'Nifty 50', [
        'Technology','Financial Services','Energy','Consumer Defensive','Healthcare',
        'Industrials','Basic Materials','Communication Services','Consumer Cyclical','Utilities'
    ])

with tab_hk50:
    render_screener_tab('hk50', HK50, 'HK$', 'HK 50', [
        'Technology','Financial Services','Real Estate','Consumer Cyclical','Energy',
        'Utilities','Healthcare','Industrials','Communication Services','Consumer Defensive'
    ])

with tab_us50:
    render_screener_tab('us50', US50, '$', 'US 50', [
        'Technology','Financial Services','Healthcare','Consumer Defensive','Energy',
        'Industrials','Consumer Cyclical','Communication Services','Utilities'
    ])

# ── Footer & Disclaimer ───────────────────────────────────────────────────────
st.markdown("""
<div class='disclaimer'>
    <b>Disclaimer:</b> For educational and research purposes only. Market data supplied via Yahoo Finance API. 
    Not SEBI, SFC, or SEC registered financial advice.
</div>
""", unsafe_allow_html=True)