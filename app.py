import os
import google.generativeai as genai

# अपनी API की सेटिंग्स यहाँ करें
genai.configure(api_key="YOUR_API_KEY")

# मॉडल का नाम यहाँ अपडेट किया गया है ताकि 404 Error न आए
generation_config = {
  "temperature": 0.7,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
}

model = genai.GenerativeModel(
  model_name="models/gemini-3.8-flash", #[span_1](start_span)[span_1](end_span) यहाँ नया मॉडल सेट किया गया है
  generation_config=generation_config,
)

# ऑडियो ड्रामा स्क्रिप्ट या प्रॉम्प्ट जनरेट करने का फंक्शन
def generate_audio_script(prompt_text):
    try:
        response = model.generate_content(prompt_text)
        return response.text
    except Exception as e:
        return f"Error occurred: {str(e)}"

# उदाहरण के लिए प्रॉम्प्ट:
audio_concept = """
क्या ध्रुव अपनी मंगेतर लारा की शर्त मानेगा? 
आखिर क्या वजह है कि ध्रुव की शक्तियां पिछले 3 सालों से आगे नहीं बढ़ पा रही थीं? 
कैसे लड़ेगा ध्रुव अपने से शक्तिशाली लारा से?
"""

if __name__ == "__main__":
    script_output = generate_audio_script(audio_concept)
    print(script_output)
    
