import os
from google import genai
from google.genai import types
import json
from dotenv import load_dotenv

load_dotenv()

def get_client():
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return None
        return genai.Client(api_key=api_key)
    except Exception as e:
        print(f"FAILED TO INITIALIZE GENAI CLIENT: {e}")
        return None

# Preferred models based on your diagnostic results
MODEL_NAMES = ["gemini-flash-latest", "gemini-2.0-flash-lite", "gemini-2.0-flash", "gemini-pro-latest"]

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

async def check_safety(message: str):
    client = get_client()
    if not client:
        return {"is_critical": False, "reason": "no_client"}
    
    for model_name in MODEL_NAMES:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=message,
                config=types.GenerateContentConfig(
                    system_instruction=SAFETY_PROMPT,
                    response_mime_type="application/json"
                )
            )
            return json.loads(response.text)
        except Exception as e:
            if "404" in str(e):
                continue
            return {"is_critical": False, "reason": str(e)}
    return {"is_critical": False, "reason": "failed"}

def stream_chat(message: str, user_name: str = "ተጠቃሚ", history=None):
    client = get_client()
    if not client:
        yield "ይቅርታ፣ አገልግሎቱ ለጊዜው ተቋርጧል።"
        return

    personalized_instruction = CHAT_SYSTEM_INSTRUCTION + f"\nከተጠቃሚው ጋር ስታወራ ስሙን ጥቀስ። የተጠቃሚው ስም፡ {user_name} ነው።"

    for model_name in MODEL_NAMES:
        try:
            response = client.models.generate_content_stream(
                model=model_name,
                contents=message,
                config=types.GenerateContentConfig(
                    system_instruction=personalized_instruction
                )
            )
            for chunk in response:
                if chunk.text:
                    yield chunk.text
            return
        except Exception as e:
            if "404" in str(e):
                continue
            break
            
    yield "ይቅርታ፣ ውይይቱን መቀጠል አልቻልኩም። እባክዎን ቆይተው ይሞክሩ።"
