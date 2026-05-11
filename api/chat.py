import os
from google import genai
from google.genai import types
import json
from dotenv import load_dotenv

load_dotenv()

# Initialize the new Google GenAI Client
def get_client():
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("WARNING: GEMINI_API_KEY is missing")
            return None
        return genai.Client(api_key=api_key)
    except Exception as e:
        print(f"FAILED TO INITIALIZE GENAI CLIENT: {e}")
        return None

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

async def check_safety(message: str):
    client = get_client()
    if not client:
        return {"is_critical": False, "reason": "client_init_failed"}
    
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=message,
            config=types.GenerateContentConfig(
                system_instruction=SAFETY_PROMPT,
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Error in safety check: {e}")
        return {"is_critical": False, "reason": str(e)}

def stream_chat(message: str, history=None):
    client = get_client()
    if not client:
        yield "ይቅርታ፣ የ AI አገልግሎት ለጊዜው አልተገኘም። እባክዎን ቆይተው ይሞክሩ።"
        return

    try:
        # Convert history to new format if needed
        # New SDK uses list of Content objects
        
        response = client.models.generate_content_stream(
            model=MODEL_NAME,
            contents=message,
            config=types.GenerateContentConfig(
                system_instruction=CHAT_SYSTEM_INSTRUCTION
            )
        )
        
        for chunk in response:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        print(f"Chat streaming error: {e}")
        yield f"AI Error: {str(e)}"
