hereimport os
from openai import OpenAI
from PIL import Image
import io
import json
import base64

# Inasoma Key kutoka kwenye Environment Variables za Koyeb (Hakikisha umeita 'OPENAI_API_KEY')
API_KEY = os.environ.get("OPENAI_API_KEY")

# Anzisha client ya OpenAI
client = None
if API_KEY:
    client = OpenAI(api_key=API_KEY)

def encode_image(image_bytes):
    """Geuza picha kuwa base64 kwa ajili ya OpenAI"""
    return base64.b64encode(image_bytes).decode('utf-8')

def analyze_nameplate(image_bytes):
    try:
        if not API_KEY or client is None:
            return {"error": "OpenAI API Key haijapatikana kule Koyeb!"}

        # Geuza picha kuwa base64 string
        base64_image = encode_image(image_bytes)
        
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
        
        # Tunatumia gpt-4o-mini kwa sababu ina uwezo wa picha na ni rahisi zaidi (cheaper)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        },
                    ],
                }
            ],
            response_format={"type": "json_object"} # Hii inahakikisha jibu linakuja kama JSON
        )
        
        # Pata jibu na ugeuze kuwa dictionary ya Python
        result_text = response.choices[0].message.content
        return json.loads(result_text)
        
    except Exception as e:
        return {"error": f"Hitilafu: {str(e)}"}
