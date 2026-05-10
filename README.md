# Aizoh (አይዞህ) - Mental Health Awareness Chatbot

A supportive, culturally sensitive, Amharic-speaking mental health chatbot powered by Gemini 2.5 Flash-Lite and Next.js.

## Core Features
- **Telegram Authentication**: Secure login using the Telegram Widget with verified phone number capture.
- **Safety First**: Real-time crisis detection layer that triggers Ethiopian emergency hotlines (822) and alerts an administrator immediately.
- **Amharic Persona**: Communicates using culturally appropriate idioms and a supportive, non-medical tone.
- **Real-time Streaming**: Instant responses using Gemini's streaming capabilities, optimized for Vercel.
- **Firebase Backend**: Secure storage for user profiles and safety logs using Firestore.

## Setup Instructions

### 1. Environment Variables
Create a `.env` file in the root directory (based on the provided `.env.example` or the one created during setup):
```env
TELEGRAM_BOT_TOKEN=your_token
GEMINI_API_KEY=your_key
FIREBASE_SERVICE_ACCOUNT_JSON=your_json_string_or_base64
ADMIN_TELEGRAM_ID=your_id
```

### 2. Local Development
#### Frontend
```bash
npm install
npm run dev
```

#### Backend (Optional for local testing)
```bash
pip install -r requirements.txt
uvicorn api.index:app --reload
```

### 3. Deployment
Deploy directly to **Vercel**:
1. Connect your GitHub/GitLab repository.
2. Add the environment variables in the Vercel dashboard.
3. Vercel will automatically handle the Next.js frontend and the FastAPI backend in the `api/` directory.

## Safety & Ethics
- This bot is **not** a replacement for professional medical care.
- It includes a clear Terms of Service in Amharic.
- Privacy is balanced with safety via the Telegram phone number verification.

## License
MIT
