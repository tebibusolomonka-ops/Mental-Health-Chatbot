import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
from dotenv import load_dotenv

load_dotenv()

def get_db():
    try:
        # Check if already initialized
        try:
            return firestore.client()
        except:
            pass

        cred_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON")
        if not cred_json:
            print("DATABASE ERROR: FIREBASE_SERVICE_ACCOUNT_JSON is missing")
            return None
        
        # Clean the JSON string
        cred_json = cred_json.strip()
        if cred_json.startswith("'") and cred_json.endswith("'"):
            cred_json = cred_json[1:-1]
        
        try:
            cred_dict = json.loads(cred_json)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            return firestore.client()
        except Exception as json_err:
            print(f"DATABASE JSON ERROR: {json_err}")
            return None
            
    except Exception as e:
        print(f"DATABASE INITIALIZATION FAILED: {e}")
        return None

# CRITICAL: We initialize 'db' as None first so the server doesn't crash on import
db = None
try:
    db = get_db()
except:
    print("CRITICAL: Final DB fallback triggered")
    db = None
