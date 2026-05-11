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

# Use the flash-latest version which has a higher free tier quota
MODEL_NAMES = ["gemini-flash-latest", "gemini-2.0-flash-lite", "gemini-2.0-flash", "gemini-pro-latest"]

SAFETY_PROMPT = """
You are a specialized safety classifier for an Ethiopian mental health chatbot.
Output ONLY a JSON object: {"is_critical": boolean, "reason": "string"}
"""

CHAT_SYSTEM_INSTRUCTION = """
የአእምሮ ጤና ግንዛቤ ረዳት ነህ። የምትግባባው በአማርኛ ብቻ ነው።
ባህሪህ፡ ደጋፊ፣ አጽናኝ እና የህክምና ምክር የማይሰጥ (non-medical) ረዳት ነህ።
"""

async def check_safety(message: str):
    if message.lower() == "list models":
        return {"is_critical": False, "reason": "debug"}
        
    client = get_client()
    if not client:
        return {"is_critical": False, "reason": "no_client"}
    
    # Try models until one works
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
                continue # Try next model
            return {"is_critical": False, "reason": str(e)}
    return {"is_critical": False, "reason": "all_models_failed"}

def stream_chat(message: str, history=None):
    client = get_client()
    if not client:
        yield "AI Client Error"
        return

    if message.lower() == "list models":
        try:
            model_list = [m.name for m in client.models.list()]
            yield f"Supported models for your key: {', '.join(model_list)}"
            return
        except Exception as e:
            yield f"Diagnostic Error: {str(e)}"
            return

    # Try models until one works
    last_error = ""
    for model_name in MODEL_NAMES:
        try:
            response = client.models.generate_content_stream(
                model=model_name,
                contents=message,
                config=types.GenerateContentConfig(
                    system_instruction=CHAT_SYSTEM_INSTRUCTION
                )
            )
            for chunk in response:
                if chunk.text:
                    yield chunk.text
            return # Success!
        except Exception as e:
            last_error = str(e)
            if "404" in last_error:
                continue
            break
            
    yield f"AI Error after trying all models: {last_error}"
