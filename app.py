def get_analysis(img_b64):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = "Analyze this Quotex chart. Return JSON: {'asset': 'NAME', 'signal': 'CALL/PUT', 'time': 'HH:MM:58', 'reason': 'WHY', 'confidence': '90%'}"
    
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
        response_data = r.json()
        
        # This part checks if the API actually worked
        if "choices" in response_data:
            return response_data['choices'][0]['message']['content']
        else:
            # This will show you the ACTUAL error from OpenRouter
            error_info = response_data.get("error", {}).get("message", "Unknown API Error")
            return f"API_ERROR: {error_info}"
            
    except Exception as e:
        return f"ERROR: {str(e)}"
