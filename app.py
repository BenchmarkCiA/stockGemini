import streamlit as st
import yfinance as yf
import google.generativeai as genai

st.set_page_config(page_title="AlphaView AI", layout="wide")

# --- API KEY CHECK ---
try:
    # This looks for the key in your Streamlit Secrets
    api_key = st.secrets["GEN_AI_KEY"]
    genai.configure(api_key=api_key)
    # Using 'flash' first as it's faster and more reliable for testing
    model = genai.GenerativeModel('gemini-1.5-flash') 
except Exception as e:
    st.error("🔑 API Key Missing or Incorrect in Streamlit Secrets.")
    st.stop()

st.title("📈 AlphaView AI")
ticker = st.text_input("Enter Ticker:", "NVDA").upper().strip()

if st.button("Analyze Stock"):
    try:
        # 1. Fetch Data
        stock = yf.Ticker(ticker)
        price = stock.info.get('currentPrice') or stock.info.get('regularMarketPrice')
        
        if not price:
            st.error(f"Could not find live data for {ticker}. Is the ticker correct?")
            st.stop()

        # 2. Try AI Analysis
        with st.spinner('Asking Google AI...'):
            prompt = f"Analyze {ticker} stock. Current price is {price}. Is it a buy? Give 2 competitors."
            
            # This is where your error happened:
            response = model.generate_content(prompt)
            st.success("Analysis Complete!")
            st.write(response.text)

    except Exception as e:
        # --- THIS IS THE DIAGNOSTIC BOX ---
        st.error("🛑 The AI call failed. Here is the specific reason:")
        st.warning(f"Error Type: {type(e).__name__}")
        st.code(str(e)) # This prints the actual message from Google
        
        if "429" in str(e):
            st.info("💡 Suggestion: You've hit the 'Free Tier' limit. Wait 60 seconds.")
        elif "403" in str(e) or "PermissionDenied" in str(e):
            st.info("💡 Suggestion: Your API Key is invalid or restricted. Check Google AI Studio.")
        elif "400" in str(e):
            st.info("💡 Suggestion: The prompt or region might be unsupported.")
