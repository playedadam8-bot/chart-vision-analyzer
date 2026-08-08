import streamlit as st
import json
import requests
from PIL import Image
import io
import base64

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
        with st.spinner("AI is reading chart timestamp and analyzing indicators..."):
            try:
                buffered = io.BytesIO()
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                img.save(buffered, format="JPEG")
                base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')

                prompt = """
                You are a professional binary options trader. Look closely at this Quotex chart screenshot.
                Extract and analyze the following details directly from the image:
                1. asset: The currency pair or asset name shown (e.g., EUR/AUD (OTC)).
                2. live_price: The current price value displayed on the right edge.
                3. chart_time: The clock time visible inside the chart interface (e.g., 22:47:45 or the top/bottom timeline values).
                4. signal: Either "CALL" or "PUT".
                5. reason: Detailed technical analysis reasoning based on the trend, indicators, and candlesticks.

                Output ONLY a valid JSON object with no markdown ticks, formatted like this:
                {
                  "asset": "...",
                  "live_price": "...",
                  "chart_time": "...",
                  "signal": "CALL" or "PUT",
                  "reason": "..."
                }
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
                        
                        if raw_content.startswith("```"):
                            raw_content = raw_content.split("```")[1]
                            if raw_content.startswith("json"):
                                raw_content = raw_content[4:].strip()
                        if raw_content.endswith("```"):
                            raw_content = raw_content[:-3].strip()

                        data = json.loads(raw_content)
                        
                        st.markdown("### 📊 AI Trading Signal & Chart Time Analysis")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric(label="Asset", value=data.get("asset", "N/A"))
                        with col2:
                            st.metric(label="Live Price", value=data.get("live_price", "N/A"))
                        with col3:
                            st.metric(label="Chart Time", value=data.get("chart_time", "N/A"))
                        
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
