from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os 

from .api_routers import gemini_test

def create_app() -> FastAPI:

    app = FastAPI(
        title="API Server",
        description="A simple API server for demonstration",
        version="1.0.0"
    )

    # CORS 미들웨어 설정
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  
        allow_credentials=True,
        allow_methods=["*"],  
        allow_headers=["*"],  
    )

    app.mount("/static", StaticFiles(directory="static"), name="static")

    app.include_router(gemini_test.router)

    return app
