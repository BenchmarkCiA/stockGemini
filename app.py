import streamlit as st
import yfinance as yf
import google.generativeai as genai
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(page_title="AI Stock Advisor", layout="wide")
GEN_AI_KEY = "AIzaSyDGdKZLxR6szgISqru4tlOhaq24jdkn1bk" # Put your key here
genai.configure(api_key=GEN_AI_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')

# --- STYLE (Google Finance Look) ---
st.markdown("""
    <style>
    .main { background-color: #121212; color: white; }
    .stMetric { background-color: #1e1e1e; padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- APP SIDEBAR (My Holdings) ---
st.sidebar.title("📁 My Holdings")
if 'holdings' not in st.session_state:
    st.session_state.holdings = []

# --- MAIN INTERFACE ---
st.title("📈 AlphaView AI")
ticker = st.text_input("Enter US Stock Ticker (e.g., NVDA, AAPL, TSLA):", "NVDA").upper()

if st.button("Analyze Stock"):
    # 1. Fetch Data
    stock = yf.Ticker(ticker)
    info = stock.info
    hist = stock.history(period="1y")

    # UI: Header like your screenshot
    col1, col2 = st.columns([2, 1])
    with col1:
        st.header(f"{info.get('longName', ticker)}")
        current_price = info.get('currentPrice', 0)
        st.subheader(f"${current_price} USD")

    # 2. AI Analysis Logic
    with st.spinner('AI is analyzing market data and news...'):
        prompt = f"""
        Analyze the following stock data for {ticker}:
        Current Price: {current_price}
        52 Week High: {info.get('fiftyTwoWeekHigh')}
        P/E Ratio: {info.get('trailingPE')}
        Business Summary: {info.get('longBusinessSummary')[:500]}

        Task:
        1. Give a definitive BUY recommendation based on data. (If not a buy, explain why).
        2. Identify 3 competitors in the {info.get('sector')} sector.
        3. For those competitors, suggest if they are also BUY candidates.
        4. Format the output with bold headers and clear bullet points.
        """
        response = model.generate_content(prompt)

    # 3. Display Results
    st.divider()
    st.markdown("### 🤖 AI Recommendation")
    st.write(response.text)

    # 4. Save to Holdings
    if st.button(f"I bought {ticker}"):
        st.session_state.holdings.append(ticker)
        st.success(f"Added {ticker} to Holdings!")

# --- HOLDINGS MANAGEMENT ---
st.sidebar.divider()
for held_stock in st.session_state.holdings:
    if st.sidebar.button(f"Manage {held_stock}"):
        # Here we would trigger the HOLD/SELL logic for items in holdings
        st.sidebar.write(f"Analyzing {held_stock} for Exit Strategy...")
