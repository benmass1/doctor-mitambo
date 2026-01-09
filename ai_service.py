import requests
import os

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # weka Koyeb ENV
MODEL = "models/gemini-1.0-pro"

def analyze_text(prompt: str):
    url = f"https://generativelanguage.googleapis.com/v1/{MODEL}:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }

    res = requests.post(url, json=payload, timeout=30)
    res.raise_for_status()
    data = res.json()

    return data["candidates"][0]["content"]["parts"][0]["text"]
