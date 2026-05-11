from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
from .auth import verify_telegram_data, verify_webapp_data
from .chat import check_safety, stream_chat
from .db import db
from .alerts import send_admin_alert
from firebase_admin import firestore
import json
import asyncio
import traceback

app = FastAPI()

CRITICAL_RESPONSE_AMHARIC = """
አዝናለሁ፣ በጣም እንደተቸገሩ ይሰማኛል። እባክዎን የእርዳታ መስመር በ 822 (የኢትዮጵያ ቀይ መስቀል ማህበር) ይደውሉ። 
ህይወትዎ ዋጋ አለው፣ ብቻዎን አይደሉም።
"""

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/auth/telegram-miniapp")
async def telegram_miniapp_auth(request: Request):
    try:
        data = await request.json()
        init_data = data.get("initData")
        
        if not init_data:
            raise HTTPException(status_code=400, detail="Missing initData")

        if not verify_webapp_data(init_data):
            raise HTTPException(status_code=401, detail="Invalid Telegram signature. Please check your BOT_TOKEN on Vercel.")
        
        from urllib.parse import parse_qsl
        params = dict(parse_qsl(init_data))
        user_json = json.loads(params.get("user", "{}"))
        user_id = str(user_json.get("id"))
        
        if not user_id or user_id == "None":
            raise HTTPException(status_code=400, detail="Invalid User ID in Telegram data")

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
                # Don't crash if firestore fails, just proceed
        
        return {"status": "success", "user_id": user_id, "has_phone": has_phone}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        # This will return the ACTUAL error message to the screen so we can see it
        error_detail = f"SERVER CRASH: {str(e)}\n{traceback.format_exc()}"
        print(error_detail)
        raise HTTPException(status_code=500, detail=error_detail)

@app.post("/api/chat")
async def chat_endpoint(request: Request):
    try:
        data = await request.json()
        message = data.get("message")
        user_id = data.get("user_id")
        
        if not message:
            raise HTTPException(status_code=400, detail="Missing message")
        
        # 1. Safety Check
        safety_result = await check_safety(message)
        
        if safety_result.get("is_critical"):
            user_name = "User"
            phone_number = "Not provided"
            
            if db and user_id and user_id != "guest_user":
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
                try:
                    db.collection("alerts").add({
                        "user_id": user_id,
                        "message": message,
                        "reason": safety_result.get("reason"),
                        "created_at": firestore.SERVER_TIMESTAMP
                    })
                except:
                    pass
            
            return {"response": CRITICAL_RESPONSE_AMHARIC, "is_critical": True}
        
        # 2. Regular Chat
        def generate():
            for chunk in stream_chat(message):
                yield chunk
                
        return StreamingResponse(generate(), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
