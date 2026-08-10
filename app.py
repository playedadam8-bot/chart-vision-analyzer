import streamlit as st
import requests
import base64
import json

# --- CONFIGURATION ---
API_KEY = "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"
PASSWORD = "Shawkatdeveloper"

# List of models to try in order (Best -> Fastest -> Most Reliable)
MODELS_TO_TRY = [
    "openai/gpt-4o",
    "google/gemini-pro-1.5-vision",
    "google/gemini-flash-1.5",
    "anthropic/claude-3-haiku"
]

st.set_page_config(page_title="Quotex AI Multi-Vision", layout="wide")

# --- UI STYLING ---
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 10px; }
    .call-box { background: linear-gradient(135deg, #052e16 0%, #064e3b 100%); border: 2px solid #22c55e; color: #4ade80; padding: 25px; border-radius: 15px; text-align: center; box-shadow: 0 4px 15px rgba(34, 197, 94, 0.3); }
    .put-box { background: linear-gradient(135deg, #450a0a 0%, #7f1d1d 100%); border: 2px solid #ef4444; color: #f87171; padding: 25px; border-radius: 15px; text-align: center; box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3); }
</style>
""", unsafe_allow_html=True)

# --- LOGIN ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Secure Terminal Login")
    user_pwd = st.text_input("Enter Developer Password", type="password")
    if st.button("Access Terminal"):
        if user_pwd == PASSWORD:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Access Denied")
    st.stop()

# --- MULTI-AI LOGIC ---
def get_analysis_multi_ai(img_b64):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://quotex-vision.com" 
    }
    
    prompt = """Analyze this Quotex chart. Identify Asset, Trend and Indicators. 
    Predict if the NEXT candle is CALL or PUT. 
    Target entry exactly 2 seconds before the next minute (HH:MM:58).
    Return ONLY JSON: 
    {"asset": "NAME", "signal": "CALL/PUT", "time": "HH:MM:58", "reason": "WHY", "confidence": "90%", "model_used": "MODEL_NAME"}"""

    for model in MODELS_TO_TRY:
        try:
            st.toast(f"Trying AI: {model}...", icon="🤖")
            payload = {
                "model": model,
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                    ]
                }],
                "response_format": {"type": "json_object"}
            }
            
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=20)
            res_json = response.json()
            
            if "choices" in res_json:
                content = res_json['choices'][0]['message']['content']
                # Inject model name into the result for tracking
                data = json.loads(content)
                data['model_used'] = model
                return data
            else:
                st.warning(f"Model {model} failed. Trying next...")
                continue
                
        except Exception as e:
            continue
            
    return {"error": "All AI models are currently unavailable. Check OpenRouter balance or API key."}

# --- MAIN UI ---
st.title("📈 Quotex Vision Analyzer & Next-Minute Predictor")
st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📸 Market Capture")
    file = st.file_uploader("Upload Screenshot", type=["jpg", "png", "jpeg"])
    if file:
        st.image(file, use_container_width=True)
        if st.button("🚀 EXECUTE AI ANALYSIS", use_container_width=True):
            with st.spinner("AI Processing (Multi-Model Fail-safe)..."):
                b64 = base64.b64encode(file.getvalue()).decode()
                result = get_analysis_multi_ai(b64)
                st.session_state.last_prediction = result

with col2:
    st.subheader("📊 Prediction Terminal")
    if 'last_prediction' in st.session_state:
        data = st.session_state.last_prediction
        
        if "error" in data:
            st.error(data["error"])
        else:
            # Metrics
            m1, m2 = st.columns(2)
            m1.metric("Asset", data.get("asset"))
            m2.metric("Confidence", data.get("confidence"))
            
            # Signal Display
            sig = data.get("signal", "CALL").upper()
            box_style = "call-box" if "CALL" in sig else "put-box"
            
            st.markdown(f"""
                <div class="{box_style}">
                    <h1 style='margin:0;'>{sig}</h1>
                    <h2 style='margin:0;'>ENTRY: {data.get('time')}</h2>
                    <p style='margin-top:10px;'><b>AI Engine:</b> {data.get('model_used')}</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Reasoning
            with st.expander("Technical Strategy Details", expanded=True):
                st.write(data.get("reason"))
