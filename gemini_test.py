import os
import google.generativeai as genai
from google.oauth2 import service_account

from config.base import settings

credentials = service_account.Credentials.from_service_account_file(
    settings.GOOGLE_APPLICATION_CREDENTIALS
)

# genai.configure(api_key=os.environ['GOOGLE_API_KEY'])
# genai.configure(api_key=settings.GEMINI_API_KEY)
genai.configure(credentials=credentials)

print(f" ================ ")
print("사용 가능한 생성 모델 목록:")
for m in genai.list_models():
  if 'generateContent' in m.supported_generation_methods:
    print(f"- {m.name}")
print(f" ================ ")

model_name = 'gemini-2.5-pro' # 'gemini-2.0-flash' # 'gemini-2.5-pro'
print(' - Model name:', model_name)
model = genai.GenerativeModel(model_name)

query = "AI가 무엇인지 한 문장으로 설명해 줘."
print(' - Query:', query)

generation_config = genai.GenerationConfig(
    # max_output_tokens=400,
    top_k=40, #2,
    top_p=1.0, #0.5,
    temperature=1.0, #0.5,
    # response_mime_type='application/json',
    stop_sequences=None, #['\n'],
)

response = model.generate_content(
    query,
    generation_config=generation_config
)
print(' --- Response ---\n', response.text)