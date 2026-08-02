"""
RSI + PE Screener — Nifty 50 | HK 50 | US 50
Built for: Srini
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import os, json as _json
from datetime import datetime, timedelta

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RSI + PE Screener",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    h1, h2, h3 { font-family: 'Space Mono', monospace; }
    .metric-box { background:#1a2d3d; border:1px solid #2a3f52; border-radius:10px; padding:0.9rem 1rem; text-align:center; }
    .metric-box .label { color:#6b8fa8; font-size:0.7rem; text-transform:uppercase; letter-spacing:1px; }
    .metric-box .value { color:#00d4aa; font-size:1.5rem; font-weight:700; font-family:'Space Mono',monospace; }
    .stTabs [data-baseweb="tab-list"] { background:#0a1628; border-radius:10px 10px 0 0; padding:4px 8px 0 8px; gap:4px; border-bottom:2px solid #1e3347; }
    .stTabs [data-baseweb="tab"] { background:transparent; border-radius:8px 8px 0 0; color:#6b8fa8 !important; font-family:'Space Mono',monospace; font-size:0.9rem; padding:10px 24px; border:none; }
    .stTabs [aria-selected="true"] { background:#1a2d3d !important; color:#00d4aa !important; border-bottom:2px solid #00d4aa; }
    .stTabs [data-baseweb="tab-panel"] { background:#0d1a26; border:1px solid #1e3347; border-top:none; border-radius:0 0 10px 10px; padding:1.5rem; }
    .stButton > button { background:linear-gradient(135deg,#00d4aa,#0099cc); color:#000 !important; font-weight:700; font-family:'Space Mono',monospace; border:none; border-radius:8px; padding:0.55rem 1.5rem; font-size:0.95rem; width:100%; }
    .stButton > button:hover { background:linear-gradient(135deg,#00ffcc,#00bbee) !important; }
    section[data-testid="stSidebar"] { display:none !important; }
    .block-container { max-width:100% !important; padding-left:2rem !important; padding-right:2rem !important; padding-top:1rem !important; }
    .disclaimer { color:#3a5060; font-size:0.72rem; text-align:center; margin-top:2rem; padding:1rem; border-top:1px solid #1e3347; }
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
    'XOM','CVX','COP','SLB',
    'CAT','DE','GE','HON',
    'SPY','QQQ','IWM','GLD','SLV',
    'T','VZ','NEE','DUK',
]

# ── Shared Functions ──────────────────────────────────────────────────────────

def calc_rsi(series, period=14):
    delta    = series.diff()
    gain     = delta.clip(lower=0)
    loss     = (-delta.clip(upper=0))
    avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    rs       = avg_gain / avg_loss.replace(0, 1e-10)
    rsi      = 100 - (100 / (1 + rs))
    return round(float(rsi.dropna().iloc[-1]), 1)

def safe_float(val, default=0.0):
    import math
    try:
        f = float(val)
        return default if math.isnan(f) or math.isinf(f) else f
    except:
        return default

def fetch_data(ticker, currency_symbol):
    try:
        raw = yf.download(ticker, period='6mo', auto_adjust=True, progress=False)
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = raw.columns.get_level_values(0)
        if raw is None or len(raw) < 20:
            return None
        close = raw['Close'].dropna()
        if len(close) < 20:
            return None
        price     = float(close.iloc[-1])
        if price <= 0:
            return None
        rsi       = calc_rsi(close)
        change_1d = ((price - float(close.iloc[-2])) / float(close.iloc[-2])) * 100 if len(close) >= 2 else 0.0
        ma50_val  = float(close.rolling(50).mean().iloc[-1]) if len(close) >= 50 else None
        try:
            info = yf.Ticker(ticker).info or {}
        except:
            info = {}
        pe         = safe_float(info.get('trailingPE'))
        forward_pe = safe_float(info.get('forwardPE'))
        pb         = safe_float(info.get('priceToBook'))
        mkt_cap    = safe_float(info.get('marketCap'))
        total_debt = safe_float(info.get('totalDebt'))
        div_yield  = 0.0
        div_raw    = info.get('dividendYield')
        div_rate   = safe_float(info.get('dividendRate'))
        if div_raw is not None:
            dv = safe_float(div_raw)
            if 0 < dv < 1:
                div_yield = dv * 100
            elif 1 <= dv <= 20:
                div_yield = dv
        if div_yield == 0.0 and div_rate > 0 and price > 0:
            div_yield = (div_rate / price) * 100
        div_yield  = round(min(div_yield, 20.0), 2)
        growth_exp = round(((pe - forward_pe) / forward_pe) * 100, 1) if pe > 0 and forward_pe > 0 else None
        sector = str(info.get('sector') or info.get('industry') or 'N/A')
        name   = str(info.get('shortName') or info.get('longName') or ticker)
        if '.HK' in ticker:
            debt_display = round(total_debt / 1e8, 0) if total_debt > 0 else 0
            debt_unit    = 'HK$100M'
        elif '.NS' in ticker:
            debt_display = round(total_debt / 1e7, 0) if total_debt > 0 else 0
            debt_unit    = 'INR Cr'
        else:
            debt_display = round(total_debt / 1e9, 1) if total_debt > 0 else 0
            debt_unit    = 'USD B'
        raw_t = ticker.replace('.NS','')
        if '.HK' in ticker:
            raw_t = ticker.replace('.HK','').lstrip('0')
        return {
            'ticker':       raw_t,
            'raw_ticker':   ticker,
            'name':         name[:24],
            'sector':       sector,
            'currency':     currency_symbol,
            'price':        round(price, 2),
            'change_1d':    round(change_1d, 2),
            'rsi':          rsi,
            'rsi_signal':   'Oversold' if rsi < 35 else ('Overbought' if rsi > 65 else 'Neutral'),
            'pe':           round(pe, 1),
            'forward_pe':   round(forward_pe, 1),
            'growth_exp':   growth_exp,
            'pb':           round(pb, 2),
            'div_yield':    div_yield,
            'debt_display': debt_display,
            'debt_unit':    debt_unit,
            'market_cap':   round(mkt_cap / 1e7, 0) if mkt_cap > 0 else 0,
            'above_50ma':   (price > ma50_val) if ma50_val and not np.isnan(ma50_val) else None,
        }
    except Exception:
        return None

# ── Shared render function ────────────────────────────────────────────────────

def render_screener(tab_key, tickers, currency_symbol, title, scan_key, time_key, sector_options=None):
    st.markdown(
        "<p style='color:#6b8fa8;font-size:0.72rem;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:0.5rem'>⚙️ Configuration</p>",
        unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns([1.5, 1.5, 1.5, 1.5, 0.8])
    with c1:
        sec_opts   = sector_options or []
        sec_filter = st.multiselect("🏭 Sector", sec_opts, default=[], placeholder="All sectors", key="sec_"+tab_key)
    with c2:
        rsi_filter = st.selectbox("📊 RSI Filter",
            ["All","Oversold (<35) 🟢","Neutral (35-65)","Overbought (>65) 🔴"], key="rsi_"+tab_key)
    with c3:
        sort_by    = st.selectbox("Sort By",
            ["RSI (Oversold first)","RSI (Overbought first)","PE (Cheapest first)",
             "PE (Most expensive)","Growth (Most growth)","Div Yield","1D Change Down","1D Change Up"],
            key="sort_"+tab_key)
    with c4:
        search     = st.text_input("Search ticker / name", placeholder="e.g. RELIANCE", key="search_"+tab_key)
    with c5:
        st.markdown("<div style='margin-top:1.85rem'></div>", unsafe_allow_html=True)
        run_btn    = st.button("Run Scan", key="run_"+tab_key, use_container_width=True)

    st.markdown("""
    <div style='display:flex;gap:10px;flex-wrap:wrap;margin-bottom:1rem;font-size:0.78rem'>
        <span style='background:#00d4aa22;color:#00d4aa;padding:3px 10px;border-radius:4px'>🟢 RSI &lt;35 — Oversold</span>
        <span style='background:#2a3f5222;color:#a0b4c0;padding:3px 10px;border-radius:4px'>⚪ RSI 35-65 — Neutral</span>
        <span style='background:#ff4b4b22;color:#ff4b4b;padding:3px 10px;border-radius:4px'>🔴 RSI &gt;65 — Overbought</span>
        <span style='background:#00d4aa22;color:#00d4aa;padding:3px 10px;border-radius:4px'>Growth% = earnings growth expected (PE vs Fwd PE)</span>
    </div>""", unsafe_allow_html=True)

    if run_btn:
        st.session_state[scan_key] = None
        bar = st.progress(0, text="Scanning "+title+"...")
        results = []
        for i, ticker in enumerate(tickers):
            bar.progress((i+1)/len(tickers), text="Fetching "+ticker.replace('.NS','').replace('.HK','')+" ("+str(i+1)+"/"+str(len(tickers))+")")
            d = fetch_data(ticker, currency_symbol)
            if d:
                results.append(d)
        bar.empty()
        st.session_state[scan_key] = results
        st.session_state[time_key] = datetime.now().strftime('%d %b %Y, %I:%M %p')

    results = st.session_state.get(scan_key)
    if results:
        df = pd.DataFrame(results)

        if sec_filter:
            df = df[df['sector'].isin(sec_filter)]
        if rsi_filter == "Oversold (<35) 🟢":
            df = df[df['rsi'] < 35]
        elif rsi_filter == "Neutral (35-65)":
            df = df[(df['rsi'] >= 35) & (df['rsi'] <= 65)]
        elif rsi_filter == "Overbought (>65) 🔴":
            df = df[df['rsi'] > 65]
        if search:
            mask = (df['ticker'].str.contains(search.upper(), na=False) |
                    df['name'].str.contains(search, case=False, na=False))
            df = df[mask]

        sort_map = {
            "RSI (Oversold first)":    ('rsi', True),
            "RSI (Overbought first)":  ('rsi', False),
            "PE (Cheapest first)":     ('pe',  True),
            "PE (Most expensive)":     ('pe',  False),
            "Growth (Most growth)":    ('growth_exp', False),
            "Div Yield":               ('div_yield', False),
            "1D Change Down":          ('change_1d', False),
            "1D Change Up":            ('change_1d', True),
        }
        sc, asc = sort_map.get(sort_by, ('rsi', True))
        if sc in ('pe','forward_pe','pb'):
            df = df[df[sc] > 0]
        df = df.sort_values(sc, ascending=asc, na_position='last')

        scan_time  = st.session_state.get(time_key, '')
        oversold   = len(df[df['rsi'] < 35])
        neutral    = len(df[(df['rsi'] >= 35) & (df['rsi'] <= 65)])
        overbought = len(df[df['rsi'] > 65])
        pe_vals    = df[df['pe'] > 0]['pe']
        avg_pe     = round(pe_vals.mean(), 1) if len(pe_vals) > 0 else 0

        st.markdown(
            "<p style='color:#6b8fa8;font-size:0.8rem;margin:0.5rem 0'>Last scan: "+scan_time+" · "+str(len(df))+" stocks shown</p>",
            unsafe_allow_html=True)

        m1,m2,m3,m4 = st.columns(4)
        for col, lbl, val, vc in [
            (m1,'🟢 Oversold',   oversold,   '#00d4aa'),
            (m2,'⚪ Neutral',    neutral,    '#a0b4c0'),
            (m3,'🔴 Overbought', overbought, '#ff4b4b'),
            (m4,'📊 Avg PE',     avg_pe,     '#f5a623'),
        ]:
            col.markdown(
                "<div style='background:#0d1a26;border:1px solid #1e3347;border-radius:10px;padding:0.8rem;text-align:center'>"
                "<div style='color:#6b8fa8;font-size:0.7rem;text-transform:uppercase;letter-spacing:1px'>"+lbl+"</div>"
                "<div style='color:"+vc+";font-family:Space Mono,monospace;font-size:1.6rem;font-weight:700'>"+str(val)+"</div>"
                "</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        debt_lbl = str(df['debt_unit'].iloc[0]) if len(df) > 0 else 'Debt'
        grid = "75px 165px 155px 70px 72px 68px 65px 65px 80px 68px 85px 90px"

        st.markdown(
            "<div style='display:grid;grid-template-columns:"+grid+";gap:4px;padding:6px 10px;"
            "background:#0d1a26;border-radius:6px;font-size:0.68rem;color:#6b8fa8;"
            "text-transform:uppercase;letter-spacing:1px;margin-bottom:4px'>"
            "<div>Ticker</div><div>Name</div><div>Sector</div>"
            "<div style='text-align:right'>Price</div>"
            "<div style='text-align:right'>1D %</div>"
            "<div style='text-align:right'>RSI</div>"
            "<div style='text-align:right'>PE</div>"
            "<div style='text-align:right'>Fwd PE</div>"
            "<div style='text-align:right'>Growth</div>"
            "<div style='text-align:right'>P/B</div>"
            "<div style='text-align:right'>Div %</div>"
            "<div style='text-align:right'>Debt "+debt_lbl+"</div>"
            "</div>", unsafe_allow_html=True)

        for _, row in df.iterrows():
            rsi_val = row['rsi']
            if rsi_val < 35:
                rsi_bg='#00d4aa18'; rsi_col='#00d4aa'; rsi_e='🟢'
            elif rsi_val > 65:
                rsi_bg='#ff4b4b18'; rsi_col='#ff4b4b'; rsi_e='🔴'
            else:
                rsi_bg='#1a2332';   rsi_col='#a0b4c0'; rsi_e='⚪'

            chg     = row['change_1d']
            chg_col = '#00d4aa' if chg >= 0 else '#ff4b4b'
            chg_str = ("+"+str(round(chg,2))+"%") if chg >= 0 else (str(round(chg,2))+"%")
            pe_str  = str(row['pe'])  if row['pe']  > 0 else '-'
            fpe_str = str(row['forward_pe']) if row['forward_pe'] > 0 else '-'
            pb_str  = str(row['pb'])  if row['pb']  > 0 else '-'
            div_str = (str(row['div_yield'])+"%") if row['div_yield'] > 0 else '-'
            cur     = row['currency']
            pr      = row['price']
            price_str = (cur+"{:,.2f}".format(pr)) if pr < 1000 else (cur+"{:,.0f}".format(pr))

            gv = row.get('growth_exp')
            if gv is not None:
                grow_str = ("+"+str(round(gv,0))+"%") if gv > 0 else (str(round(gv,0))+"%")
                grow_col = '#00d4aa' if gv > 0 else '#ff4b4b'
            else:
                grow_str = '-'; grow_col = '#6b8fa8'

            dv       = row.get('debt_display', 0) or 0
            debt_str = "{:,}".format(int(dv)) if dv > 0 else '-'
            debt_col = '#ff4b4b' if dv > 500 else ('#f5a623' if dv > 100 else '#a0b4c0')

            st.markdown(
                "<div style='display:grid;grid-template-columns:"+grid+";"
                "gap:4px;padding:8px 10px;background:"+rsi_bg+";border-radius:6px;"
                "margin-bottom:3px;border-left:3px solid "+rsi_col+";align-items:center;font-size:0.8rem'>"
                "<div style='color:#fff;font-family:Space Mono,monospace;font-weight:700;font-size:0.78rem'>"+str(row['ticker'])+"</div>"
                "<div style='color:#a0b4c0;font-size:0.75rem'>"+str(row['name'])+"</div>"
                "<div style='color:#6b8fa8;font-size:0.72rem'>"+str(row['sector'])[:18]+"</div>"
                "<div style='text-align:right;color:#fff;font-weight:600;font-size:0.78rem'>"+price_str+"</div>"
                "<div style='text-align:right;color:"+chg_col+";font-weight:600'>"+chg_str+"</div>"
                "<div style='text-align:right;color:"+rsi_col+";font-weight:700'>"+rsi_e+str(rsi_val)+"</div>"
                "<div style='text-align:right;color:#f5a623'>"+pe_str+"</div>"
                "<div style='text-align:right;color:#a0b4c0'>"+fpe_str+"</div>"
                "<div style='text-align:right;color:"+grow_col+";font-weight:600'>"+grow_str+"</div>"
                "<div style='text-align:right;color:#a0b4c0'>"+pb_str+"</div>"
                "<div style='text-align:right;color:#4b9fff'>"+div_str+"</div>"
                "<div style='text-align:right;color:"+debt_col+";font-size:0.72rem'>"+debt_str+"</div>"
                "</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        csv_cols = ['ticker','name','sector','price','change_1d','rsi','rsi_signal',
                    'pe','forward_pe','growth_exp','pb','div_yield','debt_display','debt_unit','market_cap']
        avail = [c for c in csv_cols if c in df.columns]
        st.download_button("Download "+title+" Data (CSV)",
            data=df[avail].to_csv(index=False),
            file_name=tab_key+"_rsi_pe_"+datetime.now().strftime('%Y%m%d_%H%M')+".csv",
            mime="text/csv", use_container_width=True)
    else:
        st.markdown(
            "<div style='text-align:center;padding:4rem 2rem;color:#3a5060'>"
            "<div style='font-size:3.5rem'>📊</div>"
            "<p style='font-family:Space Mono,monospace;color:#6b8fa8;margin:1rem 0 0.5rem'>"+title+" — RSI + PE Dashboard</p>"
            "<p style='font-size:0.85rem'>Click <strong style='color:#00d4aa'>Run Scan</strong> to fetch live data for all stocks</p>"
            "</div>", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────
for key, val in {
    'n50_results': None,'n50_time': None,
    'hk50_results':None,'hk50_time':None,
    'us50_results': None,'us50_time':None,
    'visitor_counted': False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── App Header ────────────────────────────────────────────────────────────────
st.markdown("""
<div style='background:linear-gradient(135deg,#0a1628,#0d2137);border-bottom:1px solid #1e3347;
     padding:1rem 2rem;display:flex;align-items:center;justify-content:space-between;margin-bottom:0'>
    <div>
        <p style='color:#00d4aa;font-family:Space Mono,monospace;font-size:1.4rem;font-weight:700;margin:0'>
            📊 RSI + PE SCREENER
        </p>
        <p style='color:#6b8fa8;font-size:0.8rem;margin:0'>Nifty 50 · HK 50 · US 50 · Real-Time Data</p>
    </div>
    <div style='text-align:right'>
        <p style='color:#00d4aa;font-size:0.78rem;margin:0'>RSI · PE · Fwd PE · Growth · Debt · Dividend</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_n50, tab_hk50, tab_us50 = st.tabs(["🇮🇳  Nifty 50", "🇭🇰  HK 50", "🇺🇸  US 50"])

