import streamlit as st
import json
import requests
from PIL import Image
import io
import base64
from datetime import datetime

# 1. Page Setup
st.set_page_config(page_title="Quotex Vision Analyzer", layout="wide")
st.title("👁️ Quotex Vision Analyzer")

# 2. OpenRouter Configuration
try:
    API_KEY = st.secrets["OPENROUTER_API_KEY"]
except Exception as e:
    st.error("Error: Please add OPENROUTER_API_KEY to your Streamlit Cloud Secrets!")
    st.stop()

# 3. User Interface
uploaded_file = st.file_uploader("Upload Quotex Chart Screenshot", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="Chart Preview", use_container_width=True)

    if st.button("Analyze Chart"):
        with st.spinner("AI is analyzing indicators..."):
            try:
                analysis_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                buffered = io.BytesIO()
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                img.save(buffered, format="JPEG")
                base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')

                prompt = f"""
                You are a professional binary options trader. Analyze this chart screenshot.
                Look at the currency pair / asset name, current live price shown on the chart, trend, and candlesticks.
                The analysis time is {analysis_time}.
                Output ONLY a valid JSON object with no markdown ticks, formatted like this:
                {{
                  "asset": "Name of asset visible on chart, e.g., EUR/AUD (OTC)",
                  "live_price": "Current price visible on the chart",
                  "trade_time": "{analysis_time}",
                  "signal": "CALL" or "PUT",
                  "reason": "detailed explanation why"
                }}
                """

                response = requests.post(
                  url="https://openrouter.ai/api/v1/chat/completions",
                  headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "HTTP-Referer": "", 
                    "X-OpenRouter-Title": "Chart Analyzer", 
                  },
                  data=json.dumps({
                    "model": "openai/gpt-4o",
                    "max_tokens": 300,
                    "messages": [
                      {
                        "role": "user",
                        "content": [
                          {
                            "type": "text",
                            "text": prompt
                          },
                          {
                            "type": "image_url",
                            "image_url": {
                              "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                          }
                        ]
                      }
                    ]
                  }),
                  timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if "choices" in result and len(result["choices"]) > 0:
                        raw_content = result['choices'][0]['message']['content'].strip()
                        
                        # Clean markdown code blocks if the model accidentally includes them
                        if raw_content.startswith("```"):
                            raw_content = raw_content.split("```")[1]
                            if raw_content.startswith("json"):
                                raw_content = raw_content[4:].strip()
                        if raw_content.endswith("```"):
                            raw_content = raw_content[:-3].strip()

                        data = json.loads(raw_content)
                        
                        # Render styled visual cards
                        st.markdown("### 📊 AI Trading Signal & Analysis")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric(label="Asset", value=data.get("asset", "N/A"))
                        with col2:
                            st.metric(label="Live Price", value=data.get("live_price", "N/A"))
                        with col3:
                            st.metric(label="Trade Time", value=data.get("trade_time", analysis_time))
                        
                        signal = data.get("signal", "NEUTRAL").upper()
                        if signal == "CALL":
                            st.success(f"**SIGNAL: CALL (UP)**")
                        elif signal == "PUT":
                            st.error(f"**SIGNAL: PUT (DOWN)**")
                        else:
                            st.warning(f"**SIGNAL: {signal}**")
                            
                        st.info(f"**Reasoning:** {data.get('reason', 'No reason provided.')}")
                        
                    else:
                        st.error(f"Unexpected API Response: {result}")
                else:
                    st.error(f"API Error ({response.status_code}): {response.text}")

            except Exception as e:
                st.error(f"Analysis failed: {e}")
