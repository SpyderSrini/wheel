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
import json
import requests
from datetime import datetime, timedelta

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
    section[data-testid="stSidebar"] { display: none !important; }
    .block-container { max-width: 100% !important; padding-left: 2rem !important; padding-right: 2rem !important; }
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

# ── US Stock Universe ────────────────────────────────────────────────────────
US_STOCKS = {
    # Tech
    'AAPL':  {'lot': 1, 'sector': 'Tech'},
    'MSFT':  {'lot': 1, 'sector': 'Tech'},
    'GOOGL': {'lot': 1, 'sector': 'Tech'},
    'META':  {'lot': 1, 'sector': 'Tech'},
    'NVDA':  {'lot': 1, 'sector': 'Tech'},
    'AMD':   {'lot': 1, 'sector': 'Tech'},
    'INTC':  {'lot': 1, 'sector': 'Tech'},
    'CRM':   {'lot': 1, 'sector': 'Tech'},
    # Finance
    'JPM':   {'lot': 1, 'sector': 'Finance'},
    'BAC':   {'lot': 1, 'sector': 'Finance'},
    'GS':    {'lot': 1, 'sector': 'Finance'},
    'MS':    {'lot': 1, 'sector': 'Finance'},
    'WFC':   {'lot': 1, 'sector': 'Finance'},
    # Energy
    'XOM':   {'lot': 1, 'sector': 'Energy'},
    'CVX':   {'lot': 1, 'sector': 'Energy'},
    'ET':    {'lot': 1, 'sector': 'Energy'},
    'OXY':   {'lot': 1, 'sector': 'Energy'},
    # ETFs (great for wheel)
    'SPY':   {'lot': 1, 'sector': 'ETF'},
    'QQQ':   {'lot': 1, 'sector': 'ETF'},
    'IWM':   {'lot': 1, 'sector': 'ETF'},
    'SLV':   {'lot': 1, 'sector': 'ETF'},
    'GLD':   {'lot': 1, 'sector': 'ETF'},
    # Consumer
    'AMZN':  {'lot': 1, 'sector': 'Consumer'},
    'WMT':   {'lot': 1, 'sector': 'Consumer'},
    'KO':    {'lot': 1, 'sector': 'Consumer'},
    'PG':    {'lot': 1, 'sector': 'Consumer'},
    # Healthcare
    'JNJ':   {'lot': 1, 'sector': 'Healthcare'},
    'PFE':   {'lot': 1, 'sector': 'Healthcare'},
    # Telecom
    'T':     {'lot': 1, 'sector': 'Telecom'},
}

# ── Metals Universe ──────────────────────────────────────────────────────────
METALS_STOCKS = {
    # Gold
    'GLD':  {'lot': 1, 'sector': 'Gold',      'metal': 'Gold',      'type': 'ETF'},
    'NEM':  {'lot': 1, 'sector': 'Gold',      'metal': 'Gold',      'type': 'Miner'},
    'GOLD': {'lot': 1, 'sector': 'Gold',      'metal': 'Gold',      'type': 'Miner'},
    # Silver
    'SLV':  {'lot': 1, 'sector': 'Silver',    'metal': 'Silver',    'type': 'ETF'},
    'AG':   {'lot': 1, 'sector': 'Silver',    'metal': 'Silver',    'type': 'Miner'},
    # Copper
    'FCX':  {'lot': 1, 'sector': 'Copper',    'metal': 'Copper',    'type': 'Miner'},
    'CPER': {'lot': 1, 'sector': 'Copper',    'metal': 'Copper',    'type': 'ETF'},
    # Steel
    'NUE':  {'lot': 1, 'sector': 'Steel',     'metal': 'Steel',     'type': 'Producer'},
    'X':    {'lot': 1, 'sector': 'Steel',     'metal': 'Steel',     'type': 'Producer'},
    'CLF':  {'lot': 1, 'sector': 'Steel',     'metal': 'Steel',     'type': 'Producer'},
    # Aluminium
    'AA':   {'lot': 1, 'sector': 'Aluminium', 'metal': 'Aluminium', 'type': 'Producer'},
}

# Metal color mapping for UI
METAL_COLORS = {
    'Gold':      '#f5a623',
    'Silver':    '#a0b4c0',
    'Copper':    '#cd7c3a',
    'Steel':     '#6b8fa8',
    'Aluminium': '#8884d8',
}

# ── Shared Score Calculator ───────────────────────────────────────────────────
def calc_wheel_score(above_50dma, above_200dma, pct_from_high, hv_30, dividend_yield, capital_required=0, max_capital=999_999_999):
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

# ── US Data Fetcher ──────────────────────────────────────────────────────────
def fetch_us_stock_data(ticker, max_capital_usd, expiry_days=30):
    try:
        stock = yf.Ticker(ticker)
        hist  = stock.history(period='1y')
        if len(hist) < 50: return None
        st.session_state.hist_data[ticker] = hist
        info          = stock.info
        current_price = hist['Close'].iloc[-1]
        ma50   = hist['Close'].rolling(50).mean().iloc[-1]
        ma200  = hist['Close'].rolling(200).mean().iloc[-1] if len(hist) >= 200 else None
        above_50dma  = bool(current_price > ma50)
        above_200dma = bool(current_price > ma200) if ma200 else None
        high_52w      = hist['High'].max()
        pct_from_high = ((high_52w - current_price) / high_52w) * 100
        hv_30  = hist['Close'].pct_change().dropna()[-30:].std() * np.sqrt(252) * 100
        annual_div     = info.get('dividendYield') or 0
        dividend_yield = min(annual_div * 100, 20.0)
        # US options: 100 shares per contract, strike rounded to nearest $0.50
        sigma      = hv_30 / 100; sqrtT = np.sqrt(expiry_days / 365)
        strike_d30  = round(current_price * np.exp(-0.524 * sigma * sqrtT) * 2) / 2
        strike_d25  = round(current_price * np.exp(-0.674 * sigma * sqrtT) * 2) / 2
        strike_5pct = round(current_price * 0.95 * 2) / 2
        capital_required = strike_5pct * 100  # 1 contract = 100 shares
        score = calc_wheel_score(above_50dma, above_200dma, pct_from_high, hv_30,
                                 dividend_yield, capital_required, max_capital_usd)
        return {
            'ticker': ticker, 'name': info.get('shortName', ticker)[:28],
            'sector': US_STOCKS[ticker]['sector'], 'lot_size': 100,
            'current_price': round(current_price, 2),
            'strike_d30': strike_d30, 'strike_d25': strike_d25, 'strike_5pct': strike_5pct,
            'capital_required': capital_required,
            'above_50dma': above_50dma, 'above_200dma': above_200dma,
            'pct_from_high': round(pct_from_high, 1), 'hv_30': round(hv_30, 1),
            'dividend_yield': round(dividend_yield, 2), 'wheel_score': score, 'currency': '$',
        }
    except: return None

# ── Wealth Builder Universe (Claude's picks) ─────────────────────────────────
WB_STOCKS = {
    # 🇮🇳 INDIA — Dividend kings + wheel-friendly
    'ITC.NS':        {'exchange': 'NSE', 'theme': 'FMCG',       'region': 'India',  'why': 'Dividend king, consistent cash flows, liquid options'},
    'COALINDIA.NS':  {'exchange': 'NSE', 'theme': 'Energy',      'region': 'India',  'why': 'PSU monopoly, massive dividend, low volatility'},
    'POWERGRID.NS':  {'exchange': 'NSE', 'theme': 'Utility',     'region': 'India',  'why': 'Regulated returns, quarterly dividends, stable'},
    'HDFCBANK.NS':   {'exchange': 'NSE', 'theme': 'Banking',     'region': 'India',  'why': 'Best private bank, quality loan book, growing'},
    'INFY.NS':       {'exchange': 'NSE', 'theme': 'IT',          'region': 'India',  'why': 'Dollar earnings, consistent buybacks, global moat'},
    'BAJAJ-AUTO.NS': {'exchange': 'NSE', 'theme': 'Auto',        'region': 'India',  'why': 'Best-in-class margins, strong dividend, EV pivot'},
    'NESTLEIND.NS':  {'exchange': 'NSE', 'theme': 'FMCG',        'region': 'India',  'why': 'Defensive FMCG, pricing power, consistent compounder'},
    'TITAN.NS':      {'exchange': 'NSE', 'theme': 'Consumer',    'region': 'India',  'why': 'Premium brand moat, aspirational consumption play'},
    # 🇭🇰 HONG KONG — Yield + stability
    '0823.HK':       {'exchange': 'HKEX', 'theme': 'REIT',       'region': 'HK',     'why': 'Best Asian REIT, inflation-linked rents, 4%+ yield'},
    '0005.HK':       {'exchange': 'HKEX', 'theme': 'Banking',    'region': 'HK',     'why': 'HSBC global franchise, high dividend, recovering HK'},
    '0002.HK':       {'exchange': 'HKEX', 'theme': 'Utility',    'region': 'HK',     'why': 'CLP utility monopoly, reliable dividend, low risk'},
    '0066.HK':       {'exchange': 'HKEX', 'theme': 'Transport',  'region': 'HK',     'why': 'MTR rail monopoly, property income, consistent dividend'},
    '1810.HK':       {'exchange': 'HKEX', 'theme': 'Tech',       'region': 'HK',     'why': 'Xiaomi ecosystem, EV growth story, undervalued tech'},
    '2318.HK':       {'exchange': 'HKEX', 'theme': 'Insurance',  'region': 'HK',     'why': 'Ping An — China insurance leader, deep value, high yield'},
    # 🇺🇸 USA — Dividend aristocrats + premium generators
    'KO':            {'exchange': 'NYSE',   'theme': 'Consumer',  'region': 'USA',    'why': 'Dividend aristocrat 60+ years, global brand, recession-proof'},
    'PG':            {'exchange': 'NYSE',   'theme': 'Consumer',  'region': 'USA',    'why': 'Consumer staples moat, pricing power, consistent grower'},
    'JNJ':           {'exchange': 'NYSE',   'theme': 'Healthcare','region': 'USA',    'why': 'Healthcare giant, dividend king, diversified revenue'},
    'ABBV':          {'exchange': 'NYSE',   'theme': 'Pharma',    'region': 'USA',    'why': 'Humira + Skyrizi pipeline, 4%+ yield, strong FCF'},
    'XOM':           {'exchange': 'NYSE',   'theme': 'Energy',    'region': 'USA',    'why': 'Energy supermajor, rising dividend, LNG tailwinds'},
    'ET':            {'exchange': 'NYSE',   'theme': 'Energy',    'region': 'USA',    'why': 'Midstream MLP, 8%+ distribution, AI energy infrastructure'},
    'T':             {'exchange': 'NYSE',   'theme': 'Telecom',   'region': 'USA',    'why': '6%+ dividend yield, 5G infrastructure, debt reducing'},
    'O':             {'exchange': 'NYSE',   'theme': 'REIT',      'region': 'USA',    'why': 'Monthly dividend REIT, 30+ years streak, net lease model'},
    'MSFT':          {'exchange': 'NASDAQ', 'theme': 'Tech',      'region': 'USA',    'why': 'Cloud monopoly, AI leader, growing dividend, fortress balance sheet'},
    'AAPL':          {'exchange': 'NASDAQ', 'theme': 'Tech',      'region': 'USA',    'why': 'Ecosystem lock-in, massive buybacks, services growth'},
    'JPM':           {'exchange': 'NYSE',   'theme': 'Banking',   'region': 'USA',    'why': 'Best US bank, growing dividend, capital return machine'},
    'SLV':           {'exchange': 'NYSE',   'theme': 'Metal',     'region': 'USA',    'why': 'Silver supply deficit, industrial demand, 3x weekly options'},
    'GLD':           {'exchange': 'NYSE',   'theme': 'Metal',     'region': 'USA',    'why': 'Safe haven, all-time highs breakout, inflation hedge'},
    'SPY':           {'exchange': 'NYSE',   'theme': 'ETF',       'region': 'USA',    'why': 'S&P500 ETF, most liquid options on earth, low cost wheel'},
    'QQQ':           {'exchange': 'NASDAQ', 'theme': 'ETF',       'region': 'USA',    'why': 'Nasdaq ETF, tech exposure, excellent option premiums'},
    'NVDA':          {'exchange': 'NASDAQ', 'theme': 'Tech',      'region': 'USA',    'why': 'AI chip monopoly, explosive growth, high premium for CSPs'},
}