with tab_n50:
    render_screener('n50', NIFTY50, '₹', 'Nifty 50', 'n50_results', 'n50_time',
        ['Technology','Financial Services','Energy','Consumer Defensive','Healthcare',
         'Industrials','Basic Materials','Communication Services','Consumer Cyclical','Utilities'])

with tab_hk50:
    render_screener('hk50', HK50, 'HK$', 'HK 50', 'hk50_results', 'hk50_time',
        ['Technology','Financial Services','Real Estate','Consumer Cyclical','Energy',
         'Utilities','Healthcare','Industrials','Communication Services','Consumer Defensive'])

with tab_us50:
    render_screener('us50', US50, '$', 'US 50', 'us50_results', 'us50_time',
        ['Technology','Financial Services','Healthcare','Consumer Defensive','Energy',
         'Industrials','Consumer Cyclical','Communication Services','Utilities'])

# ── Visitor Counter ───────────────────────────────────────────────────────────
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
    data = load_visits()
    data["total"] += 1
    data["log"].append(datetime.now().isoformat())
    data["log"] = data["log"][-10000:]
    save_visits(data)
    return data

def count_last_24h(log):
    cutoff = datetime.now() - timedelta(hours=24)
    return sum(1 for t in log if datetime.fromisoformat(t) > cutoff)

