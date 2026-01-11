import os
import google.generativeai as genai
from PIL import Image
import io
import json

# 1. Inasoma Key kutoka Koyeb (Hakikisha umeongeza GEMINI_KEY kwenye dashboard ya Koyeb)
API_KEY = os.environ.get("GEMINI_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)

def analyze_nameplate(image_bytes):
    """Inasoma picha ya nameplate na kurudisha JSON"""
    try:
        if not API_KEY:
            return {"error": "Tafadhali weka GEMINI_KEY kule Koyeb!"}

        # Tunatumia model ya flash kwa sababu ni ya bure na ina uwezo wa picha
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Geuza bytes kuwa picha
        img = Image.open(io.BytesIO(image_bytes))
        
        prompt = """
        Wewe ni mtaalamu wa kusoma nameplates za mitambo ya ujenzi.
        Soma picha hii na utoe taarifa zifuatazo kwa mfumo wa JSON pekee:
        {
          "brand": "Jina la kampuni",
          "model": "Model ya mtambo",
          "serial": "Serial Number"
        }
        Kama huoni taarifa, weka "N/A". Toa JSON pekee bila maneno mengine.
        """
        
        response = model.generate_content([prompt, img])
        
        # Safisha jibu ili kupata JSON safi
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
        
    except Exception as e:
        return {"error": f"Hitilafu ya Picha: {str(e)}"}

def get_ai_response(prompt):
    """Hii ni kwa ajili ya Chat ya msaidizi (Electrical/Diagnosis) ili kuzuia 'undefined'"""
    try:
        if not API_KEY:
            return "Hitilafu: GEMINI_KEY haijapatikana kule Koyeb."
            
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Tunatoa maelekezo ya jinsi AI inavyopaswa kuwa
        full_prompt = f"Wewe ni mtaalamu wa mitambo ya ujenzi (CAT, Komatsu, Volvo). Jibu swali hili kwa ufasaha: {prompt}"
        
        response = model.generate_content(full_prompt)
        return response.text
        
    except Exception as e:
        return f"Hitilafu ya Chat: {str(e)}"
