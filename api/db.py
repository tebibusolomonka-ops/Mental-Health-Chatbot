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
        
        # Clean the JSON string (sometimes Vercel adds extra quotes or escaping)
        cred_json = cred_json.strip()
        if cred_json.startswith("'") and cred_json.endswith("'"):
            cred_json = cred_json[1:-1]
        
        cred_dict = json.loads(cred_json)
        cred = credentials.Certificate(cred_dict)
        
        firebase_admin.initialize_app(cred)
        return firestore.client()
    except Exception as e:
        print(f"DATABASE INITIALIZATION FAILED: {e}")
        return None

db = get_db()
