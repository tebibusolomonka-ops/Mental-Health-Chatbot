import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
import base64
from dotenv import load_dotenv

load_dotenv()

def get_db():
    try:
        if not firebase_admin._apps:
            service_account_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON")
            
            if service_account_json:
                # Remove extra quotes if present
                if service_account_json.startswith("'") and service_account_json.endswith("'"):
                    service_account_json = service_account_json[1:-1]
                if service_account_json.startswith('"') and service_account_json.endswith('"'):
                    service_account_json = service_account_json[1:-1]
                
                try:
                    # Try direct JSON parsing
                    info = json.loads(service_account_json)
                    cred = credentials.Certificate(info)
                except Exception:
                    # Try base64 fallback
                    try:
                        decoded = base64.b64decode(service_account_json).decode("utf-8")
                        info = json.loads(decoded)
                        cred = credentials.Certificate(info)
                    except Exception as e:
                        print(f"Failed to parse Firebase JSON: {e}")
                        raise e
            else:
                # Local development fallback
                if os.path.exists("firebase-service-account.json"):
                    cred = credentials.Certificate("firebase-service-account.json")
                else:
                    raise ValueError("FIREBASE_SERVICE_ACCOUNT_JSON environment variable is missing")

            firebase_admin.initialize_app(cred)
        
        return firestore.client()
    except Exception as e:
        print(f"DATABASE INITIALIZATION ERROR: {e}")
        return None

db = get_db()
