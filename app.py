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
                # Capture current trade analysis time stamp
                analysis_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Convert uploaded image to base64
                buffered = io.BytesIO()
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                img.save(buffered, format="JPEG")
                base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')

                prompt = f"""
                You are a professional binary options trader. Analyze this chart.
                Look at the trend, RSI, and candlesticks. 
                The analysis timestamp is {analysis_time}.
                Output ONLY valid JSON matching this exact structure:
                {{
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
                        ai_output = result['choices'][0]['message']['content']
                        st.write("### AI Decision & Trade Time:")
                        st.code(ai_output)
                    else:
                        st.error(f"Unexpected API Response: {result}")
                else:
                    st.error(f"API Error ({response.status_code}): {response.text}")

            except Exception as e:
                st.error(f"Analysis failed: {e}")
