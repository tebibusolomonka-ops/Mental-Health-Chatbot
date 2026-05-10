import os
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_TELEGRAM_ID")

def send_admin_alert(user_name, phone_number, message_content):
    if not ADMIN_ID:
        print("ADMIN_TELEGRAM_ID not set")
        return False
    
    alert_text = (
        "🚨 **CRITICAL SAFETY ALERT** 🚨\n\n"
        f"👤 **User:** {user_name}\n"
        f"📞 **Phone:** {phone_number}\n"
        f"💬 **Message:** {message_content}\n\n"
        "Please intervene immediately."
    )
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": ADMIN_ID,
        "text": alert_text,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload)
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending telegram alert: {e}")
        return False
