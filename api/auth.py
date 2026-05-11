import hmac
import hashlib
import time
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def verify_telegram_data(data: dict) -> bool:
    try:
        if not BOT_TOKEN:
            return False
        if "hash" not in data:
            return False
        
        received_hash = data.pop("hash")
        keys = sorted(data.keys())
        data_check_string = "\n".join([f"{k}={data[k]}" for k in keys])
        
        secret_key = hashlib.sha256(BOT_TOKEN.encode()).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        
        return calculated_hash == received_hash
    except:
        return False

def verify_webapp_data(init_data: str) -> bool:
    try:
        if not BOT_TOKEN:
            print("AUTH ERROR: BOT_TOKEN is missing")
            return False
            
        from urllib.parse import parse_qsl
        params = dict(parse_qsl(init_data))
        if "hash" not in params:
            return False
        
        received_hash = params.pop("hash")
        keys = sorted(params.keys())
        data_check_string = "\n".join([f"{k}={params[k]}" for k in keys])
        
        # Proper Telegram WebApp hashing
        secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        
        return calculated_hash == received_hash
    except Exception as e:
        print(f"AUTH ERROR: {e}")
        return False