REGION_COLORS = {
    'India': '#f5a623',
    'HK':    '#00d4aa',
    'USA':   '#4b9fff',
}

THEME_ICONS = {
    'FMCG': '🛒', 'Energy': '⚡', 'Utility': '💡', 'Banking': '🏦',
    'IT': '💻', 'Auto': '🚗', 'Consumer': '🛍️', 'REIT': '🏢',
    'Transport': '🚇', 'Insurance': '🛡️', 'Healthcare': '🏥',
    'Pharma': '💊', 'Telecom': '📡', 'Tech': '🖥️', 'Metal': '🪙',
    'ETF': '📊',
}

def calc_wealth_score(above_200dma, pct_from_high, hv_30, dividend_yield,
                      profit_margins, debt_to_equity, revenue_growth, beta, analyst_upside):
    """Wealth Builder scoring — weighted toward income + quality + safety"""
    score = 0
    # 1. Trend (15 pts) — must be investable
    if above_200dma: score += 15

    # 2. Pullback sweet spot (20 pts) — buy quality on dips
    if 10 <= pct_from_high <= 30:   score += 20
    elif 5  <= pct_from_high < 10:  score += 12
    elif 30 < pct_from_high <= 45:  score += 10
    elif pct_from_high < 5:         score += 8   # near highs — less upside

    # 3. Dividend yield (25 pts) — core wealth builder criterion
    if dividend_yield >= 5:         score += 25
    elif dividend_yield >= 3:       score += 20
    elif dividend_yield >= 2:       score += 14
    elif dividend_yield >= 1:       score += 8
    # No dividend = 0 pts — penalised in wealth builder

    # 4. Option premium viability (15 pts)
    if 18 <= hv_30 <= 45:           score += 15
    elif 15 <= hv_30 < 18:          score += 8
    elif 45 < hv_30 <= 60:          score += 10

    # 5. Business quality (15 pts)
    if profit_margins and profit_margins > 20: score += 15
    elif profit_margins and profit_margins > 10: score += 10
    elif profit_margins and profit_margins > 5:  score += 5

    # 6. Balance sheet safety (10 pts)
    if debt_to_equity is not None:
        if debt_to_equity < 50:     score += 10
        elif debt_to_equity < 100:  score += 6
        elif debt_to_equity < 200:  score += 3
    else:
        score += 5  # unknown — neutral

    return min(score, 100)

def fetch_wb_stock_data(ticker, meta, expiry_days=30):
    """Fetch data for wealth builder stock"""
    try:
        stock = yf.Ticker(ticker)
        hist  = stock.history(period='1y')
        if len(hist) < 50: return None
        st.session_state.hist_data[ticker.replace('.NS','').replace('.HK','').lstrip('0')] = hist
        info          = stock.info
        current_price = hist['Close'].iloc[-1]
        ma50   = hist['Close'].rolling(50).mean().iloc[-1]
        ma200  = hist['Close'].rolling(200).mean().iloc[-1] if len(hist) >= 200 else None
        above_50dma  = bool(current_price > ma50)
        above_200dma = bool(current_price > ma200) if ma200 else False
        high_52w      = hist['High'].max()
        low_52w       = hist['Low'].min()
        pct_from_high = ((high_52w - current_price) / high_52w) * 100
        hv_30  = hist['Close'].pct_change().dropna()[-30:].std() * np.sqrt(252) * 100
        # Fundamentals
        annual_div     = info.get('dividendRate') or 0
        div_yield      = min((annual_div / current_price * 100) if current_price > 0 else 0, 20.0)
        profit_margins = (info.get('profitMargins') or 0) * 100
        debt_to_equity = info.get('debtToEquity')
        revenue_growth = (info.get('revenueGrowth') or 0) * 100
        beta           = info.get('beta')
        analyst_mean   = info.get('targetMeanPrice')
        analyst_upside = ((analyst_mean - current_price) / current_price * 100) if analyst_mean else 0
        # Strikes
        sigma       = hv_30 / 100; sqrtT = np.sqrt(expiry_days / 365)
        strike_d30  = round(current_price * np.exp(-0.524 * sigma * sqrtT), 2)
        strike_d25  = round(current_price * np.exp(-0.674 * sigma * sqrtT), 2)
        strike_5pct = round(current_price * 0.95, 2)
        # Round to conventions
        exch = meta['exchange']
        if exch == 'NSE':
            strike_d30 = round(strike_d30/5)*5; strike_d25 = round(strike_d25/5)*5; strike_5pct = round(strike_5pct/5)*5
        elif exch == 'HKEX':
            strike_d30 = round(strike_d30*2)/2; strike_d25 = round(strike_d25*2)/2; strike_5pct = round(strike_5pct*2)/2
        else:
            strike_d30 = round(strike_d30*2)/2; strike_d25 = round(strike_d25*2)/2; strike_5pct = round(strike_5pct*2)/2

        currency = {'NSE':'₹', 'HKEX':'HK$'}.get(exch, '$')
        wb_score = calc_wealth_score(above_200dma, pct_from_high, hv_30, div_yield,
                                     profit_margins, debt_to_equity, revenue_growth, beta, analyst_upside)
        return {
            'ticker':         ticker.replace('.NS','').replace('.HK','').lstrip('0') if exch != 'NSE' else ticker.replace('.NS',''),
            'raw_ticker':     ticker,
            'name':           info.get('shortName', ticker)[:28],
            'exchange':       exch,
            'region':         meta['region'],
            'theme':          meta['theme'],
            'why':            meta['why'],
            'currency':       currency,
            'current_price':  round(current_price, 2),
            'strike_d30':     strike_d30,
            'strike_d25':     strike_d25,
            'strike_5pct':    strike_5pct,
            'above_50dma':    above_50dma,
            'above_200dma':   above_200dma,
            'pct_from_high':  round(pct_from_high, 1),
            'hv_30':          round(hv_30, 1),
            'dividend_yield': round(div_yield, 2),
            'profit_margins': round(profit_margins, 1),
            'debt_to_equity': round(debt_to_equity, 1) if debt_to_equity else None,
            'revenue_growth': round(revenue_growth, 1),
            'analyst_upside': round(analyst_upside, 1),
            'beta':           round(beta, 2) if beta else None,
            'analyst_mean':   analyst_mean,
            'wheel_score':    wb_score,
            'capital_required': strike_5pct * 100,
        }
    except: return None

# ── Nifty 50 Universe ────────────────────────────────────────────────────────
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

def calc_rsi(series, period=14):
    """RSI using Wilder's Smoothing (RMA) — matches TradingView exactly"""
    delta = series.diff()
    gain  = delta.clip(lower=0)
    loss  = (-delta.clip(upper=0))
    # Wilder's RMA = EWM with alpha=1/period, adjust=False
    avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    rs  = avg_gain / avg_loss.replace(0, 1e-10)
    rsi = 100 - (100 / (1 + rs))
    return round(float(rsi.dropna().iloc[-1]), 1)

def safe_float(val, default=0.0):
    """Safely convert value to float, handling None and NaN"""
    try:
        import math
        f = float(val)
        return default if math.isnan(f) or math.isinf(f) else f
    except:
        return default

def fetch_n50_data(ticker):
    try:
        # Use yf.download — more reliable than Ticker.history for NSE
        raw = yf.download(ticker, period='6mo', auto_adjust=True, progress=False)

        # Flatten MultiIndex columns if present
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = raw.columns.get_level_values(0)

        if raw is None or len(raw) < 20:
            return None

        # Get Close column reliably
        close = raw['Close'].dropna()
        if len(close) < 20:
            return None

        price     = float(close.iloc[-1])
        if price <= 0:
            return None

        rsi       = calc_rsi(close)
        change_1d = ((price - float(close.iloc[-2])) / float(close.iloc[-2])) * 100 if len(close) >= 2 else 0.0
        ma50_series = close.rolling(50).mean()
        ma50_val    = float(ma50_series.iloc[-1]) if len(close) >= 50 and not np.isnan(ma50_series.iloc[-1]) else None

        # Get fundamentals via Ticker.info
        try:
            info = yf.Ticker(ticker).info or {}
        except:
            info = {}

        pe         = safe_float(info.get('trailingPE'))
        forward_pe = safe_float(info.get('forwardPE'))
        pb         = safe_float(info.get('priceToBook'))
        mkt_cap    = safe_float(info.get('marketCap'))

        # ── Dividend yield — careful not to multiply already-pct values ──────
        # yfinance dividendYield is already a decimal (e.g. 0.035 = 3.5%)
        # dividendRate is annual dividend in currency units
        div_yield = 0.0
        div_raw   = info.get('dividendYield')
        div_rate  = safe_float(info.get('dividendRate'))
        if div_raw is not None:
            dv = safe_float(div_raw)
            # yfinance sometimes returns it as 0.035 (decimal) or 3.5 (pct)
            if 0 < dv < 1:          # decimal form e.g. 0.035
                div_yield = dv * 100
            elif 1 <= dv <= 20:     # already percentage e.g. 3.5
                div_yield = dv
            # anything > 20 is almost certainly wrong data — skip it
        if div_yield == 0.0 and div_rate > 0 and price > 0:
            # fall back to dividendRate / price
            div_yield = (div_rate / price) * 100
        div_yield = round(min(div_yield, 20.0), 2)  # hard cap at 20%

        # ── Debt ─────────────────────────────────────────────────────────────
        total_debt_raw = safe_float(info.get('totalDebt'))
        total_debt_cr  = round(total_debt_raw / 1e7, 0) if total_debt_raw > 0 else 0  # in ₹ crores
        debt_to_equity = safe_float(info.get('debtToEquity'))  # ratio

        sector = str(info.get('sector') or info.get('industry') or 'N/A')
        name   = str(info.get('shortName') or info.get('longName') or ticker.replace('.NS',''))

        # ── Growth expected: how much earnings expected to grow ───────────────
        # Positive = earnings growing (good), Negative = earnings shrinking (bad)
        if pe > 0 and forward_pe > 0:
            growth_exp = round(((pe - forward_pe) / forward_pe) * 100, 1)
        else:
            growth_exp = None

        return {
            'ticker':         ticker.replace('.NS',''),
            'name':           name[:22],
            'sector':         sector,
            'price':          round(price, 2),
            'change_1d':      round(change_1d, 2),
            'rsi':            rsi,
            'pe':             round(pe, 1),
            'forward_pe':     round(forward_pe, 1),
            'growth_exp':     growth_exp,
            'pb':             round(pb, 2),
            'div_yield':      div_yield,
            'total_debt_cr':  total_debt_cr,
            'debt_to_equity': round(debt_to_equity, 1) if debt_to_equity else 0,
            'market_cap':     round(mkt_cap / 1e7, 0) if mkt_cap > 0 else 0,
            'above_50ma':     (price > ma50_val) if ma50_val else None,
            'rsi_signal':     'Oversold' if rsi < 35 else ('Overbought' if rsi > 65 else 'Neutral'),
        }
    except Exception:
        return None

