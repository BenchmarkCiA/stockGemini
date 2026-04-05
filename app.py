import streamlit as st
import yfinance as yf
from google import genai
import pandas as pd

# --- GOOGLE FINANCE STYLING ---
st.set_page_config(page_title="AlphaView AI", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .main { background-color: #121212; }
    .buy-dot {
        height: 12px; width: 12px; background-color: #00c853;
        border-radius: 50%; display: inline-block; margin-right: 8px;
    }
    .stock-card {
        background-color: #1e1e1e; border: 1px solid #333;
        padding: 20px; border-radius: 8px; margin-bottom: 10px;
    }
    .metric-label { color: #9aa0a6; font-size: 0.8rem; }
    .metric-value { color: white; font-size: 1.1rem; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2026 API SETUP ---
try:
    client = genai.Client(api_key=st.secrets["GEN_AI_KEY"])
    # Using the 2026 'Flash' model for high-speed dashboarding
    MODEL_ID = "gemini-3-flash-preview" 
except Exception:
    st.error("🔑 API Key Missing in Streamlit Secrets.")
    st.stop()

# --- APP LOGIC ---
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ["NVDA", "AAPL", "TSLA", "ELBT.TA"]
if 'holdings' not in st.session_state:
    st.session_state.holdings = []

# --- SIDEBAR: MY HOLDINGS ---
with st.sidebar:
    st.title("💼 My Holdings")
    if not st.session_state.holdings:
        st.write("No stocks saved yet.")
    for h in st.session_state.holdings:
        st.info(f"**{h}** - Recommendation: HOLD")

# --- MAIN DASHBOARD ---
tab1, tab2 = st.tabs(["📊 Watchlist Dashboard", "🔍 Deep Analysis"])

with tab1:
    st.title("Market Overview")
    
    # Process Watchlist
    cols = st.columns(2)
    for index, ticker in enumerate(st.session_state.watchlist):
        with cols[index % 2]:
            stock = yf.Ticker(ticker)
            price = stock.info.get('currentPrice') or stock.info.get('regularMarketPrice', 0)
            change = stock.info.get('regularMarketChangePercent', 0)
            
            # AI Logic: Quick "BUY" categorization
            # In a real app, you'd cache this to save credits
            is_buy = "BUY" if change < 2 else "WATCH" # Mock logic for visual demo
            
            st.markdown(f"""
            <div class="stock-card">
                <span style="color:#9aa0a6">{ticker}</span>
                <h2 style="margin:0">${price} <span style="color:#00c853; font-size:1rem">+{change:.2f}%</span></h2>
                <p><span class="buy-dot"></span> <b style="color:#00c853">AI RECOMMENDATION: BUY</b></p>
            </div>
            """, unsafe_allow_html=True)

with tab2:
    target = st.text_input("Enter Ticker for Deep Analysis:", "NVDA").upper()
    if st.button("Generate Recommendation & Find Competitors"):
        with st.spinner("Analyzing data and competitors..."):
            stock = yf.Ticker(target)
            data = stock.info
            
            # 1. Show Main Data (The Google Finance Grid)
            st.header(data.get('longName', target))
            m_col1, m_col2, m_col3 = st.columns(3)
            m_col1.markdown(f"<span class='metric-label'>Mkt Cap</span><br><span class='metric-value'>{data.get('marketCap', 'N/A')}</span>", unsafe_allow_html=True)
            m_col2.markdown(f"<span class='metric-label'>P/E Ratio</span><br><span class='metric-value'>{data.get('trailingPE', 'N/A')}</span>", unsafe_allow_html=True)
            m_col3.markdown(f"<span class='metric-label'>52-Wk High</span><br><span class='metric-value'>{data.get('fiftyTwoWeekHigh', 'N/A')}</span>", unsafe_allow_html=True)

            # 2. Gemini 3 "Thinking" Analysis
            prompt = f"Analyze {target} for a BUY recommendation. Also suggest 2 competitors in the {data.get('sector')} sector and state if they are also a BUY."
            response = client.models.generate_content(model=MODEL_ID, contents=prompt)
            
            st.divider()
            st.markdown("### 🤖 AI Strategy Report")
            st.write(response.text)
            
            if st.button(f"Add {target} to My Holdings"):
                st.session_state.holdings.append(target)
                st.success("Saved!")
