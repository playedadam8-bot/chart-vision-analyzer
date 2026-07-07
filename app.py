import streamlit as st
import google.generativeai as genai
from PIL import Image

# App Config
st.set_page_config(page_title="Quotex Vision Analyzer", layout="wide")
st.title("👁️ Quotex Vision Analyzer")

# Connect to Gemini
# Make sure you add GEMINI_API_KEY to Streamlit Secrets!
if "AQ.Ab8RN6JkdaIfTs9X0V9hDONuwJ4QDuT8BNRxGnF-MHi0prslVg" in st.secrets:
    genai.configure(api_key=st.secrets["AQ.Ab8RN6JkdaIfTs9X0V9hDONuwJ4QDuT8BNRxGnF-MHi0prslVg"])
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("AQ.Ab8RN6JkdaIfTs9X0V9hDONuwJ4QDuT8BNRxGnF-MHi0prslVg is missing in Secrets!")
    st.stop()

# Upload File
uploaded_file = st.file_uploader("Upload Quotex Chart Screenshot", type=["jpg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="Chart Preview", use_container_width=True)

    if st.button("Analyze Chart"):
        with st.spinner("AI is analyzing indicators and strategies..."):
            prompt = """
            You are a professional trader. Analyze this chart.
            Look at the candlesticks, trend, and indicators shown.
            Output your decision in this JSON format:
            {"signal": "CALL" or "PUT", "reason": "brief explanation of why"}
            """
            
            try:
                response = model.generate_content([prompt, img])
                st.write("### AI Analysis Result:")
                st.code(response.text)
            except Exception as e:
                st.error(f"Error: {e}")
