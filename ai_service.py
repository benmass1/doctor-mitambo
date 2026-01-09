import os
import requests

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = "models/gemini-1.0-pro"

def analyze_text(prompt: str) -> str:
    if not GEMINI_API_KEY:
        raise Exception("GEMINI_API_KEY haijawekwa kwenye Environment Variables")

    url = (
        "https://generativelanguage.googleapis.com/v1/"
        f"{MODEL}:generateContent?key={GEMINI_API_KEY}"
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            "Wewe ni DR-MITAMBO PRO AI. "
                            "Jibu kwa Kiswahili kwa mtindo wa fundi mtaalamu. "
                            f"Tatizo la mtambo: {prompt}"
                        )
                    }
                ]
            }
        ]
    }

    response = requests.post(url, json=payload, timeout=30)
    response.raise_for_status()

    data = response.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]
