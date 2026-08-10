import streamlit as st
import requests
import base64
import json
from PIL import Image
from io import BytesIO

# --- CONFIGURATION ---
OPENROUTER_API_KEY = "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"
MODEL_NAME = "openai/gpt-4o"
APP_PASSWORD = "Shawkatdeveloper"

# --- PAGE SETUP ---
st.set_page_config(
    page_title="Quotex Vision Analyzer",
    page_icon="📈",
    layout="wide"
)

# --- CSS FOR HIGH-END UI ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #161b22; border-radius: 10px; padding: 15px; border: 1px solid #30363d; }
    .signal-card { padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 20px; font-family: sans-serif; }
    .call-bg { background-color: #052e16; border: 2px solid #22c55e; color: #4ade80; }
    .put-bg { background-color: #450a0a; border: 2px solid #ef4444; color: #f87171; }
    </style>
    """, unsafe_allow_html=True)

# --- AUTHENTICATION ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def login_page():
    st.title("🔐 Secure Terminal Login")
    with st.form("login"):
        pwd = st.text_input("Enter Developer Password", type="password")
        submit = st.form_submit_button("Access Terminal")
        if submit:
            if pwd == APP_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Access Denied")

# --- UTILITY FUNCTIONS ---
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

def analyze_chart(image_b64):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = """
    Analyze this Quotex chart. Identify Asset, Indicators, and Trend.
    Calculate the next-minute prediction. 
    Return strictly JSON:
    {
        "asset": "Name",
        "signal": "CALL" or "PUT",
        "confidence": "95%",
        "entry_time": "HH:MM:58",
        "reasoning": "Description",
        "indicators": "Analysis"
    }
    """
    
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}}
                ]
            }
        ],
        "response_format": {"type": "json_object"}
    }
    
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    return response.json()['choices'][0]['message']['content']

# --- MAIN APP ---
if not st.session_state.authenticated:
    login_page()
else:
    st.title("📈 Quotex Vision Analyzer")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        uploaded_file = st.file_uploader("Upload Chart", type=["jpg", "png", "jpeg"])
        if uploaded_file:
            st.image(uploaded_file, use_container_width=True)
            if st.button("🚀 Analyze Now"):
                with st.spinner("Processing..."):
                    img_b64 = encode_image(uploaded_file)
                    result = analyze_chart(img_b64)
                    st.session_state.analysis_result = result

    with col2:
        if 'analysis_result' in st.session_state:
            data = json.loads(st.session_state.analysis_result)
            
            st.metric("Target Asset", data['asset'])
            st.metric("Accuracy Confidence", data['confidence'])
            
            sig = data['signal']
            bg_class = "call-bg" if sig == "CALL" else "put-bg"
            
            st.markdown(f"""
                <div class="signal-card {bg_class}">
                    <h2>PREDICTION: {sig}</h2>
                    <h1>ENTRY AT: {data['entry_time']}</h1>
                </div>
            """, unsafe_allow_html=True)
            
            st.write(f"**Strategy:** {data['reasoning']}")
            st.info(f"**Indicators:** {data['indicators']}")
