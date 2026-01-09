import os
import google.generativeai as genai

# Hii amri inachukua Key kisiri kutoka kule Koyeb
API_KEY = os.environ.get("GEMINI_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    # Hii itatokea kama ukisahau kubandika kule Koyeb
    print("Onyo: GEMINI_KEY haijapatikana!")

def ask_expert(query, category):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        # Tunampa AI maelekezo kulingana na sehemu aliyopo mtumiaji
        full_prompt = f"Wewe ni mtaalamu wa {category}. Jibu hili kwa Kiswahili: {query}"
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Msaidizi wa AI amepata hitilafu: {str(e)}"
