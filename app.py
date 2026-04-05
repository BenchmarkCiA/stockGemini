import streamlit as st
import yfinance as yf
import google.generativeai as genai

st.set_page_config(page_title="AlphaView AI 2026", layout="wide")

# --- 2026 API CONFIGURATION ---
try:
    api_key = st.secrets["GEN_AI_KEY"]
    genai.configure(api_key=api_key)
    
    # We are now using the Gemini 3 Series (Released 2025/2026)
    # Options: 'gemini-3-flash-preview' (Fast) or 'gemini-3.1-pro-preview' (Thinking)
    model = genai.GenerativeModel('gemini-3-flash-preview') 
    
except Exception as e:
    st.error("🔑 API Key Missing. Please check your Streamlit Secrets.")
    st.stop()

st.title("📈 AlphaView AI")
ticker = st.text_input("Enter Ticker (e.g. NVDA, TSLA, ELBT.TA):", "NVDA").upper().strip()

if st.button("Analyze Stock"):
    try:
        # 1. Fetch Data
        with st.spinner('Pulling live market data...'):
            stock = yf.Ticker(ticker)
            info = stock.info
            price = info.get('currentPrice') or info.get('regularMarketPrice')
            
            if not price:
                st.error(f"Could not find data for {ticker}. Try a major US symbol like AAPL.")
                st.stop()

        # 2. AI Recommendation Logic
        with st.spinner('Gemini 3 is thinking...'):
            prompt = f"""
            System: Act as a senior Wall Street analyst.
            Stock: {ticker} ({info.get('longName')})
            Current Price: {price} {info.get('currency')}
            Sector: {info.get('sector')}
            Summary: {info.get('longBusinessSummary')[:500]}
            
            Instruction:
            1. Provide a 'BUY' or 'NO BUY' recommendation based on the current 2026 market context.
            2. List 3 direct competitors in the same sector.
            3. Briefly state if those competitors are also eligible for a BUY.
            """
            
            response = model.generate_content(prompt)
            
            st.success("Analysis Complete!")
            st.markdown("### 🤖 AI Recommendation")
            st.write(response.text)

    except Exception as e:
        st.error(f"An error occurred: {e}")
