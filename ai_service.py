hereimport os
from groq import Groq
import google.generativeai as genai
from PIL import Image
import io
import json

# Pata Keys kutoka kwenye Environment Variables za Koyeb
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GEMINI_KEY = os.environ.get("GEMINI_KEY")

# Anzisha Client ya Groq kwa ajili ya Chat
groq_client = None
if GROQ_API_KEY:
    groq_client = Groq(api_key=GROQ_API_KEY)

# Anzisha Gemini kwa ajili ya Picha
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)

def analyze_nameplate(image_bytes):
    """Inasoma picha ya nameplate kwa kutumia Gemini (Bure)"""
    try:
        if not GEMINI_KEY:
            return {"error": "Tafadhali weka GEMINI_KEY kule Koyeb!"}

        model = genai.GenerativeModel('gemini-1.5-flash')
        img = Image.open(io.BytesIO(image_bytes))
        
        prompt = """
        Wewe ni mtaalamu wa mitambo. Soma picha hii na utoe JSON pekee:
        {
          "brand": "Jina la kampuni",
          "model": "Model ya mtambo",
          "serial": "Serial Number"
        }
        Kama huoni taarifa, weka 'N/A'.
        """
        
        response = model.generate_content([prompt, img])
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
        
    except Exception as e:
        return {"error": f"Hitilafu ya Picha (Gemini): {str(e)}"}

def get_ai_response(prompt):
    """Inajibu maswali ya Chat kwa kutumia Groq (Kasi zaidi na Bure)"""
    try:
        if not groq_client:
            return "Hitilafu: GROQ_API_KEY haijapatikana kule Koyeb."
            
        # Tunatumia Llama 3 kupitia Groq kwa majibu ya haraka sana
        completion = groq_client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "system", "content": "Wewe ni mtaalamu wa mitambo ya ujenzi (CAT, Komatsu, Volvo). Jibu kwa Kiswahili fasaha na kifupi."},
                {"role": "user", "content": prompt}
            ],
        )
        return completion.choices[0].message.content
        
    except Exception as e:
        return f"Hitilafu ya Chat (Groq): {str(e)}"