# ── Session State ─────────────────────────────────────────────────────────────
for key, val in {'show_chart': {}, 'hist_data': {}, 'nse_results': None, 'nse_time': None, 'hk_results': None, 'hk_time': None, 'us_results': None, 'us_time': None, 'metals_results': None, 'metals_time': None, 'wb_results': None, 'wb_time': None, 'n50_results': None, 'n50_time': None, 'ai_analysis': {}}.items():
    if key not in st.session_state:
        st.session_state[key] = val

def toggle_chart(key):
    st.session_state.show_chart[key] = not st.session_state.show_chart.get(key, False)

def apply_filters_and_sort(df, tab_key):
    """Render filter/sort controls and return filtered+sorted dataframe"""
    with st.expander("🔧 Filter & Sort Results", expanded=False):
        fc1, fc2, fc3, fc4 = st.columns(4)
        with fc1:
            trend_filter = st.selectbox("📈 Trend Filter",
                ["All", "Above 200 DMA only", "Above 50 DMA only", "Below MAs"],
                key=f"trend_{tab_key}")
        with fc2:
            hv_range = st.slider("🌡️ HV30 Range (%)", 0, 100, (0, 100), 5, key=f"hv_{tab_key}")
        with fc3:
            pullback_range = st.slider("📉 From 52W High (%)", 0, 80, (0, 80), 5, key=f"pull_{tab_key}")
        with fc4:
            sort_by = st.selectbox("↕️ Sort By",
                ["Wheel Score ↓", "Wheel Score ↑", "HV30 ↓", "HV30 ↑",
                 "Pullback ↓", "Pullback ↑", "Dividend Yield ↓", "CMP ↓", "CMP ↑"],
                key=f"sort_{tab_key}")

        sc1, sc2 = st.columns(2)
        with sc1:
            min_div = st.slider("💰 Min Dividend Yield (%)", 0.0, 10.0, 0.0, 0.5, key=f"div_{tab_key}")
        with sc2:
            min_score = st.slider("🎯 Min Wheel Score", 0, 100, 40, 5, key=f"minscore_{tab_key}")

    # Apply filters
    filtered = df.copy()
    if trend_filter == "Above 200 DMA only":
        filtered = filtered[filtered['above_200dma'] == True]
    elif trend_filter == "Above 50 DMA only":
        filtered = filtered[filtered['above_50dma'] == True]
    elif trend_filter == "Below MAs":
        filtered = filtered[filtered['above_50dma'] == False]

    filtered = filtered[
        (filtered['hv_30'] >= hv_range[0]) & (filtered['hv_30'] <= hv_range[1]) &
        (filtered['pct_from_high'] >= pullback_range[0]) & (filtered['pct_from_high'] <= pullback_range[1]) &
        (filtered['dividend_yield'] >= min_div) &
        (filtered['wheel_score'] >= min_score)
    ]

    # Apply sort
    sort_map = {
        "Wheel Score ↓":    ('wheel_score',    False),
        "Wheel Score ↑":    ('wheel_score',    True),
        "HV30 ↓":           ('hv_30',          False),
        "HV30 ↑":           ('hv_30',          True),
        "Pullback ↓":       ('pct_from_high',  False),
        "Pullback ↑":       ('pct_from_high',  True),
        "Dividend Yield ↓": ('dividend_yield', False),
        "CMP ↓":            ('current_price',  False),
        "CMP ↑":            ('current_price',  True),
    }
    col, asc = sort_map.get(sort_by, ('wheel_score', False))
    filtered = filtered.sort_values(col, ascending=asc)
    return filtered

def toggle_analysis(key):
    st.session_state.ai_analysis[key] = st.session_state.ai_analysis.get(key, {})
    st.session_state.ai_analysis[key]['open'] = not st.session_state.ai_analysis[key].get('open', False)

