from pydantic import BaseModel, Field
import uvicorn
import socket
import argparse
from typing import Dict
import os

from app import create_app
from model.gemini_utils import gemini_api_certification

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
PUBLIC_IP = os.getenv('PUBLIC_IP', None)

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip_address = s.getsockname()[0]
    s.close()
except Exception:
    ip_address = "127.0.0.1"
    print("외부 IP 주소를 찾을 수 없습니다. 로컬 주소로 서버를 시작합니다.")

print("=" * 60)
print("FastAPI 서버를 시작합니다. 다른 기기에서 접속하여 테스트하세요.")
print(f"   - 로컬 접속: http://127.0.0.1:{PORT}")
print(f"   - 외부 접속 (Docker IP): http://{ip_address}:{PORT}")
if PUBLIC_IP is not None:
    print(f"   - 외부 접속 (Public IP): http://{PUBLIC_IP}:{PORT}")
print(f"   - API 문서 (Swagger UI): http://{ip_address}:{PORT}/docs")
print("=" * 60)
print("서버를 중지하려면 CTRL+C를 누르세요.")

gemini_api_certification()

# FastAPI 앱 인스턴스 생성
app = create_app()