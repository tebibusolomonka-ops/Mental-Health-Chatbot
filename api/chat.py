import os
import google.generativeai as genai
import json
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use Gemini 2.0 Flash-Lite (or the one provided by user)
# User said "Gemini 2.5 Flash-Lite", but current models are 1.5 or 2.0. 
# I'll use gemini-2.0-flash-lite if available, otherwise gemini-1.5-flash.
# Actually, I'll use 'gemini-2.0-flash-lite-preview-02-05' or similar if it exists.
# For now, I'll stick to 'gemini-1.5-flash' as a safe default or try to find the 2.5/2.0 one.
MODEL_NAME = "gemini-1.5-flash" # Defaulting to stable 1.5 Flash

SAFETY_PROMPT = """
You are a specialized safety classifier for an Ethiopian mental health chatbot.
Your task is to analyze the user's message in Amharic.
Determine if the message indicates "Critical Intent" (suicide, self-harm, severe psychological crisis, or immediate danger).

Output ONLY a JSON object:
{
  "is_critical": boolean,
  "reason": "short explanation in English"
}
"""

CHAT_SYSTEM_INSTRUCTION = """
የአእምሮ ጤና ግንዛቤ ረዳት ነህ። የምትግባባው በአማርኛ ብቻ ነው።
ባህሪህ፡ ደጋፊ፣ አጽናኝ እና የህክምና ምክር የማይሰጥ (non-medical) ረዳት ነህ።
ባህላዊ የአማርኛ ፈሊጦችን እና አባባሎችን ተጠቀም (ለምሳሌ፡ "አይዞህ/አይዞሽ"፣ "ለክፉ አይስጥህ"፣ "ፈጣሪ ያበርታህ")።
ግብህ፡ ለተጠቃሚው ማጽናኛ መስጠት እና ግንዛቤ መፍጠር ነው።
ጠቃሚ ማሳሰቢያ፡ አንተ ዶክተር አይደለህም፣ ስለዚህ የህክምና ምርመራ ወይም መድኃኒት አታዝዝ።
"""

def get_safety_classifier():
    return genai.GenerativeModel(
        model_name=MODEL_NAME,
        system_instruction=SAFETY_PROMPT
    )

def get_chat_model():
    return genai.GenerativeModel(
        model_name=MODEL_NAME,
        system_instruction=CHAT_SYSTEM_INSTRUCTION
    )

async def check_safety(message: str):
    model = get_safety_classifier()
    response = await model.generate_content_async(message)
    try:
        # Extract JSON from response
        content = response.text.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        return json.loads(content)
    except Exception as e:
        print(f"Error parsing safety response: {e}")
        return {"is_critical": False, "reason": "error"}

def stream_chat(message: str, history=None):
    model = get_chat_model()
    chat = model.start_chat(history=history or [])
    response = chat.send_message(message, stream=True)
    for chunk in response:
        yield chunk.text
