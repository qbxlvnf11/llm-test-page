import google.generativeai as genai
from google.oauth2 import service_account

from config.base import settings

def gemini_api_certification():
    # --- Gemini API 인증 및 초기화 ---
    try:
        credentials = service_account.Credentials.from_service_account_file(
            settings.GOOGLE_APPLICATION_CREDENTIALS_PATH
        )
        genai.configure(credentials=credentials)
        print("✅ Gemini API has been initialized successfully.")
    except Exception as e:
        print(f"🔥 Failed to initialize Gemini API: {e}")