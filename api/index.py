from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
from .auth import verify_telegram_data, verify_webapp_data
from .chat import check_safety, stream_chat
from .db import db
from .alerts import send_admin_alert
from firebase_admin import firestore
import json
import asyncio

app = FastAPI()

CRITICAL_RESPONSE_AMHARIC = """
አዝናለሁ፣ በጣም እንደተቸገሩ ይሰማኛል። እባክዎን የእርዳታ መስመር በ 822 (የኢትዮጵያ ቀይ መስቀል ማህበር) ይደውሉ። 
ህይወትዎ ዋጋ አለው፣ ብቻዎን አይደሉም።
"""

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/auth/telegram")
async def telegram_auth(request: Request):
    data = await request.json()
    if not verify_telegram_data(data.copy()):
        raise HTTPException(status_code=400, detail="Invalid Telegram signature")
    
    if db:
        user_id = str(data.get("id"))
        user_ref = db.collection("users").document(user_id)
        user_ref.set({
            "telegram_id": data.get("id"),
            "first_name": data.get("first_name"),
            "last_name": data.get("last_name"),
            "username": data.get("username"),
            "phone_number": data.get("phone_number"),
            "last_login": firestore.SERVER_TIMESTAMP
        }, merge=True)
        return {"status": "success", "user_id": user_id}
    return {"status": "success", "user_id": "local_user"}

@app.post("/api/auth/telegram-miniapp")
async def telegram_miniapp_auth(request: Request):
    data = await request.json()
    init_data = data.get("initData")
    if not verify_webapp_data(init_data):
        raise HTTPException(status_code=400, detail="Invalid WebApp signature")
    
    from urllib.parse import parse_qsl
    params = dict(parse_qsl(init_data))
    user_json = json.loads(params.get("user", "{}"))
    user_id = str(user_json.get("id"))
    
    has_phone = False
    if db:
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
    
    return {"status": "success", "user_id": user_id, "has_phone": has_phone}

@app.post("/api/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    message = data.get("message")
    user_id = data.get("user_id")
    
    if not message:
        raise HTTPException(status_code=400, detail="Missing message")
    
    # 1. Safety Check
    safety_result = await check_safety(message)
    
    if safety_result.get("is_critical"):
        user_name = "Guest"
        phone_number = "Not provided"
        
        if db and user_id != "guest_user":
            try:
                user_doc = db.collection("users").document(str(user_id)).get()
                if user_doc.exists:
                    udata = user_doc.to_dict()
                    user_name = udata.get("first_name", "Unknown")
                    phone_number = udata.get("phone_number", "Not provided")
            except:
                pass
        
        send_admin_alert(user_name, phone_number, message)
        
        if db:
            db.collection("alerts").add({
                "user_id": user_id,
                "message": message,
                "reason": safety_result.get("reason"),
                "created_at": firestore.SERVER_TIMESTAMP
            })
        
        return {"response": CRITICAL_RESPONSE_AMHARIC, "is_critical": True}
    
    # 2. Regular Chat
    def generate():
        for chunk in stream_chat(message):
            yield chunk
            
    return StreamingResponse(generate(), media_type="text/event-stream")
