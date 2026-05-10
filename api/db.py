import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
import base64
from dotenv import load_dotenv

load_dotenv()

def get_db():
    if not firebase_admin._apps:
        service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
        if not service_account_json:
            # Fallback for local development if file exists
            if os.path.exists("firebase-service-account.json"):
                cred = credentials.Certificate("firebase-service-account.json")
            else:
                raise ValueError("FIREBASE_SERVICE_ACCOUNT_JSON environment variable or file is missing")
        else:
            try:
                # Handle base64 encoded JSON (common for Vercel env vars)
                decoded_json = base64.b64decode(service_account_json).decode('utf-8')
                cred_dict = json.loads(decoded_json)
                cred = credentials.Certificate(cred_dict)
            except Exception:
                # Handle plain JSON string
                cred_dict = json.loads(service_account_json)
                cred = credentials.Certificate(cred_dict)
        
        firebase_admin.initialize_app(cred)
    
    return firestore.client()

db = get_db()
