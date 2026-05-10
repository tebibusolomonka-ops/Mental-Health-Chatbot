import hmac
import hashlib
import time
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def verify_telegram_data(data: dict) -> bool:
    """
    Verifies the data received from the Telegram Login Widget.
    """
    if "hash" not in data:
        return False
    
    received_hash = data.pop("hash")
    
    # Check if the data is recent (e.g., within 24 hours)
    auth_date = int(data.get("auth_date", 0))
    if time.time() - auth_date > 86400:
        return False
    
    # Create the data-check-string
    # Keys should be sorted alphabetically
    keys = sorted(data.keys())
    data_check_string = "\n".join([f"{k}={data[k]}" for k in keys])
    
    # Calculate the secret key: SHA256 of the bot token
    secret_key = hashlib.sha256(BOT_TOKEN.encode()).digest()
    
    # Calculate the HMAC-SHA256 signature
    calculated_hash = hmac.new(
        secret_key, 
        data_check_string.encode(), 
        hashlib.sha256
    ).hexdigest()
    
    return calculated_hash == received_hash

def verify_webapp_data(init_data: str) -> bool:
    """
    Verifies data from Telegram WebApp (initData).
    """
    try:
        from urllib.parse import parse_qsl
        params = dict(parse_qsl(init_data))
        if "hash" not in params:
            return False
        
        received_hash = params.pop("hash")
        
        # Sort keys
        keys = sorted(params.keys())
        data_check_string = "\n".join([f"{k}={params[k]}" for k in keys])
        
        # Secret key
        import hmac
        import hashlib
        secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        
        return calculated_hash == received_hash
    except Exception:
        return False
