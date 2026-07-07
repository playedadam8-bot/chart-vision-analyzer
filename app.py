import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Page Setup
st.set_page_config(page_title="Quotex Vision Analyzer", layout="wide")
st.title("👁️ Quotex Vision Analyzer")

# 2. Gemini Configuration
# This looks for the label "GEMINI_API_KEY" in your Cloud Secrets
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("Error: Please add GEMINI_API_KEY to your Streamlit Cloud Secrets!")
    st.stop()

# 3. User Interface
uploaded_file = st.file_uploader("Upload Quotex Chart Screenshot", type=["jpg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="Chart Preview", use_container_width=True)

    if st.button("Analyze Chart"):
        with st.spinner("AI is analyzing indicators..."):
            prompt = """
            You are a professional trader. Analyze this chart.
            Look at the trend, RSI, and candlesticks. 
            Output ONLY this JSON format: {"signal": "CALL" or "PUT", "reason": "why"}
            """
            try:
                response = model.generate_content([prompt, img])
                st.write("### AI Decision:")
                st.code(response.text)
            except Exception as e:
                st.error(f"Analysis failed: {e}")
