def analyze_chart(image_b64):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8501", # Required by some OpenRouter models
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
    
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        res_json = response.json()
        
        # Check if "choices" exists in the response
        if "choices" in res_json:
            return res_json['choices'][0]['message']['content']
        else:
            # If there's an error, return the error message from the API
            error_msg = res_json.get("error", {}).get("message", "Unknown API Erro
