import os
import google.generativeai as genai
from PIL import Image
import io
import json

# Inasoma Key kisiri kutoka kwenye Environment Variables za Koyeb
API_KEY = os.environ.get("GEMINI_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)

def analyze_nameplate(image_bytes):
    try:
        if not API_KEY:
            return {"error": "API Key haijapatikana kule Koyeb!"}

        # Tunatumia model ya flash kwa sababu ina uwezo mkubwa wa kusoma picha
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Geuza bytes kuwa picha
        img = Image.open(io.BytesIO(image_bytes))
        
        prompt = """
        Wewe ni mtaalamu wa kusoma nameplates za mitambo ya ujenzi (CAT, Komatsu, Volvo, nk).
        Soma picha hii na utoe taarifa zifuatazo kwa mfumo wa JSON pekee:
        {
          "brand": "Jina la kampuni (Mfano: CAT)",
          "model": "Model ya mtambo (Mfano: 336D)",
          "serial": "Serial Number au PIN"
        }
        Kama huoni taarifa yoyote, weka "N/A". Usitoe maneno mengine, toa JSON pekee.
        """
        
        response = model.generate_content([prompt, img])
        
        # Safisha jibu la AI ili kupata JSON safi
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
        
    except Exception as e:
        return {"error": str(e)}
