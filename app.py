"""
NSE + HKEX Wheel Strategy Screener — Streamlit Web App
Tab-based UI | Built for: Srini | Cash-Secured Put (CSP) Strategy
"""

import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Wheel Strategy Screener",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    h1, h2, h3 { font-family: 'Space Mono', monospace; }
    .app-header {
        background: linear-gradient(135deg, #0a1628, #0d2137, #112840);
        border-bottom: 1px solid #1e3347;
        padding: 1rem 2rem;
        display: flex; align-items: center; justify-content: space-between;
        margin-bottom: 0;
    }
    .app-title { color: #00d4aa; font-family: 'Space Mono', monospace; font-size: 1.4rem; font-weight: 700; margin: 0; }
    .app-sub   { color: #6b8fa8; font-size: 0.8rem; margin: 0; }
    .config-panel {
        background: #111e2d; border: 1px solid #1e3347;
        border-radius: 12px; padding: 1.2rem 1.5rem; margin-bottom: 1.2rem;
    }
    .config-title { color: #6b8fa8; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 0.8rem; }
    .metric-box {
        background: #1a2d3d; border: 1px solid #2a3f52;
        border-radius: 10px; padding: 0.9rem 1rem; text-align: center;
    }
    .metric-box .label { color: #6b8fa8; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; }
    .metric-box .value { color: #00d4aa; font-size: 1.5rem; font-weight: 700; font-family: 'Space Mono', monospace; }
    .tier1-card {
        background: linear-gradient(135deg, #0d2137, #0d2318);
        border: 1px solid #00d4aa33; border-left: 4px solid #00d4aa;
        border-radius: 10px; padding: 1.2rem 1.5rem; margin-bottom: 0.8rem;
    }
    .tier2-card {
        background: #111e2d; border: 1px solid #1e3347;
        border-left: 4px solid #f5a623;
        border-radius: 10px; padding: 1.2rem 1.5rem; margin-bottom: 0.8rem;
    }
    .ticker-name { font-family: 'Space Mono', monospace; font-size: 1.1rem; font-weight: 700; color: #fff; }
    .score-badge { display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 0.78rem; font-weight: 600; font-family: 'Space Mono', monospace; }
    .score-high { background: #00d4aa22; color: #00d4aa; border: 1px solid #00d4aa44; }
    .score-mid  { background: #f5a62322; color: #f5a623; border: 1px solid #f5a62344; }
    .strike-box { background: #0a1628; border: 1px solid #1e3347; border-radius: 8px; padding: 0.8rem 1rem; margin-top: 0.8rem; }
    .strike-row { display: flex; justify-content: space-between; align-items: center; padding: 4px 0; font-size: 0.85rem; }
    .strike-label  { color: #6b8fa8; }
    .strike-value  { color: #fff; font-family: 'Space Mono', monospace; font-weight: 700; }
    .strike-capital{ color: #a0b4c0; font-size: 0.75rem; }
    .tag { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; margin-right: 4px; }
    .tag-green  { background: #00d4aa22; color: #00d4aa; }
    .tag-red    { background: #ff4b4b22; color: #ff4b4b; }
    .tag-yellow { background: #f5a62322; color: #f5a623; }
    .tag-blue   { background: #4b9fff22; color: #4b9fff; }
    .section-head { display: flex; align-items: center; gap: 10px; padding: 0.6rem 0; margin: 1rem 0 0.6rem 0; border-bottom: 1px solid #1e3347; }
    .section-head span { font-family: 'Space Mono', monospace; font-size: 1rem; color: #e8f4f8; }
    .stTabs [data-baseweb="tab-list"] { background: #0a1628; border-radius: 10px 10px 0 0; padding: 4px 8px 0 8px; gap: 4px; border-bottom: 2px solid #1e3347; }
    .stTabs [data-baseweb="tab"] { background: transparent; border-radius: 8px 8px 0 0; color: #6b8fa8 !important; font-family: 'Space Mono', monospace; font-size: 0.9rem; padding: 10px 24px; border: none; }
    .stTabs [aria-selected="true"] { background: #1a2d3d !important; color: #00d4aa !important; border-bottom: 2px solid #00d4aa; }
    .stTabs [data-baseweb="tab-panel"] { background: #0d1a26; border: 1px solid #1e3347; border-top: none; border-radius: 0 0 10px 10px; padding: 1.5rem; }
    .stButton > button { background: linear-gradient(135deg, #00d4aa, #0099cc); color: #000 !important; font-weight: 700; font-family: 'Space Mono', monospace; border: none; border-radius: 8px; padding: 0.55rem 1.5rem; font-size: 0.95rem; letter-spacing: 0.5px; width: 100%; }
    .stButton > button:hover { background: linear-gradient(135deg, #00ffcc, #00bbee) !important; }
    section[data-testid="stSidebar"] { background: #0a1628; }
    section[data-testid="stSidebar"] * { color: #e8f4f8 !important; }
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 { color: #00d4aa !important; }
    .affiliate-box { background: #111e2d; border: 1px solid #1e3347; border-radius: 10px; padding: 1rem; text-align: center; }
    .disclaimer { color: #3a5060; font-size: 0.72rem; text-align: center; margin-top: 2rem; padding: 1rem; border-top: 1px solid #1e3347; }
    .block-container { padding-top: 1rem !important; }
</style>
""", unsafe_allow_html=True)

# ── Stock Universes ───────────────────────────────────────────────────────────
FO_STOCKS = {
    'TCS.NS':        {'lot': 175,  'sector': 'IT'},
    'INFY.NS':       {'lot': 400,  'sector': 'IT'},
    'WIPRO.NS':      {'lot': 3000, 'sector': 'IT'},
    'HCLTECH.NS':    {'lot': 350,  'sector': 'IT'},
    'TECHM.NS':      {'lot': 600,  'sector': 'IT'},
    'LTTS.NS':       {'lot': 100,  'sector': 'IT'},
    'COFORGE.NS':    {'lot': 375,  'sector': 'IT'},
    'MPHASIS.NS':    {'lot': 275,  'sector': 'IT'},
    'PERSISTENT.NS': {'lot': 100,  'sector': 'IT'},
    'HDFCBANK.NS':   {'lot': 550,  'sector': 'Banking'},
    'ICICIBANK.NS':  {'lot': 700,  'sector': 'Banking'},
    'KOTAKBANK.NS':  {'lot': 2000, 'sector': 'Banking'},
    'AXISBANK.NS':   {'lot': 625,  'sector': 'Banking'},
    'SBIN.NS':       {'lot': 750,  'sector': 'Banking'},
    'BAJFINANCE.NS': {'lot': 750,  'sector': 'Finance'},
    'BAJAJFINSV.NS': {'lot': 250,  'sector': 'Finance'},
    'INDUSINDBK.NS': {'lot': 700,  'sector': 'Banking'},
    'MARUTI.NS':     {'lot': 50,   'sector': 'Auto'},
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
    'ULTRACEMCO.NS': {'lot': 50,   'sector': 'Cement'},
    'ADANIPORTS.NS': {'lot': 475,  'sector': 'Infra'},
    'TATASTEEL.NS':  {'lot': 5500, 'sector': 'Metals'},
    'HINDALCO.NS':   {'lot': 700,  'sector': 'Metals'},
    'JSWSTEEL.NS':   {'lot': 675,  'sector': 'Metals'},
    'VEDL.NS':       {'lot': 1150, 'sector': 'Metals'},
    'NMDC.NS':       {'lot': 6750, 'sector': 'Mining'},
    'BHARTIARTL.NS': {'lot': 475,  'sector': 'Telecom'},
    'BEL.NS':        {'lot': 1425, 'sector': 'Defense'},
    'HAL.NS':        {'lot': 150,  'sector': 'Defense'},
    'IRCTC.NS':      {'lot': 875,  'sector': 'Railways'},
}

HK_STOCKS = {
    '0823.HK': {'lot': 1000, 'sector': 'REIT', 'name': 'Link REIT'},
    '9888.HK': {'lot': 150,  'sector': 'Tech', 'name': 'Baidu'},
    '1810.HK': {'lot': 1000, 'sector': 'Tech', 'name': 'Xiaomi'},
}

# ── Shared Score Calculator ───────────────────────────────────────────────────
def calc_wheel_score(above_50dma, above_200dma, pct_from_high, hv_30, dividend_yield, capital_required, max_capital):
    score = 0
    if above_50dma:  score += 10
    if above_200dma: score += 15
    if 10 <= pct_from_high <= 35:  score += 25
    elif 5 <= pct_from_high < 10:  score += 15
    elif 35 < pct_from_high <= 50: score += 10
    if 20 <= hv_30 <= 45:          score += 20
    elif 15 <= hv_30 < 20:         score += 10
    elif 45 < hv_30 <= 60:         score += 10
    if dividend_yield >= 4:        score += 15
    elif dividend_yield >= 2:      score += 10
    elif dividend_yield >= 1:      score += 5
    if capital_required <= max_capital:         score += 15
    elif capital_required <= max_capital * 1.5: score += 8
    return score

# ── Data Fetchers ─────────────────────────────────────────────────────────────
def fetch_stock_data(ticker, lot_size, max_capital, expiry_days=30):
    try:
        stock = yf.Ticker(ticker)
        hist  = stock.history(period='1y')
        if len(hist) < 50: return None
        clean_key = ticker.replace('.NS','')
        st.session_state.hist_data[clean_key] = hist
        info          = stock.info
        current_price = hist['Close'].iloc[-1]
        ma50   = hist['Close'].rolling(50).mean().iloc[-1]
        ma200  = hist['Close'].rolling(200).mean().iloc[-1] if len(hist) >= 200 else None
        above_50dma  = bool(current_price > ma50)
        above_200dma = bool(current_price > ma200) if ma200 else None
        high_52w      = hist['High'].max()
        pct_from_high = ((high_52w - current_price) / high_52w) * 100
        hv_30  = hist['Close'].pct_change().dropna()[-30:].std() * np.sqrt(252) * 100
        annual_div     = info.get('dividendRate') or 0
        dividend_yield = min((annual_div / current_price * 100) if current_price > 0 else 0, 20.0)
        sigma  = hv_30 / 100; sqrtT = np.sqrt(expiry_days / 365)
        strike_d30  = round(current_price * np.exp(-0.524 * sigma * sqrtT) / 5) * 5
        strike_d25  = round(current_price * np.exp(-0.674 * sigma * sqrtT) / 5) * 5
        strike_5pct = round(current_price * 0.95 / 5) * 5
        capital_required = strike_5pct * lot_size
        score = calc_wheel_score(above_50dma, above_200dma, pct_from_high, hv_30, dividend_yield, capital_required, max_capital)
        return {
            'ticker': clean_key, 'name': info.get('longName', clean_key)[:28],
            'sector': FO_STOCKS[ticker]['sector'], 'lot_size': lot_size,
            'current_price': round(current_price, 2),
            'strike_d30': strike_d30, 'strike_d25': strike_d25, 'strike_5pct': strike_5pct,
            'capital_required': capital_required,
            'above_50dma': above_50dma, 'above_200dma': above_200dma,
            'pct_from_high': round(pct_from_high, 1), 'hv_30': round(hv_30, 1),
            'dividend_yield': round(dividend_yield, 2), 'wheel_score': score, 'currency': 'Rs.',
        }
    except: return None

def fetch_hk_stock_data(ticker, lot_size, max_capital_hkd, expiry_days=30):
    try:
        stock = yf.Ticker(ticker)
        hist  = stock.history(period='1y')
        if len(hist) < 50: return None
        clean_key = ticker.replace('.HK','').lstrip('0')
        st.session_state.hist_data[clean_key] = hist
        info          = stock.info
        current_price = hist['Close'].iloc[-1]
        ma50   = hist['Close'].rolling(50).mean().iloc[-1]
        ma200  = hist['Close'].rolling(200).mean().iloc[-1] if len(hist) >= 200 else None
        above_50dma  = bool(current_price > ma50)
        above_200dma = bool(current_price > ma200) if ma200 else None
        high_52w      = hist['High'].max()
        pct_from_high = ((high_52w - current_price) / high_52w) * 100
        hv_30  = hist['Close'].pct_change().dropna()[-30:].std() * np.sqrt(252) * 100
        annual_div     = info.get('dividendRate') or 0
        dividend_yield = min((annual_div / current_price * 100) if current_price > 0 else 0, 20.0)
        sigma  = hv_30 / 100; sqrtT = np.sqrt(expiry_days / 365)
        strike_d30  = round(current_price * np.exp(-0.524 * sigma * sqrtT) * 2) / 2
        strike_d25  = round(current_price * np.exp(-0.674 * sigma * sqrtT) * 2) / 2
        strike_5pct = round(current_price * 0.95 * 2) / 2
        capital_required = strike_5pct * lot_size
        score = calc_wheel_score(above_50dma, above_200dma, pct_from_high, hv_30, dividend_yield, capital_required, max_capital_hkd)
        return {
            'ticker': HK_STOCKS[ticker]['name'], 'hk_ticker': ticker,
            'name': info.get('longName', HK_STOCKS[ticker]['name'])[:28],
            'sector': HK_STOCKS[ticker]['sector'], 'lot_size': lot_size,
            'current_price': round(current_price, 2),
            'strike_d30': strike_d30, 'strike_d25': strike_d25, 'strike_5pct': strike_5pct,
            'capital_required': capital_required,
            'above_50dma': above_50dma, 'above_200dma': above_200dma,
            'pct_from_high': round(pct_from_high, 1), 'hv_30': round(hv_30, 1),
            'dividend_yield': round(dividend_yield, 2), 'wheel_score': score, 'currency': 'HK$',
        }
    except: return None

# ── Session State ─────────────────────────────────────────────────────────────
for key, val in {'show_chart': {}, 'hist_data': {}, 'nse_results': None, 'nse_time': None, 'hk_results': None, 'hk_time': None}.items():
    if key not in st.session_state:
        st.session_state[key] = val

def toggle_chart(key):
    st.session_state.show_chart[key] = not st.session_state.show_chart.get(key, True)

# ── Chart Renderer ────────────────────────────────────────────────────────────
def render_chart(chart_key, exchange='NSE'):
    hist = st.session_state.hist_data.get(chart_key)
    if hist is None or len(hist) < 50:
        st.warning(f"No chart data for {chart_key}"); return
    df = hist.copy(); df.index = pd.to_datetime(df.index)
    df['MA50']    = df['Close'].rolling(50).mean()
    df['MA200']   = df['Close'].rolling(200).mean()
    df['BB_mid']  = df['Close'].rolling(20).mean()
    df['BB_std']  = df['Close'].rolling(20).std()
    df['BB_upper']= df['BB_mid'] + 2 * df['BB_std']
    df['BB_lower']= df['BB_mid'] - 2 * df['BB_std']
    delta = df['Close'].diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    df['RSI'] = 100 - (100 / (1 + gain / loss.replace(0, 1e-10)))
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05,
        row_heights=[0.70, 0.30], subplot_titles=(f"{exchange}:{chart_key} — Daily", "RSI (14)"))
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'], name='Price',
        increasing_line_color='#00d4aa', decreasing_line_color='#ff4b4b'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_upper'], name='BB Upper',
        line=dict(color='#4b9fff', width=1, dash='dot'), opacity=0.7), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_lower'], name='BB Lower',
        line=dict(color='#4b9fff', width=1, dash='dot'), opacity=0.7,
        fill='tonexty', fillcolor='rgba(75,159,255,0.05)'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_mid'], name='BB Mid',
        line=dict(color='#4b9fff', width=1), opacity=0.4), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MA50'],  name='MA 50',
        line=dict(color='#00d4aa', width=1.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MA200'], name='MA 200',
        line=dict(color='#f5a623', width=1.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI',
        line=dict(color='#c084fc', width=1.5)), row=2, col=1)
    fig.add_hline(y=70, line=dict(color='#ff4b4b', dash='dot', width=1), row=2, col=1)
    fig.add_hline(y=30, line=dict(color='#00d4aa', dash='dot', width=1), row=2, col=1)
    fig.update_layout(height=540, paper_bgcolor='#0a1628', plot_bgcolor='#0a1628',
        font=dict(color='#a0b4c0', size=11),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1,
            bgcolor='rgba(0,0,0,0)', font=dict(size=10)),
        xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=40, b=10),
        yaxis=dict(showgrid=True, gridcolor='#1a2d3d', side='right'),
        yaxis2=dict(showgrid=True, gridcolor='#1a2d3d', side='right', range=[0,100]))
    fig.update_xaxes(showgrid=True, gridcolor='#1a2d3d', zeroline=False)
    st.plotly_chart(fig, use_container_width=True)

# ── Card Renderer ─────────────────────────────────────────────────────────────
def render_card(r, chart_key, exchange='NSE'):
    card_class  = 'tier1-card' if r.get('_tier') == 1 else 'tier2-card'
    trend_tag   = "<span class='tag tag-green'>📈 Above 200DMA</span>" if r['above_200dma'] else \
                  "<span class='tag tag-yellow'>〰️ Above 50DMA</span>" if r['above_50dma'] else \
                  "<span class='tag tag-red'>📉 Below MAs</span>"
    div_tag     = f"<span class='tag tag-blue'>💰 Div {r['dividend_yield']:.1f}%</span>" if r['dividend_yield'] > 0 else ""
    score_cls   = "score-high" if r['wheel_score'] >= 60 else "score-mid"
    cur         = r['currency']
    fmt         = ",.1f" if cur == 'HK$' else ",.0f"
    cap_d30     = r['strike_d30'] * r['lot_size']
    cap_d25     = r['strike_d25'] * r['lot_size']
    cap_5pct    = r['strike_5pct'] * r['lot_size']
    chart_open  = st.session_state.show_chart.get(chart_key, True)
    chart_label = "📉 Hide Chart" if chart_open else "📈 View Chart"
    st.markdown(f"""
    <div class='{card_class}'>
        <div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px'>
            <div>
                <span class='ticker-name'>{r['ticker']}</span>
                <span style='color:#6b8fa8; margin-left:8px; font-size:0.82rem'>{r['name']}</span>
            </div>
            <span class='score-badge {score_cls}'>Score {r['wheel_score']}/100</span>
        </div>
        <div style='margin-top:8px; display:flex; gap:14px; flex-wrap:wrap; font-size:0.83rem; color:#a0b4c0'>
            <span>🏭 {r['sector']}</span>
            <span>📦 Lot: {r['lot_size']:,}</span>
            <span>💵 CMP: <strong style='color:#fff'>{cur}{r['current_price']:,.2f}</strong></span>
            <span>📉 52W High: <strong style='color:#f5a623'>-{r['pct_from_high']:.1f}%</strong></span>
            <span>🌡️ HV30: {r['hv_30']:.1f}%</span>
        </div>
        <div style='margin-top:6px'>{trend_tag}{div_tag}</div>
        <div class='strike-box'>
            <div style='color:#6b8fa8; font-size:0.7rem; text-transform:uppercase; letter-spacing:1px; margin-bottom:6px'>Strike Suggestions</div>
            <div class='strike-row'>
                <span class='strike-label'>🟢 Delta ~0.30 (Aggressive)</span>
                <span class='strike-value'>{cur}{r['strike_d30']:{fmt}}</span>
                <span class='strike-capital'>Capital: {cur}{cap_d30:,.0f}</span>
            </div>
            <div class='strike-row'>
                <span class='strike-label'>🟡 Delta ~0.25 (Moderate)</span>
                <span class='strike-value'>{cur}{r['strike_d25']:{fmt}}</span>
                <span class='strike-capital'>Capital: {cur}{cap_d25:,.0f}</span>
            </div>
            <div class='strike-row'>
                <span class='strike-label'>🔵 5% OTM (Conservative)</span>
                <span class='strike-value'>{cur}{r['strike_5pct']:{fmt}}</span>
                <span class='strike-capital'>Capital: {cur}{cap_5pct:,.0f}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.button(chart_label, key=f"btn_{chart_key}_{r.get('_tier',0)}",
              on_click=toggle_chart, args=(chart_key,))
    if chart_open:
        render_chart(chart_key, exchange)

# ── App Header ────────────────────────────────────────────────────────────────
st.markdown("""
<div class='app-header'>
    <div>
        <p class='app-title'>🎯 WHEEL STRATEGY SCREENER</p>
        <p class='app-sub'>Cash-Secured Put (CSP) · NSE F&O + HKEX · Real-Time Data</p>
    </div>
    <div style='color:#6b8fa8; font-size:0.8rem; text-align:right'>
        Built for options traders<br>
        <span style='color:#00d4aa'>Wheel · CSP · Covered Call</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar — Affiliate only ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🤝 Open a Demat Account")
    st.markdown("""
    <div class='affiliate-box'>
        <p style='color:#a0b4c0; font-size:0.8rem; margin:0 0 10px 0'>Trusted brokers for options trading:</p>
        <a href='https://zerodha.com/open-account?c=SS1428' target='_blank'
           style='color:#00d4aa; text-decoration:none; font-weight:600; display:block; margin:8px 0'>
           🟢 Zerodha — Open Account</a>
        <a href='https://groww.in' target='_blank'
           style='color:#00d4aa; text-decoration:none; font-weight:600; display:block; margin:8px 0'>
           🟢 Groww — Open Account</a>
        <a href='https://www.angelone.in' target='_blank'
           style='color:#00d4aa; text-decoration:none; font-weight:600; display:block; margin:8px 0'>
           🟢 Angel One — Open Account</a>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<div style='color:#3a5060; font-size:0.72rem; text-align:center'>⚠️ Not SEBI registered.<br>For educational purposes only.<br>Options trading involves risk of loss.</div>", unsafe_allow_html=True)

# ── TABS ──────────────────────────────────────────────────────────────────────
tab_nse, tab_hk = st.tabs(["🇮🇳  NSE Screener", "🇭🇰  HK Screener"])

# ── TAB 1: NSE ────────────────────────────────────────────────────────────────
with tab_nse:
    st.markdown("<div class='config-panel'><div class='config-title'>⚙️ Screener Configuration</div>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns([2, 1.2, 1.5, 1.2, 1])
    with c1:
        max_capital = st.slider("💰 Max Capital / Lot (Rs.)", 50_000, 2_000_000, 1_500_000, 10_000, format="Rs.%d", key="nse_cap")
        st.markdown(f"<p style='color:#00d4aa;font-weight:700;font-size:0.82rem;margin-top:-8px'>Rs.{max_capital:,}</p>", unsafe_allow_html=True)
    with c2:
        expiry_days = st.selectbox("📅 Expiry", [7, 15, 30, 45], index=2, format_func=lambda x: f"{x}d", key="nse_exp")
    with c3:
        sectors = st.multiselect("🏭 Sectors", sorted(set(v['sector'] for v in FO_STOCKS.values())), default=[], placeholder="All", key="nse_sec")
    with c4:
        min_score = st.slider("🎯 Min Score", 0, 100, 40, 5, key="nse_score")
        st.markdown(f"<p style='color:#00d4aa;font-weight:700;font-size:0.82rem;margin-top:-8px'>{min_score}/100</p>", unsafe_allow_html=True)
    with c5:
        st.markdown("<br>", unsafe_allow_html=True)
        run_nse = st.button("🚀 Run Scan", key="run_nse")
    st.markdown("</div>", unsafe_allow_html=True)

    if run_nse:
        st.session_state.nse_results = None
        st.session_state.show_chart  = {}
        filtered = {k: v for k, v in FO_STOCKS.items() if not sectors or v['sector'] in sectors}
        bar      = st.progress(0, text="🔍 Scanning NSE stocks...")
        results  = []
        for i, (ticker, meta) in enumerate(filtered.items()):
            bar.progress((i+1)/len(filtered), text=f"🔍 {ticker.replace('.NS','')} ({i+1}/{len(filtered)})")
            d = fetch_stock_data(ticker, meta['lot'], max_capital, expiry_days)
            if d and d['wheel_score'] >= min_score:
                results.append(d)
                st.session_state.show_chart[d['ticker']] = True
        bar.empty()
        st.session_state.nse_results = results
        st.session_state.nse_time    = datetime.now().strftime('%d %b %Y, %I:%M %p')

    if st.session_state.nse_results:
        results = st.session_state.nse_results
        df      = pd.DataFrame(results)
        tier1   = df[(df['capital_required'] <= max_capital) & (df['wheel_score'] >= 55) & (df['above_200dma'] == True)].sort_values('wheel_score', ascending=False)
        tier2   = df[~df['ticker'].isin(tier1['ticker'])].sort_values('wheel_score', ascending=False).head(10)
        st.markdown(f"<p style='color:#6b8fa8; font-size:0.8rem; margin:0.5rem 0'>Last scan: {st.session_state.nse_time}</p>", unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns(4)
        for col, lbl, val in zip([m1,m2,m3,m4], ['Scanned','Tier 1','Tier 2','Avg Score'], [len(results), len(tier1), len(tier2), round(df['wheel_score'].mean())]):
            col.markdown(f"<div class='metric-box'><div class='label'>{lbl}</div><div class='value'>{val}</div></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-head'><span>🏆 Tier 1 — Best CSP Candidates</span></div>", unsafe_allow_html=True)
        if tier1.empty:
            st.info("No Tier 1 stocks. Try increasing capital limit or lowering min score.")
        for _, row in tier1.iterrows():
            r = row.to_dict(); r['_tier'] = 1; render_card(r, r['ticker'], 'NSE')
        st.markdown("<div class='section-head'><span>👀 Tier 2 — Watchlist</span></div>", unsafe_allow_html=True)
        for _, row in tier2.iterrows():
            r = row.to_dict(); r['_tier'] = 2; render_card(r, r['ticker'], 'NSE')
        st.markdown("<div class='section-head'><span>📊 Sector Summary</span></div>", unsafe_allow_html=True)
        sec_df = df.groupby('sector').agg(Stocks=('ticker','count'), Avg_Score=('wheel_score','mean'), Avg_HV30=('hv_30','mean')).reset_index().sort_values('Avg_Score', ascending=False)
        sec_df['Avg_Score'] = sec_df['Avg_Score'].round(0).astype(int)
        sec_df['Avg_HV30']  = sec_df['Avg_HV30'].round(1)
        st.dataframe(sec_df, use_container_width=True, hide_index=True)
        st.download_button("📥 Download Results (CSV)", data=df.sort_values('wheel_score', ascending=False).to_csv(index=False), file_name=f"nse_wheel_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", mime="text/csv", use_container_width=True)
    else:
        st.markdown("""
        <div style='text-align:center; padding:4rem 2rem; color:#3a5060'>
            <div style='font-size:3.5rem'>🇮🇳</div>
            <p style='font-family:Space Mono,monospace; color:#6b8fa8; margin:1rem 0 0.5rem'>Configure & Run Scan</p>
            <p style='font-size:0.85rem'>Set your settings above and click <strong style='color:#00d4aa'>Run Scan</strong></p>
            <p style='font-size:0.78rem; margin-top:0.5rem'>~55 F&O stocks · RSI + Bollinger Bands · 3 strike suggestions</p>
        </div>""", unsafe_allow_html=True)

# ── TAB 2: HK ─────────────────────────────────────────────────────────────────
with tab_hk:
    st.markdown("<div class='config-panel'><div class='config-title'>⚙️ Screener Configuration</div>", unsafe_allow_html=True)
    h1, h2, h3 = st.columns([2, 1.5, 1])
    with h1:
        max_cap_hkd = st.slider("💰 Max Capital / Lot (HKD)", 5_000, 500_000, 50_000, 5_000, format="HK$%d", key="hk_cap")
        st.markdown(f"<p style='color:#00d4aa;font-weight:700;font-size:0.82rem;margin-top:-8px'>HK${max_cap_hkd:,}</p>", unsafe_allow_html=True)
    with h2:
        hk_expiry = st.selectbox("📅 Expiry", [7, 15, 30, 45], index=2, format_func=lambda x: f"{x} days", key="hk_exp")
    with h3:
        st.markdown("<br>", unsafe_allow_html=True)
        run_hk = st.button("🚀 Run Scan", key="run_hk")
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='display:flex; gap:10px; flex-wrap:wrap; margin-bottom:1rem'>
        <span class='tag tag-blue' style='font-size:0.8rem; padding:4px 10px'>📌 Link REIT (0823.HK) · Lot 1,000</span>
        <span class='tag tag-blue' style='font-size:0.8rem; padding:4px 10px'>📌 Baidu (9888.HK) · Lot 150</span>
        <span class='tag tag-blue' style='font-size:0.8rem; padding:4px 10px'>📌 Xiaomi (1810.HK) · Lot 1,000</span>
    </div>""", unsafe_allow_html=True)

    if run_hk:
        st.session_state.hk_results = None
        hk_bar = st.progress(0, text="🔍 Scanning HKEX stocks...")
        hk_res = []
        for i, (ticker, meta) in enumerate(HK_STOCKS.items()):
            hk_bar.progress((i+1)/len(HK_STOCKS), text=f"🔍 {meta['name']} ({i+1}/{len(HK_STOCKS)})")
            d = fetch_hk_stock_data(ticker, meta['lot'], max_cap_hkd, hk_expiry)
            if d:
                hk_res.append(d)
                st.session_state.show_chart[ticker.replace('.HK','').lstrip('0')] = True
        hk_bar.empty()
        st.session_state.hk_results = hk_res
        st.session_state.hk_time    = datetime.now().strftime('%d %b %Y, %I:%M %p')

    if st.session_state.hk_results:
        hk_res   = st.session_state.hk_results
        tier1_hk = [r for r in hk_res if r['wheel_score'] >= 55 and r['above_200dma']]
        tier2_hk = [r for r in hk_res if r not in tier1_hk]
        st.markdown(f"<p style='color:#6b8fa8; font-size:0.8rem; margin:0.5rem 0'>Last scan: {st.session_state.hk_time}</p>", unsafe_allow_html=True)
        a1, a2, a3 = st.columns(3)
        for col, lbl, val in zip([a1,a2,a3], ['Scanned','Tier 1','Tier 2'], [len(hk_res), len(tier1_hk), len(tier2_hk)]):
            col.markdown(f"<div class='metric-box'><div class='label'>{lbl}</div><div class='value'>{val}</div></div>", unsafe_allow_html=True)
        if tier1_hk:
            st.markdown("<div class='section-head'><span>🏆 Tier 1 — Best HK CSP Candidates</span></div>", unsafe_allow_html=True)
            for r in tier1_hk:
                r['_tier'] = 1; render_card(r, r['hk_ticker'].replace('.HK','').lstrip('0'), 'HKEX')
        st.markdown("<div class='section-head'><span>👀 Tier 2 — HK Watchlist</span></div>", unsafe_allow_html=True)
        for r in tier2_hk:
            r['_tier'] = 2; render_card(r, r['hk_ticker'].replace('.HK','').lstrip('0'), 'HKEX')
    else:
        st.markdown("""
        <div style='text-align:center; padding:4rem 2rem; color:#3a5060'>
            <div style='font-size:3.5rem'>🇭🇰</div>
            <p style='font-family:Space Mono,monospace; color:#6b8fa8; margin:1rem 0 0.5rem'>Configure & Run Scan</p>
            <p style='font-size:0.85rem'>Set your HKD capital limit above and click <strong style='color:#00d4aa'>Run Scan</strong></p>
            <p style='font-size:0.78rem; margin-top:0.5rem'>Link REIT · Baidu · Xiaomi · Charts with RSI + BB</p>
        </div>""", unsafe_allow_html=True)

# ── Disclaimer ────────────────────────────────────────────────────────────────
st.markdown("""
<div class='disclaimer'>
    ⚠️ For educational purposes only. Not SEBI registered. Options trading involves substantial risk of loss.
    Do your own research. Lot sizes change quarterly — verify at
    <a href='https://www.nseindia.com' target='_blank' style='color:#3a7080'>nseindia.com</a>
</div>
""", unsafe_allow_html=True)