def get_ai_analysis(ticker, name, exchange, current_price, sector, hv30, pct_from_high, div_yield, wheel_score):
    """Rule-based wheel strategy analysis — no external API needed"""
    try:
        # Fetch enriched yfinance data
        try:
            ns_suffix = '.NS' if exchange == 'NSE' and '.' not in ticker else ''
            hk_suffix = '.HK' if exchange == 'HKEX' and '.' not in ticker else ''
            yt = yf.Ticker(ticker + ns_suffix + hk_suffix)
            info = yt.info
            analyst_mean   = info.get('targetMeanPrice')
            analyst_low    = info.get('targetLowPrice')
            analyst_high   = info.get('targetHighPrice')
            analyst_rec    = (info.get('recommendationKey') or 'N/A').upper()
            trailing_pe    = info.get('trailingPE')
            forward_pe     = info.get('forwardPE')
            revenue_growth = (info.get('revenueGrowth') or 0) * 100
            profit_margins = (info.get('profitMargins') or 0) * 100
            debt_to_equity = info.get('debtToEquity')
            beta           = info.get('beta')
            fifty_day_avg  = info.get('fiftyDayAverage')
            two_hundred_avg= info.get('twoHundredDayAverage')
        except:
            analyst_mean = analyst_low = analyst_high = None
            analyst_rec = 'N/A'
            trailing_pe = forward_pe = revenue_growth = profit_margins = None
            debt_to_equity = beta = fifty_day_avg = two_hundred_avg = None

        currency = 'HKD' if exchange == 'HKEX' else ('$' if exchange in ['NASDAQ','NYSE','NASDAQ/NYSE'] else '₹')

        # ── PROS ──────────────────────────────────────────────────────────
        pros = []
        if wheel_score >= 70:
            pros.append(f"Strong wheel score of {wheel_score}/100 — passes all key criteria for CSP strategy")
        elif wheel_score >= 55:
            pros.append(f"Solid wheel score of {wheel_score}/100 — meets core CSP criteria")

        if 20 <= hv30 <= 40:
            pros.append(f"HV30 of {hv30:.1f}% is in the sweet spot — generates good premium without excessive risk")
        elif hv30 > 40:
            pros.append(f"Elevated HV30 of {hv30:.1f}% means rich option premiums for put sellers")

        if div_yield >= 3:
            pros.append(f"Attractive dividend yield of {div_yield:.1f}% — bonus income if assigned and held")
        elif div_yield >= 1:
            pros.append(f"Dividend yield of {div_yield:.1f}% provides additional return if assigned")

        if 10 <= pct_from_high <= 25:
            pros.append(f"Healthy pullback of {pct_from_high:.1f}% from 52W high — ideal CSP entry zone")
        elif 25 < pct_from_high <= 40:
            pros.append(f"Significant pullback of {pct_from_high:.1f}% from 52W high — potential mean reversion play")

        if analyst_mean and analyst_mean > current_price:
            upside = ((analyst_mean - current_price) / current_price) * 100
            pros.append(f"Analyst mean target {currency}{analyst_mean:,.1f} implies {upside:.1f}% upside — stock fundamentally undervalued")

        if profit_margins and profit_margins > 15:
            pros.append(f"Strong profit margin of {profit_margins:.1f}% — quality business with pricing power")

        if forward_pe and trailing_pe and forward_pe < trailing_pe:
            pros.append(f"Forward PE ({forward_pe:.1f}) below trailing PE ({trailing_pe:.1f}) — earnings growth expected")

        if beta and beta < 1.2:
            pros.append(f"Beta of {beta:.2f} indicates relatively low market sensitivity — stable for wheel strategy")

        pros = pros[:4]  # Cap at 4

        # ── CONS ──────────────────────────────────────────────────────────
        cons = []
        if hv30 > 50:
            cons.append(f"Very high HV30 of {hv30:.1f}% — large price swings increase assignment risk on puts")
        if pct_from_high > 35:
            cons.append(f"Stock is {pct_from_high:.1f}% below 52W high — may indicate a longer downtrend, use wider strikes")
        if debt_to_equity and debt_to_equity > 100:
            cons.append(f"High debt/equity ratio of {debt_to_equity:.0f} — leveraged balance sheet adds fundamental risk")
        if div_yield == 0:
            cons.append("No dividend — if assigned, holding the stock generates no passive income while waiting to sell calls")
        if beta and beta > 1.5:
            cons.append(f"High beta of {beta:.2f} — stock moves sharply with market, wider stops needed on puts")
        if revenue_growth and revenue_growth < 0:
            cons.append(f"Negative revenue growth of {revenue_growth:.1f}% — business headwinds may pressure the stock further")
        if analyst_rec in ['SELL','STRONG_SELL']:
            cons.append(f"Analyst consensus is {analyst_rec} — majority recommending exit, adds downside risk")
        if not cons:
            cons.append("Monitor broader market conditions — even quality stocks can be pulled down in risk-off environments")
        cons = cons[:3]  # Cap at 3

        # ── MARKET ANALYSIS ───────────────────────────────────────────────
        trend = "above" if pct_from_high < 15 else "below"
        ma_note = ""
        if fifty_day_avg and two_hundred_avg:
            if current_price > fifty_day_avg and current_price > two_hundred_avg:
                ma_note = "Trading above both 50 and 200 DMA — trend is bullish and supportive for put selling. "
            elif current_price > two_hundred_avg:
                ma_note = "Above 200 DMA but below 50 DMA — mild short-term weakness within longer uptrend. "
            else:
                ma_note = "Below both key moving averages — be selective with strikes and use wider OTM buffer. "

        vol_note = f"HV30 at {hv30:.1f}% suggests {'elevated' if hv30 > 35 else 'moderate'} option premiums are available. "
        pullback_note = f"At {pct_from_high:.1f}% below the 52W high, the stock is in a {'healthy consolidation' if pct_from_high < 20 else 'deeper correction'} phase — {'good' if pct_from_high < 30 else 'cautious'} zone for cash-secured puts."
        market_analysis = ma_note + vol_note + pullback_note

        # ── ANALYST TARGET ────────────────────────────────────────────────
        if analyst_mean:
            upside = ((analyst_mean - current_price) / current_price) * 100
            analyst_target = (f"Analyst mean target: {currency}{analyst_mean:,.1f} ({upside:+.1f}% from CMP) | "
                              f"Range: {currency}{analyst_low:,.1f} – {currency}{analyst_high:,.1f} | "
                              f"Consensus: {analyst_rec}")
        else:
            analyst_target = "Analyst target data not available via yfinance for this stock"

        # ── CSP RECOMMENDATION ────────────────────────────────────────────
        sigma  = hv30 / 100
        sqrtT  = np.sqrt(30 / 365)
        strike_d25 = round(current_price * np.exp(-0.674 * sigma * sqrtT), 1)
        if exchange == 'NSE':
            strike_d25 = round(strike_d25 / 5) * 5
        else:
            strike_d25 = round(strike_d25 * 2) / 2

        expiry_note = "monthly expiry (last Thursday)" if exchange == 'NSE' else "30-day expiry"
        csp_recommendation = (f"Sell {currency}{strike_d25:,.1f} put (~delta 0.25) at {expiry_note}. "
                               f"This gives ~5–8% OTM buffer based on current IV. "
                               f"Target 50% profit exit. Only proceed if comfortable owning {ticker} at this price.")

        # ── RISK LEVEL ────────────────────────────────────────────────────
        risk_score = 0
        if hv30 > 45: risk_score += 2
        elif hv30 > 30: risk_score += 1
        if pct_from_high > 35: risk_score += 2
        elif pct_from_high > 20: risk_score += 1
        if debt_to_equity and debt_to_equity > 150: risk_score += 1
        if beta and beta > 1.5: risk_score += 1
        risk_level = "High" if risk_score >= 4 else "Medium" if risk_score >= 2 else "Low"

        # ── VERDICT ───────────────────────────────────────────────────────
        if wheel_score >= 65 and risk_level == "Low":
            verdict = f"{ticker} is a strong wheel candidate — good premium, solid trend, manageable risk profile."
        elif wheel_score >= 55 and risk_level != "High":
            verdict = f"{ticker} is a reasonable wheel candidate — monitor support levels before selling puts."
        else:
            verdict = f"{ticker} requires caution — use conservative strikes and smaller position size for wheel strategy."

        return {
            "pros": pros,
            "cons": cons,
            "market_analysis": market_analysis,
            "analyst_target": analyst_target,
            "csp_recommendation": csp_recommendation,
            "risk_level": risk_level,
            "verdict": verdict,
        }

    except Exception as e:
        return {"error": str(e)}

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
    chart_open  = st.session_state.show_chart.get(chart_key, False)
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
    col_chart, col_ai = st.columns([1, 1])
    with col_chart:
        st.button(chart_label, key=f"btn_{chart_key}_{r.get('_tier',0)}",
                  on_click=toggle_chart, args=(chart_key,))
    with col_ai:
        # Only show AI Analysis button for Tier 1
        if r.get('_tier') == 1:
            ai_state    = st.session_state.ai_analysis.get(chart_key, {})
            ai_open     = ai_state.get('open', False)
            ai_label    = "🤖 Hide Analysis" if ai_open else "🤖 AI Analysis"
            st.button(ai_label, key=f"ai_btn_{chart_key}_{r.get('_tier',0)}",
                      on_click=toggle_analysis, args=(chart_key,))

    if chart_open:
        render_chart(chart_key, exchange)

    # AI Analysis panel — Tier 1 only
    if r.get('_tier') == 1:
        ai_state = st.session_state.ai_analysis.get(chart_key, {})
        if ai_state.get('open', False):
            cached = ai_state.get('data')
            if not cached:
                with st.spinner(f"🤖 Analysing {r['ticker']} with live web data..."):
                    cached = get_ai_analysis(
                        r['ticker'], r['name'], exchange,
                        r['current_price'], r['sector'],
                        r['hv_30'], r['pct_from_high'],
                        r['dividend_yield'], r['wheel_score']
                    )
                    st.session_state.ai_analysis[chart_key]['data'] = cached

            if 'error' in cached:
                st.error(f"Analysis error: {cached['error']}")
            else:
                risk_color = {'Low': '#00d4aa', 'Medium': '#f5a623', 'High': '#ff4b4b'}.get(cached.get('risk_level','Medium'), '#f5a623')
                st.markdown(f"""
                <div style='background:#0a1e30; border:1px solid #1e3347; border-radius:10px; padding:1.2rem 1.5rem; margin-top:0.5rem;'>
                    <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem; flex-wrap:wrap; gap:8px'>
                        <span style='font-family:Space Mono,monospace; color:#00d4aa; font-size:0.95rem; font-weight:700'>
                            🤖 AI Analysis — {r['ticker']}
                        </span>
                        <span style='background:{risk_color}22; color:{risk_color}; border:1px solid {risk_color}44;
                              padding:2px 12px; border-radius:20px; font-size:0.78rem; font-weight:600'>
                            Risk: {cached.get('risk_level','N/A')}
                        </span>
                    </div>
                    <div style='display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin-bottom:1rem'>
                        <div style='background:#0d2318; border:1px solid #00d4aa33; border-radius:8px; padding:0.8rem'>
                            <div style='color:#00d4aa; font-size:0.72rem; text-transform:uppercase; letter-spacing:1px; margin-bottom:6px'>✅ Pros</div>
                            {''.join(f"<div style='color:#c8dce8; font-size:0.83rem; padding:3px 0; border-bottom:1px solid #1e3347'>• {p}</div>" for p in cached.get('pros', []))}
                        </div>
                        <div style='background:#1e1218; border:1px solid #ff4b4b33; border-radius:8px; padding:0.8rem'>
                            <div style='color:#ff4b4b; font-size:0.72rem; text-transform:uppercase; letter-spacing:1px; margin-bottom:6px'>⚠️ Cons</div>
                            {''.join(f"<div style='color:#c8dce8; font-size:0.83rem; padding:3px 0; border-bottom:1px solid #1e3347'>• {c}</div>" for c in cached.get('cons', []))}
                        </div>
                    </div>
                    <div style='background:#111e2d; border:1px solid #1e3347; border-radius:8px; padding:0.8rem; margin-bottom:0.8rem'>
                        <div style='color:#6b8fa8; font-size:0.72rem; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px'>📊 Market Analysis</div>
                        <div style='color:#c8dce8; font-size:0.85rem; line-height:1.6'>{cached.get('market_analysis','')}</div>
                    </div>
                    <div style='display:grid; grid-template-columns:1fr 1fr; gap:0.8rem; margin-bottom:0.8rem'>
                        <div style='background:#111e2d; border:1px solid #1e3347; border-radius:8px; padding:0.8rem'>
                            <div style='color:#6b8fa8; font-size:0.72rem; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px'>🎯 Analyst Target</div>
                            <div style='color:#f5a623; font-size:0.88rem; font-weight:600'>{cached.get('analyst_target','N/A')}</div>
                        </div>
                        <div style='background:#111e2d; border:1px solid #1e3347; border-radius:8px; padding:0.8rem'>
                            <div style='color:#6b8fa8; font-size:0.72rem; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px'>💡 CSP Recommendation</div>
                            <div style='color:#c8dce8; font-size:0.83rem'>{cached.get('csp_recommendation','N/A')}</div>
                        </div>
                    </div>
                    <div style='background:#0d2318; border:1px solid #00d4aa33; border-radius:8px; padding:0.7rem 1rem'>
                        <span style='color:#6b8fa8; font-size:0.72rem; text-transform:uppercase; letter-spacing:1px'>⚖️ Verdict: </span>
                        <span style='color:#00d4aa; font-size:0.85rem; font-weight:600'>{cached.get('verdict','')}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

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

# ── TABS ──────────────────────────────────────────────────────────────────────
tab_wb, tab_nse, tab_hk, tab_us, tab_metals, tab_n50 = st.tabs(["💎  Wealth Builder", "🇮🇳  NSE Screener", "🇭🇰  HK Screener", "🇺🇸  US Screener", "🪙  Metals", "📊  Nifty 50"])

# ── TAB 1: NSE ────────────────────────────────────────────────────────────────
with tab_nse:
    st.markdown("<p style='color:#6b8fa8;font-size:0.72rem;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:0.5rem'>⚙️ Screener Configuration</p>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns([2, 1.2, 1.5, 1.2, 1])
    with c1:
        max_capital = 999_999_999  # No capital limit
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
                st.session_state.show_chart[d['ticker']] = False
        bar.empty()
        st.session_state.nse_results = results
        st.session_state.nse_time    = datetime.now().strftime('%d %b %Y, %I:%M %p')

    if st.session_state.nse_results:
        results = st.session_state.nse_results
        df      = pd.DataFrame(results)
        filtered_df = apply_filters_and_sort(df, 'nse')
        tier1   = filtered_df[(filtered_df['wheel_score'] >= 55) & (filtered_df['above_200dma'] == True)]
        tier2   = filtered_df[~filtered_df['ticker'].isin(tier1['ticker'])].head(10)
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
    st.markdown("<p style='color:#6b8fa8;font-size:0.72rem;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:0.5rem'>⚙️ Screener Configuration</p>", unsafe_allow_html=True)
    h1, h2, h3 = st.columns([2, 1.5, 1])
    with h1:
        max_cap_hkd = 999_999_999  # No capital limit
    with h2:
        hk_expiry = st.selectbox("📅 Expiry", [7, 15, 30, 45], index=2, format_func=lambda x: f"{x} days", key="hk_exp")
    with h3:
        st.markdown("<br>", unsafe_allow_html=True)
        run_hk = st.button("🚀 Run Scan", key="run_hk")
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
                st.session_state.show_chart[ticker.replace('.HK','').lstrip('0')] = False
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

# ── TAB 3: US ─────────────────────────────────────────────────────────────────
with tab_us:
    st.markdown("<p style='color:#6b8fa8;font-size:0.72rem;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:0.5rem'>⚙️ Screener Configuration</p>", unsafe_allow_html=True)
    u1, u2, u3, u4, u5 = st.columns([2, 1.2, 1.5, 1.2, 1])
    with u1:
        max_cap_usd = 999_999_999  # No capital limit
    with u2:
        us_expiry = st.selectbox("📅 Expiry", [7, 15, 30, 45], index=2, format_func=lambda x: f"{x}d", key="us_exp")
    with u3:
        us_sectors = st.multiselect("🏭 Sectors", sorted(set(v['sector'] for v in US_STOCKS.values())), default=[], placeholder="All", key="us_sec")
    with u4:
        us_min_score = st.slider("🎯 Min Score", 0, 100, 40, 5, key="us_score")
        st.markdown(f"<p style='color:#00d4aa;font-weight:700;font-size:0.82rem;margin-top:-8px'>{us_min_score}/100</p>", unsafe_allow_html=True)
    with u5:
        st.markdown("<br>", unsafe_allow_html=True)
        run_us = st.button("🚀 Run Scan", key="run_us")
    st.markdown("""
    <div style='display:flex; gap:8px; flex-wrap:wrap; margin-bottom:1rem; font-size:0.78rem'>
        <span class='tag tag-blue' style='padding:3px 8px'>💡 1 contract = 100 shares · Capital in USD</span>
        <span class='tag tag-green' style='padding:3px 8px'>Weekly + Monthly expiries available</span>
        <span class='tag tag-yellow' style='padding:3px 8px'>ETFs (SPY, QQQ, SLV) great for wheel</span>
    </div>""", unsafe_allow_html=True)

    if run_us:
        st.session_state.us_results = None
        filtered_us = {k: v for k, v in US_STOCKS.items() if not us_sectors or v['sector'] in us_sectors}
        us_bar = st.progress(0, text="🔍 Scanning US stocks...")
        us_res = []
        for i, (ticker, meta) in enumerate(filtered_us.items()):
            us_bar.progress((i+1)/len(filtered_us), text=f"🔍 {ticker} ({i+1}/{len(filtered_us)})")
            d = fetch_us_stock_data(ticker, max_cap_usd, us_expiry)
            if d and d['wheel_score'] >= us_min_score:
                us_res.append(d)
                st.session_state.show_chart[ticker] = True
        us_bar.empty()
        st.session_state.us_results = us_res
        st.session_state.us_time = datetime.now().strftime('%d %b %Y, %I:%M %p')

    if st.session_state.us_results:
        us_res  = st.session_state.us_results
        us_df   = pd.DataFrame(us_res)
        us_df_f  = apply_filters_and_sort(us_df, 'us')
        tier1_us = us_df_f[(us_df_f['wheel_score'] >= 55) & (us_df_f['above_200dma'] == True)]
        tier2_us = us_df_f[~us_df_f['ticker'].isin(tier1_us['ticker'])].head(10)
        st.markdown(f"<p style='color:#6b8fa8; font-size:0.8rem; margin:0.5rem 0'>Last scan: {st.session_state.us_time}</p>", unsafe_allow_html=True)
        p1, p2, p3, p4 = st.columns(4)
        for col, lbl, val in zip([p1,p2,p3,p4], ['Scanned','Tier 1','Tier 2','Avg Score'],
                                  [len(us_res), len(tier1_us), len(tier2_us), round(us_df['wheel_score'].mean())]):
            col.markdown(f"<div class='metric-box'><div class='label'>{lbl}</div><div class='value'>{val}</div></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-head'><span>🏆 Tier 1 — Best US CSP Candidates</span></div>", unsafe_allow_html=True)
        if tier1_us.empty:
            st.info("No Tier 1 stocks. Try increasing capital limit or lowering min score.")
        for _, row in tier1_us.iterrows():
            r = row.to_dict(); r['_tier'] = 1; render_card(r, r['ticker'], 'NASDAQ')
        st.markdown("<div class='section-head'><span>👀 Tier 2 — Watchlist</span></div>", unsafe_allow_html=True)
        for _, row in tier2_us.iterrows():
            r = row.to_dict(); r['_tier'] = 2; render_card(r, r['ticker'], 'NASDAQ')
        st.markdown("<div class='section-head'><span>📊 Sector Summary</span></div>", unsafe_allow_html=True)
        us_sec = us_df.groupby('sector').agg(Stocks=('ticker','count'), Avg_Score=('wheel_score','mean'), Avg_HV30=('hv_30','mean')).reset_index().sort_values('Avg_Score', ascending=False)
        us_sec['Avg_Score'] = us_sec['Avg_Score'].round(0).astype(int)
        us_sec['Avg_HV30']  = us_sec['Avg_HV30'].round(1)
        st.dataframe(us_sec, use_container_width=True, hide_index=True)
        st.download_button("📥 Download Results (CSV)", data=us_df.sort_values('wheel_score', ascending=False).to_csv(index=False),
                           file_name=f"us_wheel_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", mime="text/csv", use_container_width=True)
    else:
        st.markdown("""
        <div style='text-align:center; padding:4rem 2rem; color:#3a5060'>
            <div style='font-size:3.5rem'>🇺🇸</div>
            <p style='font-family:Space Mono,monospace; color:#6b8fa8; margin:1rem 0 0.5rem'>Configure & Run Scan</p>
            <p style='font-size:0.85rem'>Set your USD capital limit and click <strong style='color:#00d4aa'>Run Scan</strong></p>
            <p style='font-size:0.78rem; margin-top:0.5rem'>30 stocks · Tech · Finance · Energy · ETFs · Healthcare</p>
        </div>""", unsafe_allow_html=True)

# ── TAB 4: METALS ────────────────────────────────────────────────────────────
with tab_metals:
    # Info banner
    st.markdown("""
    <div style='display:flex; gap:10px; flex-wrap:wrap; margin-bottom:1rem'>
        <span class='tag' style='background:#f5a62322; color:#f5a623; padding:4px 10px; font-size:0.8rem'>🥇 Gold — GLD, NEM, GOLD</span>
        <span class='tag' style='background:#a0b4c022; color:#a0b4c0; padding:4px 10px; font-size:0.8rem'>🥈 Silver — SLV, AG</span>
        <span class='tag' style='background:#cd7c3a22; color:#cd7c3a; padding:4px 10px; font-size:0.8rem'>🟤 Copper — FCX, CPER</span>
        <span class='tag' style='background:#6b8fa822; color:#6b8fa8; padding:4px 10px; font-size:0.8rem'>⚙️ Steel — NUE, X, CLF</span>
        <span class='tag' style='background:#8884d822; color:#8884d8; padding:4px 10px; font-size:0.8rem'>🔩 Aluminium — AA</span>
    </div>""", unsafe_allow_html=True)

    # Config panel
    st.markdown("<p style='color:#6b8fa8;font-size:0.72rem;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:0.5rem'>⚙️ Screener Configuration</p>", unsafe_allow_html=True)
    mt1, mt2, mt3, mt4, mt5 = st.columns([2, 1.5, 1.5, 1.2, 1])
    with mt1:
        max_cap_metals = 999_999_999  # No capital limit
    with mt2:
        metals_expiry = st.selectbox("📅 Expiry", [7, 15, 30, 45], index=2, format_func=lambda x: f"{x}d", key="metals_exp")
    with mt3:
        metals_filter = st.multiselect("🪙 Metal Type", ['Gold','Silver','Copper','Steel','Aluminium'], default=[], placeholder="All metals", key="metals_filter")
    with mt4:
        metals_min_score = st.slider("🎯 Min Score", 0, 100, 40, 5, key="metals_score")
        st.markdown(f"<p style='color:#00d4aa;font-weight:700;font-size:0.82rem;margin-top:-8px'>{metals_min_score}/100</p>", unsafe_allow_html=True)
    with mt5:
        st.markdown("<br>", unsafe_allow_html=True)
        run_metals = st.button("🚀 Run Scan", key="run_metals")

    if run_metals:
        st.session_state.metals_results = None
        filtered_metals = {k: v for k, v in METALS_STOCKS.items()
                           if not metals_filter or v['metal'] in metals_filter}
        metals_bar = st.progress(0, text="🔍 Scanning metals stocks...")
        metals_res = []
        for i, (ticker, meta) in enumerate(filtered_metals.items()):
            metals_bar.progress((i+1)/len(filtered_metals),
                text=f"🔍 {ticker} — {meta['metal']} ({i+1}/{len(filtered_metals)})")
            d = fetch_us_stock_data(ticker, max_cap_metals, metals_expiry)
            if d and d['wheel_score'] >= metals_min_score:
                d['metal']      = meta['metal']
                d['metal_type'] = meta['type']
                d['sector']     = meta['sector']
                metals_res.append(d)
                st.session_state.show_chart[ticker] = True
        metals_bar.empty()
        st.session_state.metals_results = metals_res
        st.session_state.metals_time    = datetime.now().strftime('%d %b %Y, %I:%M %p')

    if st.session_state.metals_results:
        metals_res = st.session_state.metals_results
        metals_df  = pd.DataFrame(metals_res)

        metals_df_f = apply_filters_and_sort(metals_df, 'metals')
        tier1_m = metals_df_f[(metals_df_f['wheel_score'] >= 55) & (metals_df_f['above_200dma'] == True)]
        tier2_m = metals_df_f[~metals_df_f['ticker'].isin(tier1_m['ticker'])]

        st.markdown(f"<p style='color:#6b8fa8; font-size:0.8rem; margin:0.5rem 0'>Last scan: {st.session_state.metals_time}</p>", unsafe_allow_html=True)

        # Summary metrics
        q1, q2, q3, q4 = st.columns(4)
        for col, lbl, val in zip([q1,q2,q3,q4],
            ['Stocks Scanned','Tier 1','Tier 2','Avg Score'],
            [len(metals_res), len(tier1_m), len(tier2_m), round(metals_df['wheel_score'].mean())]):
            col.markdown(f"<div class='metric-box'><div class='label'>{lbl}</div><div class='value'>{val}</div></div>", unsafe_allow_html=True)

        # Metal group summary
        st.markdown("<div class='section-head'><span>🪙 Metal Group Summary</span></div>", unsafe_allow_html=True)
        group_cols = st.columns(5)
        for idx, metal in enumerate(['Gold','Silver','Copper','Steel','Aluminium']):
            metal_stocks = metals_df[metals_df['metal'] == metal]
            color = METAL_COLORS.get(metal, '#a0b4c0')
            with group_cols[idx]:
                if not metal_stocks.empty:
                    best = metal_stocks.loc[metal_stocks['wheel_score'].idxmax()]
                    st.markdown(f"""
                    <div style='background:#111e2d; border:1px solid {color}44; border-top:3px solid {color};
                         border-radius:8px; padding:0.8rem; text-align:center'>
                        <div style='color:{color}; font-size:0.75rem; font-weight:700; text-transform:uppercase'>{metal}</div>
                        <div style='color:#fff; font-size:1rem; font-weight:700; font-family:Space Mono,monospace; margin:4px 0'>{best['ticker']}</div>
                        <div style='color:#a0b4c0; font-size:0.75rem'>Best: {best['wheel_score']}/100</div>
                        <div style='color:{color}; font-size:0.8rem'>${best['current_price']:,.2f}</div>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style='background:#111e2d; border:1px solid {color}22; border-top:3px solid {color}44;
                         border-radius:8px; padding:0.8rem; text-align:center; opacity:0.4'>
                        <div style='color:{color}; font-size:0.75rem; font-weight:700; text-transform:uppercase'>{metal}</div>
                        <div style='color:#6b8fa8; font-size:0.8rem; margin-top:4px'>No data</div>
                    </div>""", unsafe_allow_html=True)

        # Render Tier 1
        st.markdown("<div class='section-head'><span>🏆 Tier 1 — Best Metals CSP Candidates</span></div>", unsafe_allow_html=True)
        if tier1_m.empty:
            st.info("No Tier 1 metals stocks. Try increasing capital limit or lowering min score.")
        for _, row in tier1_m.iterrows():
            r = row.to_dict(); r['_tier'] = 1
            metal_color = METAL_COLORS.get(r.get('metal',''), '#a0b4c0')
            # Inject metal badge into render_card via name field
            r['name'] = f"{r.get('metal_type','')}"
            render_card(r, r['ticker'], 'NASDAQ')

        # Render Tier 2
        st.markdown("<div class='section-head'><span>👀 Tier 2 — Watchlist</span></div>", unsafe_allow_html=True)
        if tier2_m.empty:
            st.info("All metals stocks qualified for Tier 1! 🎉")
        for _, row in tier2_m.iterrows():
            r = row.to_dict(); r['_tier'] = 2
            r['name'] = f"{r.get('metal_type','')}"
            render_card(r, r['ticker'], 'NASDAQ')

        # Download
        st.download_button("📥 Download Metals Results (CSV)",
            data=metals_df.sort_values('wheel_score', ascending=False).to_csv(index=False),
            file_name=f"metals_wheel_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv", use_container_width=True)
    else:
        st.markdown("""
        <div style='text-align:center; padding:4rem 2rem; color:#3a5060'>
            <div style='font-size:3.5rem'>🪙</div>
            <p style='font-family:Space Mono,monospace; color:#6b8fa8; margin:1rem 0 0.5rem'>Metals Wheel Screener</p>
            <p style='font-size:0.85rem'>Set capital limit and click <strong style='color:#00d4aa'>Run Scan</strong></p>
            <p style='font-size:0.78rem; margin-top:0.5rem'>Gold · Silver · Copper · Steel · Aluminium · 11 stocks</p>
        </div>""", unsafe_allow_html=True)

# ── TAB 5: WEALTH BUILDER ────────────────────────────────────────────────────
with tab_wb:
    # Philosophy banner
    with st.expander("💡 The Wealth Builder Philosophy — Why these stocks?", expanded=False):
        ph1, ph2, ph3 = st.columns(3)
        with ph1:
            st.markdown("""**🎯 Strategy: Double Income**
- Collect option premiums (5–15% annually)
- Collect dividends (2–8% annually)
- Combined yield: 8–20%+ per year
- Capital appreciation as bonus""")
        with ph2:
            st.markdown("""**🏆 Stock Criteria**
- Quality moat businesses
- Consistent dividend payers
- Liquid options available
- Global diversification
- Survive market downturns""")
        with ph3:
            st.markdown("""**📊 Wealth Score Weights**
- Dividend yield: 25 pts
- Business quality: 15 pts
- Balance sheet safety: 10 pts
- Trend (200 DMA): 15 pts
- Pullback zone: 20 pts
- Option premium viability: 15 pts""")

    # Config
    st.markdown("<p style='color:#6b8fa8;font-size:0.72rem;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:0.5rem'>⚙️ Screener Configuration</p>", unsafe_allow_html=True)
    wb1, wb2, wb3, wb4 = st.columns([1.5, 1.5, 1, 0.8])
    with wb1:
        wb_regions = st.multiselect("🌍 Regions", ['India','HK','USA'], default=[], placeholder="All regions", key="wb_reg")
    with wb2:
        wb_themes  = st.multiselect("🏭 Themes", sorted(set(v['theme'] for v in WB_STOCKS.values())), default=[], placeholder="All themes", key="wb_theme")
    with wb3:
        wb_expiry  = st.selectbox("📅 Expiry", [7,15,30,45], index=2, format_func=lambda x: f"{x} days", key="wb_exp")
    with wb4:
        st.markdown("<div style='margin-top:1.85rem'></div>", unsafe_allow_html=True)
        run_wb = st.button("🚀 Run Scan", key="run_wb", use_container_width=True)

    if run_wb:
        st.session_state.wb_results = None
        filtered_wb = {k: v for k, v in WB_STOCKS.items()
                       if (not wb_regions or v['region'] in wb_regions)
                       and (not wb_themes or v['theme'] in wb_themes)}
        wb_bar = st.progress(0, text="💎 Scanning wealth builder stocks...")
        wb_res = []
        for i, (ticker, meta) in enumerate(filtered_wb.items()):
            wb_bar.progress((i+1)/len(filtered_wb),
                text=f"💎 {ticker} — {meta['theme']} · {meta['region']} ({i+1}/{len(filtered_wb)})")
            d = fetch_wb_stock_data(ticker, meta, wb_expiry)
            if d:
                wb_res.append(d)
                chart_key = d['ticker']
                st.session_state.show_chart[chart_key] = False
        wb_bar.empty()
        st.session_state.wb_results = wb_res
        st.session_state.wb_time = datetime.now().strftime('%d %b %Y, %I:%M %p')

    if st.session_state.wb_results:
        wb_res = st.session_state.wb_results
        wb_df  = pd.DataFrame(wb_res)

        st.markdown(f"<p style='color:#6b8fa8; font-size:0.8rem; margin:0.5rem 0'>Last scan: {st.session_state.wb_time}</p>", unsafe_allow_html=True)

        # Summary metrics
        wm1, wm2, wm3, wm4, wm5 = st.columns(5)
        for col, lbl, val in zip([wm1,wm2,wm3,wm4,wm5],
            ['Stocks Scanned','🇮🇳 India','🇭🇰 HK','🇺🇸 USA','Avg Wealth Score'],
            [len(wb_res),
             len(wb_df[wb_df['region']=='India']),
             len(wb_df[wb_df['region']=='HK']),
             len(wb_df[wb_df['region']=='USA']),
             round(wb_df['wheel_score'].mean())]):
            col.markdown(f"<div class='metric-box'><div class='label'>{lbl}</div><div class='value'>{val}</div></div>", unsafe_allow_html=True)

        # Filter & sort
        wb_df = apply_filters_and_sort(wb_df, 'wb')

        # Region tabs within Wealth Builder
        st.markdown("---")
        reg_all, reg_in, reg_hk, reg_us = st.tabs(["🌍 All", "🇮🇳 India", "🇭🇰 Hong Kong", "🇺🇸 USA"])

        def render_wb_card(r, tab_id='all'):
            import math
            # ── helper ────────────────────────────────────────────────────
            def sv(v):
                return v if (v is not None and not (isinstance(v, float) and math.isnan(v))) else None

            region_color = REGION_COLORS.get(r['region'], '#a0b4c0')
            theme_icon   = THEME_ICONS.get(r['theme'], '📌')
            score_bg     = '#00d4aa22' if r['wheel_score'] >= 65 else '#f5a62322'
            score_col    = '#00d4aa'   if r['wheel_score'] >= 65 else '#f5a623'
            chart_key    = r['ticker']
            chart_open   = st.session_state.show_chart.get(chart_key, False)
            chart_label  = "📉 Hide Chart" if chart_open else "📈 View Chart"

            # ── pre-build all dynamic snippets ────────────────────────────
            tag_s  = "display:inline-block;padding:2px 8px;border-radius:4px;font-size:0.72rem;margin-right:4px;"
            if r['above_200dma']:
                trend_tag = f"<span style='{tag_s}background:#00d4aa22;color:#00d4aa;border:1px solid #00d4aa44'>📈 Above 200DMA</span>"
            elif r['above_50dma']:
                trend_tag = f"<span style='{tag_s}background:#f5a62322;color:#f5a623;border:1px solid #f5a62344'>〰️ Above 50DMA</span>"
            else:
                trend_tag = f"<span style='{tag_s}background:#ff4b4b22;color:#ff4b4b;border:1px solid #ff4b4b44'>📉 Below MAs</span>"

            div_v   = sv(r.get('dividend_yield'))
            div_tag = f"<span style='{tag_s}background:#4b9fff22;color:#4b9fff;border:1px solid #4b9fff44'>💰 Div {div_v:.1f}%</span>" if div_v and div_v > 0 else ""

            up_v    = sv(r.get('analyst_upside', 0)) or 0
            up_tag  = f"<span style='{tag_s}background:#8884d822;color:#8884d8;border:1px solid #8884d844'>📈 Analyst +{up_v:.0f}%</span>" if up_v > 5 else ""

            mg_v    = sv(r.get('profit_margins'))
            mg_tag  = f"<span>📊 {mg_v:.1f}%</span>" if mg_v else ""

            bt_v    = sv(r.get('beta'))
            bt_tag  = f"<span>⚡ β {bt_v:.2f}</span>" if bt_v else ""

            # ── inline-style strike rows ───────────────────────────────────
            row_s   = "display:flex;justify-content:space-between;align-items:center;padding:4px 0;font-size:0.85rem;"
            lbl_s   = "color:#6b8fa8;"
            val_s   = "color:#fff;font-family:Space Mono,monospace;font-weight:700;"

            html = (
                "<div style='background:linear-gradient(135deg,#0d1a26,#0d1f18);"
                f"border:1px solid {region_color}44;border-left:4px solid {region_color};"
                "border-radius:10px;padding:1.2rem 1.5rem;margin-bottom:1rem'>"

                "<div style='display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px'>"
                "<div style='display:flex;align-items:center;gap:10px;flex-wrap:wrap'>"
                f"<span style='font-family:Space Mono,monospace;font-size:1.2rem;font-weight:700;color:#fff'>{r['ticker']}</span>"
                f"<span style='color:#6b8fa8;font-size:0.82rem'>{r['name']}</span>"
                f"<span style='background:{region_color}22;color:{region_color};border:1px solid {region_color}44;"
                f"padding:2px 8px;border-radius:4px;font-size:0.72rem;font-weight:600'>{r['region']} · {r['exchange']}</span>"
                "</div>"
                f"<span style='background:{score_bg};color:{score_col};border:1px solid {score_col}44;"
                f"padding:2px 12px;border-radius:20px;font-size:0.8rem;font-weight:600'>💎 {r['wheel_score']}/100</span>"
                "</div>"

                f"<div style='margin-top:6px;color:#7fb3a0;font-size:0.8rem;font-style:italic'>{theme_icon} {r['theme']} · {r['why']}</div>"

                "<div style='margin-top:8px;display:flex;gap:12px;flex-wrap:wrap;font-size:0.84rem;color:#a0b4c0'>"
                f"<span>💵 CMP: <strong style='color:#fff'>{r['currency']}{r['current_price']:,.2f}</strong></span>"
                f"<span>📉 <strong style='color:#f5a623'>-{r['pct_from_high']:.1f}%</strong> from 52W High</span>"
                f"<span>🌡️ HV30: {r['hv_30']:.1f}%</span>"
                f"{mg_tag}{bt_tag}"
                "</div>"

                f"<div style='margin-top:6px'>{trend_tag}{div_tag}{up_tag}</div>"

                "<div style='background:#0d1a26;border:1px solid #1e3347;border-radius:8px;padding:0.8rem;margin-top:0.8rem'>"
                "<div style='color:#6b8fa8;font-size:0.72rem;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px'>"
                f"CSP Strike Suggestions · {wb_expiry}-day expiry</div>"
                f"<div style='{row_s}'><span style='{lbl_s}'>🟢 Delta ~0.30 (Aggressive)</span><span style='{val_s}'>{r['currency']}{r['strike_d30']:,.2f}</span></div>"
                f"<div style='{row_s}'><span style='{lbl_s}'>🟡 Delta ~0.25 (Moderate)</span><span style='{val_s}'>{r['currency']}{r['strike_d25']:,.2f}</span></div>"
                f"<div style='{row_s}'><span style='{lbl_s}'>🔵 5% OTM (Conservative)</span><span style='{val_s}'>{r['currency']}{r['strike_5pct']:,.2f}</span></div>"
                "</div>"
                "</div>"
            )
            st.markdown(html, unsafe_allow_html=True)

            cb1, cb2 = st.columns([1,1])
            with cb1:
                st.button(chart_label, key=f"wb_chart_{r['ticker']}_{tab_id}", on_click=toggle_chart, args=(chart_key,))
            with cb2:
                if r['wheel_score'] >= 55:
                    ai_state = st.session_state.ai_analysis.get(chart_key, {})
                    ai_open  = ai_state.get('open', False)
                    st.button("🤖 Hide Analysis" if ai_open else "🤖 AI Analysis",
                              key=f"wb_ai_{r['ticker']}_{tab_id}", on_click=toggle_analysis, args=(chart_key,))
            if chart_open:
                render_chart(chart_key, r['exchange'])
            if r['wheel_score'] >= 55:
                ai_state = st.session_state.ai_analysis.get(chart_key, {})
                if ai_state.get('open', False):
                    cached = ai_state.get('data')
                    if not cached:
                        with st.spinner(f"🤖 Analysing {r['ticker']}..."):
                            cached = get_ai_analysis(r['ticker'], r['name'], r['exchange'],
                                        r['current_price'], r['theme'], r['hv_30'],
                                        r['pct_from_high'], r['dividend_yield'], r['wheel_score'])
                            st.session_state.ai_analysis[chart_key]['data'] = cached
                    if 'error' not in cached:
                        risk_color = {'Low':'#00d4aa','Medium':'#f5a623','High':'#ff4b4b'}.get(cached.get('risk_level','Medium'),'#f5a623')
                        st.markdown(f"""
                        <div style='background:#0a1e30;border:1px solid #1e3347;border-radius:10px;padding:1.2rem 1.5rem;margin-top:0.5rem'>
                            <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;flex-wrap:wrap;gap:8px'>
                                <span style='font-family:Space Mono,monospace;color:#ffd700;font-size:0.95rem;font-weight:700'>🤖 Wealth Analysis — {r['ticker']}</span>
                                <span style='background:{risk_color}22;color:{risk_color};border:1px solid {risk_color}44;padding:2px 12px;border-radius:20px;font-size:0.78rem;font-weight:600'>Risk: {cached.get('risk_level','N/A')}</span>
                            </div>
                            <div style='display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:1rem'>
                                <div style='background:#0d2318;border:1px solid #00d4aa33;border-radius:8px;padding:0.8rem'>
                                    <div style='color:#00d4aa;font-size:0.72rem;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px'>✅ Pros</div>
                                    {''.join(f"<div style='color:#c8dce8;font-size:0.83rem;padding:3px 0;border-bottom:1px solid #1e3347'>• {p}</div>" for p in cached.get('pros',[]))}
                                </div>
                                <div style='background:#1e1218;border:1px solid #ff4b4b33;border-radius:8px;padding:0.8rem'>
                                    <div style='color:#ff4b4b;font-size:0.72rem;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px'>⚠️ Cons</div>
                                    {''.join(f"<div style='color:#c8dce8;font-size:0.83rem;padding:3px 0;border-bottom:1px solid #1e3347'>• {c}</div>" for c in cached.get('cons',[]))}
                                </div>
                            </div>
                            <div style='background:#111e2d;border:1px solid #1e3347;border-radius:8px;padding:0.8rem;margin-bottom:0.8rem'>
                                <div style='color:#6b8fa8;font-size:0.72rem;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px'>📊 Market Analysis</div>
                                <div style='color:#c8dce8;font-size:0.85rem;line-height:1.6'>{cached.get('market_analysis','')}</div>
                            </div>
                            <div style='display:grid;grid-template-columns:1fr 1fr;gap:0.8rem;margin-bottom:0.8rem'>
                                <div style='background:#111e2d;border:1px solid #1e3347;border-radius:8px;padding:0.8rem'>
                                    <div style='color:#6b8fa8;font-size:0.72rem;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px'>🎯 Analyst Target</div>
                                    <div style='color:#f5a623;font-size:0.88rem;font-weight:600'>{cached.get('analyst_target','N/A')}</div>
                                </div>
                                <div style='background:#111e2d;border:1px solid #1e3347;border-radius:8px;padding:0.8rem'>
                                    <div style='color:#6b8fa8;font-size:0.72rem;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px'>💡 CSP Recommendation</div>
                                    <div style='color:#c8dce8;font-size:0.83rem'>{cached.get('csp_recommendation','N/A')}</div>
                                </div>
                            </div>
                            <div style='background:#0d2318;border:1px solid #ffd70033;border-radius:8px;padding:0.7rem 1rem'>
                                <span style='color:#6b8fa8;font-size:0.72rem;text-transform:uppercase;letter-spacing:1px'>⚖️ Verdict: </span>
                                <span style='color:#ffd700;font-size:0.85rem;font-weight:600'>{cached.get('verdict','')}</span>
                            </div>
                        </div>""", unsafe_allow_html=True)

        def render_wb_region(df_region, tab_id='all'):
            if df_region.empty:
                st.info("No stocks match your filters for this region.")
                return
            top = df_region[df_region['wheel_score'] >= 65].sort_values('wheel_score', ascending=False)
            rest = df_region[df_region['wheel_score'] < 65].sort_values('wheel_score', ascending=False)
            if not top.empty:
                st.markdown("<div class='section-head'><span>🏆 Top Picks</span></div>", unsafe_allow_html=True)
                for _, row in top.iterrows():
                    r = row.to_dict(); r['_tier'] = 1
                    render_wb_card(r, tab_id)
            if not rest.empty:
                st.markdown("<div class='section-head'><span>👀 Watchlist</span></div>", unsafe_allow_html=True)
                for _, row in rest.iterrows():
                    r = row.to_dict(); r['_tier'] = 2
                    render_wb_card(r, tab_id)

        with reg_all:
            render_wb_region(wb_df, 'all')
        with reg_in:
            render_wb_region(wb_df[wb_df['region']=='India'], 'india')
        with reg_hk:
            render_wb_region(wb_df[wb_df['region']=='HK'], 'hk')
        with reg_us:
            render_wb_region(wb_df[wb_df['region']=='USA'], 'us')

        st.markdown("---")
        st.download_button("📥 Download Wealth Builder Results (CSV)",
            data=wb_df.sort_values('wheel_score', ascending=False).to_csv(index=False),
            file_name=f"wealth_builder_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv", use_container_width=True)
    else:
        st.markdown("""
        <div style='text-align:center; padding:4rem 2rem; color:#3a5060'>
            <div style='font-size:3.5rem'>💎</div>
            <p style='font-family:Space Mono,monospace; color:#ffd700; margin:1rem 0 0.5rem; font-size:1.1rem'>Wealth Builder Screener</p>
            <p style='font-size:0.9rem; color:#6b8fa8'>Claude's curated picks for dividend + premium double income</p>
            <p style='font-size:0.82rem; margin-top:0.5rem'>30 stocks · 🇮🇳 India · 🇭🇰 Hong Kong · 🇺🇸 USA · No lot size constraints</p>
            <div style='display:flex; gap:10px; justify-content:center; flex-wrap:wrap; margin-top:1.5rem'>
                <span class='tag tag-blue' style='padding:5px 12px'>💰 Dividend yield weighted 25%</span>
                <span class='tag tag-green' style='padding:5px 12px'>📈 Quality business moats</span>
                <span class='tag tag-yellow' style='padding:5px 12px'>🌍 Global diversification</span>
            </div>
        </div>""", unsafe_allow_html=True)

# ── TAB 6: NIFTY 50 ──────────────────────────────────────────────────────────
with tab_n50:
    st.markdown("<p style='color:#6b8fa8;font-size:0.72rem;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:0.5rem'>⚙️ Configuration</p>", unsafe_allow_html=True)

    nc1, nc2, nc3, nc4 = st.columns([1.5, 1.5, 1.5, 1])
    with nc1:
        n50_sector = st.multiselect("🏭 Sector Filter", ['Technology','Financial Services','Energy','Consumer Defensive','Healthcare','Industrials','Basic Materials','Communication Services','Consumer Cyclical','Utilities'], default=[], placeholder="All sectors", key="n50_sec")
    with nc2:
        rsi_filter = st.selectbox("📊 RSI Filter", ["All", "Oversold (<35) 🟢", "Neutral (35–65)", "Overbought (>65) 🔴"], key="n50_rsi")
    with nc3:
        n50_sort   = st.selectbox("↕️ Sort By", ["RSI ↑ (Oversold first)", "RSI ↓ (Overbought first)", "Growth Expected ↓", "PE ↑ (Cheapest first)", "PE ↓ (Most expensive)", "1D Change ↓", "1D Change ↑", "Market Cap ↓"], key="n50_sort")
    with nc4:
        st.markdown("<div style='margin-top:1.85rem'></div>", unsafe_allow_html=True)
        run_n50 = st.button("🚀 Run Scan", key="run_n50", use_container_width=True)

    # Legend
    st.markdown("""
    <div style='display:flex;gap:12px;flex-wrap:wrap;margin-bottom:1rem;font-size:0.78rem'>
        <span style='background:#00d4aa22;color:#00d4aa;padding:3px 10px;border-radius:4px;border:1px solid #00d4aa44'>🟢 RSI &lt;35 — Oversold (CSP opportunity)</span>
        <span style='background:#6b8fa822;color:#a0b4c0;padding:3px 10px;border-radius:4px;border:1px solid #2a3f52'>⚪ RSI 35–65 — Neutral</span>
        <span style='background:#ff4b4b22;color:#ff4b4b;padding:3px 10px;border-radius:4px;border:1px solid #ff4b4b44'>🔴 RSI &gt;65 — Overbought (avoid puts)</span>
    </div>""", unsafe_allow_html=True)

    if run_n50:
        st.session_state.n50_results = None
        n50_bar = st.progress(0, text="📊 Fetching Nifty 50 data...")
        n50_res = []
        for i, ticker in enumerate(NIFTY50):
            n50_bar.progress((i+1)/len(NIFTY50), text=f"📊 {ticker.replace('.NS','')} ({i+1}/{len(NIFTY50)})")
            d = fetch_n50_data(ticker)
            if d: n50_res.append(d)
        n50_bar.empty()
        st.session_state.n50_results = n50_res
        st.session_state.n50_time    = datetime.now().strftime('%d %b %Y, %I:%M %p')

    if st.session_state.n50_results:
        res  = st.session_state.n50_results
        df50 = pd.DataFrame(res)

        # Apply filters
        if n50_sector:
            df50 = df50[df50['sector'].isin(n50_sector)]
        if rsi_filter == "Oversold (<35) 🟢":
            df50 = df50[df50['rsi'] < 35]
        elif rsi_filter == "Neutral (35–65)":
            df50 = df50[(df50['rsi'] >= 35) & (df50['rsi'] <= 65)]
        elif rsi_filter == "Overbought (>65) 🔴":
            df50 = df50[df50['rsi'] > 65]

        # Apply sort
        sort_map = {
            "RSI ↑ (Oversold first)":    ('rsi',        True),
            "RSI ↓ (Overbought first)":  ('rsi',        False),
            "Growth Expected ↓":         ('growth_exp', False),
            "PE ↑ (Cheapest first)":     ('pe',         True),
            "PE ↓ (Most expensive)":     ('pe',         False),
            "1D Change ↓":               ('change_1d',  False),
            "1D Change ↑":               ('change_1d',  True),
            "Market Cap ↓":              ('market_cap', False),
        }
        sc, asc = sort_map.get(n50_sort, ('rsi', True))
        # Only filter out zeros/nulls for specific columns
        if sc in ('pe', 'forward_pe', 'pb'):
            df50 = df50[df50[sc] > 0]
        elif sc == 'growth_exp':
            df50 = df50[df50[sc].notna()]
        df50 = df50.sort_values(sc, ascending=asc)

        st.markdown(f"<p style='color:#6b8fa8;font-size:0.8rem;margin:0.5rem 0'>Last scan: {st.session_state.n50_time} · {len(df50)} stocks shown</p>", unsafe_allow_html=True)

        # Summary boxes
        oversold  = len(df50[df50['rsi'] < 35])
        neutral   = len(df50[(df50['rsi'] >= 35) & (df50['rsi'] <= 65)])
        overbought= len(df50[df50['rsi'] > 65])
        avg_pe    = round(df50[df50['pe'] > 0]['pe'].mean(), 1)

        sm1,sm2,sm3,sm4 = st.columns(4)
        for col,lbl,val,col_style in [
            (sm1,'🟢 Oversold',    oversold,   '#00d4aa'),
            (sm2,'⚪ Neutral',     neutral,    '#a0b4c0'),
            (sm3,'🔴 Overbought',  overbought, '#ff4b4b'),
            (sm4,'📊 Avg Nifty PE',avg_pe,     '#f5a623'),
        ]:
            col.markdown(f"<div style='background:#0d1a26;border:1px solid #1e3347;border-radius:10px;padding:0.8rem;text-align:center'>"
                         f"<div style='color:#6b8fa8;font-size:0.7rem;text-transform:uppercase;letter-spacing:1px'>{lbl}</div>"
                         f"<div style='color:{col_style};font-family:Space Mono,monospace;font-size:1.6rem;font-weight:700'>{val}</div>"
                         f"</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Table header
        st.markdown("""
        <div style='display:grid;grid-template-columns:75px 140px 140px 65px 70px 65px 60px 65px 80px 75px 85px;
             gap:4px;padding:6px 10px;background:#0d1a26;border-radius:6px;
             font-size:0.7rem;color:#6b8fa8;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px'>
            <div>Ticker</div><div>Name</div><div>Sector</div>
            <div style='text-align:right'>Price</div>
            <div style='text-align:right'>1D %</div>
            <div style='text-align:right'>RSI</div>
            <div style='text-align:right'>PE</div>
            <div style='text-align:right'>Fwd PE</div>
            <div style='text-align:right'>Growth</div>
            <div style='text-align:right'>P/B</div>
            <div style='text-align:right'>Div Yield</div>
        </div>""", unsafe_allow_html=True)

        # Table rows
        for _, row in df50.iterrows():
            rsi_val  = row['rsi']
            if rsi_val < 35:
                rsi_bg = '#00d4aa22'; rsi_col = '#00d4aa'; rsi_emoji = '🟢'
            elif rsi_val > 65:
                rsi_bg = '#ff4b4b22'; rsi_col = '#ff4b4b'; rsi_emoji = '🔴'
            else:
                rsi_bg = '#1a2332';   rsi_col = '#a0b4c0'; rsi_emoji = '⚪'

            chg      = row['change_1d']
            chg_col  = '#00d4aa' if chg >= 0 else '#ff4b4b'
            chg_str  = f"+{chg:.2f}%" if chg >= 0 else f"{chg:.2f}%"
            pe_str   = f"{row['pe']:.1f}" if row['pe'] > 0 else '—'
            fpe_str  = f"{row['forward_pe']:.1f}" if row['forward_pe'] > 0 else '—'
            pb_str   = f"{row['pb']:.2f}" if row['pb'] > 0 else '—'
            div_str  = f"{row['div_yield']:.1f}%" if row['div_yield'] > 0 else '—'
            ma_dot   = "🟢" if row['above_50ma'] else ("🔴" if row['above_50ma'] is False else "⚪")

            # Growth expected
            g_val = row.get('growth_exp')
            if g_val is not None:
                if g_val > 10:   g_col = '#00d4aa'; g_str = f'▲ {g_val:.1f}%'
                elif g_val > 0:  g_col = '#7fbf7f'; g_str = f'▲ {g_val:.1f}%'
                elif g_val < -5: g_col = '#ff4b4b'; g_str = f'▼ {abs(g_val):.1f}%'
                else:            g_col = '#6b8fa8'; g_str = f'▼ {abs(g_val):.1f}%'
            else:
                g_col = '#6b8fa8'; g_str = 'N/A'

            st.markdown(
                f"<div style='display:grid;grid-template-columns:75px 140px 140px 65px 70px 65px 60px 65px 80px 75px 85px;"
                f"gap:4px;padding:8px 10px;background:{rsi_bg};border-radius:6px;margin-bottom:3px;"
                f"border-left:3px solid {rsi_col};align-items:center;font-size:0.82rem'>"
                f"<div style='color:#fff;font-family:Space Mono,monospace;font-weight:700'>{row['ticker']}</div>"
                f"<div style='color:#a0b4c0'>{row['name']}</div>"
                f"<div style='color:#6b8fa8;font-size:0.75rem'>{row['sector'][:18]}</div>"
                f"<div style='text-align:right;color:#fff;font-weight:600'>₹{row['price']:,.1f}</div>"
                f"<div style='text-align:right;color:{chg_col};font-weight:600'>{chg_str}</div>"
                f"<div style='text-align:right;color:{rsi_col};font-weight:700'>{rsi_emoji} {rsi_val:.1f}</div>"
                f"<div style='text-align:right;color:#f5a623'>{pe_str}</div>"
                f"<div style='text-align:right;color:#a0b4c0'>{fpe_str}</div>"
                f"<div style='text-align:right;color:{g_col};font-weight:700'>{g_str}</div>"
                f"<div style='text-align:right;color:#a0b4c0'>{pb_str}</div>"
                f"<div style='text-align:right;color:#4b9fff'>{div_str}</div>"
                f"</div>",
                unsafe_allow_html=True
            )

        # Download
        st.markdown("<br>", unsafe_allow_html=True)
        csv_cols = ['ticker','name','sector','price','change_1d','rsi','rsi_signal','pe','forward_pe','growth_exp','pb','div_yield','total_debt_cr','debt_to_equity','market_cap']
        st.download_button("📥 Download Nifty 50 Data (CSV)",
            data=df50[csv_cols].to_csv(index=False),
            file_name=f"nifty50_rsi_pe_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv", use_container_width=True)
    else:
        st.markdown("""
        <div style='text-align:center;padding:4rem 2rem;color:#3a5060'>
            <div style='font-size:3.5rem'>📊</div>
            <p style='font-family:Space Mono,monospace;color:#6b8fa8;margin:1rem 0 0.5rem'>Nifty 50 — RSI + PE Dashboard</p>
            <p style='font-size:0.85rem'>Click <strong style='color:#00d4aa'>Run Scan</strong> to fetch live data for all 50 stocks</p>
            <div style='display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-top:1.5rem'>
                <span style='background:#00d4aa22;color:#00d4aa;padding:4px 12px;border-radius:4px;font-size:0.78rem'>🟢 Oversold RSI — CSP opportunity</span>
                <span style='background:#f5a62322;color:#f5a623;padding:4px 12px;border-radius:4px;font-size:0.78rem'>📊 PE + Forward PE + P/B</span>
                <span style='background:#4b9fff22;color:#4b9fff;padding:4px 12px;border-radius:4px;font-size:0.78rem'>💰 Dividend yield</span>
            </div>
        </div>""", unsafe_allow_html=True)

# ── Visitor Counter ──────────────────────────────────────────────────────────
import os, json as _json
from datetime import datetime, timedelta

COUNTER_FILE = "/tmp/visitor_log.json"

def load_visits():
    try:
        if os.path.exists(COUNTER_FILE):
            return _json.loads(open(COUNTER_FILE).read())
    except: pass
    return {"total": 0, "log": []}

def save_visits(data):
    try:
        open(COUNTER_FILE, "w").write(_json.dumps(data))
    except: pass

def record_visit():
    data  = load_visits()
    now   = datetime.now().isoformat()
    data["total"] += 1
    data["log"].append(now)
    # Keep only last 10000 entries
    data["log"] = data["log"][-10000:]
    save_visits(data)
    return data

def count_last_24h(log):
    cutoff = datetime.now() - timedelta(hours=24)
    return sum(1 for t in log if datetime.fromisoformat(t) > cutoff)

# Record visit once per session
if 'visitor_counted' not in st.session_state:
    st.session_state.visitor_counted = True
    visit_data = record_visit()
else:
    visit_data = load_visits()

total_visits  = visit_data.get("total", 0)
visits_24h    = count_last_24h(visit_data.get("log", []))

st.markdown(f"""
<div style='text-align:center; padding:1.5rem 1rem 0.5rem; margin-top:2rem'>
    <div style='display:inline-flex; align-items:center; gap:0; flex-wrap:wrap; justify-content:center;
         background:#0d1a26; border:1px solid #1e3347; border-radius:12px; padding:0.8rem 2.5rem; gap:2rem'>
        <div style='text-align:center'>
            <div style='color:#6b8fa8; font-size:0.7rem; text-transform:uppercase; letter-spacing:1px'>Total Visits</div>
            <div style='color:#00d4aa; font-family:Space Mono,monospace; font-size:1.8rem; font-weight:700'>{total_visits:,}</div>
        </div>
        <div style='width:1px; height:40px; background:#1e3347'></div>
        <div style='text-align:center'>
            <div style='color:#6b8fa8; font-size:0.7rem; text-transform:uppercase; letter-spacing:1px'>Last 24 Hours</div>
            <div style='color:#f5a623; font-family:Space Mono,monospace; font-size:1.8rem; font-weight:700'>{visits_24h:,}</div>
        </div>
        <div style='width:1px; height:40px; background:#1e3347'></div>
        <div style='text-align:center'>
            <div style='color:#6b8fa8; font-size:0.7rem; text-transform:uppercase; letter-spacing:1px'>Last Visit</div>
            <div style='color:#a0b4c0; font-size:0.82rem; font-weight:600'>{datetime.now().strftime('%d %b %Y')}<br>{datetime.now().strftime('%I:%M %p')}</div>
        </div>
        <div style='width:1px; height:40px; background:#1e3347'></div>
        <div style='text-align:center'>
            <div style='color:#6b8fa8; font-size:0.7rem; text-transform:uppercase; letter-spacing:1px'>Status</div>
            <div style='color:#00d4aa; font-size:0.9rem; font-weight:700'>🟢 Live</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Disclaimer ────────────────────────────────────────────────────────────────
st.markdown("""
<div class='disclaimer'>
    ⚠️ For educational purposes only. Not SEBI registered. Options trading involves substantial risk of loss.
    Do your own research. Lot sizes change quarterly — verify at
    <a href='https://www.nseindia.com' target='_blank' style='color:#3a7080'>nseindia.com</a>
</div>
""", unsafe_allow_html=True)
