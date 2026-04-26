"""
NSE Wheel Strategy Screener — Streamlit Web App
Built for: Srini | Cash-Secured Put (CSP) Strategy
"""

import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NSE Wheel Screener",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }
    h1, h2, h3 {
        font-family: 'Space Mono', monospace;
    }
    .main-header {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    .main-header h1 {
        color: #00d4aa;
        font-size: 2rem;
        margin: 0;
        letter-spacing: -1px;
    }
    .main-header p {
        color: #a0b4c0;
        margin: 0.5rem 0 0 0;
        font-size: 0.95rem;
    }
    .metric-box {
        background: #1a2332;
        border: 1px solid #2a3f52;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        text-align: center;
    }
    .metric-box .label {
        color: #6b8fa8;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .metric-box .value {
        color: #00d4aa;
        font-size: 1.6rem;
        font-weight: 700;
        font-family: 'Space Mono', monospace;
    }
    .tier1-card {
        background: linear-gradient(135deg, #0d2137, #0f2a1a);
        border: 1px solid #00d4aa44;
        border-left: 4px solid #00d4aa;
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
    }
    .tier2-card {
        background: #1a2332;
        border: 1px solid #2a3f52;
        border-left: 4px solid #f5a623;
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
    }
    .ticker-name {
        font-family: 'Space Mono', monospace;
        font-size: 1.2rem;
        font-weight: 700;
        color: #ffffff;
    }
    .score-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        font-family: 'Space Mono', monospace;
    }
    .score-high { background: #00d4aa22; color: #00d4aa; border: 1px solid #00d4aa55; }
    .score-mid  { background: #f5a62322; color: #f5a623; border: 1px solid #f5a62355; }
    .strike-box {
        background: #0d1a26;
        border: 1px solid #1e3347;
        border-radius: 8px;
        padding: 0.8rem 1rem;
        margin-top: 0.8rem;
    }
    .strike-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 4px 0;
        font-size: 0.88rem;
    }
    .strike-label { color: #6b8fa8; }
    .strike-value { color: #ffffff; font-family: 'Space Mono', monospace; font-weight: 700; }
    .strike-capital { color: #a0b4c0; font-size: 0.78rem; }
    .tag {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.72rem;
        margin-right: 4px;
    }
    .tag-green { background: #00d4aa22; color: #00d4aa; }
    .tag-red   { background: #ff4b4b22; color: #ff4b4b; }
    .tag-yellow{ background: #f5a62322; color: #f5a623; }
    .tag-blue  { background: #4b9fff22; color: #4b9fff; }
    .affiliate-box {
        background: #1a2332;
        border: 1px solid #2a3f52;
        border-radius: 10px;
        padding: 1.2rem;
        margin-top: 1rem;
        text-align: center;
    }
    .disclaimer {
        color: #4a6070;
        font-size: 0.75rem;
        text-align: center;
        margin-top: 2rem;
        padding: 1rem;
        border-top: 1px solid #1e3347;
    }
   div[data-testid="stSidebarContent"] {
        background: #0d1a26;
    }
    /* Force ALL sidebar text to white */
    section[data-testid="stSidebar"] *,
    div[data-testid="stSidebarContent"] * {
        color: #e8f4f8 !important;
    }
    /* Section headers in teal */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    div[data-testid="stSidebarContent"] h1,
    div[data-testid="stSidebarContent"] h2,
    div[data-testid="stSidebarContent"] h3 {
        color: #00d4aa !important;
    }
    /* Slider value in teal */
    section[data-testid="stSidebar"] .stSlider p,
    section[data-testid="stSidebar"] .stSlider span {
        color: #00d4aa !important;
        font-weight: 700;
    }
    /* Selectbox dropdown text */
    section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] *,
    section[data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"] * {
        color: #e8f4f8 !important;
        background-color: #1a2d3d !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #00d4aa, #0099cc);
        color: #000;
        font-weight: 700;
        font-family: 'Space Mono', monospace;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        width: 100%;
        font-size: 1rem;
        letter-spacing: 0.5px;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #00ffcc, #00bbee);
        color: #000;
    }
</style>
""", unsafe_allow_html=True)

# ── F&O Stock Universe ───────────────────────────────────────────────────────
FO_STOCKS = {
    'TCS.NS':        {'lot': 175,  'sector': 'IT'},
    'INFY.NS':       {'lot': 400,  'sector': 'IT'},
    'WIPRO.NS':      {'lot': 3000, 'sector': 'IT'},
    'HCLTECH.NS':    {'lot': 350,  'sector': 'IT'},
    'TECHM.NS':      {'lot': 600,  'sector': 'IT'},
    'LTTS.NS':       {'lot': 100,  'sector': 'IT'},
    'COFORGE.NS':    {'lot': 375,  'sector': 'IT'},
    'MPHASIS.NS':    {'lot': 275,  'sector': 'IT'},
    'PERSISTENT.NS': {'lot': 100,   'sector': 'IT'},
    'HDFCBANK.NS':   {'lot': 550,  'sector': 'Banking'},
    'ICICIBANK.NS':  {'lot': 700,  'sector': 'Banking'},
    'KOTAKBANK.NS':  {'lot': 2000,  'sector': 'Banking'},
    'AXISBANK.NS':   {'lot': 625, 'sector': 'Banking'},
    'SBIN.NS':       {'lot': 750, 'sector': 'Banking'},
    'BAJFINANCE.NS': {'lot': 750,  'sector': 'Finance'},
    'BAJAJFINSV.NS': {'lot': 250,  'sector': 'Finance'},
    'INDUSINDBK.NS': {'lot': 700,  'sector': 'Banking'},
    'MARUTI.NS':     {'lot': 50,  'sector': 'Auto'},
    'BAJAJ-AUTO.NS': {'lot': 75,   'sector': 'Auto'},
    'EICHERMOT.NS':  {'lot': 100,  'sector': 'Auto'},
    'HEROMOTOCO.NS': {'lot': 150,  'sector': 'Auto'},
    'M&M.NS':        {'lot': 200,  'sector': 'Auto'},
    'SUNPHARMA.NS':  {'lot': 350,  'sector': 'Pharma'},
    'DRREDDY.NS':    {'lot': 625,  'sector': 'Pharma'},
    'CIPLA.NS':      {'lot': 375,  'sector': 'Pharma'},
    'DIVISLAB.NS':   {'lot': 100,  'sector': 'Pharma'},
    'LUPIN.NS':      {'lot': 425,  'sector': 'Pharma'},
    'HINDUNILVR.NS': {'lot': 300,  'sector': 'FMCG'},
    'ITC.NS':        {'lot': 1600, 'sector': 'FMCG'},
    'NESTLEIND.NS':  {'lot': 500,  'sector': 'FMCG'},
    'BRITANNIA.NS':  {'lot': 125,  'sector': 'FMCG'},
    'DABUR.NS':      {'lot': 1250, 'sector': 'FMCG'},
    'MARICO.NS':     {'lot': 1200, 'sector': 'FMCG'},
    'TATACONSUM.NS': {'lot': 550,  'sector': 'FMCG'},
    'GODREJCP.NS':   {'lot': 275,  'sector': 'FMCG'},
    'RELIANCE.NS':   {'lot': 500,  'sector': 'Energy'},
    'ONGC.NS':       {'lot': 2250, 'sector': 'Energy'},
    'NTPC.NS':       {'lot': 1500, 'sector': 'Power'},
    'POWERGRID.NS':  {'lot': 1900, 'sector': 'Power'},
    'IOC.NS':        {'lot': 4875, 'sector': 'Energy'},
    'BPCL.NS':       {'lot': 1975, 'sector': 'Energy'},
    'TATAPOWER.NS':  {'lot': 1450, 'sector': 'Power'},
    'COALINDIA.NS':  {'lot': 1350, 'sector': 'Mining'},
    'LT.NS':         {'lot': 175,  'sector': 'Infra'},
    'ULTRACEMCO.NS': {'lot': 50,  'sector': 'Cement'},
    'ADANIPORTS.NS': {'lot': 475, 'sector': 'Infra'},
    'TATASTEEL.NS':  {'lot': 5500, 'sector': 'Metals'},
    'HINDALCO.NS':   {'lot': 700, 'sector': 'Metals'},
    'JSWSTEEL.NS':   {'lot': 675, 'sector': 'Metals'},
    'VEDL.NS':       {'lot': 1150, 'sector': 'Metals'},
    'NMDC.NS':       {'lot': 6750, 'sector': 'Mining'},
    'BHARTIARTL.NS': {'lot': 475,  'sector': 'Telecom'},
    'BEL.NS':        {'lot': 1425, 'sector': 'Defense'},
    'HAL.NS':        {'lot': 150,  'sector': 'Defense'},
    'IRCTC.NS':      {'lot': 875,  'sector': 'Railways'},
}

# ── Screener Logic ───────────────────────────────────────────────────────────
def fetch_stock_data(ticker, lot_size, max_capital, expiry_days=30):
    try:
        stock = yf.Ticker(ticker)
        hist  = stock.history(period='1y')
        if len(hist) < 50:
            return None
        info          = stock.info
        current_price = hist['Close'].iloc[-1]

        ma50  = hist['Close'].rolling(50).mean().iloc[-1]
        ma200 = hist['Close'].rolling(200).mean().iloc[-1] if len(hist) >= 200 else None
        above_50dma  = bool(current_price > ma50)
        above_200dma = bool(current_price > ma200) if ma200 else None

        high_52w      = hist['High'].max()
        low_52w       = hist['Low'].min()
        pct_from_high = ((high_52w - current_price) / high_52w) * 100
        pct_from_low  = ((current_price - low_52w) / low_52w) * 100

        returns = hist['Close'].pct_change().dropna()
        hv_30   = returns[-30:].std() * np.sqrt(252) * 100

        avg_vol_30     = hist['Volume'][-30:].mean()
        annual_div     = info.get('dividendRate') or 0
        dividend_yield = min((annual_div / current_price * 100) if current_price > 0 else 0, 20.0)
        pe_ratio       = info.get('trailingPE', None)
        market_cap_cr  = (info.get('marketCap') or 0) / 10_000_000

        # Strike calculations
        sigma     = hv_30 / 100
        sqrtT     = np.sqrt(expiry_days / 365)
        strike_d30 = round(current_price * np.exp(-0.524 * sigma * sqrtT) / 5) * 5
        strike_d25 = round(current_price * np.exp(-0.674 * sigma * sqrtT) / 5) * 5
        strike_5pct = round(current_price * 0.95 / 5) * 5
        capital_required = strike_5pct * lot_size

        # Wheel Score
        score = 0
        if above_50dma:  score += 10
        if above_200dma: score += 15
        if 10 <= pct_from_high <= 35:   score += 25
        elif 5 <= pct_from_high < 10:   score += 15
        elif 35 < pct_from_high <= 50:  score += 10
        if 20 <= hv_30 <= 45:           score += 20
        elif 15 <= hv_30 < 20:          score += 10
        elif 45 < hv_30 <= 60:          score += 10
        if dividend_yield >= 4:         score += 15
        elif dividend_yield >= 2:       score += 10
        elif dividend_yield >= 1:       score += 5
        if capital_required <= max_capital:          score += 15
        elif capital_required <= max_capital * 1.5:  score += 8

        return {
            'ticker':         ticker.replace('.NS', ''),
            'name':           info.get('longName', ticker)[:28],
            'sector':         FO_STOCKS[ticker]['sector'],
            'lot_size':       lot_size,
            'current_price':  round(current_price, 2),
            'strike_d30':     strike_d30,
            'strike_d25':     strike_d25,
            'strike_5pct':    strike_5pct,
            'capital_required': capital_required,
            'above_50dma':    above_50dma,
            'above_200dma':   above_200dma,
            'pct_from_high':  round(pct_from_high, 1),
            'hv_30':          round(hv_30, 1),
            'dividend_yield': round(dividend_yield, 2),
            'pe_ratio':       round(pe_ratio, 1) if pe_ratio else None,
            'market_cap_cr':  round(market_cap_cr, 0),
            'wheel_score':    score,
        }
    except:
        return None

# ── Session State ────────────────────────────────────────────────────────────
if 'show_chart' not in st.session_state:
    st.session_state.show_chart = {}
if 'scan_results' not in st.session_state:
    st.session_state.scan_results = None
if 'scan_time' not in st.session_state:
    st.session_state.scan_time = None

def toggle_chart(ticker):
    st.session_state.show_chart[ticker] = not st.session_state.show_chart.get(ticker, False)

def render_tradingview_chart(ticker):
    """Render an embedded TradingView chart for an NSE stock"""
    tv_symbol = f"NSE:{ticker}"
    unique_id = f"tv_{ticker.replace('-','_')}"
    chart_html = f"""
    <div style="border-radius:10px; overflow:hidden; margin-top:12px; background:#0d1a26;">
      <div class="tradingview-widget-container">
        <div id="{unique_id}" style="height:500px;"></div>
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
          new TradingView.widget({{
            "width": "100%",
            "height": 500,
            "symbol": "{tv_symbol}",
            "interval": "D",
            "timezone": "Asia/Kolkata",
            "theme": "dark",
            "style": "1",
            "locale": "en",
            "toolbar_bg": "#0d1a26",
            "enable_publishing": false,
            "hide_side_toolbar": false,
            "allow_symbol_change": false,
            "withdateranges": true,
            "range": "12M",
            "studies": [
              "MASimple@tv-basicstudies",
              "MAExp@tv-basicstudies",
              "RSI@tv-basicstudies",
              "BB@tv-basicstudies"
            ],
            "studies_overrides": {{
              "moving average.length": 50,
              "moving average.plot.color": "#00d4aa",
              "moving average exponential.length": 200,
              "moving average exponential.plot.color": "#f5a623",
              "bollinger bands.length": 20,
              "bollinger bands.source": "close",
              "bollinger bands.upper.color": "#4b9fff",
              "bollinger bands.lower.color": "#4b9fff",
              "rsi.length": 14
            }},
            "container_id": "{unique_id}"
          }});
        </script>
      </div>
    </div>
    """
    components.html(chart_html, height=515)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    st.markdown("---")

    max_capital = st.slider(
        "💰 Max Capital per Lot (₹)",
        min_value=50_000,
        max_value=2_000_000,
        value=1500_000,
        step=10_000,
        format="₹%d"
    )
    st.markdown(f"<p style='color:#00d4aa; font-weight:700; font-size:0.9rem; margin-top:-10px'>Selected: ₹{max_capital:,}</p>", unsafe_allow_html=True)

    expiry_days = st.selectbox(
        "📅 Expiry Target",
        options=[7, 15, 30, 45],
        index=2,
        format_func=lambda x: f"{x} days"
    )

    sectors = st.multiselect(
        "🏭 Filter Sectors",
        options=sorted(set(v['sector'] for v in FO_STOCKS.values())),
        default=[],
        placeholder="All sectors"
    )

    min_score = st.slider("🎯 Minimum Wheel Score", 0, 100, 40, 5)
    st.markdown(f"<p style='color:#00d4aa; font-weight:700; font-size:0.9rem; margin-top:-10px'>Selected: {min_score}/100</p>", unsafe_allow_html=True)

    st.markdown("---")
    run_btn = st.button("🚀 Run Screener", use_container_width=True)

    st.markdown("---")
    st.markdown("### 📌 Open a Demat Account")
    st.markdown("""
    <div class='affiliate-box'>
        <p style='color:#a0b4c0; font-size:0.8rem; margin:0'>
        Start trading options with trusted brokers:
        </p>
        <br>
        <a href='https://zerodha.com/open-account?c=SS1428' target='_blank' style='color:#00d4aa; text-decoration:none; font-weight:600'>
        🟢 Zerodha — Open Account
        </a><br><br>
      
    </div>
    """, unsafe_allow_html=True)

# ── Main Header ──────────────────────────────────────────────────────────────
st.markdown("""
<div class='main-header'>
    <h1>🇮🇳 NSE WHEEL SCREENER</h1>
    <p>Cash-Secured Put (CSP) Candidates · F&O Stocks Only · Real-Time Data</p>
</div>
""", unsafe_allow_html=True)

# ── How it works ─────────────────────────────────────────────────────────────
with st.expander("ℹ️ How this screener works"):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**📊 Wheel Score (0–100)**")
        st.markdown("""
        - Trend vs 50/200 DMA: 25 pts
        - Pullback from 52W high: 25 pts
        - Volatility (HV30): 20 pts
        - Dividend yield: 15 pts
        - Capital affordability: 15 pts
        """)
    with col2:
        st.markdown("**🎯 Strike Methods**")
        st.markdown("""
        - 🟢 **Delta ~0.30**: More premium, closer to price
        - 🟡 **Delta ~0.25**: Balanced — recommended
        - 🔵 **5% OTM**: Conservative, wider buffer
        """)
    with col3:
        st.markdown("**⚡ Tier System**")
        st.markdown("""
        - **Tier 1**: Above 200 DMA + within budget + score ≥ 55
        - **Tier 2**: Watchlist — slightly outside criteria
        - **Best zone**: 10–35% below 52W high
        """)

# ── Results ──────────────────────────────────────────────────────────────────
if run_btn:
    # Clear previous results on fresh scan
    st.session_state.scan_results = None
    st.session_state.show_chart = {}  # will be set to True per ticker after scan

    filtered_stocks = {
        k: v for k, v in FO_STOCKS.items()
        if not sectors or v['sector'] in sectors
    }

    total = len(filtered_stocks)
    progress_bar = st.progress(0, text="🔍 Scanning F&O stocks...")
    results = []

    for i, (ticker, meta) in enumerate(filtered_stocks.items()):
        progress_bar.progress(
            (i + 1) / total,
            text=f"🔍 Scanning {ticker.replace('.NS', '')} ({i+1}/{total})..."
        )
        data = fetch_stock_data(ticker, meta['lot'], max_capital, expiry_days)
        if data and data['wheel_score'] >= min_score:
            results.append(data)

    progress_bar.empty()
    st.session_state.scan_results = results
    st.session_state.scan_time = datetime.now().strftime('%d %b %Y, %I:%M %p')
    # Open all charts by default
    for r in results:
        st.session_state.show_chart[r['ticker']] = True

    if not results:
        st.warning("No stocks matched your criteria. Try lowering the minimum score or increasing capital limit.")
    else:
        df = pd.DataFrame(results)

        # Tier split
        tier1 = df[
            (df['capital_required'] <= max_capital) &
            (df['wheel_score'] >= 55) &
            (df['above_200dma'] == True)
        ].sort_values('wheel_score', ascending=False)

        tier2 = df[
            ~df['ticker'].isin(tier1['ticker'])
        ].sort_values('wheel_score', ascending=False).head(10)

        # Summary metrics
        st.markdown(f"### 📊 Scan Results — {datetime.now().strftime('%d %b %Y, %I:%M %p')}")
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f"<div class='metric-box'><div class='label'>Stocks Scanned</div><div class='value'>{len(results)}</div></div>", unsafe_allow_html=True)
        with m2:
            st.markdown(f"<div class='metric-box'><div class='label'>Tier 1 (Best)</div><div class='value'>{len(tier1)}</div></div>", unsafe_allow_html=True)
        with m3:
            st.markdown(f"<div class='metric-box'><div class='label'>Tier 2 (Watch)</div><div class='value'>{len(tier2)}</div></div>", unsafe_allow_html=True)
        with m4:
            avg_score = round(df['wheel_score'].mean())
            st.markdown(f"<div class='metric-box'><div class='label'>Avg Score</div><div class='value'>{avg_score}</div></div>", unsafe_allow_html=True)

        st.markdown("---")

        def render_card(r, card_class):
            trend_tag = "<span class='tag tag-green'>📈 Above 200DMA</span>" if r['above_200dma'] else \
                        "<span class='tag tag-yellow'>〰️ Above 50DMA</span>" if r['above_50dma'] else \
                        "<span class='tag tag-red'>📉 Below MAs</span>"
            div_tag   = f"<span class='tag tag-blue'>💰 Div {r['dividend_yield']:.1f}%</span>" if r['dividend_yield'] > 0 else ""
            score_cls = "score-high" if r['wheel_score'] >= 60 else "score-mid"
            cap_d30   = r['strike_d30'] * r['lot_size']
            cap_d25   = r['strike_d25'] * r['lot_size']
            cap_5pct  = r['strike_5pct'] * r['lot_size']
            chart_open = st.session_state.show_chart.get(r['ticker'], False)
            chart_label = "📉 Hide Chart" if chart_open else "📈 View Chart"

            st.markdown(f"""
            <div class='{card_class}'>
                <div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px'>
                    <div>
                        <span class='ticker-name'>{r['ticker']}</span>
                        <span style='color:#6b8fa8; margin-left:8px; font-size:0.85rem'>{r['name']}</span>
                    </div>
                    <span class='score-badge {score_cls}'>Score {r['wheel_score']}/100</span>
                </div>
                <div style='margin-top:8px; display:flex; gap:12px; flex-wrap:wrap; font-size:0.85rem; color:#a0b4c0'>
                    <span>🏭 {r['sector']}</span>
                    <span>📦 Lot: {r['lot_size']:,}</span>
                    <span>💵 CMP: <strong style='color:#fff'>₹{r['current_price']:,.2f}</strong></span>
                    <span>📉 From 52W High: <strong style='color:#f5a623'>-{r['pct_from_high']:.1f}%</strong></span>
                    <span>🌡️ HV30: {r['hv_30']:.1f}%</span>
                </div>
                <div style='margin-top:6px'>{trend_tag}{div_tag}</div>
                <div class='strike-box'>
                    <div style='color:#6b8fa8; font-size:0.72rem; text-transform:uppercase; letter-spacing:1px; margin-bottom:6px'>
                        Strike Suggestions · {expiry_days}-day expiry
                    </div>
                    <div class='strike-row'>
                        <span class='strike-label'>🟢 Delta ~0.30 (Aggressive)</span>
                        <span class='strike-value'>₹{r['strike_d30']:,.0f}</span>
                        <span class='strike-capital'>Capital: ₹{cap_d30/1000:.0f}K</span>
                    </div>
                    <div class='strike-row'>
                        <span class='strike-label'>🟡 Delta ~0.25 (Moderate)</span>
                        <span class='strike-value'>₹{r['strike_d25']:,.0f}</span>
                        <span class='strike-capital'>Capital: ₹{cap_d25/1000:.0f}K</span>
                    </div>
                    <div class='strike-row'>
                        <span class='strike-label'>🔵 5% OTM (Conservative)</span>
                        <span class='strike-value'>₹{r['strike_5pct']:,.0f}</span>
                        <span class='strike-capital'>Capital: ₹{cap_5pct/1000:.0f}K</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Chart toggle button
            st.button(
                chart_label,
                key=f"chart_btn_{r['ticker']}_{card_class}",
                on_click=toggle_chart,
                args=(r['ticker'],)
            )

            # Render TradingView chart if toggled on
            if chart_open:
                render_tradingview_chart(r['ticker'])

        # Tier 1
        st.markdown("## 🏆 Tier 1 — Best CSP Candidates")
        if tier1.empty:
            st.info("No Tier 1 stocks with current settings. Try increasing capital limit or lowering score threshold.")
        for _, row in tier1.iterrows():
            render_card(row, 'tier1-card')

        st.markdown("---")

        # Tier 2
        st.markdown("## 👀 Tier 2 — Watchlist")
        for _, row in tier2.iterrows():
            render_card(row, 'tier2-card')

        st.markdown("---")

        # Sector Summary
        st.markdown("## 📊 Sector Summary")
        sector_df = df.groupby('sector').agg(
            Stocks=('ticker', 'count'),
            Avg_Score=('wheel_score', 'mean'),
            Avg_HV30=('hv_30', 'mean'),
        ).reset_index().sort_values('Avg_Score', ascending=False)
        sector_df['Avg_Score'] = sector_df['Avg_Score'].round(0).astype(int)
        sector_df['Avg_HV30']  = sector_df['Avg_HV30'].round(1)
        st.dataframe(sector_df, use_container_width=True, hide_index=True)

        # Download
        st.markdown("---")
        csv = df.sort_values('wheel_score', ascending=False).to_csv(index=False)
        st.download_button(
            label="📥 Download Full Results (CSV)",
            data=csv,
            file_name=f"nse_wheel_screener_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )

elif st.session_state.scan_results is None:
    # Landing state — no scan run yet
    st.markdown("""
    <div style='text-align:center; padding:3rem; color:#4a6070'>
        <div style='font-size:4rem'>🎯</div>
        <h3 style='color:#6b8fa8; font-family:Space Mono, monospace'>Ready to scan</h3>
        <p>Configure your settings in the sidebar and click <strong style='color:#00d4aa'>Run Screener</strong></p>
        <p style='font-size:0.85rem'>Scans ~55 F&O stocks · Real-time data · 3 strike suggestions per stock</p>
    </div>
    """, unsafe_allow_html=True)

else:
    # Re-render results from session state (triggered by chart toggle button clicks)
    results = st.session_state.scan_results
    df = pd.DataFrame(results)

    tier1 = df[
        (df['capital_required'] <= max_capital) &
        (df['wheel_score'] >= 55) &
        (df['above_200dma'] == True)
    ].sort_values('wheel_score', ascending=False)

    tier2 = df[
        ~df['ticker'].isin(tier1['ticker'])
    ].sort_values('wheel_score', ascending=False).head(10)

    st.markdown(f"### 📊 Scan Results — {st.session_state.get('scan_time', '')}")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"<div class='metric-box'><div class='label'>Stocks Scanned</div><div class='value'>{len(results)}</div></div>", unsafe_allow_html=True)
    with m2:
        st.markdown(f"<div class='metric-box'><div class='label'>Tier 1 (Best)</div><div class='value'>{len(tier1)}</div></div>", unsafe_allow_html=True)
    with m3:
        st.markdown(f"<div class='metric-box'><div class='label'>Tier 2 (Watch)</div><div class='value'>{len(tier2)}</div></div>", unsafe_allow_html=True)
    with m4:
        avg_score = round(df['wheel_score'].mean())
        st.markdown(f"<div class='metric-box'><div class='label'>Avg Score</div><div class='value'>{avg_score}</div></div>", unsafe_allow_html=True)

    st.markdown("---")

    def render_card(r, card_class):
        trend_tag = "<span class='tag tag-green'>📈 Above 200DMA</span>" if r['above_200dma'] else                     "<span class='tag tag-yellow'>〰️ Above 50DMA</span>" if r['above_50dma'] else                     "<span class='tag tag-red'>📉 Below MAs</span>"
        div_tag   = f"<span class='tag tag-blue'>💰 Div {r['dividend_yield']:.1f}%</span>" if r['dividend_yield'] > 0 else ""
        score_cls = "score-high" if r['wheel_score'] >= 60 else "score-mid"
        cap_d30   = r['strike_d30'] * r['lot_size']
        cap_d25   = r['strike_d25'] * r['lot_size']
        cap_5pct  = r['strike_5pct'] * r['lot_size']
        chart_open  = st.session_state.show_chart.get(r['ticker'], True)
        chart_label = "📉 Hide Chart" if chart_open else "📈 View Chart"

        st.markdown(f"""
        <div class='{card_class}'>
            <div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px'>
                <div>
                    <span class='ticker-name'>{r['ticker']}</span>
                    <span style='color:#6b8fa8; margin-left:8px; font-size:0.85rem'>{r['name']}</span>
                </div>
                <span class='score-badge {score_cls}'>Score {r['wheel_score']}/100</span>
            </div>
            <div style='margin-top:8px; display:flex; gap:12px; flex-wrap:wrap; font-size:0.85rem; color:#a0b4c0'>
                <span>🏭 {r['sector']}</span>
                <span>📦 Lot: {r['lot_size']:,}</span>
                <span>💵 CMP: <strong style='color:#fff'>₹{r['current_price']:,.2f}</strong></span>
                <span>📉 From 52W High: <strong style='color:#f5a623'>-{r['pct_from_high']:.1f}%</strong></span>
                <span>🌡️ HV30: {r['hv_30']:.1f}%</span>
            </div>
            <div style='margin-top:6px'>{trend_tag}{div_tag}</div>
            <div class='strike-box'>
                <div style='color:#6b8fa8; font-size:0.72rem; text-transform:uppercase; letter-spacing:1px; margin-bottom:6px'>
                    Strike Suggestions · {expiry_days}-day expiry
                </div>
                <div class='strike-row'>
                    <span class='strike-label'>🟢 Delta ~0.30 (Aggressive)</span>
                    <span class='strike-value'>₹{r['strike_d30']:,.0f}</span>
                    <span class='strike-capital'>Capital: ₹{cap_d30/1000:.0f}K</span>
                </div>
                <div class='strike-row'>
                    <span class='strike-label'>🟡 Delta ~0.25 (Moderate)</span>
                    <span class='strike-value'>₹{r['strike_d25']:,.0f}</span>
                    <span class='strike-capital'>Capital: ₹{cap_d25/1000:.0f}K</span>
                </div>
                <div class='strike-row'>
                    <span class='strike-label'>🔵 5% OTM (Conservative)</span>
                    <span class='strike-value'>₹{r['strike_5pct']:,.0f}</span>
                    <span class='strike-capital'>Capital: ₹{cap_5pct/1000:.0f}K</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.button(
            chart_label,
            key=f"chart_btn_{r['ticker']}_{card_class}",
            on_click=toggle_chart,
            args=(r['ticker'],)
        )

        if chart_open:
            render_tradingview_chart(r['ticker'])

    st.markdown("## 🏆 Tier 1 — Best CSP Candidates")
    if tier1.empty:
        st.info("No Tier 1 stocks with current settings. Try increasing capital limit or lowering score threshold.")
    for _, row in tier1.iterrows():
        render_card(row.to_dict(), 'tier1-card')

    st.markdown("---")
    st.markdown("## 👀 Tier 2 — Watchlist")
    for _, row in tier2.iterrows():
        render_card(row.to_dict(), 'tier2-card')

    st.markdown("---")
    st.markdown("## 📊 Sector Summary")
    sector_df = df.groupby('sector').agg(
        Stocks=('ticker', 'count'),
        Avg_Score=('wheel_score', 'mean'),
        Avg_HV30=('hv_30', 'mean'),
    ).reset_index().sort_values('Avg_Score', ascending=False)
    sector_df['Avg_Score'] = sector_df['Avg_Score'].round(0).astype(int)
    sector_df['Avg_HV30']  = sector_df['Avg_HV30'].round(1)
    st.dataframe(sector_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    csv = df.sort_values('wheel_score', ascending=False).to_csv(index=False)
    st.download_button(
        label="📥 Download Full Results (CSV)",
        data=csv,
        file_name=f"nse_wheel_screener_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        use_container_width=True
    )

# ── Disclaimer ───────────────────────────────────────────────────────────────
st.markdown("""
<div class='disclaimer'>
    ⚠️ For educational purposes only. Not SEBI registered. Options trading involves substantial risk of loss.
    Do your own research before trading. Past performance does not guarantee future results.
    Lot sizes change quarterly — verify at <a href='https://www.nseindia.com' target='_blank' style='color:#4a8fa8'>nseindia.com</a>
</div>
""", unsafe_allow_html=True)
