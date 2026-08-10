import streamlit as st
import requests
import base64
import json

# --- SETTINGS ---
API_KEY = "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"
MODEL = "openai/gpt-4o"
PASSWORD = "Shawkatdeveloper"

st.set_page_config(page_title="Quotex AI Predictor", layout="wide")

# --- UI STYLING ---
st.markdown("""
<style>
    .reportview-container { background: #0e1117; }
    .stMetric { background: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 10px; }
    .call-box { background: #052e16; border: 2px solid #22c55e; color: #4ade80; padding: 20px; border-radius: 15px; text-align: center; }
    .put-box { background: #450a0a; border: 2px solid #ef4444; color: #f87171; padding: 20px; border-radius: 15px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- LOGIN ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Secure Login")
    user_pwd = st.text_input("Enter Password", type="password")
    if st.button("Login"):
        if user_pwd == PASSWORD:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Wrong Password")
    st.stop()

# --- APP LOGIC ---
def get_analysis(img_b64):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    
    prompt = "Analyze this Quotex chart. Identify Asset and Indicators. Determine if next candle is CALL or PUT. Target entry is 58th second of current minute. Return JSON: {'asset': 'NAME', 'signal': 'CALL/PUT', 'time': 'HH:MM:58', 'reason': 'WHY', 'confidence': '90%'}"
    
    payload = {
        "model": MODEL,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
            ]
        }],
        "response_format": {"type": "json_object"}
    }
    
    try:
        r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        return r.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"ERROR: {str(e)}"

# --- MAIN UI ---
st.title("📈 Quotex Vision Analyzer")

col1, col2 = st.columns(2)

with col1:
    file = st.file_uploader("Upload Chart Screenshot", type=["jpg", "png", "jpeg"])
    if file:
        st.image(file, caption="Chart Uploaded")
        if st.button("🚀 PREDICT NEXT MINUTE"):
            with st.spinner("AI analyzing market..."):
                b64 = base64.b64encode(file.getvalue()).decode()
                res = get_analysis(b64)
                if "ERROR" in res:
                    st.error(res)
                else:
                    st.session_state.last_res = res

with col2:
    if 'last_res' in st.session_state:
        data = json.loads(st.session_state.last_res)
        
        st.metric("Asset", data.get("asset"))
        st.metric("Confidence", data.get("confidence"))
        
        sig = data.get("signal", "CALL")
        style = "call-box" if sig == "CALL" else "put-box"
        
        st.markdown(f"""<div class="{style}">
            <h1>{sig}</h1>
            <h2>ENTRY AT: {data.get('time')}</h2>
        </div>""", unsafe_allow_html=True)
        
        st.write(f"**Reasoning:** {data.get('reason')}")
