from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
import json
import asyncio
import traceback

# Import our crash-proof modules
try:
    from .auth import verify_telegram_data, verify_webapp_data
    from .chat import check_safety, stream_chat
    from .db import db
    from .alerts import send_admin_alert
except Exception as e:
    print(f"IMPORT ERROR: {e}")
    # Define fallbacks so the app still runs
    db = None
    verify_webapp_data = lambda x: False
    check_safety = lambda x: {"is_critical": False}
    stream_chat = lambda x: ["Error: System failed to load."]

from firebase_admin import firestore

app = FastAPI()

@app.get("/api")
def api_root():
    return {"message": "API is Working"}

@app.get("/api/health")
def health_check():
    if db is None:
        return {
            "status": "warning",
            "database": "DEAD",
            "reason": "FIREBASE_SERVICE_ACCOUNT_JSON might be invalid or missing",
            "tip": "Check your Vercel Environment Variables"
        }
    return {
        "status": "ok",
        "database": "ALIVE"
    }

@app.post("/api/auth/telegram-miniapp")
async def telegram_miniapp_auth(request: Request):
    try:
        data = await request.json()
        init_data = data.get("initData")
        
        if not init_data:
            raise HTTPException(status_code=400, detail="Missing initData")

        if not verify_webapp_data(init_data):
            raise HTTPException(status_code=401, detail="Invalid Telegram signature")
        
        from urllib.parse import parse_qsl
        params = dict(parse_qsl(init_data))
        user_json = json.loads(params.get("user", "{}"))
        user_id = str(user_json.get("id"))
        
        has_phone = False
        if db:
            try:
                user_doc = db.collection("users").document(user_id).get()
                if user_doc.exists:
                    has_phone = "phone_number" in user_doc.to_dict()
                else:
                    db.collection("users").document(user_id).set({
                        "telegram_id": user_json.get("id"),
                        "first_name": user_json.get("first_name"),
                        "last_name": user_json.get("last_name"),
                        "username": user_json.get("username"),
                        "created_at": firestore.SERVER_TIMESTAMP
                    })
            except Exception as e:
                print(f"Firestore Error: {e}")
        else:
            print("Running in Guest Mode (No Database)")
        
        return {"status": "success", "user_id": user_id, "has_phone": has_phone}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat_endpoint(request: Request):
    try:
        data = await request.json()
        message = data.get("message")
        user_id = data.get("user_id")
        
        safety_result = await check_safety(message)
        
        if safety_result.get("is_critical"):
            return {"response": "Safety alert triggered.", "is_critical": True}
        
        def generate():
            for chunk in stream_chat(message):
                yield chunk
                
        return StreamingResponse(generate(), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
