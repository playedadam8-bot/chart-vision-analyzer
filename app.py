import streamlit as st
import json
import requests
from PIL import Image
import io
import base64

# 1. Page Setup
st.set_page_config(page_title="Quotex Vision Analyzer", layout="wide")
st.title("👁️ Quotex Vision Analyzer & Next-Minute Predictor")

# 2. OpenRouter Configuration with New API Key
API_KEY = "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"

# 3. User Interface
uploaded_file = st.file_uploader("Upload Quotex Chart Screenshot", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="Chart Preview", use_container_width=True)

    if st.button("Analyze & Get Next-Minute Signal"):
        with st.spinner("GPT-4o is analyzing candlesticks, indicators & calculating entry timing..."):
            try:
                buffered = io.BytesIO()
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                img.save(buffered, format="JPEG")
                base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')

                prompt = """
                You are an expert binary options algorithmic trader analyzing a Quotex trading chart screenshot.
                
                Tasks:
                1. Read the current timestamp/clock time shown on the chart interface.
                2. Identify the asset name and live price.
                3. Analyze the current trend, candlesticks, and any visible technical indicators.
                4. Calculate the precise entry target for the NEXT upcoming candle (target entry time exactly 2 seconds before the new minute starts, e.g., HH:MM:58).
                5. Provide your directional signal ("CALL" or "PUT") and technical reasoning.

                Output ONLY a valid JSON object with no markdown ticks, formatted exactly like this:
                {
                  "asset": "...",
                  "live_price": "...",
                  "chart_time": "...",
                  "next_trade_entry_time": "Exact target time to click trade (e.g., HH:MM:58)",
                  "signal": "CALL" or "PUT",
                  "reason": "Detailed technical explanation."
                }
                """

                response = requests.post(
                  url="https://openrouter.ai/api/v1/chat/completions",
                  headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "HTTP-Referer": "https://shawkat-tradez.streamlit.app", 
                    "X-OpenRouter-Title": "Quotex Vision Analyzer", 
                  },
                  data=json.dumps({
                    "model": "openai/gpt-4o",
                    "max_tokens": 400,
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
                        
                        st.markdown("### 🎯 Precision Next-Minute Trade Setup")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric(label="Asset", value=data.get("asset", "N/A"))
                            st.metric(label="Live Price", value=data.get("live_price", "N/A"))
                        with col2:
                            st.metric(label="Chart Time", value=data.get("chart_time", "N/A"))
                            st.metric(label="⚡ Precise Entry Target", value=data.get("next_trade_entry_time", "N/A"))
                        
                        signal = data.get("signal", "NEUTRAL").upper()
                        if signal == "CALL":
                            st.success(f"**SIGNAL: CALL (UP) — Enter 2s before candle close!**")
                        elif signal == "PUT":
                            st.error(f"**SIGNAL: PUT (DOWN) — Enter 2s before candle close!**")
                        else:
                            st.warning(f"**SIGNAL: {signal}**")
                            
                        st.info(f"**Indicator & Trend Reasoning:** {data.get('reason', 'No reason provided.')}")
                        
                    else:
                        st.error(f"Unexpected API Response: {result}")
                else:
                    st.error(f"API Error ({response.status_code}): {response.text}")

            except Exception as e:
                st.error(f"Analysis failed: {e}")
