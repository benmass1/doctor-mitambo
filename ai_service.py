hereimport os
from openai import OpenAI
from PIL import Image
import io
import json
import base64

# Hakikisha jina hili linafanana na Variable uliyoweka kwenye dashboard ya Koyeb
API_KEY = os.environ.get("OPENAI_API_KEY")

# Anzisha client ya OpenAI
client = None
if API_KEY:
    client = OpenAI(api_key=API_KEY)

def encode_image(image_bytes):
    """Geuza picha kuwa base64 kwa ajili ya OpenAI"""
    return base64.b64encode(image_bytes).decode('utf-8')

def analyze_nameplate(image_bytes):
    """Inasoma nameplate za mitambo kutumia picha"""
    try:
        if not client:
            return {"error": "OpenAI API Key haijapatikana kule Koyeb!"}

        base64_image = encode_image(image_bytes)
        
        prompt = """
        Soma picha hii na utoe taarifa zifuatazo kwa mfumo wa JSON pekee:
        {
          "brand": "Jina la kampuni",
          "model": "Model ya mtambo",
          "serial": "Serial Number"
        }
        Kama huoni taarifa, weka 'N/A'. Toa JSON pekee.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        },
                    ],
                }
            ],
            response_format={"type": "json_object"}
        )
        
        result_text = response.choices[0].message.content
        return json.loads(result_text)
        
    except Exception as e:
        return {"error": f"Hitilafu kwenye Picha: {str(e)}"}

def get_ai_response(prompt):
    """Hii ni kwa ajili ya Msaidizi wa Chat (Electrical/Diagnosis) ili kuzuia 'undefined'"""
    try:
        if not client:
            return "Hitilafu: API Key haijawekwa kwenye mfumo wa Koyeb."
            
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Wewe ni mtaalamu wa mitambo ya ujenzi."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Hitilafu kwenye Chat: {str(e)}"
