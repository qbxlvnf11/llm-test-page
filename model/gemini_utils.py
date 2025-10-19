import time

import google.generativeai as genai
from google.oauth2 import service_account
import google.generativeai as genai
from google.generativeai.types import generation_types

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

def get_model(model_name, max_output_tokens, top_k, top_p, temperature):

    model = genai.GenerativeModel(model_name)

    generation_config = genai.types.GenerationConfig(
        max_output_tokens=max_output_tokens,
        top_k=top_k,
        top_p=top_p,
        temperature=temperature,
    )

    return model, generation_config

def generate(model, generation_config, query, stream):
    
    start_time = time.perf_counter()
    response = model.generate_content(
        query,
        generation_config=generation_config,
        stream=stream
    )

    return response, start_time