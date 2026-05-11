import os
import google.generativeai as genai
import json
from dotenv import load_dotenv

load_dotenv()

# Safely configure genai
try:
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
    else:
        print("WARNING: GEMINI_API_KEY is missing from environment")
except Exception as e:
    print(f"FAILED TO CONFIGURE GEMINI: {e}")

MODEL_NAME = "gemini-1.5-flash"

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
    try:
        return genai.GenerativeModel(
            model_name=MODEL_NAME,
            system_instruction=SAFETY_PROMPT
        )
    except Exception as e:
        print(f"Error creating safety model: {e}")
        return None

def get_chat_model():
    try:
        return genai.GenerativeModel(
            model_name=MODEL_NAME,
            system_instruction=CHAT_SYSTEM_INSTRUCTION
        )
    except Exception as e:
        print(f"Error creating chat model: {e}")
        return None

async def check_safety(message: str):
    model = get_safety_classifier()
    if not model:
        return {"is_critical": False, "reason": "model_init_failed"}
    
    try:
        response = await model.generate_content_async(message)
        content = response.text.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        return json.loads(content)
    except Exception as e:
        print(f"Error parsing safety response: {e}")
        return {"is_critical": False, "reason": "error"}

def stream_chat(message: str, history=None):
    model = get_chat_model()
    if not model:
        yield "ይቅርታ፣ የ AI አገልግሎት ለጊዜው አልተገኘም። እባክዎን ቆይተው ይሞክሩ።"
        return

    try:
        chat = model.start_chat(history=history or [])
        response = chat.send_message(message, stream=True)
        for chunk in response:
            yield chunk.text
    except Exception as e:
        print(f"Chat streaming error: {e}")
        yield "ይቅርታ፣ ውይይቱን መቀጠል አልቻልኩም።"
