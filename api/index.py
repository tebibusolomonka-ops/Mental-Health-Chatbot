from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
from .auth import verify_telegram_data, verify_webapp_data
from .chat import check_safety, stream_chat
from .db import db
from .alerts import send_admin_alert
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
    
    # Store or update user in Firestore
    user_id = str(data.get("id"))
    user_ref = db.collection("users").document(user_id)
    user_ref.set({
        "telegram_id": data.get("id"),
        "first_name": data.get("first_name"),
        "last_name": data.get("last_name"),
        "username": data.get("username"),
        "phone_number": data.get("phone_number"), # MUST use request_access="phone" in widget
        "photo_url": data.get("photo_url"),
        "last_login": firestore.SERVER_TIMESTAMP
    }, merge=True)
    
    return {"status": "success", "user_id": user_id}

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
    
    # Check if user exists and has phone
    user_doc = db.collection("users").document(user_id).get()
    has_phone = False
    if user_doc.exists:
        has_phone = "phone_number" in user_doc.to_dict()
    else:
        # Create user profile
        db.collection("users").document(user_id).set({
            "telegram_id": user_json.get("id"),
            "first_name": user_json.get("first_name"),
            "last_name": user_json.get("last_name"),
            "username": user_json.get("username"),
            "created_at": firestore.SERVER_TIMESTAMP
        })
    
    return {"status": "success", "user_id": user_id, "has_phone": has_phone}

@app.post("/api/auth/save-phone")
async def save_phone(request: Request):
    data = await request.json()
    user_id = str(data.get("user_id"))
    contact = data.get("contact", {})
    phone_number = contact.get("phone_number")
    
    if not phone_number:
        raise HTTPException(status_code=400, detail="No phone number provided")
        
    db.collection("users").document(user_id).update({
        "phone_number": phone_number,
        "updated_at": firestore.SERVER_TIMESTAMP
    })
    
    return {"status": "success"}

@app.post("/api/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    message = data.get("message")
    user_id = data.get("user_id")
    
    if not message or not user_id:
        raise HTTPException(status_code=400, detail="Missing message or user_id")
    
    # 1. Safety Check
    safety_result = await check_safety(message)
    
    if safety_result.get("is_critical"):
        # Fetch user info for alert
        user_doc = db.collection("users").document(str(user_id)).get()
        user_data = user_doc.to_dict() if user_doc.exists else {}
        user_name = user_data.get("first_name", "Unknown")
        phone_number = user_data.get("phone_number", "Not provided")
        
        # Trigger Admin Alert
        send_admin_alert(user_name, phone_number, message)
        
        # Store alert in DB
        db.collection("alerts").add({
            "user_id": user_id,
            "message": message,
            "reason": safety_result.get("reason"),
            "created_at": firestore.SERVER_TIMESTAMP
        })
        
        # Return hard-coded hotline message
        return {"response": CRITICAL_RESPONSE_AMHARIC, "is_critical": True}
    
    # 2. Regular Chat (Streaming)
    def generate():
        for chunk in stream_chat(message):
            yield chunk
            
    return StreamingResponse(generate(), media_type="text/event-stream")

# Add a fake firestore for types if needed or just import it
from firebase_admin import firestore