if not st.session_state.visitor_counted:
    st.session_state.visitor_counted = True
    visit_data = record_visit()
else:
    visit_data = load_visits()

total_visits = visit_data.get("total", 0)
visits_24h   = count_last_24h(visit_data.get("log", []))

st.markdown(
    "<div style='text-align:center;padding:1.5rem 1rem 0.5rem;margin-top:2rem'>"
    "<div style='display:inline-flex;align-items:center;flex-wrap:wrap;justify-content:center;"
    "background:#0d1a26;border:1px solid #1e3347;border-radius:12px;padding:0.8rem 2.5rem;gap:2rem'>"
    "<div style='text-align:center'>"
    "<div style='color:#6b8fa8;font-size:0.7rem;text-transform:uppercase;letter-spacing:1px'>Total Visits</div>"
    "<div style='color:#00d4aa;font-family:Space Mono,monospace;font-size:1.8rem;font-weight:700'>"+"{:,}".format(total_visits)+"</div>"
    "</div>"
    "<div style='width:1px;height:40px;background:#1e3347'></div>"
    "<div style='text-align:center'>"
    "<div style='color:#6b8fa8;font-size:0.7rem;text-transform:uppercase;letter-spacing:1px'>Last 24 Hours</div>"
    "<div style='color:#f5a623;font-family:Space Mono,monospace;font-size:1.8rem;font-weight:700'>"+"{:,}".format(visits_24h)+"</div>"
    "</div>"
    "<div style='width:1px;height:40px;background:#1e3347'></div>"
    "<div style='text-align:center'>"
    "<div style='color:#6b8fa8;font-size:0.7rem;text-transform:uppercase;letter-spacing:1px'>Last Visit</div>"
    "<div style='color:#a0b4c0;font-size:0.82rem;font-weight:600'>"+datetime.now().strftime('%d %b %Y')+"<br>"+datetime.now().strftime('%I:%M %p')+"</div>"
    "</div>"
    "<div style='width:1px;height:40px;background:#1e3347'></div>"
    "<div style='text-align:center'>"
    "<div style='color:#6b8fa8;font-size:0.7rem;text-transform:uppercase;letter-spacing:1px'>Status</div>"
    "<div style='color:#00d4aa;font-size:0.9rem;font-weight:700'>🟢 Live</div>"
    "</div>"
    "</div></div>", unsafe_allow_html=True)

# ── Disclaimer ────────────────────────────────────────────────────────────────
st.markdown("""
<div class='disclaimer'>
    For educational purposes only. Not SEBI/SFC/SEC registered. Do your own research before investing.
    RSI and PE data sourced from Yahoo Finance — verify independently before trading.
</div>
""", unsafe_allow_html=True)
